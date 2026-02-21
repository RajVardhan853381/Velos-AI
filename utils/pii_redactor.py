"""
PII Redactor Utility for Velos
Uses spaCy NER + regex to remove personally identifiable information
"""

import re
import spacy
from typing import Dict, List, Tuple


class PIIRedactor:
    """
    Removes all PII from resume text to enable blind hiring.
    Uses spaCy NER for names and regex for emails, phones, etc.
    """
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("⚠️ spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Regex patterns for PII
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'linkedin': r'linkedin\.com/in/[A-Za-z0-9_-]+',
            'github': r'github\.com/[A-Za-z0-9_-]+',
            'url': r'https?://[^\s]+',
        }
        
        # Universities/colleges to redact (expandable list)
        self.colleges = [
            # Indian
            "IIT", "NIT", "BITS", "IIIT", "Delhi University", "Mumbai University",
            "Anna University", "VIT", "SRM", "AKTU", "Manipal", "Amity",
            "IIM", "ISB", "XLRI", "FMS", "JBIMS",
            # International
            "Stanford", "MIT", "Harvard", "Cambridge", "Oxford", "Princeton",
            "Yale", "Columbia", "Berkeley", "UCLA", "Carnegie Mellon", "Caltech",
            "Georgia Tech", "University of", "College of",
            # Tier indicators
            "Tier-1", "Tier-2", "Tier 1", "Tier 2", "top-tier", "elite",
            "Ivy League", "ivy league"
        ]
        
        # Gendered words and honorifics to redact
        self.gendered_words = [
            "male", "female", "man", "woman", "boy", "girl",
            "he/him", "she/her", "they/them",
            "Mr.", "Mrs.", "Ms.", "Miss", "Dr.",
            "husband", "wife", "father", "mother",
            "son", "daughter", "brother", "sister",
            "his", "her", "hers",
            "maternity", "paternity"
        ]
        
        # Age-related words
        self.age_indicators = [
            "years old", "year old", "age:", "born in", "DOB:",
            "date of birth", "birthday"
        ]
        
        # Religious/ethnic indicators
        self.protected_class_words = [
            "christian", "muslim", "hindu", "jewish", "buddhist", "sikh",
            "church", "mosque", "temple", "synagogue",
            "caste", "tribe", "ethnicity"
        ]

    def extract_names(self, text: str) -> List[str]:
        """Extract person names using NER"""
        if not self.nlp:
            return []
        
        # Process first 1000 chars for efficiency (names usually appear early)
        doc = self.nlp(text[:1000])
        names = []
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                names.append(ent.text)
            # Also catch organization names that might be personal
            elif ent.label_ == "ORG" and len(ent.text.split()) <= 2:
                # Skip if it looks like a company
                if not any(corp in ent.text.lower() for corp in 
                          ["inc", "corp", "ltd", "llc", "company", "tech"]):
                    pass  # Don't add orgs
        
        return list(set(names))

    def redact_pii(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Remove all PII from text.
        
        Returns:
            Tuple of (redacted_text, stats_dict with counts of redactions)
        """
        stats = {
            "emails": 0,
            "phones": 0,
            "names": 0,
            "colleges": 0,
            "gender_refs": 0,
            "age_refs": 0,
            "locations": 0
        }
        
        original_text = text
        
        # 1. Redact emails
        text, count = re.subn(self.patterns['email'], '[EMAIL_REDACTED]', text)
        stats["emails"] = count
        
        # 2. Redact phone numbers
        text, count = re.subn(self.patterns['phone'], '[PHONE_REDACTED]', text)
        stats["phones"] = count
        
        # 3. Redact SSN
        text, count = re.subn(self.patterns['ssn'], '[SSN_REDACTED]', text)
        
        # 4. Redact LinkedIn/GitHub URLs
        text = re.sub(self.patterns['linkedin'], '[LINKEDIN_REDACTED]', text)
        text = re.sub(self.patterns['github'], '[GITHUB_REDACTED]', text)
        
        # 5. Redact names using NER
        names = self.extract_names(original_text)
        for name in names:
            if len(name) > 2:  # Avoid single letters
                text = re.sub(re.escape(name), '[NAME_REDACTED]', text, flags=re.IGNORECASE)
                stats["names"] += 1
        
        # 6. Redact college/university names
        for college in self.colleges:
            if college.lower() in text.lower():
                text = re.sub(re.escape(college), '[COLLEGE_REDACTED]', text, flags=re.IGNORECASE)
                stats["colleges"] += 1
        
        # 7. Redact gendered language
        for word in self.gendered_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)
                stats["gender_refs"] += 1
        
        # 8. Redact age indicators
        for age_word in self.age_indicators:
            if age_word.lower() in text.lower():
                text = re.sub(
                    re.escape(age_word) + r'\s*\d*',
                    '[AGE_REDACTED]',
                    text,
                    flags=re.IGNORECASE
                )
                stats["age_refs"] += 1
        
        # 9. Redact locations (after Location:, Based in:, From:)
        location_patterns = [
            r'(Location|Based in|From|Address|City|State|Country):\s*[A-Za-z\s,]+(?=\n|$)',
            r'(Location|Based in|From|Address|City|State|Country):\s*[A-Za-z\s,]+'
        ]
        for pattern in location_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(
                    pattern,
                    r'\1: [LOCATION_REDACTED]',
                    text,
                    flags=re.IGNORECASE
                )
                stats["locations"] += 1
        
        # 10. Redact protected class references
        for word in self.protected_class_words:
            text = re.sub(r'\b' + re.escape(word) + r'\b', '[REDACTED]', text, flags=re.IGNORECASE)
        
        return text, stats

    def extract_skills_and_projects(self, text: str) -> Dict[str, List[str]]:
        """
        Extract structured data: skills and projects from resume text.
        This is what gets passed to Agent 2 (no PII here).
        """
        
        # Technical skills keywords (case-insensitive matching)
        skills_keywords = [
            # Languages
            'python', 'java', 'javascript', 'typescript', 'rust', 'go', 'golang',
            'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r',
            # Frameworks
            'react', 'angular', 'vue', 'nextjs', 'next.js', 'fastapi', 'django',
            'flask', 'express', 'node.js', 'nodejs', 'spring', 'rails',
            # AI/ML
            'machine learning', 'deep learning', 'neural network', 'tensorflow',
            'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'opencv',
            'nlp', 'natural language', 'computer vision', 'cv',
            # GenAI
            'genai', 'generative ai', 'llm', 'large language model', 'gpt',
            'langchain', 'llamaindex', 'rag', 'retrieval augmented', 'transformer',
            'fine-tuning', 'prompt engineering', 'embeddings', 'vector database',
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
            'terraform', 'jenkins', 'ci/cd', 'github actions', 'gitlab',
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'pinecone', 'weaviate', 'chromadb', 'neo4j', 'dynamodb',
            # Tools
            'git', 'linux', 'unix', 'bash', 'rest api', 'graphql', 'microservices',
            'agile', 'scrum', 'jira'
        ]
        
        # Find skills in text using word boundaries
        skills_found = []
        for skill in skills_keywords:
            escaped_skill = re.escape(skill)
            # Use \b boundaries for alphanumeric skills, allow symbol limits for C++
            if re.match(r'^\w+$', skill):
                pattern = r'\b' + escaped_skill + r'\b'
            else:
                pattern = r'(?:\b|\s)' + escaped_skill + r'(?:\b|\s)'
            if re.search(pattern, text, re.IGNORECASE):
                skills_found.append(skill)
        
        # Extract projects (look for common patterns)
        project_patterns = [
            r'(?:Project|Built|Developed|Created|Implemented|Designed):\s*([^\n]+)',
            r'(?:Project|Built|Developed|Created|Implemented|Designed)\s+([^\n]+?)(?:\n|$)',
            r'•\s*([A-Z][^•\n]+(?:system|app|application|platform|tool|service|api|pipeline|model))',
        ]
        
        projects = []
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            projects.extend(matches)
        
        # Clean up projects
        projects = [p.strip() for p in projects if len(p) > 10][:10]  # Max 10 projects
        
        return {
            "skills": list(set(skills_found)),
            "projects": projects
        }

    def get_redaction_summary(self, original: str, redacted: str, stats: Dict) -> str:
        """Generate a human-readable summary of redactions performed"""
        summary = "📋 **PII Redaction Summary**\n"
        summary += "-" * 30 + "\n"
        
        total = sum(stats.values())
        summary += f"**Total redactions**: {total}\n\n"
        
        for category, count in stats.items():
            if count > 0:
                emoji = {
                    "emails": "📧",
                    "phones": "📱",
                    "names": "👤",
                    "colleges": "🎓",
                    "gender_refs": "⚧",
                    "age_refs": "🎂",
                    "locations": "📍"
                }.get(category, "•")
                summary += f"{emoji} {category.replace('_', ' ').title()}: {count}\n"
        
        return summary
