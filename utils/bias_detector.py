"""
Advanced Bias Detection Module
Detects and flags potential biases in hiring processes
For ZYND AIckathon 2025 - Fair Hiring Network
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class BiasType(Enum):
    GENDER = "gender"
    AGE = "age"
    RACE = "race"
    EDUCATION = "education_prestige"
    LOCATION = "location"
    NAME = "name_based"
    DISABILITY = "disability"
    RELIGION = "religion"


@dataclass
class BiasFlag:
    """Represents a detected bias"""
    bias_type: BiasType
    severity: str  # "low", "medium", "high"
    original_text: str
    suggested_replacement: str
    confidence: float
    explanation: str


class BiasDetector:
    """
    Detects various types of bias in text
    """
    
    def __init__(self):
        # Gender-biased terms
        self.gender_terms = {
            # Male-coded words
            "rockstar": ("high-performer", "high"),
            "ninja": ("expert", "medium"),
            "guru": ("specialist", "medium"),
            "aggressive": ("assertive", "medium"),
            "dominant": ("leading", "medium"),
            "chairman": ("chairperson", "high"),
            "manpower": ("workforce", "high"),
            "man-hours": ("person-hours", "high"),
            "salesman": ("salesperson", "high"),
            "businessman": ("businessperson", "high"),
            "fireman": ("firefighter", "high"),
            "policeman": ("police officer", "high"),
            "spokesman": ("spokesperson", "high"),
            "manmade": ("artificial", "medium"),
            "mankind": ("humanity", "medium"),
            "cameraman": ("camera operator", "high"),
            "foreman": ("supervisor", "high"),
            "workmanship": ("craftsmanship", "medium"),
        }
        
        # Age-biased terms
        self.age_terms = {
            "young": ("energetic", "high"),
            "youthful": ("dynamic", "high"),
            "digital native": ("tech-savvy", "medium"),
            "recent graduate": ("entry-level candidate", "medium"),
            "fresh": ("new", "low"),
            "mature": ("experienced", "medium"),
            "seasoned": ("experienced", "low"),
            "senior citizen": ("experienced professional", "high"),
            "overqualified": ("highly qualified", "high"),
            "young and hungry": ("motivated", "high"),
            "old school": ("traditional", "medium"),
            "millennial": ("professional", "high"),
            "gen z": ("professional", "high"),
            "boomer": ("experienced professional", "high"),
        }
        
        # Education prestige bias
        self.education_terms = {
            "ivy league": ("top university", "high"),
            "tier-1": ("reputed institution", "high"),
            "tier-2": ("accredited institution", "high"),
            "tier 1": ("reputed institution", "high"),
            "tier 2": ("accredited institution", "high"),
            "iit": ("engineering graduate", "high"),
            "iim": ("management graduate", "high"),
            "nit": ("engineering graduate", "high"),
            "bits": ("engineering graduate", "high"),
            "stanford": ("top university graduate", "high"),
            "mit": ("top university graduate", "high"),
            "harvard": ("top university graduate", "high"),
            "oxford": ("top university graduate", "high"),
            "cambridge": ("top university graduate", "high"),
            "princeton": ("top university graduate", "high"),
            "yale": ("top university graduate", "high"),
            "berkeley": ("top university graduate", "high"),
        }
        
        # Location bias
        self.location_terms = {
            "local candidates only": ("candidates in region preferred", "high"),
            "must be from": ("preferably located in", "medium"),
            "native speaker": ("fluent speaker", "high"),
            "native english": ("fluent in english", "high"),
            "must relocate": ("relocation may be required", "medium"),
            "no remote": ("on-site preferred", "medium"),
        }
        
        # Disability bias
        self.disability_terms = {
            "must be able to lift": ("physical requirements may apply", "medium"),
            "standing required": ("mobility requirements apply", "medium"),
            "physically fit": ("able to perform job duties", "medium"),
            "able-bodied": ("capable of performing duties", "high"),
            "normal": ("standard", "medium"),
        }
        
        # Compile all patterns
        self.all_bias_patterns = {
            BiasType.GENDER: self.gender_terms,
            BiasType.AGE: self.age_terms,
            BiasType.EDUCATION: self.education_terms,
            BiasType.LOCATION: self.location_terms,
            BiasType.DISABILITY: self.disability_terms,
        }
    
    def detect_bias(self, text: str) -> List[BiasFlag]:
        """
        Detect all biases in text
        Returns list of BiasFlag objects
        """
        flags = []
        text_lower = text.lower()
        
        for bias_type, patterns in self.all_bias_patterns.items():
            for term, (replacement, severity) in patterns.items():
                if term.lower() in text_lower:
                    # Find the actual occurrence in text
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    matches = pattern.finditer(text)
                    
                    for match in matches:
                        flags.append(BiasFlag(
                            bias_type=bias_type,
                            severity=severity,
                            original_text=match.group(),
                            suggested_replacement=replacement,
                            confidence=0.85 if severity == "high" else 0.7 if severity == "medium" else 0.5,
                            explanation=self._get_explanation(bias_type, term)
                        ))
        
        return flags
    
    def _get_explanation(self, bias_type: BiasType, term: str) -> str:
        """Get explanation for why a term is biased"""
        explanations = {
            BiasType.GENDER: f"'{term}' may discourage candidates of certain genders from applying",
            BiasType.AGE: f"'{term}' may discriminate against candidates based on age",
            BiasType.EDUCATION: f"'{term}' creates prestige bias and may exclude qualified candidates from other institutions",
            BiasType.LOCATION: f"'{term}' may unfairly limit the candidate pool geographically",
            BiasType.DISABILITY: f"'{term}' may exclude candidates with disabilities who could perform the job",
            BiasType.RACE: f"'{term}' may have racial implications",
            BiasType.RELIGION: f"'{term}' may discriminate based on religion",
            BiasType.NAME: f"'{term}' may indicate name-based discrimination",
        }
        return explanations.get(bias_type, f"'{term}' may introduce bias")
    
    def rewrite_text(self, text: str) -> Tuple[str, List[BiasFlag]]:
        """
        Rewrite text to remove biases
        Returns (rewritten_text, list of changes made)
        """
        flags = self.detect_bias(text)
        rewritten = text
        
        # Sort by position (reverse) to avoid index shifting
        sorted_flags = sorted(flags, key=lambda f: text.lower().find(f.original_text.lower()), reverse=True)
        
        for flag in sorted_flags:
            pattern = re.compile(re.escape(flag.original_text), re.IGNORECASE)
            rewritten = pattern.sub(flag.suggested_replacement, rewritten, count=1)
        
        return rewritten, flags
    
    def calculate_bias_score(self, text: str) -> Dict:
        """
        Calculate overall bias score (0-100, lower is better)
        """
        flags = self.detect_bias(text)
        
        if not flags:
            return {
                "score": 0,
                "rating": "Excellent",
                "flags_count": 0,
                "breakdown": {},
                "flags": []
            }
        
        # Weight by severity
        severity_weights = {"high": 3, "medium": 2, "low": 1}
        total_weight = sum(severity_weights.get(f.severity, 1) for f in flags)
        
        # Normalize to 0-100 scale
        score = min(100, total_weight * 8)
        
        # Rating
        if score < 15:
            rating = "Good"
        elif score < 30:
            rating = "Fair"
        elif score < 50:
            rating = "Needs Improvement"
        else:
            rating = "High Bias Risk"
        
        # Breakdown by type
        breakdown = {}
        for flag in flags:
            bias_name = flag.bias_type.value
            if bias_name not in breakdown:
                breakdown[bias_name] = 0
            breakdown[bias_name] += 1
        
        return {
            "score": score,
            "rating": rating,
            "flags_count": len(flags),
            "breakdown": breakdown,
            "flags": flags
        }
    
    def get_bias_report(self, text: str) -> str:
        """Generate a human-readable bias report"""
        result = self.calculate_bias_score(text)
        
        report = f"""
📊 BIAS ANALYSIS REPORT
{'='*40}
Score: {result['score']}/100 ({result['rating']})
Issues Found: {result['flags_count']}

"""
        if result['flags_count'] > 0:
            report += "🚩 FLAGGED TERMS:\n"
            for flag in result['flags']:
                report += f"  • '{flag.original_text}' → '{flag.suggested_replacement}'\n"
                report += f"    Type: {flag.bias_type.value} | Severity: {flag.severity}\n"
                report += f"    {flag.explanation}\n\n"
        else:
            report += "✅ No significant bias detected!\n"
        
        return report


# Singleton instance
bias_detector = BiasDetector()


# Test
if __name__ == "__main__":
    print("🔍 Testing Bias Detector")
    print("=" * 50)
    
    test_jd = """
    We're looking for a rockstar developer who is a digital native.
    Must be from IIT or Stanford. Young and hungry candidates preferred.
    Chairman of engineering will interview you. Manpower needed immediately.
    Must be able to lift 50 lbs. Native English speakers only.
    """
    
    result = bias_detector.calculate_bias_score(test_jd)
    print(f"Score: {result['score']}/100")
    print(f"Rating: {result['rating']}")
    print(f"Flags: {result['flags_count']}")
    
    print("\n" + bias_detector.get_bias_report(test_jd))
    
    # Rewrite
    rewritten, flags = bias_detector.rewrite_text(test_jd)
    print("\n📝 REWRITTEN JD:")
    print(rewritten)
