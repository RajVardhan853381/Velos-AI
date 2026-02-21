"""
Agent 1: Blind Gatekeeper
Handles eligibility check and PII anonymization.
First line of defense - removes all bias-inducing information.
"""

import os
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Import with fallback for testing
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

from utils.pii_redactor import PIIRedactor
from utils.experience_extractor import ExperienceExtractor


class BlindGatekeeper:
    """
    Agent 1: The Blind Gatekeeper
    
    Responsibilities:
    1. Extract years of experience from resume
    2. Check eligibility against minimum requirement
    3. Anonymize ALL PII (names, emails, colleges, gender, etc.)
    4. Generate Zynd-style authentication token
    5. Pass only clean data to Agent 2
    
    Key principle: Agent 2 and 3 NEVER see raw PII.
    """
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        
        if api_key and ChatGroq:
            self.llm = ChatGroq(
                temperature=0,
                api_key=api_key,  # type: ignore[arg-type]
                model="llama-3.3-70b-versatile"  # Updated from decommissioned llama-3.1-70b
            )
        else:
            print("⚠️ GROQ_API_KEY not found or ChatGroq unavailable. Using fallback mode.")
            self.llm = None
        
        self.pii_redactor = PIIRedactor()
        self.exp_extractor = ExperienceExtractor(self.llm)
        self.audit_log = []
    
    def generate_clean_data_token(self, resume_hash: str) -> str:
        """
        Generate Zynd-like authentication token.
        This proves the data passed through the gatekeeper and was anonymized.
        
        Token format: CLEAN-{16_char_hash}
        """
        timestamp = datetime.now().isoformat()
        token_base = f"{resume_hash}:{timestamp}:GATEKEEPER_APPROVED:v1"
        token = hashlib.sha256(token_base.encode()).hexdigest()[:16].upper()
        return f"CLEAN-{token}"
    
    def extract_clean_data(self, redacted_text: str) -> Dict:
        """
        Extract only safe data: Skills, Projects, Education type (no PII).
        This is what Agent 2 sees.
        """
        
        # Get skills and projects
        structured = self.pii_redactor.extract_skills_and_projects(redacted_text)
        
        # Extract education level (not specific college)
        education_levels: List[str] = []
        edu_patterns = [
            r"(Bachelor'?s?|B\.?S\.?|B\.?Tech|B\.?E\.?)",
            r"(Master'?s?|M\.?S\.?|M\.?Tech|MBA|M\.?E\.?)",
            r"(Ph\.?D\.?|Doctorate)",
            r"(Associate'?s?|Diploma)",
        ]
        
        for pattern in edu_patterns:
            match = re.search(pattern, redacted_text, re.IGNORECASE)
            if match:
                education_levels.append(match.group(1))
        
        # Extract certifications (safe to pass)
        cert_patterns = [
            r"(AWS Certified[^,\n]+)",
            r"(Google Cloud[^,\n]+)",
            r"(Azure[^,\n]+Certified)",
            r"(PMP|Scrum Master|CISSP)",
        ]
        
        certifications = []
        for pattern in cert_patterns:
            matches = re.findall(pattern, redacted_text, re.IGNORECASE)
            certifications.extend(matches)
        
        return {
            "skills": structured["skills"],
            "projects": structured["projects"],
            "education_level": list(set(education_levels)),
            "certifications": list(set(certifications))[:5]
        }
    
    def detect_bias_indicators(self, text: str) -> List[Dict]:
        """
        Detect potential bias indicators in resume.
        Returns list of flagged items for audit.
        """
        flags = []
        
        # Age indicators — only flag plausible birth years (1940-1989),
        # NOT employment/graduation years like 2016-2024
        if re.search(r'\b(19[4-8]\d)\b', text):
            flags.append({
                "type": "age",
                "description": "Possible birth year detected",
                "action": "Redacted"
            })
        
        # Gender indicators
        gender_words = ["he/him", "she/her", "mr.", "mrs.", "ms."]
        for word in gender_words:
            if word.lower() in text.lower():
                flags.append({
                    "type": "gender",
                    "description": f"Gender indicator '{word}' detected",
                    "action": "Redacted"
                })
        
        # Elite college mentions (can introduce bias)
        elite_colleges = ["IIT", "Stanford", "MIT", "Harvard", "Ivy League"]
        for college in elite_colleges:
            if college.lower() in text.lower():
                flags.append({
                    "type": "education_prestige",
                    "description": f"Elite institution '{college}' detected",
                    "action": "Redacted"
                })
        
        return flags
    
    def process(self, raw_resume_text: str, min_years: float = 2.0) -> Dict:
        """
        MAIN GATEKEEPER LOGIC
        
        Process flow:
        1. Extract years of experience
        2. Check eligibility (>= min_years)
        3. If eligible: Anonymize PII
        4. Generate clean data token
        5. Return clean data OR rejection
        
        Args:
            raw_resume_text: Raw resume text (with PII)
            min_years: Minimum years of experience required
            
        Returns:
            {
                "status": "PASS" or "FAIL",
                "reason": explanation,
                "years_exp": float,
                "clean_data": dict (only if PASS),
                "clean_data_full_text": str (redacted text, only if PASS),
                "clean_token": str (Zynd auth token, only if PASS),
                "bias_flags": list (detected bias indicators),
                "redaction_stats": dict (PII redaction counts),
                "audit_log": list
            }
        """
        
        # Reset audit log for this run
        self.audit_log = []

        # Initialize audit entry
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "BlindGatekeeper",
            "action": "Processing resume",
            "resume_length": len(raw_resume_text)
        }
        
        # ============ STEP 1: Extract Experience ============
        print("🛡️ Agent 1: Extracting experience...")
        years = self.exp_extractor.extract_years(raw_resume_text)
        audit_entry["years_extracted"] = years
        
        # ============ STEP 2: Check Eligibility ============
        is_eligible, reason = self.exp_extractor.validate_experience(years, min_years)
        audit_entry["eligibility_check"] = {
            "passed": is_eligible,
            "min_required": min_years,
            "actual": years,
            "reason": reason
        }
        
        # If not eligible, reject early (don't waste processing)
        if not is_eligible:
            audit_entry["decision"] = "REJECTED"
            audit_entry["rejection_reason"] = "Insufficient experience"
            self.audit_log.append(audit_entry)
            
            return {
                "status": "FAIL",
                "reason": reason,
                "years_exp": years,
                "bias_flags": [],
                "audit_log": self.audit_log
            }
        
        # ============ STEP 3: Detect Bias Indicators ============
        print("🛡️ Agent 1: Detecting bias indicators...")
        bias_flags = self.detect_bias_indicators(raw_resume_text)
        audit_entry["bias_flags_detected"] = len(bias_flags)
        
        # ============ STEP 4: Anonymize PII ============
        print("🛡️ Agent 1: Anonymizing PII...")
        redacted_text, redaction_stats = self.pii_redactor.redact_pii(raw_resume_text)
        audit_entry["redaction_stats"] = redaction_stats
        audit_entry["pii_redacted"] = True
        
        # ============ STEP 5: Extract Clean Data ============
        clean_data = self.extract_clean_data(raw_resume_text)
        audit_entry["clean_data_extracted"] = {
            "skills_count": len(clean_data["skills"]),
            "projects_count": len(clean_data["projects"])
        }
        
        # ============ STEP 6: Generate Token ============
        resume_hash = hashlib.sha256(raw_resume_text.encode()).hexdigest()
        clean_token = self.generate_clean_data_token(resume_hash)
        audit_entry["token_generated"] = clean_token
        audit_entry["decision"] = "APPROVED"
        
        self.audit_log.append(audit_entry)
        
        return {
            "status": "PASS",
            "reason": f"✅ Eligible: {years:.1f}y experience, PII removed",
            "years_exp": years,
            "clean_data": clean_data,
            "clean_data_full_text": redacted_text,
            "clean_token": clean_token,
            "bias_flags": bias_flags,
            "redaction_stats": redaction_stats,
            "audit_log": self.audit_log
        }
    
    def get_audit_summary(self) -> str:
        """Generate human-readable audit summary"""
        if not self.audit_log:
            return "No processing done yet."
        
        latest = self.audit_log[-1]
        summary = f"""
🛡️ **Agent 1: Blind Gatekeeper Audit**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Timestamp**: {latest.get('timestamp', 'N/A')}
**Decision**: {latest.get('decision', 'N/A')}
**Experience Detected**: {latest.get('years_extracted', 0):.1f} years
**Bias Flags Found**: {latest.get('bias_flags_detected', 0)}
**PII Redacted**: {latest.get('pii_redacted', False)}
**Token**: {latest.get('token_generated', 'N/A')[:20]}...
"""
        return summary


# Quick test
if __name__ == "__main__":
    gatekeeper = BlindGatekeeper()
    
    test_resume = """
    John Doe
    Email: john.doe@example.com
    Phone: 555-123-4567
    Location: San Francisco, CA
    LinkedIn: linkedin.com/in/johndoe
    
    PROFESSIONAL SUMMARY
    3.5 years of experience in AI/ML engineering with expertise in Python and GenAI.
    
    WORK EXPERIENCE
    
    Senior AI Engineer | TechCorp Inc. (2022-2025)
    - Built RAG systems using LangChain and Pinecone
    - Developed production LLM pipelines
    - Tech: Python, FastAPI, AWS
    
    AI Developer | StartupXYZ (2020-2022)
    - Created NLP pipelines for document processing
    - Implemented transformer-based models
    
    EDUCATION
    Bachelor's in Computer Science from IIT Delhi (2020)
    
    SKILLS
    Python, FastAPI, LangChain, RAG, LLMs, AWS, Docker, SQL
    """
    
    result = gatekeeper.process(test_resume, min_years=2.0)
    
    print("\n" + "="*50)
    print("AGENT 1 TEST RESULT")
    print("="*50)
    print(f"Status: {result['status']}")
    print(f"Years: {result['years_exp']}")
    print(f"Reason: {result['reason']}")
    
    if result['status'] == 'PASS':
        print(f"Token: {result['clean_token']}")
        print(f"Skills found: {result['clean_data']['skills']}")
        print(f"Bias flags: {len(result['bias_flags'])}")
        print(f"\nRedacted text preview:")
        print(result['clean_data_full_text'][:300] + "...")
