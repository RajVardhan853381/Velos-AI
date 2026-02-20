"""
ReportGenerator: Export Hiring Dossiers

Generates downloadable reports (CSV) for HR managers to share with stakeholders.
Includes candidate rankings, scores, trust verification, and timestamps.
"""

import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime


class ReportGenerator:
    """
    Generates exportable reports for hiring decisions.
    
    Features:
    - CSV export of candidate data
    - Customizable columns
    - Batch report generation
    - Trust verification included
    """
    
    # Default columns for the report
    DEFAULT_COLUMNS = [
        "Rank",
        "Candidate ID",
        "Status",
        "Skill Score",
        "Years Experience",
        "Authenticity Score",
        "Trust Hash",
        "Verified",
        "Timestamp"
    ]
    
    def __init__(self, audit_db: Any = None):
        """
        Initialize report generator.
        
        Args:
            audit_db: AuditLog database instance for fetching data
        """
        self.audit_db = audit_db
    
    def generate_csv_report(self, candidate_ids: Optional[List[str]] = None,
                            include_all: bool = False,
                            columns: Optional[List[str]] = None) -> str:
        """
        Generate a CSV report for specified candidates.
        
        Args:
            candidate_ids: List of candidate IDs to include
            include_all: If True, include all candidates from DB
            columns: Custom column list (uses DEFAULT_COLUMNS if None)
            
        Returns:
            CSV string ready for download
        """
        
        output = io.StringIO()
        cols = columns or self.DEFAULT_COLUMNS
        
        writer = csv.writer(output)
        writer.writerow(cols)
        
        # Fetch candidates
        candidates = self._fetch_candidates(candidate_ids, include_all)
        
        # Sort by score (descending)
        sorted_candidates = sorted(
            candidates,
            key=lambda x: (x.get("skill_score", 0), x.get("years_experience", 0)),
            reverse=True
        )
        
        # Write rows
        for rank, candidate in enumerate(sorted_candidates, 1):
            row = self._format_row(candidate, rank, cols)
            writer.writerow(row)
        
        return output.getvalue()
    
    def generate_csv_bytes(self, candidate_ids: Optional[List[str]] = None,
                           include_all: bool = False) -> bytes:
        """Generate CSV as bytes for file download"""
        csv_string = self.generate_csv_report(candidate_ids, include_all)
        return csv_string.encode('utf-8')
    
    def _fetch_candidates(self, candidate_ids: Optional[List[str]],
                          include_all: bool) -> List[Dict[str, Any]]:
        """Fetch candidate data from database"""
        
        candidates = []
        
        if not self.audit_db:
            return candidates
        
        try:
            if include_all:
                # Get all candidates
                all_candidates = self.audit_db.get_all_candidates()
                for c in all_candidates:
                    candidates.append(self._normalize_candidate(c))
            elif candidate_ids:
                # Get specific candidates
                for cid in candidate_ids:
                    result = self.audit_db.get_verification_result(cid)
                    if result:
                        candidates.append(self._normalize_from_result(cid, result))
                    else:
                        # Try candidate record
                        c = self.audit_db.get_candidate(cid)
                        if c:
                            candidates.append(self._normalize_candidate(c))
        except Exception as e:
            print(f"⚠️ Failed to fetch candidates: {e}")
        
        return candidates
    
    def _normalize_candidate(self, candidate: Dict) -> Dict[str, Any]:
        """Normalize candidate data from DB record"""
        return {
            "candidate_id": candidate.get("candidate_id", ""),
            "status": candidate.get("status", ""),
            "skill_score": candidate.get("match_score", 0) or 0,
            "years_experience": candidate.get("years_exp", 0) or 0,
            "authenticity_score": candidate.get("authenticity_score", 0) or 0,
            "trust_hash": "",
            "verified": "N/A",
            "timestamp": candidate.get("updated_at", "")
        }
    
    def _normalize_from_result(self, cid: str, result: Dict) -> Dict[str, Any]:
        """Normalize candidate data from full verification result"""
        trust_layer = result.get("trust_layer", {})
        
        return {
            "candidate_id": cid,
            "status": result.get("final_status", ""),
            "skill_score": result.get("agent_2_score", 0) or 0,
            "years_experience": result.get("years_exp", 0) or 0,
            "authenticity_score": result.get("agent_3_authenticity", 0) or 0,
            "trust_hash": trust_layer.get("data_hash", "")[:16] if trust_layer.get("data_hash") else "",
            "verified": "Yes" if trust_layer.get("data_hash") else "No",
            "timestamp": result.get("timestamp", "")
        }
    
    def _format_row(self, candidate: Dict, rank: int, columns: List[str]) -> List[Any]:
        """Format a candidate as a CSV row"""
        
        column_mapping = {
            "Rank": rank,
            "Candidate ID": candidate.get("candidate_id", ""),
            "Status": candidate.get("status", ""),
            "Skill Score": candidate.get("skill_score", 0),
            "Years Experience": candidate.get("years_experience", 0),
            "Authenticity Score": candidate.get("authenticity_score", 0),
            "Trust Hash": candidate.get("trust_hash", ""),
            "Verified": candidate.get("verified", "N/A"),
            "Timestamp": candidate.get("timestamp", "")
        }
        
        return [column_mapping.get(col, "") for col in columns]
    
    def generate_detailed_report(self, candidate_id: str) -> str:
        """
        Generate a detailed report for a single candidate.
        
        Returns:
            Formatted text report
        """
        
        if not self.audit_db:
            return "Database not available"
        
        try:
            result = self.audit_db.get_verification_result(candidate_id)
            
            if not result:
                return f"Candidate {candidate_id} not found"
            
            trust_layer = result.get("trust_layer", {})
            
            report = f"""
╔══════════════════════════════════════════════════════════════════╗
║                      VELOS HIRING DOSSIER                         ║
╠══════════════════════════════════════════════════════════════════╣
║ Candidate ID: {candidate_id:<50} ║
║ Generated:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<50} ║
╠══════════════════════════════════════════════════════════════════╣
║                         FINAL DECISION                            ║
╠══════════════════════════════════════════════════════════════════╣
║ Status:       {result.get('final_status', 'N/A'):<50} ║
║ Reason:       {result.get('final_reason', 'N/A')[:50]:<50} ║
╠══════════════════════════════════════════════════════════════════╣
║                         SCORING BREAKDOWN                         ║
╠══════════════════════════════════════════════════════════════════╣
║ Skill Match Score:     {result.get('agent_2_score', 0):>3}%                                     ║
║ Years of Experience:   {result.get('years_exp', 0):>3} years                                  ║
║ Authenticity Score:    {result.get('agent_3_authenticity', 0):>3}%                                     ║
╠══════════════════════════════════════════════════════════════════╣
║                         TRUST VERIFICATION                        ║
╠══════════════════════════════════════════════════════════════════╣
║ Data Hash:    {trust_layer.get('data_hash', 'N/A')[:50]:<50} ║
║ Block ID:     {trust_layer.get('block_id', 'N/A')[:50]:<50} ║
║ Sealed At:    {trust_layer.get('sealed_at', 'N/A')[:50]:<50} ║
╠══════════════════════════════════════════════════════════════════╣
║                         PIPELINE RESULTS                          ║
╠══════════════════════════════════════════════════════════════════╣
║ Agent 1 (Gatekeeper):  {result.get('agent_1_status', 'N/A'):<42} ║
║ Agent 2 (Validator):   {result.get('agent_2_status', 'N/A'):<42} ║
║ Agent 3 (Inquisitor):  {result.get('agent_3_status', 'N/A'):<42} ║
╚══════════════════════════════════════════════════════════════════╝
"""
            return report
            
        except Exception as e:
            return f"Error generating report: {e}"
    
    def generate_batch_summary(self, batch_results: List[Dict]) -> str:
        """
        Generate a summary report for a batch processing run.
        
        Args:
            batch_results: Results from BatchProcessor
            
        Returns:
            CSV string with batch summary
        """
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Filename",
            "Candidate ID",
            "Status",
            "Score",
            "Years Exp",
            "Processing Time (s)",
            "Data Hash"
        ])
        
        # Sort by score
        sorted_results = sorted(
            batch_results,
            key=lambda x: x.get("score", 0),
            reverse=True
        )
        
        # Write rows
        for result in sorted_results:
            writer.writerow([
                result.get("filename", ""),
                result.get("candidate_id", ""),
                result.get("status", ""),
                result.get("score", 0),
                result.get("years_exp", 0),
                result.get("processing_time", 0),
                result.get("data_hash", "")
            ])
        
        # Summary footer
        writer.writerow([])
        writer.writerow(["SUMMARY"])
        writer.writerow(["Total Processed", len(batch_results)])
        
        passed = sum(1 for r in batch_results if "PASS" in r.get("status", "") or "APPROVED" in r.get("status", ""))
        writer.writerow(["Passed", passed])
        writer.writerow(["Pass Rate", f"{round(passed/len(batch_results)*100, 1)}%" if batch_results else "0%"])
        
        scores = [r.get("score", 0) for r in batch_results if r.get("score")]
        if scores:
            writer.writerow(["Average Score", round(sum(scores)/len(scores), 1)])
            writer.writerow(["Highest Score", max(scores)])
        
        return output.getvalue()
    
    def get_report_filename(self, report_type: str = "candidates") -> str:
        """Generate a filename for the report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"velos_{report_type}_{timestamp}.csv"


# Quick test
if __name__ == "__main__":
    print("="*60)
    print("REPORT GENERATOR TEST")
    print("="*60)
    
    generator = ReportGenerator()
    
    # Test with mock batch results
    mock_batch = [
        {"filename": "resume1.pdf", "candidate_id": "CAND-001", "status": "APPROVED", "score": 85, "years_exp": 5, "processing_time": 2.3, "data_hash": "abc123"},
        {"filename": "resume2.pdf", "candidate_id": "CAND-002", "status": "APPROVED", "score": 92, "years_exp": 3, "processing_time": 1.8, "data_hash": "def456"},
        {"filename": "resume3.pdf", "candidate_id": "CAND-003", "status": "REJECTED", "score": 45, "years_exp": 2, "processing_time": 1.5, "data_hash": ""},
    ]
    
    csv_report = generator.generate_batch_summary(mock_batch)
    
    print("\nGenerated Batch Summary CSV:")
    print("-" * 40)
    print(csv_report)
    
    print(f"\nSuggested filename: {generator.get_report_filename('batch')}")
    print("\n✅ Report Generator ready!")
