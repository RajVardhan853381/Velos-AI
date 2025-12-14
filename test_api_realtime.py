"""
Quick test to verify API responses are unique for different inputs
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

# Test 1: Junior developer
test1_resume = """
Sarah Johnson
Email: sarah@email.com
Phone: 555-1234

SOFTWARE DEVELOPER

EXPERIENCE:
ABC Tech (2021-2024) - 3 years
- Built web applications using React and Node.js
- Worked on user authentication features
- Fixed bugs in production systems

SKILLS: JavaScript, React, Node.js, HTML, CSS, Git

EDUCATION:
Bachelor of Science in Computer Science, 2021
"""

# Test 2: Senior engineer with different skills
test2_resume = """
Michael Chen
Email: mchen@email.com
Phone: 555-5678

SENIOR SOFTWARE ENGINEER

WORK HISTORY:
Google (2015-2020) - Senior Engineer - 5 years
- Led team of 8 engineers building distributed systems
- Architected microservices handling 1M requests/sec
- Mentored junior developers

Microsoft (2020-2024) - Principal Engineer - 4 years  
- Designed cloud infrastructure solutions
- Reduced deployment time by 70%

TECHNICAL SKILLS: Python, Java, Kubernetes, AWS, Terraform, Docker

EDUCATION:
PhD in Computer Science, Stanford University, 2015
"""

job_desc = "We need a software engineer with at least 2 years of experience"

print("=" * 70)
print("TESTING: Are responses real-time and unique for different inputs?")
print("=" * 70)

print("\\n[TEST 1] Sending resume #1 (Junior: 3 years, React/Node.js)...")
start1 = time.time()
response1 = requests.post(
    f"{API_BASE}/api/verify",
    json={"resume_text": test1_resume, "job_description": job_desc},
    timeout=30
)
elapsed1 = time.time() - start1
result1 = response1.json()

print(f"  ✅ Response received in {elapsed1:.1f}s")
print(f"  Candidate ID: {result1.get('id')}")
print(f"  Status: {result1.get('status')}")
print(f"  Years Experience: {result1.get('years_exp', 'N/A')}")
print(f"  Trust Score: {result1.get('trust_score')}")
print(f"  Simulation Mode: {result1.get('simulation_mode', False)}")
print(f"  Questions ({len(result1.get('questions', []))}): {result1.get('questions', ['None'])[0][:80]}...")

time.sleep(2)

print("\\n[TEST 2] Sending resume #2 (Senior: 9 years, Python/Java/K8s)...")
start2 = time.time()
response2 = requests.post(
    f"{API_BASE}/api/verify",
    json={"resume_text": test2_resume, "job_description": job_desc},
    timeout=30
)
elapsed2 = time.time() - start2
result2 = response2.json()

print(f"  ✅ Response received in {elapsed2:.1f}s")
print(f"  Candidate ID: {result2.get('id')}")
print(f"  Status: {result2.get('status')}")
print(f"  Years Experience: {result2.get('years_exp', 'N/A')}")
print(f"  Trust Score: {result2.get('trust_score')}")
print(f"  Simulation Mode: {result2.get('simulation_mode', False)}")
print(f"  Questions ({len(result2.get('questions', []))}): {result2.get('questions', ['None'])[0][:80]}...")

print("\\n" + "=" * 70)
print("RESULTS COMPARISON:")
print("=" * 70)

# Check uniqueness
different_ids = result1.get('id') != result2.get('id')
different_years = result1.get('years_exp') != result2.get('years_exp')
different_questions = result1.get('questions', [None])[0] != result2.get('questions', [None])[0]
different_scores = result1.get('trust_score') != result2.get('trust_score')

simulation1 = result1.get('simulation_mode', False)
simulation2 = result2.get('simulation_mode', False)

print(f"✓ Different Candidate IDs: {different_ids} ({result1.get('id')} vs {result2.get('id')})")
print(f"✓ Different Years Extracted: {different_years} ({result1.get('years_exp')} vs {result2.get('years_exp')} years)")
print(f"✓ Different Trust Scores: {different_scores} ({result1.get('trust_score')} vs {result2.get('trust_score')})")
print(f"✓ Different Questions: {different_questions}")
print(f"\\nUsing Real AI: {not simulation1 and not simulation2}")

if simulation1 or simulation2:
    print("\\n⚠️  WARNING: Responses are in SIMULATION MODE (not using real AI)")
    print("   This means GROQ LLM is not being called - questions will be identical")
else:
    print("\\n✅ SUCCESS: Responses are REAL-TIME from AI models")
    print("   Each resume gets unique analysis based on actual content!")

if different_years and different_questions and not (simulation1 or simulation2):
    print("\\n🎉 PASS: API is working correctly with real-time, unique responses!")
else:
    print("\\n❌ FAIL: Responses are still identical or using simulation mode")

