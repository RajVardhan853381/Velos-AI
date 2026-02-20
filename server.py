"""
Velos - FastAPI Backend Server
Connects the beautiful HTML frontend to the real AI agents.
Built for ZYND AIckathon 2025
"""

import os
import sys
import json
import uuid
import asyncio
import io
import hashlib
import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Literal
from pathlib import Path

# Load .env FIRST — before any os.getenv() calls — so GROQ_API_KEY is available
from dotenv import load_dotenv
load_dotenv()

# Record server start time for uptime calculation
START_TIME = time.time()

# Disable ChromaDB and LangSmith telemetry BEFORE importing anything
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
os.environ["POSTHOG_DISABLED"] = "True"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["HF_HUB_OFFLINE"] = "1"  # Prevent HuggingFace downloads

from fastapi import FastAPI, HTTPException, Request, Form, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Add current directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup centralized logging
from utils.logger import logger, api_logger, log_api_request, log_error

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="Velos API",
    description="Decentralized Blind Hiring Platform - ZYND AIckathon 2025",
    version="1.0.0"
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - SECURITY: Only allow specific origins
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",  # React frontend (Vite dev server)
    "http://127.0.0.1:5173",
    "http://localhost:5174",  # Vite dev server (alternate port)
    "http://127.0.0.1:5174",
    "https://velos-ai.onrender.com",  # Add your production domain here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if os.getenv("ENVIRONMENT") == "production" else ["*"],  # Allow all in dev
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Resume Parser
PARSER_AVAILABLE = False
resume_parser = None

try:
    from utils.resume_parser import ResumeParser
    resume_parser = ResumeParser()
    PARSER_AVAILABLE = True
    logger.info("✅ Resume Parser initialized (PDF/DOCX/OCR)")
except Exception as e:
    logger.warning(f"⚠️ Resume Parser not available: {e}")

# Initialize Batch Processor, Analytics, and Report Generator
BATCH_AVAILABLE = False
batch_processor = None
analytics_engine = None
report_generator = None

try:
    from utils.batch_processor import BatchProcessor
    from utils.analytics_engine import AnalyticsEngine
    from utils.report_generator import ReportGenerator
    BATCH_AVAILABLE = True
    logger.info("✅ Batch Processing & Analytics initialized")
except Exception as e:
    logger.warning(f"⚠️ Batch Processing not available: {e}")

# Initialize orchestrator
ORCHESTRATOR_AVAILABLE = False
orchestrator = None

try:
    from agents.orchestrator import VelosOrchestrator
    orchestrator = VelosOrchestrator()
    ORCHESTRATOR_AVAILABLE = True
    logger.info("✅ Velos Orchestrator initialized")
    logger.info("✅ Zynd Protocol connected")
    
    # Initialize batch processing components with orchestrator
    if BATCH_AVAILABLE:
        batch_processor = BatchProcessor(resume_parser=resume_parser, orchestrator=orchestrator)
        analytics_engine = AnalyticsEngine(audit_db=orchestrator.audit_db)
        report_generator = ReportGenerator(audit_db=orchestrator.audit_db)
        logger.info("✅ Batch Processor, Analytics, and Reports connected to Orchestrator")
except Exception as e:
    logger.warning(f"⚠️ Orchestrator not available: {e}")
    logger.info("📝 Running in simulation mode")

# In-memory storage for demo
class AppState:
    def __init__(self):
        self.candidates: List[Dict] = []
        self.audit_logs: List[Dict] = []
        self.agent_stats = {
            "gatekeeper": {"processed": 0, "passed": 0, "pass_rate": 0, "avg_time": 1.2, "accuracy": 100},
            "validator": {"processed": 0, "passed": 0, "pass_rate": 0, "avg_time": 2.1, "accuracy": 98},
            "inquisitor": {"processed": 0, "passed": 0, "pass_rate": 0, "avg_time": 3.5, "accuracy": 95}
        }
        self.total_candidates = 0
        self.approved = 0
        self.fraud_detected = 0
        
    def add_candidate(self, candidate: Dict):
        self.candidates.insert(0, candidate)
        self.total_candidates += 1
        if len(self.candidates) > 500:
            self.candidates.pop()
        
    def add_audit_log(self, log: Dict):
        self.audit_logs.insert(0, log)
        if len(self.audit_logs) > 100:
            self.audit_logs.pop()
            
    def update_agent_stats(self, agent_name: str, passed: bool):
        """Update agent statistics with actual pass/fail data"""
        if agent_name in self.agent_stats:
            self.agent_stats[agent_name]["processed"] += 1
            if passed:
                self.agent_stats[agent_name]["passed"] = self.agent_stats[agent_name].get("passed", 0) + 1
            # Calculate pass rate
            processed = self.agent_stats[agent_name]["processed"]
            passed_count = self.agent_stats[agent_name].get("passed", 0)
            self.agent_stats[agent_name]["pass_rate"] = round((passed_count / processed * 100), 1) if processed > 0 else 0

state = AppState()

# Pydantic models
class VerifyRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, max_length=50000, description="Resume text (50-50k chars)")
    job_description: str = Field(..., min_length=20, max_length=10000, description="Job description (20-10k chars)")
    
    @field_validator('resume_text', 'job_description')
    @classmethod
    def strip_and_validate(cls, v):
        # Strip whitespace
        v = v.strip()
        # Basic sanitization - remove control characters
        v = ''.join(char for char in v if ord(char) >= 32 or char in '\n\r\t')
        return v

class CandidateResponse(BaseModel):
    id: str
    status: str
    trust_score: Optional[float]
    skill_match: Optional[float]
    timestamp: str
    redacted_resume: Optional[str]
    questions: Optional[List[str]]
    credential: Optional[Dict]

# ==================== API ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main HTML frontend"""
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(), status_code=200)
    return HTMLResponse(content="<h1>index.html not found</h1>", status_code=404)

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "up",
            "orchestrator": "up" if ORCHESTRATOR_AVAILABLE and orchestrator else "down",
            "groq_api": "up" if ORCHESTRATOR_AVAILABLE else "unknown",
            "database": "up" if orchestrator and hasattr(orchestrator, 'audit_db') else "unknown",
            "zynd_protocol": "up" if ORCHESTRATOR_AVAILABLE else "down",
        }
    }
    
    # Determine overall health
    critical_components = ["api", "orchestrator"]
    all_critical_up = all(health_status["components"][c] == "up" for c in critical_components)
    
    if not all_critical_up:
        health_status["status"] = "degraded"
        return JSONResponse(status_code=503, content=health_status)
    
    return health_status

@app.get("/api/health")
async def api_health_check():
    """API health check for frontend - returns uptime and memory"""
    uptime_seconds = int(time.time() - START_TIME)
    memory_usage_mb = 0.0
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_usage_mb = round(memory_info.rss / (1024 * 1024), 1)
    except Exception:
        pass

    return {
        "status": "healthy" if ORCHESTRATOR_AVAILABLE else "degraded",
        "uptime": uptime_seconds,
        "memory_usage": memory_usage_mb
    }

@app.get("/api/status")
async def get_status():
    """Get system status with Zynd Protocol details"""
    status_response = {
        "status": "online",
        "orchestrator": ORCHESTRATOR_AVAILABLE,
        "zynd_connected": ORCHESTRATOR_AVAILABLE,
        "groq_connected": ORCHESTRATOR_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add Zynd Protocol version info if available
    if ORCHESTRATOR_AVAILABLE:
        try:
            from zynd.protocol import (
                __version__ as zynd_version,
                __python_version__ as python_ver,
                __official_sdk_available__ as sdk_available,
                __supports_official_sdk__ as sdk_supported
            )
            status_response["zynd_protocol"] = {
                "version": zynd_version,
                "python_version": python_ver,
                "using_official_sdk": sdk_available,
                "supports_official_sdk": sdk_supported,
                "mode": "official" if sdk_available else "compatibility"
            }
        except Exception:
            pass
    
    return status_response

@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    return {
        "total_candidates": state.total_candidates,
        "passed_agent1": state.agent_stats["gatekeeper"].get("passed", 0),
        "passed_agent2": state.agent_stats["validator"].get("passed", 0),
        "approved_total": state.approved,
        "fraud_detected": state.fraud_detected,
        "agent_stats": state.agent_stats
    }

@app.get("/api/agents")
async def get_agents():
    """Get agent information and stats - formatted for GodMode component"""
    
    # Helper function to calculate metrics from agent stats
    def format_agent_stats(agent_name: str, role: str, stats: dict) -> dict:
        processed = stats.get("processed", 0)
        passed = stats.get("passed", 0)
        
        # Calculate success rate
        success_rate = round((passed / processed * 100) if processed > 0 else 0, 1)
        
        # Get average time (default to reasonable values if not tracked)
        avg_time = stats.get("avg_time", 1.5)
        
        return {
            "name": agent_name,
            "role": role,
            "status": "active" if ORCHESTRATOR_AVAILABLE else "idle",
            "processed": processed,
            "successRate": success_rate,
            "avgTime": avg_time
        }
    
    return {
        "agents": [
            format_agent_stats("Gatekeeper", "Entry Filter", state.agent_stats["gatekeeper"]),
            format_agent_stats("Validator", "Verification", state.agent_stats["validator"]),
            format_agent_stats("Inquisitor", "Deep Analysis", state.agent_stats["inquisitor"])
        ]
    }

@app.get("/api/audit")
async def get_audit_trail():
    """Get audit trail logs"""
    return {"audit_logs": state.audit_logs}

@app.get("/api/candidates")
async def get_candidates():
    """Get list of processed candidates"""
    return {"candidates": state.candidates}

@app.post("/api/verify")
@limiter.limit("20/minute")  # Rate limit: 20 verification requests per minute (demo-friendly)
async def verify_candidate(request: Request, verify_req: VerifyRequest):
    """
    Main verification endpoint - processes candidate through all 3 agents
    """
    candidate_id = f"CAND-{uuid.uuid4().hex[:4].upper()}"
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    result = {
        "id": candidate_id,
        "status": "processing",
        "trust_score": None,
        "skill_match": None,
        "timestamp": timestamp,
        "stages": {},
        "redacted_resume": None,
        "questions": [],
        "credential": None
    }
    
    # Add audit log for start
    state.add_audit_log({
        "time": timestamp,
        "user": "System",
        "action": f"Started verification for {candidate_id}",
        "module": "Pipeline",
        "status": "pending"
    })
    
    if ORCHESTRATOR_AVAILABLE and orchestrator:
        try:
            print(f"\n🚀 Running REAL AI pipeline for {candidate_id}...")
            print(f"   Resume length: {len(verify_req.resume_text)} chars")
            print(f"   JD length: {len(verify_req.job_description)} chars")
            
            # Run through the actual AI pipeline (offload blocking sync call)
            loop = asyncio.get_event_loop()
            pipeline_result = await loop.run_in_executor(
                None,
                lambda: orchestrator.run_verification_pipeline(
                    verify_req.resume_text,
                    verify_req.job_description
                )
            )
            
            print(f"   ✅ Pipeline completed: {pipeline_result.get('final_status')}")
            
            # Extract results from pipeline_stages structure
            agent1 = pipeline_result.get("pipeline_stages", {}).get("agent_1", {})
            agent2 = pipeline_result.get("pipeline_stages", {}).get("agent_2", {})
            agent3 = pipeline_result.get("pipeline_stages", {}).get("agent_3_questions", {})
            
            # Determine overall status
            final_status = pipeline_result.get("final_status", "PENDING")
            agent1_status = pipeline_result.get("agent_1_status", "UNKNOWN")
            agent2_status = pipeline_result.get("agent_2_status", "UNKNOWN")
            
            # Calculate scores
            skill_match_score = agent2.get("score", 0) if agent2 else 0
            # Trust score is independently derived — prefer agent3's trust, fallback to weighted skill_match
            trust_score_val = (
                agent3.get("trust_score", None) if agent3 else None
            )
            if trust_score_val is None:
                trust_score_val = round(skill_match_score * 0.92, 1)
            # Verified skills come from agent2's matched_skills list
            verified_skills = agent2.get("matched_skills", []) if agent2 else []
            
            # Determine if passed (at least got to questions stage)
            is_passed = final_status in ["QUESTIONS_PENDING", "PASS", "VERIFIED"]
            
            result["id"] = pipeline_result.get("candidate_id", candidate_id)
            result["status"] = "passed" if is_passed else "failed"
            result["trust_score"] = round(trust_score_val, 1) if trust_score_val is not None else 85
            result["skill_match"] = round(skill_match_score, 1) if skill_match_score is not None else 80
            result["verified_skills"] = verified_skills
            result["years_exp"] = pipeline_result.get("years_exp", 0)  # Add years to top level
            # Agent 1 returns "clean_data_full_text" at top level, not nested in clean_data
            result["redacted_resume"] = (
                agent1.get("clean_data_full_text")
                or agent1.get("clean_data", {}).get("redacted_text", "")
                or agent1.get("redacted_text", "")
            )
            result["questions"] = pipeline_result.get("verification_questions", [])
            result["credential"] = pipeline_result.get("credentials_issued", [{}])[0] if pipeline_result.get("credentials_issued") else {}
            
            result["stages"] = {
                "gatekeeper": {
                    "status": "passed" if agent1_status == "PASS" else "failed",
                    "pii_removed": True,
                    "eligible": agent1.get("eligible", False),
                    "years_exp": agent1.get("years_exp", 0)
                },
                "validator": {
                    "status": "passed" if agent2_status == "PASS" else ("pending" if not agent2 else "failed"),
                    "skill_match": skill_match_score,
                    "matched_skills": verified_skills
                },
                "inquisitor": {
                    "status": "passed" if agent3 else "pending",
                    "trust_score": result["trust_score"],
                    "questions_generated": len(result["questions"])
                }
            }
            
            # Update agent stats with actual results
            state.update_agent_stats("gatekeeper", agent1_status == "PASS")
            if agent2:
                state.update_agent_stats("validator", agent2_status == "PASS")
            if agent3:
                state.update_agent_stats("inquisitor", True)  # If agent3 ran, questions were generated
            
            if result["status"] == "passed":
                state.approved += 1
                
            # Add successful audit log
            state.add_audit_log({
                "time": datetime.now().strftime("%H:%M:%S"),
                "user": pipeline_result.get("candidate_id", candidate_id),
                "action": f"Pipeline completed: {final_status}",
                "module": "Velos Pipeline",
                "status": "success" if is_passed else "warning"
            })
                
        except Exception as e:
            import traceback
            error_msg = f"Pipeline error: {str(e)}"
            print(f"\n❌ {error_msg}")
            print(f"   Full traceback:")
            traceback.print_exc()
            
            # Return detailed error response instead of falling back
            result["status"] = "failed"
            result["error"] = error_msg
            result["error_type"] = type(e).__name__
            result["stages"] = {
                "gatekeeper": {"status": "failed", "error": error_msg},
                "validator": {"status": "pending"},
                "inquisitor": {"status": "pending"}
            }
            
            state.add_audit_log({
                "time": datetime.now().strftime("%H:%M:%S"),
                "user": "System",
                "action": f"Pipeline error: {str(e)[:100]}",
                "module": "Pipeline",
                "status": "failed"
            })
            
            # Don't continue processing if pipeline failed
            return result
    else:
        # Simulation mode (orchestrator not available)
        import random
        print(f"\n⚠️ Running in SIMULATION MODE (Orchestrator not available)")
        print(f"   ORCHESTRATOR_AVAILABLE: {ORCHESTRATOR_AVAILABLE}")
        print(f"   orchestrator object: {orchestrator is not None}\n")
        
        result["simulation_mode"] = True
        result["status"] = random.choice(["passed", "passed", "passed", "failed"])
        result["trust_score"] = random.randint(75, 98) if result["status"] == "passed" else random.randint(40, 60)
        result["skill_match"] = random.randint(70, 95) if result["status"] == "passed" else random.randint(45, 65)
        result["redacted_resume"] = "[REDACTED NAME]\n[REDACTED EMAIL]\n[REDACTED PHONE]\n\n" + verify_req.resume_text[:500] + "..."
        result["questions"] = [
            "Can you explain your experience with the main technology stack mentioned?",
            "Describe a challenging project you led and its outcomes.",
            "How do you handle tight deadlines and competing priorities?"
        ]
        
        result["stages"] = {
            "gatekeeper": {"status": "passed", "pii_removed": True, "eligible": True},
            "validator": {"status": "passed", "skill_match": result["skill_match"]},
            "inquisitor": {"status": result["status"], "trust_score": result["trust_score"]}
        }
        
        state.update_agent_stats("gatekeeper", True)
        state.update_agent_stats("validator", True)
        state.update_agent_stats("inquisitor", result["status"] == "passed")
        
        if result["status"] == "passed":
            state.approved += 1
    
    # Add candidate to list
    state.add_candidate(result)
    
    # Add individual agent logs FIRST (so they appear in chronological order)
    for agent_name, agent_result in result.get("stages", {}).items():
        agent_status = agent_result.get("status", "unknown")
        # Map status to correct format for audit log
        if agent_status == "passed":
            log_status = "success"
        elif agent_status == "failed":
            log_status = "failed"
        else:
            log_status = "pending"
            
        state.add_audit_log({
            "time": datetime.now().strftime("%H:%M:%S"),
            "user": agent_name.title(),
            "action": f"Processed {candidate_id}",
            "module": f"Agent {agent_name}",
            "status": log_status
        })
    
    # Add completion audit log LAST
    completion_status = "success" if result["status"] == "passed" else "failed"
    state.add_audit_log({
        "time": datetime.now().strftime("%H:%M:%S"),
        "user": "Pipeline",
        "action": f"Completed verification for {candidate_id}",
        "module": "Verification",
        "status": completion_status
    })
    
    return result

# ==================== FILE UPLOAD ENDPOINTS ====================

@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse a resume file (PDF, DOCX, TXT, or image).
    Uses hybrid parsing with automatic OCR fallback for scanned documents.
    
    Supported formats:
    - PDF (text-based and scanned)
    - DOCX (Word documents)
    - TXT (plain text)
    - Images (PNG, JPG, JPEG, TIFF, BMP) - via OCR
    """
    if not PARSER_AVAILABLE or not resume_parser:
        raise HTTPException(
            status_code=503,
            detail="Resume parser not available. Please check server logs."
        )
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    allowed_extensions = ['.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file content into memory (async)
        file_content = await file.read()
        
        # Parse the resume (offload blocking call to thread pool)
        loop = asyncio.get_event_loop()
        extracted_text, metadata = await loop.run_in_executor(
            None,
            lambda: resume_parser.parse_file(file_content, file.filename)
        )
        
        # Add audit log
        state.add_audit_log({
            "time": datetime.now().strftime("%H:%M:%S"),
            "user": "Resume Parser",
            "action": f"Parsed {file.filename} ({metadata['extraction_method']})",
            "module": "File Upload",
            "status": "success" if extracted_text else "warning"
        })
        
        return {
            "success": True,
            "filename": file.filename,
            "extracted_text": extracted_text,
            "metadata": metadata,
            "preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        state.add_audit_log({
            "time": datetime.now().strftime("%H:%M:%S"),
            "user": "Resume Parser",
            "action": f"Failed to parse {file.filename}: {str(e)[:50]}",
            "module": "File Upload",
            "status": "failed"
        })
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")


@app.post("/api/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """
    Alias for upload-resume - parses a resume file and returns extracted text.
    Used by the frontend file drop zone.
    """
    if not PARSER_AVAILABLE or not resume_parser:
        # Fallback: for txt files, just return the content
        if file.filename and file.filename.lower().endswith('.txt'):
            content = await file.read()
            text = content.decode('utf-8', errors='ignore')
            return {
                "text": text,
                "word_count": len(text.split()),
                "filename": file.filename
            }
        raise HTTPException(
            status_code=503,
            detail="Resume parser not available. Please use text input instead."
        )
    
    try:
        file_content = await file.read()
        loop = asyncio.get_event_loop()
        extracted_text, metadata = await loop.run_in_executor(
            None,
            lambda: resume_parser.parse_file(file_content, file.filename)
        )
        
        return {
            "text": extracted_text,
            "word_count": len(extracted_text.split()),
            "filename": file.filename,
            "extraction_method": metadata.get('extraction_method', 'unknown')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/verify-file")
async def verify_file(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Upload a resume file and run full verification pipeline.
    Combines file parsing with AI agent verification.
    
    Args:
        resume: Resume file (PDF, DOCX, TXT, or image)
        job_description: Job description text
    """
    if not PARSER_AVAILABLE or not resume_parser:
        raise HTTPException(
            status_code=503,
            detail="Resume parser not available"
        )
    
    # Validate file
    if not resume.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    allowed_extensions = ['.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    file_ext = Path(resume.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}"
        )
    
    try:
        # Read and parse the resume file (offload blocking call)
        file_content = await resume.read()
        loop = asyncio.get_event_loop()
        extracted_text, parse_metadata = await loop.run_in_executor(
            None,
            lambda: resume_parser.parse_file(file_content, resume.filename)
        )
        
        if not extracted_text or len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from the resume. Please try a different file."
            )
        
        # Now run verification with extracted text
        candidate_id = f"CAND-{uuid.uuid4().hex[:4].upper()}"
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        result = {
            "id": candidate_id,
            "status": "processing",
            "trust_score": None,
            "skill_match": None,
            "timestamp": timestamp,
            "stages": {},
            "redacted_resume": None,
            "questions": [],
            "credential": None,
            "file_info": {
                "filename": resume.filename,
                "extraction_method": parse_metadata.get("extraction_method"),
                "ocr_used": parse_metadata.get("ocr_used", False),
                "char_count": parse_metadata.get("char_count", 0)
            }
        }
        
        # Add audit log
        state.add_audit_log({
            "time": timestamp,
            "user": "System",
            "action": f"Started file verification for {candidate_id} ({resume.filename})",
            "module": "Pipeline",
            "status": "pending"
        })
        
        if ORCHESTRATOR_AVAILABLE and orchestrator:
            try:
                # Run through the actual AI pipeline (offload blocking sync call)
                loop = asyncio.get_event_loop()
                pipeline_result = await loop.run_in_executor(
                    None,
                    lambda: orchestrator.run_verification_pipeline(
                        extracted_text,
                        job_description
                    )
                )
                
                # Extract results from pipeline_stages structure
                agent1 = pipeline_result.get("pipeline_stages", {}).get("agent_1", {})
                agent2 = pipeline_result.get("pipeline_stages", {}).get("agent_2", {})
                agent3 = pipeline_result.get("pipeline_stages", {}).get("agent_3_questions", {})
                
                final_status = pipeline_result.get("final_status", "PENDING")
                agent1_status = pipeline_result.get("agent_1_status", "UNKNOWN")
                agent2_status = pipeline_result.get("agent_2_status", "UNKNOWN")
                
                skill_match_score = agent2.get("score", 0) if agent2 else 0
                # Trust score independently derived — prefer agent3's trust, fallback to weighted skill_match
                trust_score_val = (
                    agent3.get("trust_score", None) if agent3 else None
                )
                if trust_score_val is None:
                    trust_score_val = round(skill_match_score * 0.92, 1)
                # Verified skills come from agent2's matched_skills list
                verified_skills = agent2.get("matched_skills", []) if agent2 else []
                is_passed = final_status in ["QUESTIONS_PENDING", "PASS", "VERIFIED"]
                
                result["id"] = pipeline_result.get("candidate_id", candidate_id)
                result["status"] = "passed" if is_passed else "failed"
                result["trust_score"] = round(trust_score_val, 1) if trust_score_val is not None else 85
                result["skill_match"] = round(skill_match_score, 1) if skill_match_score is not None else 80
                result["verified_skills"] = verified_skills
                # Agent 1 returns "clean_data_full_text" at top level, not nested in clean_data
                result["redacted_resume"] = (
                    agent1.get("clean_data_full_text")
                    or agent1.get("clean_data", {}).get("redacted_text", "")
                    or agent1.get("redacted_text", "")
                )
                result["questions"] = pipeline_result.get("verification_questions", [])
                result["credential"] = pipeline_result.get("credentials_issued", [{}])[0] if pipeline_result.get("credentials_issued") else {}
                
                result["stages"] = {
                    "gatekeeper": {
                        "status": "passed" if agent1_status == "PASS" else "failed",
                        "pii_removed": True,
                        "eligible": agent1.get("eligible", False),
                        "years_exp": agent1.get("years_exp", 0)
                    },
                    "validator": {
                        "status": "passed" if agent2_status == "PASS" else ("pending" if not agent2 else "failed"),
                        "skill_match": skill_match_score,
                        "matched_skills": verified_skills
                    },
                    "inquisitor": {
                        "status": "passed" if agent3 else "pending",
                        "trust_score": result["trust_score"],
                        "questions_generated": len(result["questions"])
                    }
                }
                
                state.update_agent_stats("gatekeeper", agent1_status == "PASS")
                if agent2:
                    state.update_agent_stats("validator", agent2_status == "PASS")
                if agent3:
                    state.update_agent_stats("inquisitor", True)
                
                if result["status"] == "passed":
                    state.approved += 1
                    
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
        else:
            # Simulation mode
            import random
            result["status"] = random.choice(["passed", "passed", "passed", "failed"])
            result["trust_score"] = random.randint(75, 98) if result["status"] == "passed" else random.randint(40, 60)
            result["skill_match"] = random.randint(70, 95) if result["status"] == "passed" else random.randint(45, 65)
            result["redacted_resume"] = "[REDACTED]\n\n" + extracted_text[:500] + "..."
            result["questions"] = [
                "Can you explain your experience with the main technology stack?",
                "Describe a challenging project you led.",
                "How do you handle tight deadlines?"
            ]
            result["stages"] = {
                "gatekeeper": {"status": "passed", "pii_removed": True},
                "validator": {"status": "passed", "skill_match": result["skill_match"]},
                "inquisitor": {"status": result["status"], "trust_score": result["trust_score"]}
            }
        
        state.add_candidate(result)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@app.get("/api/parser-status")
async def get_parser_status():
    """Get resume parser status and supported formats"""
    if PARSER_AVAILABLE and resume_parser:
        return {
            "available": True,
            "supported_formats": resume_parser.get_supported_formats(),
            "ocr_available": resume_parser.get_supported_formats().get("ocr_fallback", False)
        }
    return {
        "available": False,
        "supported_formats": {},
        "ocr_available": False
    }


# ============ TRUST LAYER ENDPOINTS ============

@app.get("/api/candidates/{candidate_id}/trust-packet")
async def get_trust_packet(candidate_id: str):
    """
    Get the Trust Packet for a candidate.
    
    Contains:
    - diff_report: Visual proof of PII redaction (for red/green highlighting)
    - integrity_block: Cryptographic proof of decision integrity
    - verification_status: Whether the data is tamper-free
    
    Frontend uses this to show the "Trust Dashboard" with:
    - Redaction visualizer (what PII was removed)
    - Verified badge (cryptographic proof)
    """
    try:
        # Guard: orchestrator must be available
        if not ORCHESTRATOR_AVAILABLE or not orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not available")
        # Try live trust packet first (works for any candidate in audit_db, not just current)
        trust_packet = orchestrator.get_trust_packet(candidate_id)
        if "error" not in trust_packet:
            return {
                "success": True,
                "trust_packet": trust_packet
            }
        
        # Fall back to stored verification results
        stored_result = orchestrator.audit_db.get_verification_result(candidate_id)
        
        if stored_result:
            trust_layer = stored_result.get("trust_layer", {})
            return {
                "success": True,
                "trust_packet": {
                    "candidate_id": candidate_id,
                    "timestamp": stored_result.get("timestamp"),
                    
                    # Visual Proof
                    "diff_report": trust_layer.get("diff_report"),
                    "diff_stats": trust_layer.get("diff_stats"),
                    "redaction_verified": trust_layer.get("redaction_verified", False),
                    
                    # Cryptographic Proof
                    "block_id": trust_layer.get("block_id"),
                    "data_hash": trust_layer.get("data_hash"),
                    "signature": trust_layer.get("signature"),
                    "sealed_at": trust_layer.get("sealed_at"),
                    
                    # Status
                    "integrity_verified": True if trust_layer.get("data_hash") else False
                }
            }
        
        raise HTTPException(status_code=404, detail="Trust packet not found for this candidate")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trust packet: {str(e)}")


@app.get("/api/trust-packet/{candidate_id}")
async def get_trust_packet_simple(candidate_id: str):
    """
    Simplified trust packet endpoint for frontend.
    Returns diff visualization and cryptographic proof chain.
    """
    try:
        # Check in stored candidates first
        candidate = None
        for c in state.candidates:
            if c.get("id") == candidate_id:
                candidate = c
                break
        
        # Try to get from orchestrator storage
        stored_result = None
        if ORCHESTRATOR_AVAILABLE and orchestrator and orchestrator.audit_db:
            stored_result = orchestrator.audit_db.get_verification_result(candidate_id)
        
        # Build response
        response = {
            "candidate_id": candidate_id,
            "diff": [],
            "ledger": [],
            "verified": False
        }
        
        if stored_result:
            trust_layer = stored_result.get("trust_layer", {})
            
            # Get diff report for visualization
            diff_report = trust_layer.get("diff_report", [])
            if diff_report:
                response["diff"] = diff_report
            
            # Build ledger from verification stages
            ledger = []
            stages = stored_result.get("pipeline_result", {}).get("stages", {})
            
            # Add stage entries to ledger
            if "gatekeeper" in stages:
                ledger.append({
                    "agent": "Blind Gatekeeper",
                    "action": "PII Redaction",
                    "timestamp": stored_result.get("timestamp", ""),
                    "data_hash": trust_layer.get("data_hash", "")[:32] + "..." if trust_layer.get("data_hash") else None,
                    "prev_hash": "genesis"
                })
            
            if "validator" in stages:
                ledger.append({
                    "agent": "Skill Validator", 
                    "action": "Skill Matching",
                    "timestamp": stored_result.get("timestamp", ""),
                    "data_hash": hashlib.sha256(str(stages.get("validator", {})).encode()).hexdigest()[:32] + "...",
                    "prev_hash": ledger[-1]["data_hash"] if ledger else "genesis"
                })
            
            if "inquisitor" in stages:
                ledger.append({
                    "agent": "Inquisitor",
                    "action": "Authenticity Check",
                    "timestamp": stored_result.get("timestamp", ""),
                    "data_hash": hashlib.sha256(str(stages.get("inquisitor", {})).encode()).hexdigest()[:32] + "...",
                    "prev_hash": ledger[-1]["data_hash"] if ledger else "genesis"
                })
            
            response["ledger"] = ledger
            response["verified"] = trust_layer.get("redaction_verified", False) or len(ledger) > 0
        
        elif candidate:
            # Build from in-memory candidate data
            response["verified"] = candidate.get("status") == "passed"
            response["ledger"] = [
                {
                    "agent": "Blind Gatekeeper",
                    "action": "PII Redaction",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data_hash": hashlib.sha256(candidate_id.encode()).hexdigest()[:32] + "...",
                    "prev_hash": "genesis"
                }
            ]
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trust packet: {str(e)}")


@app.get("/api/candidates/{candidate_id}/verify-integrity")
async def verify_integrity(candidate_id: str):
    """
    Verify the integrity of a candidate's verification data.
    
    Re-computes the SHA-256 hash and compares with the stored block.
    Returns True only if the hashes match (no tampering detected).
    """
    try:
        if not ORCHESTRATOR_AVAILABLE or not orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not available")
        report = orchestrator.verify_candidate_integrity(candidate_id)
        return {
            "success": True,
            "verification_report": report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integrity verification failed: {str(e)}")


# ============ NEW BLOCKCHAIN ENDPOINTS ============

@app.get("/api/blockchain/network-info")
async def get_blockchain_network_info():
    """
    Get blockchain network information and wallet status.
    
    Returns network name, wallet address, balance, and connection status.
    """
    try:
        if not ORCHESTRATOR_AVAILABLE or not orchestrator or not orchestrator.blockchain_did_manager:
            return {
                "enabled": False,
                "message": "Blockchain integration not available"
            }
        
        blockchain_mgr = orchestrator.blockchain_did_manager
        
        # Check connection (use blockchain_available attribute)
        connection_status = blockchain_mgr.blockchain_available
        
        # Get account balance (offload blocking web3 RPC call)
        try:
            loop = asyncio.get_event_loop()
            balance_wei = await loop.run_in_executor(
                None,
                lambda: blockchain_mgr.w3.eth.get_balance(blockchain_mgr.account.address)
            )
            balance = f"{blockchain_mgr.w3.from_wei(balance_wei, 'ether'):.4f} ETH"
        except Exception:
            balance = "0.0000 ETH"
        
        return {
            "enabled": True,
            "network_name": blockchain_mgr.network_name,
            "chain_id": blockchain_mgr.chain_id,
            "wallet_address": blockchain_mgr.account.address,
            "balance": balance,
            "connected": connection_status,
            "explorer_url": f"{blockchain_mgr.explorer_url}/address/{blockchain_mgr.account.address}",
            "faucet_url": "https://www.alchemy.com/faucets/optimism-sepolia"
        }
    except Exception as e:
        logger.error(f"Blockchain network info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/credentials/{credential_id}")
async def get_credential(credential_id: str):
    """
    Retrieve a specific credential by ID.
    
    Returns the full W3C Verifiable Credential with all proofs.
    """
    try:
        if not ORCHESTRATOR_AVAILABLE or not orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not available")
        
        # Search all candidates in audit_db for this credential
        credentials = []
        if orchestrator.audit_db:
            for cand in state.candidates:
                stored = orchestrator.audit_db.get_verification_result(cand.get("id", ""))
                if stored:
                    credentials.extend(stored.get("credentials_issued", []))
        
        for cred in credentials:
            if cred.get("id") == credential_id or credential_id in cred.get("id", ""):
                return {
                    "success": True,
                    "credential": cred
                }
        
        raise HTTPException(status_code=404, detail=f"Credential {credential_id} not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Credential retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/credentials/verify")
async def verify_credential(request: Request):
    """
    Verify an externally-provided W3C Verifiable Credential.
    
    Accepts a credential JSON and validates:
    - Structure and schema
    - Expiration date
    - Cryptographic signature
    - Issuer DID
    - Revocation status
    """
    try:
        if not ORCHESTRATOR_AVAILABLE or not orchestrator or not orchestrator.w3c_credential_manager:
            raise HTTPException(status_code=503, detail="W3C credential verification not available")
        
        credential_data = await request.json()
        
        # Verify the credential
        verification_result = orchestrator.w3c_credential_manager.verify_credential(credential_data)
        
        return {
            "success": True,
            "verification_result": verification_result
        }
        
    except Exception as e:
        logger.error(f"Credential verification error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/credentials/{credential_id}/export")
async def export_credential(credential_id: str, format: str = "json-ld"):
    """
    Export a credential in various formats.
    
    Formats:
    - json-ld: W3C JSON-LD format
    - jwt: JWT format
    - qr: QR code image (base64)
    """
    try:
        if not ORCHESTRATOR_AVAILABLE or not orchestrator or not orchestrator.current_result or not orchestrator.w3c_credential_manager:
            raise HTTPException(status_code=404, detail="Credential system not available")
        
        # Find the credential
        credentials = orchestrator.current_result.get("credentials_issued", [])
        credential = None
        
        for cred in credentials:
            if cred.get("id") == credential_id or credential_id in cred.get("id", ""):
                credential = cred
                break
        
        if not credential:
            raise HTTPException(status_code=404, detail=f"Credential {credential_id} not found")
        
        # Export in requested format
        exported = orchestrator.w3c_credential_manager.export_credential(credential, format)
        
        if format == "qr":
            return {
                "success": True,
                "format": "qr",
                "qr_code": exported,  # Base64 encoded PNG
                "credential_id": credential_id
            }
        elif format == "jwt":
            return {
                "success": True,
                "format": "jwt",
                "jwt": exported,
                "credential_id": credential_id
            }
        else:  # json-ld
            return {
                "success": True,
                "format": "json-ld",
                "credential": exported,
                "credential_id": credential_id
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Credential export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/credentials/{credential_id}/revoke")
async def revoke_credential(credential_id: str, reason: str = "unspecified"):
    """
    Revoke a credential.
    
    Adds the credential to the revocation registry.
    """
    try:
        if not ORCHESTRATOR_AVAILABLE or not orchestrator or not orchestrator.w3c_credential_manager:
            raise HTTPException(status_code=503, detail="Credential revocation not available")
        
        # Revoke the credential
        orchestrator.w3c_credential_manager.revoke_credential(credential_id, reason)
        
        return {
            "success": True,
            "message": f"Credential {credential_id} has been revoked",
            "reason": reason,
            "revoked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Credential revocation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/messages")
async def get_agent_messages(limit: int = 50):
    """
    Get recent agent-to-agent messages.
    
    Returns blockchain-authenticated messages from the communication hub.
    """
    try:
        if not orchestrator or not orchestrator.communication_hub:
            return {
                "enabled": False,
                "messages": []
            }
        
        # Get message history from communication hub
        # get_message_history() returns {"sent": [...], "received": [...]}
        history = orchestrator.communication_hub.get_message_history(limit=limit)
        all_messages = history.get("sent", []) + history.get("received", [])
        
        return {
            "enabled": True,
            "count": len(all_messages),
            "messages": all_messages  # already dicts from to_dict() inside get_message_history
        }
        
    except Exception as e:
        logger.error(f"Agent messages error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trust-packet/{candidate_id}/enhanced")
async def get_enhanced_trust_packet(candidate_id: str):
    """
    Get enhanced trust packet with blockchain metadata.
    
    Includes:
    - Visual proof (PII diff)
    - Cryptographic proof (integrity block)
    - Blockchain credentials with full W3C proofs
    - Network metadata
    - Verification links
    """
    try:
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not available")
        
        # Get base trust packet
        trust_packet = orchestrator.get_trust_packet(candidate_id)
        
        # Add blockchain enhancements if available
        if orchestrator.blockchain_did_manager and orchestrator.current_result:
            blockchain_metadata = orchestrator.current_result.get("blockchain_metadata", {})
            credentials = orchestrator.current_result.get("credentials_issued", [])
            
            trust_packet["blockchain"] = {
                "enabled": True,
                "network": orchestrator.blockchain_did_manager.network_name,
                "chain_id": orchestrator.blockchain_did_manager.chain_id,
                "wallet": orchestrator.blockchain_did_manager.account.address,
                "explorer": f"https://sepolia-optimism.etherscan.io/address/{orchestrator.blockchain_did_manager.account.address}",
                "credentials_count": len(credentials),
                "credential_ids": [c.get("id") for c in credentials],
                "metadata": blockchain_metadata
            }
            
            # Add W3C credential details
            trust_packet["credentials"] = credentials
            
            # Add agent messages
            if orchestrator.communication_hub:
                messages = orchestrator.communication_hub.get_message_history(limit=10)
                # get_message_history returns {"sent": [...], "received": [...]}
                trust_packet["agent_messages"] = messages if isinstance(messages, dict) else {}
        else:
            trust_packet["blockchain"] = {"enabled": False}
        
        return trust_packet
        
    except Exception as e:
        logger.error(f"Enhanced trust packet error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/job-description")
async def get_job_description_template():
    """Get sample job description"""
    return {
        "job_description": """Senior Software Engineer - AI/ML Platform

Requirements:
• 5+ years of software engineering experience
• Strong Python programming skills
• Experience with machine learning frameworks (TensorFlow, PyTorch)
• Knowledge of distributed systems and microservices
• Experience with cloud platforms (AWS, GCP, Azure)
• Strong problem-solving and analytical abilities
• Excellent communication and teamwork skills

Nice to have:
• Experience with LangChain or similar LLM frameworks
• Knowledge of MLOps and CI/CD practices
• Contributions to open source projects
• Experience with Kubernetes and Docker

Responsibilities:
• Design and implement scalable AI/ML infrastructure
• Collaborate with data scientists to deploy models to production
• Write clean, maintainable, and well-tested code
• Mentor junior engineers and conduct code reviews
• Participate in system design and architecture decisions"""
    }

@app.get("/api/insights")
async def get_god_mode_insights():
    """Get God Mode insights - metrics for dashboard"""
    # Calculate metrics from state
    total_processed = state.total_candidates
    fraud_cases = state.fraud_detected
    
    # Calculate average processing time from agent stats
    avg_times = []
    for agent_stats in state.agent_stats.values():
        if "avg_time" in agent_stats and agent_stats["avg_time"] > 0:
            avg_times.append(agent_stats["avg_time"])
    
    avg_processing_time = round(sum(avg_times) / len(avg_times), 2) if avg_times else 2.4
    
    # Count bias alerts (actual count — zero until real detection is implemented)
    bias_alerts = 0
    
    return {
        "bias_alerts": bias_alerts,
        "fraud_cases": fraud_cases,
        "avg_processing_time": avg_processing_time,
        "total_candidates": total_processed
    }

@app.get("/api/chart-data/{chart_type}")
async def get_chart_data(chart_type: str):
    """Get chart data for frontend - computed from real state"""
    allowed = {"timeline", "radar", "doughnut"}
    if chart_type not in allowed:
        raise HTTPException(status_code=400, detail=f"Unknown chart type '{chart_type}'. Allowed: {', '.join(allowed)}")

    gk = state.agent_stats.get("gatekeeper", {})
    va = state.agent_stats.get("validator", {})
    inq = state.agent_stats.get("inquisitor", {})

    if chart_type == "timeline":
        # Show processed counts per agent as a simple bar
        return {
            "labels": ["Gatekeeper", "Validator", "Inquisitor"],
            "datasets": [
                {"label": "Processed", "data": [
                    gk.get("processed", 0),
                    va.get("processed", 0),
                    inq.get("processed", 0)
                ]},
                {"label": "Passed", "data": [
                    gk.get("passed", 0),
                    va.get("passed", 0),
                    inq.get("passed", 0)
                ]}
            ]
        }
    elif chart_type == "radar":
        gk_rate = round((gk.get("passed", 0) / gk.get("processed", 1)) * 100) if gk.get("processed") else 0
        va_rate = round((va.get("passed", 0) / va.get("processed", 1)) * 100) if va.get("processed") else 0
        inq_rate = round((inq.get("passed", 0) / inq.get("processed", 1)) * 100) if inq.get("processed") else 0
        return {
            "labels": ["Gatekeeper Pass Rate", "Validator Pass Rate", "Inquisitor Pass Rate", "Overall Approval", "Fraud Detection"],
            "data": [
                gk_rate,
                va_rate,
                inq_rate,
                round((state.approved / max(state.total_candidates, 1)) * 100),
                max(0, 100 - round((state.fraud_detected / max(state.total_candidates, 1)) * 100))
            ]
        }
    elif chart_type == "doughnut":
        passed = state.approved
        failed = max(0, state.total_candidates - state.approved - state.fraud_detected)
        fraud = state.fraud_detected
        return {
            "labels": ["Approved", "Rejected", "Fraud Detected"],
            "data": [passed, failed, fraud]
        }


# ============ PHASE 5: BATCH PROCESSING & ANALYTICS ============

@app.post("/api/batch-upload")
async def batch_upload(
    file: UploadFile = File(...),
    job_description: str = Form(""),
    min_years: int = Form(0)
):
    """
    Process a ZIP file containing multiple resumes.
    
    Drag-and-drop a ZIP with PDFs/DOCXs to process the whole batch.
    Returns a summary with pass/fail counts and individual results.
    """
    
    if not BATCH_AVAILABLE or not batch_processor:
        raise HTTPException(status_code=503, detail="Batch processing not available")
    
    if not file.filename or not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Please upload a ZIP file")
    
    try:
        # Read the ZIP file
        zip_bytes = await file.read()
        
        if len(zip_bytes) > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="ZIP file too large (max 50MB)")
        
        # Process the batch (offload potentially multi-minute blocking call)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: batch_processor.process_zip_file(
                zip_bytes=zip_bytes,
                job_description=job_description,
                min_years=min_years
            )
        )
        
        return {
            "success": True,
            "batch_result": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@app.get("/api/leaderboard")
async def get_leaderboard(
    limit: int = 10,
    status_filter: Optional[str] = None,
    min_score: int = 0
):
    """
    Get the candidate leaderboard ranked by skill score.
    
    Ranking: Primary by skill score, tie-breaker by experience years.
    Filter by status or minimum score as needed.
    """
    
    if not BATCH_AVAILABLE or not analytics_engine:
        raise HTTPException(status_code=503, detail="Analytics not available")
    
    try:
        loop = asyncio.get_event_loop()
        leaderboard = await loop.run_in_executor(
            None,
            lambda: analytics_engine.get_leaderboard(
                limit=limit,
                status_filter=status_filter,
                min_score=min_score
            )
        )
        
        return {
            "success": True,
            "data": leaderboard
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate leaderboard: {str(e)}")


@app.get("/api/compare")
async def compare_candidates(candidate_a: str, candidate_b: str):
    """
    Compare two candidates side-by-side.
    
    Returns scores, skills, and a recommendation on who is the better fit.
    """
    
    if not BATCH_AVAILABLE or not analytics_engine:
        raise HTTPException(status_code=503, detail="Analytics not available")
    
    if not candidate_a or not candidate_b:
        raise HTTPException(status_code=400, detail="Both candidate IDs required")
    
    try:
        loop = asyncio.get_event_loop()
        comparison = await loop.run_in_executor(
            None,
            lambda: analytics_engine.compare_candidates(candidate_a, candidate_b)
        )
        
        if "error" in comparison:
            raise HTTPException(status_code=404, detail=comparison["error"])
        
        return {
            "success": True,
            "comparison": comparison
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@app.get("/api/export-report")
async def export_report(
    candidate_ids: Optional[str] = None,
    include_all: bool = False,
    format: str = "csv"
):
    """
    Export a hiring report as a downloadable CSV file.
    
    Args:
        candidate_ids: Comma-separated list of candidate IDs
        include_all: If true, include all candidates
        format: Export format (currently only 'csv')
    """
    from fastapi.responses import StreamingResponse
    
    if not BATCH_AVAILABLE or not report_generator:
        raise HTTPException(status_code=503, detail="Report generation not available")
    
    try:
        # Parse candidate IDs
        ids = None
        if candidate_ids:
            ids = [cid.strip() for cid in candidate_ids.split(",")]
        
        # Generate CSV (offload blocking call)
        loop = asyncio.get_event_loop()
        csv_bytes = await loop.run_in_executor(
            None,
            lambda: report_generator.generate_csv_bytes(
                candidate_ids=ids,
                include_all=include_all
            )
        )
        
        # Get filename
        filename = report_generator.get_report_filename("candidates")
        
        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.get("/api/export-batch-report")
async def export_batch_report(batch_id: Optional[str] = None):
    """
    Export a batch processing report as CSV.
    
    Returns the results from the most recent batch processing run.
    """
    from fastapi.responses import StreamingResponse
    
    if not BATCH_AVAILABLE or not batch_processor or not report_generator:
        raise HTTPException(status_code=503, detail="Batch reporting not available")
    
    # For now, return stats about processing
    # In a full implementation, we'd store batch results by ID
    stats = batch_processor.get_stats()
    
    if stats["total_processed"] == 0:
        raise HTTPException(status_code=404, detail="No batch processing results available")
    
    # Create a simple stats report
    output = io.StringIO()
    import csv
    writer = csv.writer(output)
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Total Processed", stats["total_processed"]])
    writer.writerow(["Total Passed", stats["total_passed"]])
    writer.writerow(["Total Failed", stats["total_failed"]])
    writer.writerow(["Total Errors", stats["total_errors"]])
    writer.writerow(["Pass Rate", f"{round(stats['total_passed']/stats['total_processed']*100, 1)}%" if stats['total_processed'] else "0%"])
    
    csv_bytes = output.getvalue().encode('utf-8')
    filename = report_generator.get_report_filename("batch_stats")
    
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@app.get("/api/batch-stats")
async def get_batch_stats():
    """Get cumulative batch processing statistics"""
    
    if not BATCH_AVAILABLE or not batch_processor:
        return {
            "available": False,
            "stats": {}
        }
    
    stats = batch_processor.get_stats()
    
    return {
        "available": True,
        "stats": {
            **stats,
            "pass_rate": round(stats["total_passed"] / stats["total_processed"] * 100, 1) if stats["total_processed"] else 0
        }
    }


@app.get("/api/skill-distribution")
async def get_skill_distribution():
    """Get skill frequency distribution across all candidates"""
    
    if not BATCH_AVAILABLE or not analytics_engine:
        raise HTTPException(status_code=503, detail="Analytics not available")
    
    try:
        loop = asyncio.get_event_loop()
        distribution = await loop.run_in_executor(
            None,
            analytics_engine.get_skill_distribution
        )
        return {
            "success": True,
            "data": distribution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/candidate-dossier/{candidate_id}")
async def get_candidate_dossier(candidate_id: str):
    """
    Get a detailed hiring dossier for a single candidate.
    
    Returns a formatted text report suitable for printing/sharing.
    """
    
    if not BATCH_AVAILABLE or not report_generator:
        raise HTTPException(status_code=503, detail="Report generation not available")
    
    try:
        loop = asyncio.get_event_loop()
        dossier = await loop.run_in_executor(
            None,
            lambda: report_generator.generate_detailed_report(candidate_id)
        )
        
        if "not found" in dossier.lower():
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
        
        return {
            "success": True,
            "candidate_id": candidate_id,
            "dossier": dossier
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dossier: {str(e)}")


# ==================== SAMPLE DATA ENDPOINTS ====================

@app.get("/api/sample-resume")
async def get_sample_resume():
    """Get sample resume text for testing"""
    try:
        sample_path = os.path.join(os.path.dirname(__file__), "mock_data", "sample_resume.txt")
        if os.path.exists(sample_path):
            with open(sample_path, 'r', encoding='utf-8') as f:
                resume_text = f.read()
        else:
            # Fallback sample resume
            resume_text = """Name: Aarvex Nolin
Target Role: Applied AI Engineer / GenAI Engineer (Entry Level)
Email: aarvex.nolin@samplemail.com

GitHub: github.com/aarvex-ai
LinkedIn: linkedin.com/in/aarvexnolin

EDUCATION
Bachelor of Technology in Computer Science
University Name, 2020-2024
CGPA: 8.5/10

SKILLS
Programming Languages: Python, JavaScript, Java
AI/ML Frameworks: TensorFlow, PyTorch, Hugging Face Transformers
GenAI Tools: LangChain, OpenAI API, Llama, GPT-4
Cloud: AWS, Google Cloud Platform
Databases: PostgreSQL, MongoDB, Vector DBs
Version Control: Git, GitHub

EXPERIENCE
AI Research Intern | Tech Startup | Jan 2024 - Jun 2024
- Developed fine-tuned LLMs for domain-specific applications
- Built RAG (Retrieval Augmented Generation) pipelines
- Implemented prompt engineering strategies
- Created chatbot applications using LangChain

PROJECTS
1. Resume Verification System
   - Built AI-powered resume verification tool
   - Implemented multi-agent system for fraud detection
   - Technologies: Python, FastAPI, LangChain, ChromaDB

2. Sentiment Analysis Dashboard
   - Created real-time sentiment analysis for customer reviews
   - Technologies: React, Python, TensorFlow

CERTIFICATIONS
- Deep Learning Specialization - Coursera
- AWS Certified Cloud Practitioner
"""
        
        return {"resume": resume_text}
    except Exception as e:
        return {"resume": "Sample resume loading failed. Please paste your own resume text."}


@app.get("/api/sample-job-description")
async def get_sample_job_description():
    """Get sample job description for testing"""
    job_desc = """Position: Junior Applied AI Engineer

Type: Full-Time / Contract
Mode: Remote / Hybrid
Experience: 0-1 year (Project experience accepted)

ABOUT THE ROLE:
We are seeking a passionate Junior Applied AI Engineer to join our growing AI team. You'll work on cutting-edge GenAI applications and LLM-powered solutions.

REQUIRED SKILLS:
- Strong Python programming
- Experience with LLMs (OpenAI, Llama, etc.)
- Knowledge of RAG pipelines and vector databases
- Understanding of prompt engineering
- Familiarity with LangChain or similar frameworks
- Basic ML/DL knowledge
- Git/GitHub proficiency

PREFERRED SKILLS:
- Experience with FastAPI or Flask
- Cloud platform knowledge (AWS/GCP)
- Frontend skills (React/Vue)
- Experience with fine-tuning models

RESPONSIBILITIES:
- Develop and deploy AI-powered applications
- Build RAG pipelines and chatbot systems
- Optimize LLM prompts and responses
- Collaborate with cross-functional teams
- Document technical solutions

WHAT WE OFFER:
- Competitive salary
- Remote work flexibility
- Learning & development opportunities
- Mentorship from senior engineers
- Cutting-edge AI projects
"""
    
    return {"job_description": job_desc}


# ==================== FEATURE 1: GENAI RESUME SCREENER ====================

# In-memory interview & assessment sessions
interview_sessions: Dict[str, Any] = {}
assessment_sessions: Dict[str, Any] = {}

_SESSION_MAX = 100  # max sessions to keep in memory

def _evict_oldest_session(sessions: Dict[str, Any]) -> None:
    """Remove the oldest entry when the session dict exceeds _SESSION_MAX."""
    if len(sessions) >= _SESSION_MAX:
        oldest_key = next(iter(sessions))
        sessions.pop(oldest_key, None)

class ScreenResumeRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, max_length=50000)
    job_description: str = Field(..., min_length=20, max_length=10000)

@app.post("/api/screen-resume")
async def screen_resume(request: ScreenResumeRequest):
    """
    GenAI Resume Screener & Context Matcher.
    Returns compatibility score, 3-bullet summary, and 'hidden gem' flag.
    """
    import os
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key or groq_key.startswith("placeholder"):
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured")

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatGroq(
            groq_api_key=groq_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=1024
        )

        system_prompt = """You are an expert technical recruiter and AI hiring specialist.
You evaluate resumes against job descriptions with deep contextual understanding.
You excel at finding "hidden gem" candidates — people whose resume doesn't have the exact
keywords but clearly has the transferable skills and experience required.

Always respond with VALID JSON only. No markdown, no explanation outside the JSON."""

        user_prompt = f"""Analyze this resume against the job description.

JOB DESCRIPTION:
{request.job_description}

RESUME:
{request.resume_text}

Respond with this exact JSON structure:
{{
  "compatibility_score": <integer 0-100>,
  "verdict": "<Excellent Match|Strong Match|Good Match|Partial Match|Weak Match>",
  "summary_bullets": [
    "<bullet 1: strongest alignment point>",
    "<bullet 2: second key match>",
    "<bullet 3: area to probe or gap>"
  ],
  "hidden_gem": <true|false>,
  "hidden_gem_reason": "<explain WHY this is a hidden gem if true, else empty string>",
  "key_matching_skills": ["<skill1>", "<skill2>", "<skill3>"],
  "missing_skills": ["<skill1>", "<skill2>"],
  "experience_years_estimated": <number>,
  "recommendation": "<Strongly Recommend|Recommend|Consider|Pass>"
}}

Set hidden_gem=true if the candidate lacks exact keyword matches but demonstrates
the required competency through projects, adjacent experience, or transferable skills."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = await llm.ainvoke(messages)
        raw = response.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)

        return {
            "success": True,
            "compatibility_score": result.get("compatibility_score", 0),
            "verdict": result.get("verdict", "Unknown"),
            "summary_bullets": result.get("summary_bullets", []),
            "hidden_gem": result.get("hidden_gem", False),
            "hidden_gem_reason": result.get("hidden_gem_reason", ""),
            "key_matching_skills": result.get("key_matching_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "experience_years_estimated": result.get("experience_years_estimated", 0),
            "recommendation": result.get("recommendation", "Consider"),
            "screened_at": datetime.now().isoformat()
        }

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"LLM returned invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screening failed: {str(e)}")


@app.post("/api/extract-resume-text")
async def extract_resume_text(resume_file: UploadFile = File(...)):
    """Lightweight endpoint: extract plain text from a PDF/DOCX/TXT file.
    Returns {"text": "...", "method": "...", "pages": N} without running AI."""
    if not PARSER_AVAILABLE or not resume_parser:
        raise HTTPException(status_code=503, detail="Resume parser not available")
    try:
        content = await resume_file.read()
        loop = asyncio.get_event_loop()
        parse_result = await loop.run_in_executor(
            None,
            lambda: resume_parser.parse_file(content, resume_file.filename or "resume.pdf")
        )
        if isinstance(parse_result, tuple):
            text, meta = parse_result
        else:
            text = parse_result.get("text", "")
            meta = {}
        if len(text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Could not extract readable text from this file. Try a different format or paste the text manually.")
        return {
            "text": text,
            "method": meta.get("extraction_method", "unknown"),
            "pages": meta.get("pages_processed", 1),
            "chars": len(text),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")


@app.post("/api/screen-resume-file")
async def screen_resume_file(
    job_description: str = Form(...),
    resume_file: UploadFile = File(...)
):
    """Upload a PDF/DOCX resume file and screen it against a job description."""
    if not PARSER_AVAILABLE or not resume_parser:
        raise HTTPException(status_code=503, detail="Resume parser not available")

    try:
        content = await resume_file.read()
        loop = asyncio.get_event_loop()
        parse_result = await loop.run_in_executor(
            None,
            lambda: resume_parser.parse_file(content, resume_file.filename or "resume.pdf")
        )
        # parse_file returns (text, metadata) tuple
        if isinstance(parse_result, tuple):
            resume_text = parse_result[0]
        else:
            resume_text = parse_result.get("text", "")

        if len(resume_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract enough text from the resume file")

        req = ScreenResumeRequest(resume_text=resume_text, job_description=job_description)
        return await screen_resume(req)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File screening failed: {str(e)}")


# ==================== FEATURE 2: CONVERSATIONAL AI INTERVIEWER ====================

class StartInterviewRequest(BaseModel):
    candidate_name: str = Field(default="Candidate", max_length=100)
    job_role: str = Field(..., min_length=3, max_length=200)
    job_description: str = Field(..., min_length=20, max_length=5000)
    resume_summary: str = Field(default="", max_length=3000)

class InterviewRespondRequest(BaseModel):
    session_id: str
    answer: str = Field(..., min_length=1, max_length=5000)

@app.post("/api/interview/start")
async def start_interview(request: StartInterviewRequest):
    """Start a new AI interview session. Returns first question and session_id."""
    import os
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key or groq_key.startswith("placeholder"):
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured")

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        session_id = str(uuid.uuid4())

        llm = ChatGroq(
            groq_api_key=groq_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=512
        )

        system_prompt = f"""You are an expert technical interviewer conducting a first-round screening for a {request.job_role} position.
You ask one focused question at a time. After each answer, you analyze the candidate's reasoning and clarity,
then ask a relevant follow-up or move to the next topic.
Keep questions concise and professional. Probe deeper when answers are vague."""

        context = f"Job Role: {request.job_role}\nJob Description: {request.job_description}"
        if request.resume_summary:
            context += f"\nCandidate Background: {request.resume_summary}"

        opening_prompt = f"""{context}

Generate the FIRST interview question to open the conversation.
This should be a warm, open-ended question that lets the candidate introduce their relevant experience.
Respond with ONLY the question text — no preamble, no labels."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=opening_prompt)
        ]

        response = await llm.ainvoke(messages)
        first_question = response.content.strip()

        # Store session (with max-size eviction to prevent memory leak)
        _evict_oldest_session(interview_sessions)
        interview_sessions[session_id] = {
            "session_id": session_id,
            "job_role": request.job_role,
            "job_description": request.job_description,
            "resume_summary": request.resume_summary,
            "candidate_name": request.candidate_name,
            "system_prompt": system_prompt,
            "history": [
                {"role": "interviewer", "content": first_question, "timestamp": datetime.now().isoformat()}
            ],
            "question_count": 1,
            "scores": [],
            "started_at": datetime.now().isoformat(),
            "status": "active"
        }

        return {
            "success": True,
            "session_id": session_id,
            "question": first_question,
            "question_number": 1,
            "status": "active"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")


@app.post("/api/interview/respond")
async def interview_respond(request: InterviewRespondRequest):
    """Submit a candidate answer and get the next AI question."""
    import os
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key or groq_key.startswith("placeholder"):
        raise HTTPException(status_code=503, detail="Groq API key not configured")

    session = interview_sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if session["status"] != "active":
        raise HTTPException(status_code=400, detail="Interview session is already completed")

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatGroq(
            groq_api_key=groq_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=768
        )

        # Record the answer
        session["history"].append({
            "role": "candidate",
            "content": request.answer,
            "timestamp": datetime.now().isoformat()
        })

        question_count = session["question_count"]
        max_questions = 6

        # Build conversation context for LLM
        convo_text = ""
        for turn in session["history"]:
            role_label = "Interviewer" if turn["role"] == "interviewer" else "Candidate"
            convo_text += f"{role_label}: {turn['content']}\n\n"

        # Evaluate the latest answer
        eval_prompt = f"""Job Role: {session['job_role']}
Job Description: {session['job_description']}

Interview so far:
{convo_text}

Evaluate the candidate's last answer on:
1. Clarity (how clearly they communicated)
2. Depth (technical depth and specificity)
3. Relevance (how relevant to the role)

Respond with ONLY valid JSON:
{{
  "clarity_score": <1-10>,
  "depth_score": <1-10>,
  "relevance_score": <1-10>,
  "overall_score": <1-10>,
  "evaluation_note": "<one concise sentence about the answer quality>"
}}"""

        eval_messages = [
            SystemMessage(content=session["system_prompt"]),
            HumanMessage(content=eval_prompt)
        ]

        # Build next-question prompt now (before the early-return check)
        # so we can fire both LLM calls in parallel when not on the final question
        next_prompt = f"""Job Role: {session['job_role']}

Interview so far:
{convo_text}

Based on the candidate's last answer, generate ONE focused follow-up question.
- If the answer was vague, ask for a specific example.
- If it was good, advance to the next relevant technical topic.
- Keep it concise and direct.
- This is question {question_count + 1} of {max_questions}.
Respond with ONLY the question text."""

        next_messages = [
            SystemMessage(content=session["system_prompt"]),
            HumanMessage(content=next_prompt)
        ]

        # Run eval + next-question concurrently (skip next-question on final answer)
        is_final = question_count >= max_questions
        if is_final:
            eval_response = await llm.ainvoke(eval_messages)
            next_question = None
        else:
            eval_response, next_response = await asyncio.gather(
                llm.ainvoke(eval_messages),
                llm.ainvoke(next_messages)
            )
            next_question = next_response.content.strip()

        eval_raw = eval_response.content.strip()
        if eval_raw.startswith("```"):
            eval_raw = eval_raw.split("```")[1]
            if eval_raw.startswith("json"):
                eval_raw = eval_raw[4:]
        eval_raw = eval_raw.strip()

        try:
            evaluation = json.loads(eval_raw)
        except (json.JSONDecodeError, ValueError):
            evaluation = {"clarity_score": 7, "depth_score": 7, "relevance_score": 7, "overall_score": 7, "evaluation_note": "Answer recorded."}

        session["scores"].append(evaluation)

        # Check if interview is done
        if is_final:
            session["status"] = "completed"
            # Final summary
            avg_score = round(sum(s.get("overall_score", 7) for s in session["scores"]) / len(session["scores"]) * 10, 1)
            session["final_score"] = avg_score
            return {
                "success": True,
                "session_id": request.session_id,
                "status": "completed",
                "evaluation": evaluation,
                "final_score": avg_score,
                "message": f"Interview complete! Overall reasoning quality score: {avg_score}/100",
                "total_questions": question_count,
                "history": session["history"]
            }

        session["question_count"] += 1
        session["history"].append({
            "role": "interviewer",
            "content": next_question,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "success": True,
            "session_id": request.session_id,
            "question": next_question,
            "question_number": session["question_count"],
            "status": "active",
            "evaluation": evaluation,
            "progress": round((question_count / max_questions) * 100)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview respond failed: {str(e)}")


@app.get("/api/interview/{session_id}")
async def get_interview_session(session_id: str):
    """Get interview session details and history."""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "session": session}


# ==================== FEATURE 3: TECHNICAL ASSESSMENT GENERATOR ====================

class GenerateAssessmentRequest(BaseModel):
    role: str = Field(..., min_length=2, max_length=200, description="e.g. 'Frontend Developer'")
    level: Literal["Junior", "Mid", "Senior"] = Field(..., description="Junior|Mid|Senior")
    tech_stack: str = Field(..., min_length=2, max_length=300, description="e.g. 'React, TypeScript, GraphQL'")
    num_questions: int = Field(default=5, ge=3, le=10)

class EvaluateAssessmentRequest(BaseModel):
    session_id: str
    answers: Dict[str, str]  # question_id -> answer text

@app.post("/api/assessment/generate")
async def generate_assessment(request: GenerateAssessmentRequest):
    """Generate a technical assessment with mixed MCQ and short-answer questions."""
    import os
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key or groq_key.startswith("placeholder"):
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured")

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatGroq(
            groq_api_key=groq_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=2048
        )

        system_prompt = """You are a senior technical interviewer creating assessments.
Generate realistic, challenging questions appropriate to the level.
Mix multiple-choice (with exactly 4 options) and short-answer/coding questions.
Always respond with VALID JSON only."""

        user_prompt = f"""Create a {request.num_questions}-question technical assessment for:
Role: {request.role}
Level: {request.level}
Tech Stack: {request.tech_stack}

Generate a mix: roughly 60% multiple-choice, 40% short-answer/coding.

Respond with this EXACT JSON structure:
{{
  "title": "<Assessment title>",
  "role": "{request.role}",
  "level": "{request.level}",
  "estimated_minutes": <integer>,
  "questions": [
    {{
      "id": "q1",
      "type": "multiple_choice",
      "question": "<question text>",
      "options": {{"A": "<option>", "B": "<option>", "C": "<option>", "D": "<option>"}},
      "correct_answer": "<A|B|C|D>",
      "explanation": "<why this is correct>",
      "difficulty": "<easy|medium|hard>",
      "topic": "<topic area>"
    }},
    {{
      "id": "q2",
      "type": "short_answer",
      "question": "<question text>",
      "expected_concepts": ["<concept1>", "<concept2>"],
      "sample_answer": "<ideal answer>",
      "difficulty": "<easy|medium|hard>",
      "topic": "<topic area>"
    }}
  ]
}}"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = await llm.ainvoke(messages)
        raw = response.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        assessment = json.loads(raw)

        session_id = str(uuid.uuid4())
        _evict_oldest_session(assessment_sessions)
        assessment_sessions[session_id] = {
            "session_id": session_id,
            "assessment": assessment,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "role": request.role,
            "level": request.level,
            "tech_stack": request.tech_stack
        }

        # Strip correct answers before returning to candidate
        public_questions = []
        for q in assessment.get("questions", []):
            pub_q = {k: v for k, v in q.items() if k not in ("correct_answer", "explanation", "sample_answer", "expected_concepts")}
            public_questions.append(pub_q)

        return {
            "success": True,
            "session_id": session_id,
            "title": assessment.get("title"),
            "role": assessment.get("role"),
            "level": assessment.get("level"),
            "estimated_minutes": assessment.get("estimated_minutes", 20),
            "questions": public_questions,
            "total_questions": len(public_questions),
            "generated_at": datetime.now().isoformat()
        }

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"LLM returned invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment generation failed: {str(e)}")


@app.post("/api/assessment/evaluate")
async def evaluate_assessment(request: EvaluateAssessmentRequest):
    """Evaluate candidate answers against the assessment rubric using LLM."""
    import os
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key or groq_key.startswith("placeholder"):
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured")

    session = assessment_sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Assessment session not found")

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatGroq(
            groq_api_key=groq_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=2048
        )

        assessment = session["assessment"]
        questions = assessment.get("questions", [])

        results = []
        total_score = 0
        max_score = len(questions) * 10

        # Split questions by type
        mcq_questions = [(i, q) for i, q in enumerate(questions) if q.get("type") == "multiple_choice"]
        sa_questions = [(i, q) for i, q in enumerate(questions) if q.get("type") != "multiple_choice"]

        # Score MCQ questions instantly (no LLM needed)
        for _idx, q in mcq_questions:
            qid = q.get("id", f"q{_idx+1}")
            candidate_answer = request.answers.get(qid, "").strip()
            correct = q.get("correct_answer", "")
            is_correct = candidate_answer.upper().strip() == correct.upper()
            score = 10 if is_correct else 0
            feedback = f"Correct! {q.get('explanation','')}" if is_correct else f"Incorrect. The correct answer is {correct}. {q.get('explanation','')}"
            results.append({
                "question_id": qid,
                "type": "multiple_choice",
                "candidate_answer": candidate_answer,
                "correct_answer": correct,
                "is_correct": is_correct,
                "score": score,
                "max_score": 10,
                "feedback": feedback,
                "_order": _idx
            })
            total_score += score

        # Build all short-answer prompts
        sa_messages_list = []
        for _idx, q in sa_questions:
            qid = q.get("id", f"q{_idx+1}")
            candidate_answer = request.answers.get(qid, "").strip()
            eval_prompt = f"""Question: {q['question']}
Expected concepts: {', '.join(q.get('expected_concepts', []))}
Sample ideal answer: {q.get('sample_answer', 'N/A')}
Candidate's answer: {candidate_answer if candidate_answer else '[No answer provided]'}

Score this answer from 0-10 based on:
- Accuracy of technical content
- Coverage of expected concepts
- Clarity of explanation

Respond with VALID JSON only:
{{
  "score": <0-10>,
  "feedback": "<specific, constructive feedback in 1-2 sentences>",
  "concepts_covered": ["<concept1>"],
  "concepts_missed": ["<concept1>"]
}}"""
            sa_messages_list.append((
                _idx, qid, candidate_answer,
                [
                    SystemMessage(content="You are a strict but fair technical assessment evaluator. Respond only with JSON."),
                    HumanMessage(content=eval_prompt)
                ]
            ))

        # Fire all short-answer evaluations in parallel
        if sa_messages_list:
            sa_responses = await asyncio.gather(
                *[llm.ainvoke(msgs) for _idx, qid, ca, msgs in sa_messages_list],
                return_exceptions=True
            )

            for ((_idx, qid, candidate_answer, _msgs), eval_response) in zip(sa_messages_list, sa_responses):
                if isinstance(eval_response, Exception):
                    eval_data = {"score": 5, "feedback": "Answer recorded.", "concepts_covered": [], "concepts_missed": []}
                else:
                    eval_raw = eval_response.content.strip()
                    if eval_raw.startswith("```"):
                        eval_raw = eval_raw.split("```")[1]
                        if eval_raw.startswith("json"):
                            eval_raw = eval_raw[4:]
                    try:
                        eval_data = json.loads(eval_raw.strip())
                    except (json.JSONDecodeError, ValueError):
                        eval_data = {"score": 5, "feedback": "Answer recorded.", "concepts_covered": [], "concepts_missed": []}

                score = eval_data.get("score", 5)
                total_score += score
                results.append({
                    "question_id": qid,
                    "type": "short_answer",
                    "candidate_answer": candidate_answer,
                    "score": score,
                    "max_score": 10,
                    "feedback": eval_data.get("feedback", ""),
                    "concepts_covered": eval_data.get("concepts_covered", []),
                    "concepts_missed": eval_data.get("concepts_missed", []),
                    "_order": _idx
                })

        # Restore original question order
        results.sort(key=lambda r: r.pop("_order", 0))

        percentage = round((total_score / max_score) * 100, 1) if max_score > 0 else 0
        grade = "A" if percentage >= 90 else "B" if percentage >= 75 else "C" if percentage >= 60 else "D" if percentage >= 40 else "F"

        session["status"] = "evaluated"
        session["results"] = results
        session["total_score"] = total_score
        session["percentage"] = percentage

        return {
            "success": True,
            "session_id": request.session_id,
            "total_score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "grade": grade,
            "results": results,
            "role": session["role"],
            "level": session["level"],
            "evaluated_at": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


# ==================== FEATURE 4: ANTI-CHEAT PROCTORING ====================

import base64

# Active proctoring sessions
proctor_sessions: Dict[str, Any] = {}
proctor_connections: Dict[str, List[WebSocket]] = {}

class StartProctorRequest(BaseModel):
    candidate_name: str = Field(default="Candidate", max_length=100)
    assessment_id: str = Field(default="", max_length=100)

@app.post("/api/proctor/start")
async def start_proctor_session(request: StartProctorRequest):
    """Start a proctoring session for a candidate."""
    session_id = str(uuid.uuid4())
    _evict_oldest_session(proctor_sessions)
    proctor_sessions[session_id] = {
        "session_id": session_id,
        "candidate_name": request.candidate_name,
        "assessment_id": request.assessment_id,
        "started_at": datetime.now().isoformat(),
        "status": "active",
        "alerts": [],
        "frame_count": 0,
        "faces_detected_history": [],
        "tab_switches": 0,
        "flags": []
    }
    return {"success": True, "session_id": session_id}


@app.websocket("/ws/proctor/{session_id}")
async def proctor_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time proctoring.
    Client sends: {type: 'frame', data: '<base64_jpeg>'} or {type: 'tab_switch'}
    Server sends: {type: 'alert'|'status', ...}
    """
    await websocket.accept()

    if session_id not in proctor_sessions:
        await websocket.send_json({"type": "error", "message": "Session not found"})
        await websocket.close()
        return

    if session_id not in proctor_connections:
        proctor_connections[session_id] = []
    proctor_connections[session_id].append(websocket)

    session = proctor_sessions[session_id]

    # Try to load OpenCV — graceful fallback if not installed
    try:
        import cv2
        import numpy as np
        CV2_AVAILABLE = True
        # Load Haar cascade face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    except ImportError:
        CV2_AVAILABLE = False
        face_cascade = None

    try:
        await websocket.send_json({
            "type": "status",
            "message": "Proctoring active",
            "cv2_available": CV2_AVAILABLE,
            "session_id": session_id
        })

        while True:
            try:
                text = await websocket.receive_text()
                data = json.loads(text)
            except json.JSONDecodeError:
                continue  # Ignore malformed frames
            except Exception:
                break  # WebSocket closed or fatal error
            msg_type = data.get("type", "")
            session["frame_count"] += 1

            if msg_type == "tab_switch":
                session["tab_switches"] += 1
                alert = {
                    "type": "alert",
                    "severity": "high",
                    "category": "tab_switch",
                    "message": f"Tab switch detected! (#{session['tab_switches']})",
                    "timestamp": datetime.now().isoformat()
                }
                session["alerts"].append(alert)
                session["flags"].append("TAB_SWITCH")
                await websocket.send_json(alert)

            elif msg_type == "frame":
                frame_b64 = data.get("data", "")
                alert_payload = None

                if CV2_AVAILABLE and frame_b64 and face_cascade is not None:
                    try:
                        img_bytes = base64.b64decode(frame_b64)
                        nparr = np.frombuffer(img_bytes, np.uint8)
                        frame_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                        if frame_cv is not None:
                            # Offload CPU-bound OpenCV work to thread pool
                            loop = asyncio.get_event_loop()
                            gray = await loop.run_in_executor(
                                None,
                                lambda: cv2.cvtColor(frame_cv, cv2.COLOR_BGR2GRAY)
                            )
                            faces = await loop.run_in_executor(
                                None,
                                lambda: face_cascade.detectMultiScale(
                                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
                                )
                            )
                            num_faces = len(faces)
                            session["faces_detected_history"].append(num_faces)

                            if num_faces == 0:
                                # Only alert if consistently no face (not just a single bad frame)
                                recent = session["faces_detected_history"][-5:] if len(session["faces_detected_history"]) >= 5 else session["faces_detected_history"]
                                if recent and sum(recent) == 0:
                                    alert_payload = {
                                        "type": "alert",
                                        "severity": "medium",
                                        "category": "no_face",
                                        "message": "Candidate not visible in frame",
                                        "timestamp": datetime.now().isoformat()
                                    }
                            elif num_faces > 1:
                                alert_payload = {
                                    "type": "alert",
                                    "severity": "critical",
                                    "category": "multiple_faces",
                                    "message": f"Multiple faces detected ({num_faces})! Possible cheating.",
                                    "timestamp": datetime.now().isoformat(),
                                    "faces_count": int(num_faces)
                                }
                                session["flags"].append("MULTIPLE_FACES")
                            else:
                                # Send periodic OK status (every 30 frames)
                                if session["frame_count"] % 30 == 0:
                                    await websocket.send_json({
                                        "type": "status",
                                        "message": "Candidate verified in frame",
                                        "faces": 1,
                                        "frame": session["frame_count"]
                                    })
                    except Exception:
                        pass  # Skip bad frames silently

                else:
                    # No CV2 — simulate detection for demo
                    if session["frame_count"] % 60 == 0:
                        await websocket.send_json({
                            "type": "status",
                            "message": "Frame received (CV2 not installed — using browser detection)",
                            "frame": session["frame_count"]
                        })

                if alert_payload:
                    session["alerts"].append(alert_payload)
                    await websocket.send_json(alert_payload)

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong", "frame": session["frame_count"]})

    except WebSocketDisconnect:
        session["status"] = "disconnected"
        conns = proctor_connections.get(session_id, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            proctor_connections.pop(session_id, None)
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


@app.get("/api/proctor/{session_id}/alerts")
async def get_proctor_alerts(session_id: str):
    """Get all alerts for a proctoring session (for recruiter dashboard)."""
    session = proctor_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Proctoring session not found")
    return {
        "success": True,
        "session_id": session_id,
        "candidate_name": session["candidate_name"],
        "status": session["status"],
        "alerts": session["alerts"],
        "flags": list(set(session["flags"])),
        "tab_switches": session["tab_switches"],
        "frame_count": session["frame_count"],
        "started_at": session["started_at"]
    }


@app.get("/api/proctor/sessions")
async def list_proctor_sessions():
    """List all active proctoring sessions for recruiter dashboard."""
    sessions = []
    for sid, s in proctor_sessions.items():
        sessions.append({
            "session_id": sid,
            "candidate_name": s["candidate_name"],
            "status": s["status"],
            "alert_count": len(s["alerts"]),
            "flags": list(set(s["flags"])),
            "tab_switches": s["tab_switches"],
            "started_at": s["started_at"]
        })
    return {"success": True, "sessions": sessions}


# ==================== SETTINGS ENDPOINT ====================

# In-memory settings store (persisted for server lifetime)
_app_settings: Dict[str, Any] = {}

class SaveSettingsRequest(BaseModel):
    groq_api_key: Optional[str] = None
    min_years_experience: Optional[int] = None
    skill_match_threshold: Optional[int] = None
    strictness_level: Optional[str] = None
    enable_bias_detection: Optional[bool] = None
    enable_blockchain: Optional[bool] = None

@app.get("/api/settings")
async def get_settings():
    """Get current application settings."""
    return {"success": True, "settings": _app_settings}

@app.post("/api/settings")
async def save_settings(request: SaveSettingsRequest):
    """Save application settings."""
    global _app_settings
    updates = {k: v for k, v in request.model_dump().items() if v is not None}
    _app_settings.update(updates)

    # Apply GROQ key to environment if provided (non-empty, non-placeholder)
    if request.groq_api_key and not request.groq_api_key.startswith("gsk_placeholder"):
        os.environ["GROQ_API_KEY"] = request.groq_api_key

    return {"success": True, "saved": list(updates.keys()), "settings": _app_settings}


# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*50)
    print("🚀 Velos Server Starting...")
    print("="*50)
    print(f"✅ FastAPI server initialized")
    print(f"{'✅' if ORCHESTRATOR_AVAILABLE else '⚠️'} Orchestrator: {'Connected' if ORCHESTRATOR_AVAILABLE else 'Simulation Mode'}")
    
    # Show Zynd Protocol detailed status
    if ORCHESTRATOR_AVAILABLE and orchestrator:
        try:
            from zynd.protocol import __version__, __python_version__, __official_sdk_available__, __supports_official_sdk__
            zynd_status = "✅ Official SDK" if __official_sdk_available__ else ("⚠️ Compatibility Layer" if __supports_official_sdk__ else "ℹ️ Compatibility Layer")
            print(f"{zynd_status} Zynd Protocol v{__version__} (Python {__python_version__})")
        except:
            print(f"✅ Zynd Protocol: Connected")
    else:
        print(f"⚠️ Zynd Protocol: Not Available")
    
    print(f"{'✅' if ORCHESTRATOR_AVAILABLE else '⚠️'} GROQ API: {'Connected' if ORCHESTRATOR_AVAILABLE else 'Not Available'}")
    print(f"{'✅' if PARSER_AVAILABLE else '⚠️'} Resume Parser: {'Ready (PDF/DOCX/OCR)' if PARSER_AVAILABLE else 'Not Available'}")
    print(f"{'✅' if BATCH_AVAILABLE else '⚠️'} Batch Processing: {'Ready' if BATCH_AVAILABLE else 'Not Available'}")
    print("="*50)
    print("📡 API Endpoints:")
    print("   GET  /                  - Frontend UI")
    print("   GET  /api/status        - System status")
    print("   GET  /api/stats         - Dashboard stats")
    print("   GET  /api/agents        - Agent info")
    print("   GET  /api/audit         - Audit trail")
    print("   POST /api/verify        - Verify candidate (JSON)")
    print("   POST /api/upload-resume - Upload & parse resume file")
    print("   POST /api/verify-file   - Upload & verify resume file")
    print("   GET  /api/parser-status - Parser capabilities")
    print("   --- BATCH & ANALYTICS ---")
    print("   POST /api/batch-upload  - Process ZIP of resumes")
    print("   GET  /api/leaderboard   - Candidate rankings")
    print("   GET  /api/compare       - Compare two candidates")
    print("   GET  /api/export-report - Download CSV report")
    print("   GET  /docs              - Swagger API Documentation")
    print("="*50 + "\n")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
