"""
Experience Extractor Utility for Velos
Uses LLM to extract years of professional experience from resume text
"""

import os
import re
from datetime import datetime
from typing import Tuple, Optional
from dotenv import load_dotenv

load_dotenv()


class ExperienceExtractor:
    """
    Extracts years of professional experience from resume text.
    Uses LLM for intelligent extraction with regex fallback.
    """
    
    def __init__(self, llm=None):
        self.llm = llm
        
    def _extract_via_llm(self, text: str) -> float:
        """Extract years of experience using LLM"""
        if not self.llm:
            return self._extract_via_regex(text)
        
        prompt = f"""Extract the TOTAL YEARS OF PROFESSIONAL WORK EXPERIENCE from this resume.

Instructions:
1. Look for explicit mentions like "X years of experience"
2. Calculate from work history dates (e.g., "2020-2023" = 3 years)
3. Sum up all professional roles (not internships unless substantial)
4. Return ONLY a single number (e.g., 3.5 or 2 or 0)
5. If unclear or no experience found, return 0

Resume text (first 2000 chars):
{text[:2000]}

IMPORTANT: Return ONLY a number, nothing else."""

        try:
            response = self.llm.invoke(prompt)
            years_str = response.content.strip()
            
            # Extract number from response
            match = re.search(r'(\d+\.?\d*)', years_str)
            if match:
                years = float(match.group(1))
                # Sanity check: cap at 50 years
                return min(years, 50.0)
            return 0.0
        except Exception as e:
            print(f"⚠️ LLM extraction failed: {e}, falling back to regex")
            return self._extract_via_regex(text)
    
    def _extract_via_regex(self, text: str) -> float:
        """Fallback: Extract years using regex patterns"""
        
        patterns = [
            # "X years of experience"
            r'(\d+\.?\d*)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+)?experience',
            # "X+ years"
            r'(\d+\.?\d*)\+?\s*(?:years?|yrs?)\s+in',
            # "experience: X years"
            r'experience[:\s]+(\d+\.?\d*)\s*(?:years?|yrs?)',
        ]
        
        max_years = 0.0
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    years = float(match)
                    max_years = max(max_years, years)
                except ValueError:
                    continue
        
        # If no explicit mention, try to calculate from dates
        if max_years == 0:
            max_years = self._calculate_from_dates(text)
        
        return max_years
    
    def _calculate_from_dates(self, text: str) -> float:
        """Calculate experience from date ranges in resume"""
        
        # Pattern for date ranges like "2020-2023", "2020 - Present", "Jan 2020 - Dec 2023"
        date_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4}|present|current|now)',
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*(\d{4})\s*[-–]\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?[a-z]*\.?\s*(\d{4}|present|current|now)',
        ]
        
        total_years = 0.0
        current_year = datetime.now().year  # Dynamic current year
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    start_year = int(match[0])
                    end_str = match[1].lower()
                    
                    if end_str in ['present', 'current', 'now']:
                        end_year = current_year
                    else:
                        end_year = int(end_str)
                    
                    if 1980 <= start_year <= current_year and start_year <= end_year:
                        years = end_year - start_year
                        total_years += min(years, 10)  # Cap individual roles at 10 years
                except (ValueError, IndexError):
                    continue
        
        return min(total_years, 50.0)  # Cap total at 50 years
    
    def extract_years(self, text: str) -> float:
        """
        Main method: Extract total years of experience.
        Uses LLM if available, else regex fallback.
        """
        return self._extract_via_llm(text)
    
    def validate_experience(self, years: float, minimum_required: float) -> Tuple[bool, str]:
        """
        Check if candidate meets minimum experience requirement.
        
        Returns:
            Tuple of (is_eligible, reason_string)
        """
        if years >= minimum_required:
            return True, f"✅ {years:.1f} years experience meets requirement ({minimum_required:.0f}y minimum)"
        else:
            return False, f"❌ {years:.1f} years < {minimum_required:.0f} years required"
    
    def get_experience_breakdown(self, text: str) -> dict:
        """
        Get detailed breakdown of experience calculation.
        Useful for audit trail.
        """
        llm_years = self._extract_via_llm(text) if self.llm else None
        regex_years = self._extract_via_regex(text)
        date_calc_years = self._calculate_from_dates(text)
        
        return {
            "llm_extracted": llm_years,
            "regex_extracted": regex_years,
            "date_calculated": date_calc_years,
            "final_value": llm_years if llm_years is not None else regex_years,
            "method_used": "LLM" if llm_years is not None else "Regex"
        }
