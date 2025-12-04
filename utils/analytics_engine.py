"""
AnalyticsEngine: Leaderboards and Candidate Comparison

Provides ranking and comparison features for batch-processed candidates.
HR managers can see "Who are the top 5?" and compare candidates side-by-side.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


class AnalyticsEngine:
    """
    Analytics and comparison engine for processed candidates.
    
    Features:
    - Leaderboard ranking by score and experience
    - Side-by-side candidate comparison
    - Skill gap analysis
    - Batch statistics
    """
    
    def __init__(self, audit_db: Any = None):
        """
        Initialize analytics engine.
        
        Args:
            audit_db: AuditLog database instance for fetching candidate data
        """
        self.audit_db = audit_db
        self._cache: Dict[str, Any] = {}
    
    def get_leaderboard(self, limit: int = 10, 
                        status_filter: Optional[str] = None,
                        min_score: int = 0) -> Dict[str, Any]:
        """
        Get ranked leaderboard of candidates.
        
        Ranking Logic:
        1. Primary: Skill match score (descending)
        2. Tie-breaker: Years of experience (descending)
        3. Secondary tie-breaker: Authenticity score (if available)
        
        Args:
            limit: Maximum number of candidates to return
            status_filter: Filter by status ("APPROVED", "QUESTIONS_PENDING", etc.)
            min_score: Minimum skill score to include
            
        Returns:
            {
                "leaderboard": [ranked list of candidates],
                "total_candidates": int,
                "filters_applied": dict,
                "generated_at": timestamp
            }
        """
        
        candidates = []
        
        if self.audit_db:
            # Fetch all candidates from database
            try:
                all_candidates = self.audit_db.get_all_candidates()
                
                for candidate in all_candidates:
                    # Extract relevant fields
                    cid = candidate.get("candidate_id", "")
                    status = candidate.get("status", "")
                    score = candidate.get("match_score", 0) or candidate.get("skill_score", 0) or 0
                    years = candidate.get("years_exp", 0) or 0
                    authenticity = candidate.get("authenticity_score", 0) or 0
                    
                    # Apply filters
                    if status_filter and status_filter not in status:
                        continue
                    if score < min_score:
                        continue
                    
                    # Only include candidates that passed Agent 1 at least
                    if "REJECTED_BY_AGENT_1" in status:
                        continue
                    
                    candidates.append({
                        "candidate_id": cid,
                        "status": status,
                        "skill_score": score,
                        "years_experience": years,
                        "authenticity_score": authenticity,
                        "timestamp": candidate.get("updated_at", "")
                    })
            except Exception as e:
                print(f"⚠️ Failed to fetch candidates: {e}")
        
        # Sort: Primary by score (desc), secondary by years (desc), tertiary by authenticity (desc)
        sorted_candidates = sorted(
            candidates,
            key=lambda x: (
                x.get("skill_score", 0),
                x.get("years_experience", 0),
                x.get("authenticity_score", 0)
            ),
            reverse=True
        )
        
        # Add rank
        leaderboard = []
        for i, candidate in enumerate(sorted_candidates[:limit], 1):
            candidate["rank"] = i
            leaderboard.append(candidate)
        
        return {
            "leaderboard": leaderboard,
            "total_candidates": len(candidates),
            "showing": len(leaderboard),
            "filters_applied": {
                "status_filter": status_filter,
                "min_score": min_score,
                "limit": limit
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def compare_candidates(self, candidate_id_1: str, 
                           candidate_id_2: str) -> Dict[str, Any]:
        """
        Compare two candidates side-by-side.
        
        Args:
            candidate_id_1: First candidate ID
            candidate_id_2: Second candidate ID
            
        Returns:
            {
                "candidate_A": {...details...},
                "candidate_B": {...details...},
                "winner": "candidate_A" or "candidate_B" or "TIE",
                "diff_summary": str,
                "comparison_details": {...}
            }
        """
        
        # Fetch candidate data
        candidate_a = self._get_candidate_details(candidate_id_1)
        candidate_b = self._get_candidate_details(candidate_id_2)
        
        if not candidate_a:
            return {"error": f"Candidate {candidate_id_1} not found"}
        if not candidate_b:
            return {"error": f"Candidate {candidate_id_2} not found"}
        
        # Extract scores
        score_a = candidate_a.get("skill_score", 0)
        score_b = candidate_b.get("skill_score", 0)
        years_a = candidate_a.get("years_experience", 0)
        years_b = candidate_b.get("years_experience", 0)
        auth_a = candidate_a.get("authenticity_score", 0)
        auth_b = candidate_b.get("authenticity_score", 0)
        
        # Determine winner
        if score_a > score_b:
            winner = "candidate_A"
            winner_id = candidate_id_1
        elif score_b > score_a:
            winner = "candidate_B"
            winner_id = candidate_id_2
        else:
            # Tie-breaker: experience
            if years_a > years_b:
                winner = "candidate_A"
                winner_id = candidate_id_1
            elif years_b > years_a:
                winner = "candidate_B"
                winner_id = candidate_id_2
            else:
                winner = "TIE"
                winner_id = None
        
        # Generate comparison summary
        diff_summary = self._generate_comparison_summary(
            candidate_a, candidate_b, winner, winner_id
        )
        
        # Skill comparison
        skills_a = set(candidate_a.get("skills", []))
        skills_b = set(candidate_b.get("skills", []))
        
        return {
            "candidate_A": {
                "id": candidate_id_1,
                "skill_score": score_a,
                "years_experience": years_a,
                "authenticity_score": auth_a,
                "status": candidate_a.get("status", ""),
                "skills": list(skills_a),
                "matched_skills": candidate_a.get("matched_skills", []),
                "missing_skills": candidate_a.get("missing_skills", [])
            },
            "candidate_B": {
                "id": candidate_id_2,
                "skill_score": score_b,
                "years_experience": years_b,
                "authenticity_score": auth_b,
                "status": candidate_b.get("status", ""),
                "skills": list(skills_b),
                "matched_skills": candidate_b.get("matched_skills", []),
                "missing_skills": candidate_b.get("missing_skills", [])
            },
            "winner": winner,
            "winner_id": winner_id,
            "diff_summary": diff_summary,
            "comparison_details": {
                "score_difference": abs(score_a - score_b),
                "experience_difference": abs(years_a - years_b),
                "unique_skills_A": list(skills_a - skills_b),
                "unique_skills_B": list(skills_b - skills_a),
                "common_skills": list(skills_a & skills_b)
            },
            "compared_at": datetime.now().isoformat()
        }
    
    def _get_candidate_details(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full candidate details from database"""
        
        if not self.audit_db:
            return None
        
        try:
            # Try to get from verification results first
            result = self.audit_db.get_verification_result(candidate_id)
            
            if result:
                # Extract relevant fields from full result
                agent2_data = result.get("pipeline_stages", {}).get("agent_2", {})
                agent1_data = result.get("pipeline_stages", {}).get("agent_1", {})
                
                return {
                    "candidate_id": candidate_id,
                    "status": result.get("final_status", ""),
                    "skill_score": result.get("agent_2_score", 0),
                    "years_experience": result.get("years_exp", 0),
                    "authenticity_score": result.get("agent_3_authenticity", 0),
                    "skills": agent1_data.get("clean_data", {}).get("skills", []),
                    "matched_skills": agent2_data.get("matched_skills", []),
                    "missing_skills": agent2_data.get("missing_skills", []),
                    "timestamp": result.get("timestamp", "")
                }
            
            # Fallback to candidate record
            candidate = self.audit_db.get_candidate(candidate_id)
            if candidate:
                return {
                    "candidate_id": candidate_id,
                    "status": candidate.get("status", ""),
                    "skill_score": candidate.get("match_score", 0),
                    "years_experience": candidate.get("years_exp", 0),
                    "authenticity_score": candidate.get("authenticity_score", 0),
                    "skills": [],
                    "matched_skills": [],
                    "missing_skills": []
                }
        except Exception as e:
            print(f"⚠️ Failed to fetch candidate {candidate_id}: {e}")
        
        return None
    
    def _generate_comparison_summary(self, candidate_a: Dict, candidate_b: Dict,
                                     winner: str, winner_id: Optional[str]) -> str:
        """Generate human-readable comparison summary"""
        
        score_a = candidate_a.get("skill_score", 0)
        score_b = candidate_b.get("skill_score", 0)
        years_a = candidate_a.get("years_experience", 0)
        years_b = candidate_b.get("years_experience", 0)
        
        if winner == "TIE":
            return "Both candidates are equally matched in skills and experience."
        
        score_diff = abs(score_a - score_b)
        exp_diff = abs(years_a - years_b)
        
        summary_parts = []
        
        if winner == "candidate_A":
            if score_a > score_b:
                summary_parts.append(f"Candidate A has a higher skill match ({score_a}% vs {score_b}%)")
            if years_a > years_b:
                summary_parts.append(f"has {exp_diff} more years of experience")
        else:
            if score_b > score_a:
                summary_parts.append(f"Candidate B has a higher skill match ({score_b}% vs {score_a}%)")
            if years_b > years_a:
                summary_parts.append(f"has {exp_diff} more years of experience")
        
        if summary_parts:
            return " and ".join(summary_parts) + "."
        
        return f"{winner.replace('_', ' ').title()} is the recommended choice."
    
    def get_batch_statistics(self, batch_results: List[Dict]) -> Dict[str, Any]:
        """
        Calculate statistics for a batch of processed candidates.
        
        Args:
            batch_results: List of processing results from BatchProcessor
            
        Returns:
            Aggregate statistics for the batch
        """
        
        if not batch_results:
            return {"error": "No results to analyze"}
        
        scores = [r.get("score", 0) for r in batch_results if r.get("score")]
        years = [r.get("years_exp", 0) for r in batch_results if r.get("years_exp")]
        
        passed = sum(1 for r in batch_results if "PASS" in r.get("status", "") or "APPROVED" in r.get("status", ""))
        failed = sum(1 for r in batch_results if "FAIL" in r.get("status", "") or "REJECTED" in r.get("status", ""))
        pending = sum(1 for r in batch_results if "PENDING" in r.get("status", ""))
        
        return {
            "total_candidates": len(batch_results),
            "passed": passed,
            "failed": failed,
            "pending": pending,
            "pass_rate": round(passed / len(batch_results) * 100, 1) if batch_results else 0,
            "score_stats": {
                "average": round(sum(scores) / len(scores), 1) if scores else 0,
                "highest": max(scores) if scores else 0,
                "lowest": min(scores) if scores else 0
            },
            "experience_stats": {
                "average": round(sum(years) / len(years), 1) if years else 0,
                "highest": max(years) if years else 0,
                "lowest": min(years) if years else 0
            },
            "analyzed_at": datetime.now().isoformat()
        }
    
    def get_skill_distribution(self, candidate_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze skill distribution across candidates.
        
        Returns frequency of each skill across the candidate pool.
        """
        
        skill_counts: Dict[str, int] = {}
        total_candidates = 0
        
        if self.audit_db:
            try:
                if candidate_ids:
                    candidates = [self._get_candidate_details(cid) for cid in candidate_ids]
                else:
                    candidates = self.audit_db.get_all_candidates()
                
                for candidate in candidates:
                    if not candidate:
                        continue
                    
                    total_candidates += 1
                    skills = candidate.get("skills", [])
                    
                    for skill in skills:
                        skill_lower = skill.lower()
                        skill_counts[skill_lower] = skill_counts.get(skill_lower, 0) + 1
            except Exception as e:
                print(f"⚠️ Skill distribution analysis failed: {e}")
        
        # Sort by frequency
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "skill_distribution": [
                {"skill": skill, "count": count, "percentage": round(count/total_candidates*100, 1) if total_candidates else 0}
                for skill, count in sorted_skills[:20]  # Top 20 skills
            ],
            "total_candidates": total_candidates,
            "unique_skills": len(skill_counts),
            "analyzed_at": datetime.now().isoformat()
        }


# Quick test
if __name__ == "__main__":
    print("="*60)
    print("ANALYTICS ENGINE TEST")
    print("="*60)
    
    engine = AnalyticsEngine()
    
    # Test with mock data
    mock_batch = [
        {"candidate_id": "CAND-001", "status": "APPROVED", "score": 85, "years_exp": 5},
        {"candidate_id": "CAND-002", "status": "APPROVED", "score": 92, "years_exp": 3},
        {"candidate_id": "CAND-003", "status": "REJECTED", "score": 45, "years_exp": 2},
        {"candidate_id": "CAND-004", "status": "QUESTIONS_PENDING", "score": 78, "years_exp": 7},
        {"candidate_id": "CAND-005", "status": "APPROVED", "score": 88, "years_exp": 4},
    ]
    
    stats = engine.get_batch_statistics(mock_batch)
    
    print("\nBatch Statistics:")
    print(f"  Total: {stats['total_candidates']}")
    print(f"  Passed: {stats['passed']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Pass Rate: {stats['pass_rate']}%")
    print(f"  Avg Score: {stats['score_stats']['average']}")
    print(f"  Avg Experience: {stats['experience_stats']['average']} years")
    
    print("\n✅ Analytics Engine ready!")
