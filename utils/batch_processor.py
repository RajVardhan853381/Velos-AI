"""
BatchProcessor: Handle ZIP files containing multiple resumes

Processes a batch of resumes (PDF/DOCX) from a ZIP file,
running each through the full Velos verification pipeline.

For HR managers who need to process 20-50 resumes at once.
"""

import zipfile
import io
import os
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


class BatchProcessor:
    """
    Processes ZIP files containing multiple resumes.
    
    Features:
    - Extracts and validates files from ZIP
    - Skips system files (__MACOSX, .DS_Store)
    - Processes each resume through the full pipeline
    - Returns aggregated results for dashboard display
    """
    
    # File extensions we can process
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}
    
    # System files to skip
    SKIP_PATTERNS = {
        '__MACOSX',
        '.DS_Store',
        'Thumbs.db',
        '.gitkeep',
        '__pycache__'
    }
    
    def __init__(self, resume_parser: Any = None, orchestrator: Any = None):
        """
        Initialize batch processor.
        
        Args:
            resume_parser: ResumeParser instance for text extraction
            orchestrator: VelosOrchestrator instance for verification
        """
        self.resume_parser = resume_parser
        self.orchestrator = orchestrator
        self.processing_stats = {
            "total_processed": 0,
            "total_passed": 0,
            "total_failed": 0,
            "total_errors": 0
        }
    
    def _is_valid_file(self, filename: str) -> bool:
        """Check if file should be processed (not a system file)"""
        
        # Skip directories
        if filename.endswith('/'):
            return False
        
        # Skip system files
        for pattern in self.SKIP_PATTERNS:
            if pattern in filename:
                return False
        
        # Skip hidden files
        basename = os.path.basename(filename)
        if basename.startswith('.'):
            return False
        
        # Check extension
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.SUPPORTED_EXTENSIONS
    
    def _extract_files_from_zip(self, zip_bytes: bytes) -> List[Tuple[str, bytes]]:
        """
        Extract valid files from a ZIP archive.
        
        Returns:
            List of (filename, file_bytes) tuples
        """
        files = []
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
                for file_info in zf.infolist():
                    filename = file_info.filename
                    
                    if self._is_valid_file(filename):
                        try:
                            file_bytes = zf.read(filename)
                            files.append((filename, file_bytes))
                        except Exception as e:
                            print(f"⚠️ Failed to read {filename}: {e}")
        except zipfile.BadZipFile:
            raise ValueError("Invalid ZIP file")
        
        return files
    
    def _process_single_resume(self, filename: str, file_bytes: bytes,
                               job_description: str, min_years: int) -> Dict[str, Any]:
        """
        Process a single resume file through the pipeline.
        
        Returns:
            Result dictionary with candidate_id, status, score, etc.
        """
        result = {
            "filename": filename,
            "candidate_id": None,
            "status": "ERROR",
            "reason": "",
            "score": 0,
            "processing_time": 0
        }
        
        start_time = time.time()
        
        try:
            # Step 1: Parse resume to text
            if self.resume_parser:
                try:
                    resume_text, _metadata = self.resume_parser.parse_file(file_bytes, filename)
                except Exception as parse_err:
                    result["status"] = "PARSE_ERROR"
                    result["reason"] = str(parse_err)
                    return result
            else:
                # Fallback: Try to decode as text
                try:
                    resume_text = file_bytes.decode('utf-8')
                except (UnicodeDecodeError, AttributeError):
                    result["status"] = "PARSE_ERROR"
                    result["reason"] = "No parser available and file is not plain text"
                    return result
            
            if not resume_text or len(resume_text) < 50:
                result["status"] = "PARSE_ERROR"
                result["reason"] = "Resume text too short or empty"
                return result
            
            # Step 2: Run through verification pipeline
            if self.orchestrator:
                pipeline_result = self.orchestrator.run_verification_pipeline(
                    raw_resume=resume_text,
                    job_description=job_description,
                    min_years=min_years
                )
                
                result["candidate_id"] = pipeline_result.get("candidate_id")
                result["status"] = pipeline_result.get("final_status", "UNKNOWN")
                result["reason"] = pipeline_result.get("final_reason", "")
                result["score"] = pipeline_result.get("agent_2_score", 0)
                result["years_exp"] = pipeline_result.get("years_exp", 0)
                result["agent_1_status"] = pipeline_result.get("agent_1_status")
                result["agent_2_status"] = pipeline_result.get("agent_2_status")
                
                # Include trust layer info if available
                trust_layer = pipeline_result.get("trust_layer", {})
                if trust_layer:
                    result["data_hash"] = trust_layer.get("data_hash", "")[:16]
            else:
                result["status"] = "ERROR"
                result["reason"] = "No orchestrator available"
        
        except Exception as e:
            result["status"] = "ERROR"
            result["reason"] = str(e)
        
        result["processing_time"] = round(time.time() - start_time, 2)
        return result
    
    def process_zip_file(self, zip_bytes: bytes, job_description: str,
                         min_years: int = 0) -> Dict[str, Any]:
        """
        Process a ZIP file containing multiple resumes.
        
        Args:
            zip_bytes: The ZIP file as bytes
            job_description: Job description for skill matching
            min_years: Minimum years of experience required
            
        Returns:
            {
                "total": int,
                "processed": int,
                "passed": int,
                "failed": int,
                "errors": int,
                "results": [list of individual results],
                "processing_time": float,
                "summary": str
            }
        """
        
        start_time = time.time()
        
        # Extract files
        print("📦 Extracting files from ZIP...")
        files = self._extract_files_from_zip(zip_bytes)
        
        total_files = len(files)
        print(f"   Found {total_files} valid resume files")
        
        if total_files == 0:
            return {
                "total": 0,
                "processed": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "results": [],
                "processing_time": 0,
                "summary": "No valid resume files found in ZIP"
            }
        
        # Process each file
        results = []
        passed = 0
        failed = 0
        errors = 0
        
        for i, (filename, file_bytes) in enumerate(files, 1):
            print(f"📄 Processing {i}/{total_files}: {os.path.basename(filename)}...")
            
            result = self._process_single_resume(
                filename, file_bytes, job_description, min_years
            )
            results.append(result)
            
            # Update counters
            status = result.get("status", "ERROR")
            if "PASS" in status or "APPROVED" in status or status == "QUESTIONS_PENDING":
                passed += 1
            elif "ERROR" in status or "PARSE" in status:
                errors += 1
            else:
                failed += 1
            
            print(f"   → {result['status']} (Score: {result.get('score', 0)})")
        
        total_time = round(time.time() - start_time, 2)
        
        # Update stats
        self.processing_stats["total_processed"] += len(results)
        self.processing_stats["total_passed"] += passed
        self.processing_stats["total_failed"] += failed
        self.processing_stats["total_errors"] += errors
        
        return {
            "total": total_files,
            "processed": len(results),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "results": results,
            "processing_time": total_time,
            "summary": f"Processed {len(results)}/{total_files} resumes: {passed} passed, {failed} failed, {errors} errors"
        }
    
    def process_files_list(self, files: List[Tuple[str, bytes]], 
                           job_description: str, min_years: int = 0) -> Dict[str, Any]:
        """
        Process a list of files (alternative to ZIP).
        
        Args:
            files: List of (filename, file_bytes) tuples
            job_description: Job description for matching
            min_years: Minimum experience required
            
        Returns:
            Same format as process_zip_file
        """
        
        start_time = time.time()
        results = []
        passed = failed = errors = 0
        
        for i, (filename, file_bytes) in enumerate(files, 1):
            print(f"📄 Processing {i}/{len(files)}: {filename}...")
            
            result = self._process_single_resume(
                filename, file_bytes, job_description, min_years
            )
            results.append(result)
            
            status = result.get("status", "ERROR")
            if "PASS" in status or "APPROVED" in status or status == "QUESTIONS_PENDING":
                passed += 1
            elif "ERROR" in status:
                errors += 1
            else:
                failed += 1
        
        return {
            "total": len(files),
            "processed": len(results),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "results": results,
            "processing_time": round(time.time() - start_time, 2),
            "summary": f"Processed {len(results)} resumes: {passed} passed, {failed} failed, {errors} errors"
        }
    
    def get_stats(self) -> Dict[str, int]:
        """Get cumulative processing statistics"""
        return self.processing_stats.copy()


# Quick test
if __name__ == "__main__":
    print("="*60)
    print("BATCH PROCESSOR TEST")
    print("="*60)
    
    processor = BatchProcessor()
    
    # Test file validation
    test_files = [
        "resume.pdf",
        "cv.docx",
        "__MACOSX/._resume.pdf",
        ".DS_Store",
        "notes.txt",
        "folder/",
        ".hidden.pdf"
    ]
    
    print("\nFile validation test:")
    for f in test_files:
        valid = processor._is_valid_file(f)
        status = "✓" if valid else "✗"
        print(f"  {status} {f}")
    
    print("\n✅ Batch Processor ready!")
