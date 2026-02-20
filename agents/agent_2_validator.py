"""
Agent 2: Skill Validator
Matches anonymized candidate skills against job description.
Uses semantic matching - operates ONLY on clean data (no PII).
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dotenv import load_dotenv

load_dotenv()

# Import with fallback
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except Exception as e:
    EMBEDDINGS_AVAILABLE = False
    SentenceTransformer = None  # type: ignore
    np = None  # type: ignore
    print(f"⚠️ sentence-transformers not available ({e}). Using keyword matching.")


class SkillValidator:
    """
    Agent 2: Skill Validator
    
    Responsibilities:
    1. Validate the clean data token (verify it came from Agent 1)
    2. Parse job description requirements
    3. Calculate semantic skill match score
    4. Pass/Fail based on threshold
    
    Key principle: Only sees anonymized data - can't be biased.
    """
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        
        if api_key and ChatGroq:
            self.llm = ChatGroq(
                temperature=0.2,  # Slightly creative for natural responses
                api_key=api_key,  # type: ignore[arg-type]
                model="llama-3.3-70b-versatile"  # Updated from decommissioned llama-3.1-70b
            )
        else:
            self.llm = None
        
        # Initialize embeddings model for semantic matching
        if EMBEDDINGS_AVAILABLE and SentenceTransformer is not None:
            try:
                # Try to load from cache, don't download if not available
                self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder="/tmp/sentence_transformers")
                print("✅ Semantic matching enabled")
            except Exception as e:
                print(f"⚠️ Could not load embeddings model (may need download), continuing without semantic matching: {e}")
                self.embeddings_model = None
        else:
            self.embeddings_model = None
            print("⚠️ Semantic matching not available")
        
        self.audit_log = []
        self.pass_threshold = 60  # Minimum score to pass
    
    def validate_clean_token(self, token: str) -> Tuple[bool, str]:
        """
        Verify token came from Gatekeeper (Agent 1).
        Token must start with "CLEAN-" and be proper length.
        """
        if not token:
            return False, "No token provided"
        
        if not token.startswith("CLEAN-"):
            return False, "Invalid token prefix (must start with CLEAN-)"
        
        if len(token) != 22:  # "CLEAN-" (6) + 16 char hash
            return False, f"Invalid token length: {len(token)} (expected 22)"
        
        return True, "Token validated successfully"
    
    def extract_job_requirements(self, job_description: str) -> Dict:
        """
        Extract key requirements from job description using LLM.
        Falls back to keyword extraction if LLM unavailable.
        """
        
        if self.llm:
            prompt = f"""Analyze this job description and extract:
1. required_skills: List of MUST-HAVE technical skills
2. nice_to_have: List of preferred but not required skills  
3. min_years: Minimum years of experience (number only, 0 if not specified)
4. role_level: junior/mid/senior/lead based on description

Return ONLY valid JSON, no other text:
{{
    "required_skills": ["skill1", "skill2"],
    "nice_to_have": ["skill3"],
    "min_years": 2,
    "role_level": "mid"
}}

Job Description:
{job_description[:1500]}
"""
            try:
                response = self.llm.invoke(prompt)
                content = str(response.content).strip()
                
                # Try to extract JSON from response
                if "{" in content and "}" in content:
                    json_start = content.index("{")
                    json_end = content.rindex("}") + 1
                    json_str = content[json_start:json_end]
                    return json.loads(json_str)
            except Exception as e:
                print(f"⚠️ LLM JD parsing failed: {e}")
        
        # Fallback: Simple keyword extraction
        return self._extract_requirements_regex(job_description)
    
    def _extract_requirements_regex(self, jd: str) -> Dict:
        """Fallback JD parsing using keywords"""
        
        common_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular',
            'node.js', 'sql', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'machine learning', 'deep learning', 'nlp', 'llm', 'genai',
            'fastapi', 'django', 'flask', 'tensorflow', 'pytorch',
            'git', 'ci/cd', 'agile', 'scrum'
        ]
        
        jd_lower = jd.lower()
        found_skills = [s for s in common_skills if s in jd_lower]
        
        # Determine level
        role_level = "mid"
        if any(word in jd_lower for word in ["senior", "sr.", "lead", "principal"]):
            role_level = "senior"
        elif any(word in jd_lower for word in ["junior", "jr.", "entry", "intern"]):
            role_level = "junior"
        
        return {
            "required_skills": found_skills[:8],  # Top 8
            "nice_to_have": [],
            "min_years": 2 if role_level == "mid" else (4 if role_level == "senior" else 0),
            "role_level": role_level
        }
    
    def calculate_semantic_score(self, candidate_skills: List[str], 
                                  required_skills: List[str]) -> float:
        """
        Calculate semantic similarity between candidate skills and requirements.
        Uses embeddings if available, else keyword matching.
        """
        
        if not required_skills:
            return 75.0  # No specific requirements = good but not perfect match
        
        if not candidate_skills:
            return 0.0  # No skills = fail
        
        if self.embeddings_model and np is not None:
            try:
                # Create skill descriptions
                candidate_text = ", ".join(candidate_skills)
                required_text = ", ".join(required_skills)
                
                # Get embeddings
                embeddings = self.embeddings_model.encode([candidate_text, required_text])
                
                # Calculate cosine similarity
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
                
                # Convert to 0-100 scale with more variation
                # Similarity typically ranges 0.4-0.95 for tech skills
                # Map: 0.0->0, 0.4->28, 0.6->58, 0.8->86, 0.95->100
                score = min(100, max(0, (similarity - 0.4) * 72 + 60))
                return round(score, 1)
            except Exception as e:
                print(f"⚠️ Semantic matching failed: {e}")
        
        # Fallback: Simple keyword matching
        return self._calculate_keyword_score(candidate_skills, required_skills)
    
    def _calculate_keyword_score(self, candidate_skills: List[str],
                                  required_skills: List[str]) -> float:
        """Fallback: Simple keyword overlap scoring"""
        
        candidate_lower = set(s.lower() for s in candidate_skills)
        
        matches = 0
        for req in required_skills:
            req_lower = req.lower()
            # Check for exact match or partial match
            if req_lower in candidate_lower:
                matches += 1
            elif any(req_lower in c or c in req_lower for c in candidate_lower):
                matches += 0.5
        
        if not required_skills:
            return 100.0
        
        return round((matches / len(required_skills)) * 100, 1)
    
    def calculate_project_bonus(self, projects: List[str], 
                                required_skills: List[str]) -> float:
        """
        Calculate bonus points for relevant projects.
        Max bonus: 20 points
        """
        if not projects:
            return 0.0
        
        bonus = 0.0
        projects_text = " ".join(projects).lower()
        
        # Check if projects mention required skills
        for skill in required_skills:
            if skill.lower() in projects_text:
                bonus += 3
        
        # Base points for having projects
        bonus += min(len(projects) * 2, 8)
        
        return min(bonus, 20.0)
    
    def _get_skill_evidence(self, skill: str, vector_store: Any, 
                             candidate_id: str) -> Dict[str, Any]:
        """
        Query vector store for evidence of a specific skill.
        Returns context snippets and citations.
        """
        evidence = {
            "skill": skill,
            "found": False,
            "citations": [],
            "context_snippets": [],
            "confidence": 0.0
        }
        
        if not vector_store or not candidate_id:
            return evidence
        
        try:
            # Query vector store for skill-related context
            results = vector_store.get_context_with_scores(
                query=f"{skill} experience project work",
                candidate_id=candidate_id,
                k=3
            )
            
            if results:
                evidence["found"] = True
                for chunk, score in results:
                    if score > 0.3:  # Relevance threshold
                        evidence["context_snippets"].append({
                            "text": chunk[:300] + "..." if len(chunk) > 300 else chunk,
                            "relevance_score": round(score, 3)
                        })
                        # Extract citation (first 50 chars as reference)
                        citation = chunk[:50].strip().replace("\n", " ")
                        evidence["citations"].append(f'"{citation}..."')
                
                # Calculate confidence based on best score
                if results:
                    evidence["confidence"] = round(max(s for _, s in results) * 100, 1)
        except Exception as e:
            print(f"⚠️ Evidence lookup failed for '{skill}': {e}")
        
        return evidence
    
    def process(self, clean_data: Dict, job_description: str, 
                clean_token: str, vector_store: Any = None,
                candidate_id: str = "") -> Dict:
        """
        MAIN VALIDATOR LOGIC - Evidence-Based Verification
        
        Process flow:
        1. Validate token (verify clean data)
        2. Parse JD requirements
        3. Evidence Loop: Query vector store for each skill
        4. Calculate skill match score with evidence weighting
        5. Add project bonus
        6. Pass/Fail based on threshold
        
        Args:
            clean_data: Anonymized data from Agent 1
            job_description: Job description text
            clean_token: Token from Agent 1
            vector_store: ResumeVectorStore instance for RAG
            candidate_id: Unique candidate identifier for filtering
            
        Returns:
            {
                "status": "PASS" or "FAIL",
                "reason": explanation,
                "score": 0-100,
                "missing_skills": list,
                "matched_skills": list,
                "skill_evidence": dict with citations,
                "jd_requirements": dict,
                "audit_log": list
            }
        """
        
        # Reset audit log for this run
        self.audit_log = []

        audit_entry: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "agent": "SkillValidator",
            "action": "Processing clean data with evidence-based verification"
        }
        
        # ============ STEP 1: Validate Token ============
        print("🎯 Agent 2: Validating token...")
        token_valid, token_msg = self.validate_clean_token(clean_token)
        audit_entry["token_validation"] = {
            "valid": token_valid,
            "message": token_msg
        }
        
        if not token_valid:
            audit_entry["decision"] = "REJECTED"
            audit_entry["rejection_reason"] = "Invalid token"
            self.audit_log.append(audit_entry)
            
            return {
                "status": "FAIL",
                "reason": f"❌ Token validation failed: {token_msg}",
                "score": 0,
                "audit_log": self.audit_log
            }
        
        # ============ STEP 2: Parse JD Requirements ============
        print("🎯 Agent 2: Parsing job requirements...")
        jd_requirements = self.extract_job_requirements(job_description)
        print(f"   Required skills found: {jd_requirements.get('required_skills', [])}")
        print(f"   Role level: {jd_requirements.get('role_level', 'unknown')}")
        audit_entry["jd_parsed"] = jd_requirements
        
        # ============ STEP 3: Evidence Loop - RAG Lookup ============
        print("🎯 Agent 2: Gathering evidence from resume...")
        candidate_skills = clean_data.get("skills", [])
        required_skills = jd_requirements.get("required_skills", [])
        
        skill_evidence: Dict[str, Any] = {}
        evidence_boost = 0.0
        
        if vector_store and candidate_id:
            print(f"   📚 Querying vector store for {len(required_skills)} required skills...")
            for skill in required_skills:
                evidence = self._get_skill_evidence(skill, vector_store, candidate_id)
                skill_evidence[skill] = evidence
                
                # Boost score for skills with strong evidence
                if evidence["found"] and evidence["confidence"] > 50:
                    evidence_boost += 2  # +2 points per well-evidenced skill
                    print(f"   ✓ Found evidence for '{skill}' (confidence: {evidence['confidence']}%)")
                elif evidence["found"]:
                    print(f"   ~ Weak evidence for '{skill}' (confidence: {evidence['confidence']}%)")
                else:
                    print(f"   ✗ No evidence found for '{skill}'")
        
        audit_entry["skill_evidence"] = skill_evidence
        audit_entry["evidence_boost"] = evidence_boost
        
        # ============ STEP 4: Calculate Skill Match ============
        print("🎯 Agent 2: Calculating skill match...")
        
        base_score = self.calculate_semantic_score(candidate_skills, required_skills)
        audit_entry["base_skill_score"] = base_score
        
        # ============ STEP 5: Calculate Project Bonus ============
        projects = clean_data.get("projects", [])
        project_bonus = self.calculate_project_bonus(projects, required_skills)
        audit_entry["project_bonus"] = project_bonus
        
        # ============ STEP 6: Final Score (with evidence boost) ============
        final_score = min(base_score + project_bonus + evidence_boost, 100)
        audit_entry["final_score"] = final_score
        
        # Find missing and matched skills
        candidate_lower = set(s.lower() for s in candidate_skills)
        matched = [s for s in required_skills if s.lower() in candidate_lower]
        missing = [s for s in required_skills if s.lower() not in candidate_lower]
        
        # Also mark skills as matched if we found evidence for them
        for skill in missing[:]:  # Copy to avoid modifying during iteration
            if skill in skill_evidence and skill_evidence[skill].get("found"):
                if skill_evidence[skill].get("confidence", 0) > 40:
                    matched.append(skill)
                    missing.remove(skill)
        
        audit_entry["matched_skills"] = matched
        audit_entry["missing_skills"] = missing
        
        # ============ STEP 7: Decision ============
        if final_score >= self.pass_threshold:
            status = "PASS"
            reason = f"✅ {final_score:.0f}% skill match ({self.pass_threshold}% threshold)"
            audit_entry["decision"] = "APPROVED"
        else:
            status = "FAIL"
            reason = f"❌ {final_score:.0f}% skill match (minimum {self.pass_threshold}% required)"
            audit_entry["decision"] = "REJECTED"
            audit_entry["rejection_reason"] = "Insufficient skill match"
        
        self.audit_log.append(audit_entry)
        
        return {
            "status": status,
            "reason": reason,
            "score": round(final_score),
            "base_score": round(base_score),
            "project_bonus": round(project_bonus),
            "evidence_boost": round(evidence_boost),
            "missing_skills": missing,
            "matched_skills": matched,
            "skill_evidence": skill_evidence,
            "jd_requirements": jd_requirements,
            "audit_log": self.audit_log
        }
    
    def get_audit_summary(self) -> str:
        """Generate human-readable audit summary"""
        if not self.audit_log:
            return "No processing done yet."
        
        latest = self.audit_log[-1]
        summary = f"""
🎯 **Agent 2: Skill Validator Audit**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Timestamp**: {latest.get('timestamp', 'N/A')}
**Decision**: {latest.get('decision', 'N/A')}
**Final Score**: {latest.get('final_score', 0):.0f}%
**Base Skill Score**: {latest.get('base_skill_score', 0):.0f}%
**Project Bonus**: {latest.get('project_bonus', 0):.0f}%
**Matched Skills**: {len(latest.get('matched_skills', []))}
**Missing Skills**: {len(latest.get('missing_skills', []))}
"""
        return summary


# Quick test
if __name__ == "__main__":
    validator = SkillValidator()
    
    # Simulated clean data (what Agent 1 would pass)
    clean_data = {
        "skills": ["python", "fastapi", "langchain", "rag", "aws", "docker", "sql"],
        "projects": [
            "Built RAG system for document Q&A",
            "Developed LLM fine-tuning pipeline"
        ],
        "education_level": ["Bachelor's"],
        "certifications": ["AWS Certified"]
    }
    
    job_description = """
    Senior AI Engineer
    
    We're looking for an experienced AI Engineer to join our team.
    
    Requirements:
    - 3+ years of Python development
    - Experience with LLMs and RAG systems
    - FastAPI or Django experience
    - AWS or GCP cloud experience
    - Strong SQL skills
    
    Nice to have:
    - LangChain experience
    - Docker/Kubernetes
    - Production ML experience
    """
    
    # Simulated clean token
    clean_token = "CLEAN-ABCD1234EFGH5678"
    
    result = validator.process(clean_data, job_description, clean_token)
    
    print("\n" + "="*50)
    print("AGENT 2 TEST RESULT")
    print("="*50)
    print(f"Status: {result['status']}")
    print(f"Score: {result['score']}%")
    print(f"Reason: {result['reason']}")
    print(f"Matched: {result['matched_skills']}")
    print(f"Missing: {result['missing_skills']}")
