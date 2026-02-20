"""
Integration Tests for Velos Pipeline
Tests the complete verification flow from resume to decision.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_1_gatekeeper import BlindGatekeeper
from agents.agent_2_validator import SkillValidator
from agents.agent_3_inquisitor import Inquisitor
from agents.orchestrator import VelosOrchestrator
from utils.pii_redactor import PIIRedactor
from utils.experience_extractor import ExperienceExtractor
from database.storage import AuditLog


# Test data
VALID_RESUME = """
John Smith
Email: john.smith@email.com
Phone: 555-987-6543
Location: New York, NY

PROFESSIONAL SUMMARY
3 years of AI/ML engineering experience with Python and LLMs.

WORK EXPERIENCE

AI Engineer | TechCorp (2022-2025)
- Built RAG systems using LangChain
- Deployed LLM pipelines to production
- Tech: Python, FastAPI, AWS

Software Developer | StartupXYZ (2021-2022)
- Developed REST APIs
- Worked with databases
- Tech: Python, PostgreSQL

SKILLS
Python, FastAPI, LangChain, RAG, AWS, SQL, Docker

PROJECTS
Built: Document Q&A system using RAG
Developed: API gateway for ML models

EDUCATION
Bachelor's in Computer Science from MIT (2021)
"""

VALID_JD = """
AI Engineer Position

Requirements:
- 2+ years Python experience
- LLM and RAG experience
- FastAPI or Django
- AWS or cloud experience
- SQL skills
"""


def test_pii_redactor():
    """Test PII redaction functionality"""
    print("\n" + "="*50)
    print("TEST: PII Redactor")
    print("="*50)
    
    redactor = PIIRedactor()
    
    test_text = """
    John Doe
    Email: john@example.com
    Phone: 555-123-4567
    Graduated from Stanford University
    He/Him pronouns
    Location: San Francisco, CA
    """
    
    redacted, stats = redactor.redact_pii(test_text)
    
    # Assertions
    assert "[EMAIL_REDACTED]" in redacted, "Email should be redacted"
    assert "[PHONE_REDACTED]" in redacted, "Phone should be redacted"
    assert "john@example.com" not in redacted, "Original email should not appear"
    assert "555-123-4567" not in redacted, "Original phone should not appear"
    
    print(f"✅ PII Redactor: All tests passed")
    print(f"   Redaction stats: {stats}")
    
    return True


def test_experience_extractor():
    """Test experience extraction functionality"""
    print("\n" + "="*50)
    print("TEST: Experience Extractor")
    print("="*50)
    
    extractor = ExperienceExtractor(llm=None)  # Use regex fallback
    
    test_texts = [
        ("3 years of experience in Python", 3.0),
        ("5+ years of ML experience", 5.0),
        ("2022-2025: Software Engineer", 3.0),
    ]
    
    for text, expected_min in test_texts:
        years = extractor.extract_years(text)
        assert years >= expected_min - 1, f"Expected at least {expected_min-1} years, got {years}"
        print(f"   '{text[:30]}...' → {years} years ✓")
    
    # Test validation
    is_valid, reason = extractor.validate_experience(3.0, 2.0)
    assert is_valid == True, "3 years should pass 2 year requirement"
    
    is_valid, reason = extractor.validate_experience(1.0, 2.0)
    assert is_valid == False, "1 year should fail 2 year requirement"
    
    print(f"✅ Experience Extractor: All tests passed")
    
    return True


def test_blind_gatekeeper():
    """Test Agent 1: Blind Gatekeeper"""
    print("\n" + "="*50)
    print("TEST: Agent 1 - Blind Gatekeeper")
    print("="*50)
    
    gatekeeper = BlindGatekeeper()
    
    # Test with valid resume
    result = gatekeeper.process(VALID_RESUME, min_years=2.0)
    
    assert result["status"] == "PASS", f"Valid resume should PASS, got {result['status']}"
    assert result["years_exp"] >= 2.0, f"Should detect at least 2 years exp"
    assert "clean_token" in result, "Should generate clean token"
    assert result["clean_token"].startswith("CLEAN-"), "Token should start with CLEAN-"
    assert "clean_data" in result, "Should return clean_data"
    assert "skills" in result["clean_data"], "Clean data should have skills"
    
    print(f"✅ Valid resume: PASS (years={result['years_exp']}, token={result['clean_token'][:15]}...)")
    
    # Test with insufficient experience
    junior_resume = "Entry level developer. Internship in 2024."
    result_fail = gatekeeper.process(junior_resume, min_years=3.0)
    
    assert result_fail["status"] == "FAIL", "Junior resume should FAIL"
    
    print(f"✅ Junior resume: FAIL (correctly rejected)")
    
    print(f"✅ Agent 1: All tests passed")
    
    return True


def test_skill_validator():
    """Test Agent 2: Skill Validator"""
    print("\n" + "="*50)
    print("TEST: Agent 2 - Skill Validator")
    print("="*50)
    
    validator = SkillValidator()
    
    # Test with matching skills
    clean_data = {
        "skills": ["python", "fastapi", "rag", "aws", "sql"],
        "projects": ["Built RAG system", "Created API gateway"],
        "education_level": ["Bachelor's"]
    }
    
    clean_token = "CLEAN-1234567890ABCDEF"
    
    result = validator.process(clean_data, VALID_JD, clean_token)
    
    assert "status" in result, "Should return status"
    assert "score" in result, "Should return score"
    assert result["score"] > 0, "Score should be positive"
    
    print(f"✅ Skill matching: Score={result['score']}%, Status={result['status']}")
    
    # Test with invalid token
    result_bad_token = validator.process(clean_data, VALID_JD, "INVALID-TOKEN")
    
    assert result_bad_token["status"] == "FAIL", "Invalid token should fail"
    
    print(f"✅ Invalid token: Correctly rejected")
    
    print(f"✅ Agent 2: All tests passed")
    
    return True


def test_inquisitor():
    """Test Agent 3: Inquisitor"""
    print("\n" + "="*50)
    print("TEST: Agent 3 - Inquisitor")
    print("="*50)
    
    inquisitor = Inquisitor()
    
    clean_data = {
        "skills": ["python", "fastapi", "rag", "aws"],
        "projects": ["Built RAG system for Q&A"]
    }
    
    # Test question generation
    result = inquisitor.process(clean_data, num_questions=3)
    
    assert result["status"] == "READY", "Should be ready to ask questions"
    assert "questions" in result, "Should have questions"
    assert len(result["questions"]) > 0, "Should generate at least 1 question"
    
    print(f"✅ Generated {len(result['questions'])} questions")
    for i, q in enumerate(result["questions"][:2], 1):
        print(f"   Q{i}: {q[:60]}...")
    
    # Test answer evaluation
    qa_pairs = [
        {
            "question": result["questions"][0] if result["questions"] else "Tell about your project",
            "answer": "I built a RAG system using LangChain. The main challenge was chunking - I experimented with different sizes and found 800 tokens optimal. Used Pinecone for vector storage and implemented re-ranking for better relevance."
        }
    ]
    
    eval_result = inquisitor.evaluate_candidate_answers(clean_data, qa_pairs)
    
    assert "authenticity_score" in eval_result, "Should have authenticity score"
    assert eval_result["authenticity_score"] >= 0, "Score should be non-negative"
    
    print(f"✅ Answer evaluation: Score={eval_result['authenticity_score']}%, Verdict={eval_result.get('verdict', 'N/A')}")
    
    print(f"✅ Agent 3: All tests passed")
    
    return True


def test_database():
    """Test SQLite database storage"""
    print("\n" + "="*50)
    print("TEST: Database Storage")
    print("="*50)
    
    import tempfile
    
    # Create temp database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = AuditLog(db_path)
    
    # Test candidate creation
    candidate_id = "CAND-TEST1234"
    db.save_candidate(candidate_id)
    
    # Test audit entry
    db.save_audit_entry(candidate_id, {
        "agent": "TestAgent",
        "action": "Test action",
        "decision": "APPROVED"
    })
    
    # Test verification result
    db.save_verification_result(candidate_id, {
        "agent_1_status": "PASS",
        "agent_2_score": 85,
        "final_status": "APPROVED"
    })
    
    # Retrieve and verify
    history = db.get_candidate_history(candidate_id)
    assert len(history) > 0, "Should have audit history"
    
    stats = db.get_pipeline_stats()
    assert "total_candidates" in stats, "Should have stats"
    
    print(f"✅ Database: All operations successful")
    print(f"   Candidates: {stats['total_candidates']}")
    
    # Cleanup
    db.close()
    os.remove(db_path)
    
    return True


def test_full_pipeline():
    """Test complete orchestrated pipeline"""
    print("\n" + "="*50)
    print("TEST: Full Pipeline (Orchestrator)")
    print("="*50)
    
    import tempfile
    
    # Create temp database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    orchestrator = VelosOrchestrator(db_path)
    
    # Run pipeline
    result = orchestrator.run_verification_pipeline(
        VALID_RESUME,
        VALID_JD,
        min_years=2.0
    )
    
    assert "candidate_id" in result, "Should have candidate ID"
    assert result["agent_1_status"] == "PASS", "Agent 1 should pass"
    
    print(f"✅ Pipeline executed:")
    print(f"   Candidate: {result['candidate_id']}")
    print(f"   Agent 1: {result['agent_1_status']} ({result['years_exp']} years)")
    print(f"   Agent 2: {result.get('agent_2_status', 'N/A')} ({result.get('agent_2_score', 0)}%)")
    
    # If questions pending, evaluate
    if result.get("final_status") == "QUESTIONS_PENDING":
        print(f"   Questions: {len(result.get('verification_questions', []))} generated")
        
        # Simulate answers
        qa_pairs = [
            {"question": q, "answer": f"Detailed technical answer about {q.split()[0].lower()}. I implemented this using best practices and thorough testing."}
            for q in result.get("verification_questions", [])[:2]
        ]
        
        if qa_pairs:
            final_result = orchestrator.evaluate_candidate_answers(qa_pairs)
            print(f"   Final: {final_result['final_status']}")
    
    # Cleanup
    orchestrator.audit_db.close()
    os.remove(db_path)
    
    print(f"✅ Full Pipeline: All tests passed")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("VELOS TEST SUITE")
    print("="*60)
    
    tests = [
        ("PII Redactor", test_pii_redactor),
        ("Experience Extractor", test_experience_extractor),
        ("Agent 1 - Gatekeeper", test_blind_gatekeeper),
        ("Agent 2 - Validator", test_skill_validator),
        ("Agent 3 - Inquisitor", test_inquisitor),
        ("Database Storage", test_database),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, "✅ PASS" if passed else "❌ FAIL"))
        except Exception as e:
            results.append((name, f"❌ ERROR: {str(e)[:50]}"))
            print(f"❌ {name}: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, status in results:
        print(f"   {status} - {name}")
    
    passed = sum(1 for _, s in results if "PASS" in s)
    total = len(results)
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Velos is ready to ship! 🚀")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
