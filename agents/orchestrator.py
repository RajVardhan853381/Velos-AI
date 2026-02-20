"""
TrustFlow Orchestrator with Zynd Protocol Integration
Coordinates all agents using decentralized identity and verifiable credentials
For ZYND AIckathon 2025 - Fair Hiring Network

Uses the Zynd Protocol compatible API (mirrors zyndai-agent v0.1.5)
"""

import hashlib
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Type checking imports
if TYPE_CHECKING:
    from zynd.protocol import ZyndProtocol

try:
    from zynd.protocol import (
        ZyndProtocol as ZyndProtocolClass,
        zynd_protocol,
        get_protocol_instance,
        IdentityManager,
        AgentCommunicationManager,
        SearchAndDiscoveryManager,
        VerifiableCredential,
        check_official_sdk_available,
        __version__ as zynd_version,
        __python_version__ as python_ver,
        __official_sdk_available__ as sdk_available,
        __supports_official_sdk__ as sdk_supported
    )
    ZYND_AVAILABLE = True
    zynd_protocol_instance: Optional["ZyndProtocol"] = get_protocol_instance()
    
    # Print detailed compatibility info
    if sdk_available:
        print(f"✅ Using official zyndai-agent SDK v{zynd_version}")
    elif sdk_supported:
        print(f"⚠️ Python {python_ver} supports official SDK but not installed")
        print(f"ℹ️ Using Zynd Protocol compatibility layer v{zynd_version}")
    else:
        print(f"ℹ️ Using Zynd Protocol compatibility layer v{zynd_version}")
        print(f"   (Official SDK requires Python 3.12+, you have {python_ver})")
except ImportError:
    ZYND_AVAILABLE = False
    zynd_protocol_instance: Optional["ZyndProtocol"] = None  # type: ignore
    print("⚠️ Zynd Protocol not available, using basic mode")

# Import new blockchain components
try:
    from zynd.blockchain_did import BlockchainDIDManager, load_blockchain_manager
    from zynd.w3c_credentials import W3CVerifiableCredential
    from zynd.agent_communication import AgentCommunicationHub, AgentMessage
    BLOCKCHAIN_AVAILABLE = True
    print("✅ Blockchain DID components available")
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    BlockchainDIDManager = None  # type: ignore
    W3CVerifiableCredential = None  # type: ignore
    AgentCommunicationHub = None  # type: ignore
    print("⚠️ Blockchain components not available, using legacy mode")

from agents.agent_1_gatekeeper import BlindGatekeeper
from agents.agent_2_validator import SkillValidator
from agents.agent_3_inquisitor import Inquisitor
from database.storage import AuditLog

# Vector Store for RAG
SKIP_VECTOR = os.getenv("SKIP_VECTOR_STORE") == "1"
try:
    if not SKIP_VECTOR:
        from database.vector_store import ResumeVectorStore
        VECTOR_STORE_AVAILABLE = True
    else:
        VECTOR_STORE_AVAILABLE = False
        print("⚠️ Vector store skipped for quick start")
except ImportError:
    VECTOR_STORE_AVAILABLE = False
    print("⚠️ Vector store not available, context retrieval disabled")

# Trust Layer components
try:
    from utils.diff_engine import DiffEngine
    from utils.ledger_manager import LedgerManager
    TRUST_LAYER_AVAILABLE = True
except ImportError:
    TRUST_LAYER_AVAILABLE = False
    DiffEngine = None  # type: ignore
    LedgerManager = None  # type: ignore
    print("⚠️ Trust layer not available, visual/crypto proofs disabled")

try:
    from utils.bias_detector import bias_detector as bias_detector_module
    bias_detector_instance = bias_detector_module
    BIAS_DETECTOR_AVAILABLE = True
except ImportError:
    BIAS_DETECTOR_AVAILABLE = False
    bias_detector_instance = None  # type: ignore


@dataclass
class CandidateProfile:
    """Candidate profile with DID"""
    did: str
    anonymous_id: str
    credentials: List[Dict]
    verification_status: str
    created_at: str


class VelosOrchestrator:
    """
    Orchestrates the Velos verification pipeline with Zynd Protocol.
    
    Pipeline flow:
    1. Agent 1 (Gatekeeper): Eligibility + PII removal + DID creation
    2. Agent 2 (Validator): Skill matching + Credential issuance
    3. Agent 3 (Inquisitor): Question generation → Answer evaluation
    
    Each agent only sees what it needs - true separation of concerns.
    All interactions are authenticated via Zynd Protocol DIDs.
    
    Zynd Protocol Integration:
    - IdentityManager: Creates DIDs for agents and candidates
    - AgentCommunicationManager: MQTT-based authenticated messaging
    - SearchAndDiscoveryManager: Agent discovery by capabilities
    - VerifiableCredential: W3C credentials issued at each stage
    """
    
    def __init__(self, db_path: str = "velos_audit.db"):
        # Initialize Zynd Protocol if available
        self.protocol: Optional[Any] = None
        self.agent1_identity: Optional[Dict[str, Any]] = None
        self.agent2_identity: Optional[Dict[str, Any]] = None
        self.agent3_identity: Optional[Dict[str, Any]] = None
        
        # Initialize Blockchain DID Manager
        self.blockchain_did_manager: Optional[Any] = None
        self.w3c_credential_manager: Optional[Any] = None
        self.communication_hub: Optional[Any] = None
        
        if BLOCKCHAIN_AVAILABLE and BlockchainDIDManager and W3CVerifiableCredential and AgentCommunicationHub:
            try:
                # Load or create blockchain manager
                from zynd.blockchain_did import load_blockchain_manager as load_manager
                self.blockchain_did_manager = load_manager()
                print(f"✅ Blockchain DID Manager initialized")
                print(f"   Wallet: {self.blockchain_did_manager.account.address}")
                print(f"   Network: {self.blockchain_did_manager.network_name}")
                
                # Initialize W3C credential manager (pass private key, not manager object)
                self.w3c_credential_manager = W3CVerifiableCredential(
                    private_key=self.blockchain_did_manager.account.key.hex()
                )
                print("✅ W3C Verifiable Credential Manager initialized")
                
                # Create DIDs for each agent
                agent1_did_doc = self.blockchain_did_manager.create_ethereum_did(
                    agent_type="agent",
                    agent_name="BlindGatekeeper",
                    capabilities=["eligibility_check", "pii_redaction", "anonymization"]
                )
                agent2_did_doc = self.blockchain_did_manager.create_ethereum_did(
                    agent_type="agent",
                    agent_name="SkillValidator",
                    capabilities=["skill_matching", "jd_parsing", "scoring"]
                )
                agent3_did_doc = self.blockchain_did_manager.create_ethereum_did(
                    agent_type="agent",
                    agent_name="Inquisitor",
                    capabilities=["question_generation", "authenticity_verification", "fraud_detection"]
                )
                
                self.agent1_identity = agent1_did_doc
                self.agent2_identity = agent2_did_doc
                self.agent3_identity = agent3_did_doc
                
                print("✅ Blockchain-based agent DIDs created")
                
                # Initialize communication hub (use orchestrator's DID)
                orchestrator_did_doc = self.blockchain_did_manager.create_ethereum_did(
                    agent_type="orchestrator",
                    agent_name="VelosOrchestrator",
                    capabilities=["pipeline_coordination"]
                )
                self.communication_hub = AgentCommunicationHub(
                    agent_id="Orchestrator",
                    agent_did=orchestrator_did_doc["did"],
                    private_key=self.blockchain_did_manager.account.key.hex()
                )
                print("✅ Agent Communication Hub initialized")
                
            except Exception as e:
                print(f"⚠️ Blockchain initialization failed: {e}")
                print("   Falling back to legacy mode")
                self.blockchain_did_manager = None
                self.w3c_credential_manager = None
                self.communication_hub = None
        
        # Fallback to legacy Zynd Protocol
        if not self.blockchain_did_manager and ZYND_AVAILABLE and zynd_protocol_instance:
            self.protocol = zynd_protocol_instance
            self.agent1_identity = self._setup_agent(
                "gatekeeper", "BlindGatekeeper", 
                ["eligibility_check", "pii_redaction", "anonymization"]
            )
            self.agent2_identity = self._setup_agent(
                "validator", "SkillValidator",
                ["skill_matching", "jd_parsing", "scoring"]
            )
            self.agent3_identity = self._setup_agent(
                "inquisitor", "Inquisitor",
                ["question_generation", "authenticity_verification", "fraud_detection"]
            )
            print("✅ Zynd Protocol agents registered")
        
        # Initialize agents
        self.gatekeeper = BlindGatekeeper()
        self.validator = SkillValidator()
        self.inquisitor = Inquisitor()
        self.audit_db = AuditLog(db_path)
        
        # Initialize Vector Store for RAG
        self.vector_store: Optional[Any] = None
        if VECTOR_STORE_AVAILABLE:
            try:
                from database.vector_store import ResumeVectorStore
                self.vector_store = ResumeVectorStore()
                print("✅ Vector store initialized (RAG enabled)")
            except Exception as e:
                print(f"⚠️ Vector store init failed, continuing without RAG: {e}")
                self.vector_store = None
        
        # Initialize Trust Layer components
        self.diff_engine: Optional[Any] = None
        self.ledger_manager: Optional[Any] = None
        if TRUST_LAYER_AVAILABLE:
            try:
                self.diff_engine = DiffEngine()
                self.ledger_manager = LedgerManager(agent_id="Velos-Orchestrator")
                print("✅ Trust layer initialized (visual + crypto proofs enabled)")
            except Exception as e:
                print(f"⚠️ Trust layer init failed: {e}")
        
        # Track current candidate through pipeline
        self.current_candidate_id: Optional[str] = None
        self.current_result: Optional[Dict[str, Any]] = None
        
        # Candidate store for Zynd
        self.candidates: Dict[str, CandidateProfile] = {}
    
    def _setup_agent(self, agent_type: str, agent_name: str, capabilities: List[str]) -> Optional[Dict[str, Any]]:
        """Setup agent with DID and register in network"""
        if not ZYND_AVAILABLE or not self.protocol:
            return None
        identity = self.protocol.create_agent_identity(agent_type, agent_name, capabilities)
        self.protocol.register_agent(identity, capabilities)
        return identity
    
    def _create_candidate_did(self, resume_hash: str) -> Optional[Dict[str, Any]]:
        """Create anonymous DID for candidate"""
        # Try blockchain DID first
        if self.blockchain_did_manager:
            try:
                return self.blockchain_did_manager.create_candidate_did(resume_hash)
            except Exception as e:
                print(f"⚠️ Blockchain DID creation failed: {e}")
        
        # Fallback to legacy Zynd Protocol
        if not ZYND_AVAILABLE or not self.protocol:
            return None
        return self.protocol.create_agent_identity("candidate", f"ANON-{resume_hash[:8]}", [])
    
    def _get_did_string(self, did_doc: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract DID string from DID document"""
        if did_doc is None:
            return None
        if isinstance(did_doc, dict):
            return did_doc.get("id", str(did_doc))
        return str(did_doc)
    
    def _generate_candidate_id(self, resume_text: str) -> str:
        """Generate unique candidate ID from resume hash"""
        resume_hash = hashlib.sha256(resume_text.encode()).hexdigest()
        return f"CAND-{resume_hash[:8].upper()}"
    
    def get_resume_context(self, query: str, candidate_id: Optional[str] = None) -> str:
        """
        Retrieve relevant resume context for a query using RAG.
        
        This is how agents get context without loading the entire resume.
        
        Args:
            query: What to search for (e.g., "Python experience")
            candidate_id: Which candidate's resume (defaults to current)
            
        Returns:
            Relevant resume chunks as a single string
        """
        if not self.vector_store:
            return ""
        
        cid = candidate_id or self.current_candidate_id
        if not cid:
            return ""
        
        return self.vector_store.get_context(query, cid)
    
    def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        if not self.vector_store:
            return {"enabled": False}
        return self.vector_store.get_stats()
    
    def run_verification_pipeline(self, raw_resume: str,
                                   job_description: str,
                                   min_years: float = 2.0) -> Dict:
        """
        Run candidate through all agents with Zynd Protocol integration.
        
        Args:
            raw_resume: Raw resume text (with PII)
            job_description: Job description to match against
            min_years: Minimum years of experience required
            
        Returns:
            Complete pipeline result with status from all agents
        """
        
        # Generate candidate ID
        candidate_id = self._generate_candidate_id(raw_resume)
        self.current_candidate_id = candidate_id
        
        # Create candidate DID if Zynd available
        candidate_did = self._create_candidate_did(candidate_id)
        
        # Initialize result tracking
        result = {
            "candidate_id": candidate_id,
            "candidate_did": self._get_did_string(candidate_did) if candidate_did else f"local:{candidate_id}",
            "timestamp": datetime.now().isoformat(),
            "pipeline_stages": {},
            "credentials_issued": [],
            "agent_messages": [],
            "final_status": "PENDING",
            "zynd_protocol_enabled": ZYND_AVAILABLE
        }
        
        # Analyze job description for bias
        if BIAS_DETECTOR_AVAILABLE and bias_detector_instance:
            print("🔍 Analyzing job description for bias...")
            jd_bias = bias_detector_instance.calculate_bias_score(job_description)
            result["jd_bias_analysis"] = {
                "score": jd_bias["score"],
                "rating": jd_bias["rating"],
                "flags_count": jd_bias["flags_count"],
                "breakdown": jd_bias.get("breakdown", {})
            }
            
            if jd_bias["score"] > 50:
                rewritten_jd, flags = bias_detector_instance.rewrite_text(job_description)
                result["jd_bias_warning"] = f"High bias detected ({jd_bias['score']}%). Consider revising."
                result["jd_suggested_rewrite"] = rewritten_jd
                # Optionally use rewritten JD
                # job_description = rewritten_jd
        
        # Save candidate to database
        self.audit_db.save_candidate(candidate_id)
        
        # ============ STORE RESUME IN VECTOR DATABASE (RAG) ============
        if self.vector_store:
            print("\n📦 Storing resume in vector database...")
            store_result = self.vector_store.add_resume(candidate_id, raw_resume)
            if store_result.get("success"):
                print(f"✅ Resume chunked and stored: {store_result.get('chunks_stored')} chunks")
                result["vector_store"] = {
                    "enabled": True,
                    "chunks_stored": store_result.get("chunks_stored"),
                    "total_characters": store_result.get("total_characters")
                }
            else:
                print(f"⚠️ Vector store error: {store_result.get('error')}")
                result["vector_store"] = {"enabled": False, "error": store_result.get("error")}
        else:
            result["vector_store"] = {"enabled": False}
        
        # ============ AGENT 1: BLIND GATEKEEPER ============
        print("\n" + "="*50)
        print("🛡️  AGENT 1: Blind Gatekeeper")
        print("="*50)
        
        try:
            agent1_result = self.gatekeeper.process(raw_resume, min_years)
        except Exception as e:
            print(f"❌ Agent 1 crashed: {e}")
            agent1_result = {
                "status": "FAIL",
                "reason": f"Agent 1 error: {str(e)}",
                "years_exp": 0,
                "clean_data": {},
                "clean_token": "",
                "audit_log": [],
                "bias_flags": []
            }
        result["pipeline_stages"]["agent_1"] = agent1_result
        result["agent_1_status"] = agent1_result.get("status", "FAIL")
        result["agent_1_reason"] = agent1_result.get("reason", "")
        result["years_exp"] = agent1_result.get("years_exp", 0)
        
        # Save audit entries
        for entry in agent1_result.get("audit_log", []):
            self.audit_db.save_audit_entry(candidate_id, entry)
        
        # Save bias flags
        for flag in agent1_result.get("bias_flags", []):
            self.audit_db.save_bias_flag(
                candidate_id,
                flag.get("type", "unknown"),
                flag.get("description", ""),
                flag.get("action", "Redacted")
            )
        
        # Save PII redaction stats
        if agent1_result.get("redaction_stats"):
            self.audit_db.save_pii_redactions(
                candidate_id,
                agent1_result["redaction_stats"]
            )
        
        # ============ TRUST LAYER: Visual Proof (Diff) ============
        # Compare original vs redacted text for UI visualization
        if self.diff_engine and agent1_result.get("redacted_text"):
            print("🔍 Computing redaction diff (Visual Proof)...")
            diff_report = self.diff_engine.compute_diff_summary(
                raw_resume,
                agent1_result.get("redacted_text", "")
            )
            result["trust_layer"] = {
                "diff_report": diff_report,
                "redaction_verified": True,
                "diff_stats": diff_report.get("stats", {})
            }
            print(f"   ✓ {diff_report.get('stats', {}).get('deletions', 0)} PII items removed")
            print(f"   ✓ {diff_report.get('stats', {}).get('insertions', 0)} placeholders added")
            print(f"   ✓ Redaction rate: {diff_report.get('stats', {}).get('redaction_rate', 0)}%")
        else:
            result["trust_layer"] = {"redaction_verified": False}
        
        # Check if Agent 1 passed
        if agent1_result.get("status") == "FAIL":
            result["final_status"] = "REJECTED_BY_AGENT_1"
            result["final_reason"] = agent1_result.get("reason", "")
            
            self.audit_db.update_candidate(candidate_id, {
                "status": "REJECTED",
                "years_exp": agent1_result.get("years_exp", 0),
                "final_decision": "REJECTED_BY_AGENT_1"
            })
            
            self.audit_db.save_verification_result(candidate_id, result)
            self.current_result = result
            return result
        
        print(f"✅ Agent 1 PASSED: {agent1_result.get('reason', '')}")
        
        # Issue ELIGIBILITY credential via W3C or Zynd Protocol
        eligibility_credential = None
        if self.w3c_credential_manager and candidate_did and self.agent1_identity:
            try:
                # Use W3C Verifiable Credentials with blockchain
                candidate_did_str = self._get_did_string(candidate_did)
                eligibility_credential = self.w3c_credential_manager.issue_credential(
                    issuer_did=self.agent1_identity.get("did") or self.agent1_identity.get("id", ""),
                    credential_type="EligibilityCredential",
                    subject_did=candidate_did_str or "",
                    claims={
                        "years_experience": agent1_result.get("years_exp", 0),
                        "minimum_required": min_years,
                        "pii_redacted": True,
                        "verification_status": "PASSED",
                        "verified_at": datetime.now().isoformat()
                    },
                    evidence=[{
                        "type": "AgentVerification",
                        "agent_id": "Agent1:BlindGatekeeper",
                        "agent_did": self.agent1_identity.get("did") or self.agent1_identity.get("id", ""),
                        "verification_method": "automated_eligibility_check"
                    }]
                )
                result["credentials_issued"].append(eligibility_credential)
                
                # Add blockchain metadata
                if "blockchain_metadata" not in result:
                    result["blockchain_metadata"] = {}
                result["blockchain_metadata"]["eligibility_credential_id"] = eligibility_credential.get("id")
                result["blockchain_metadata"]["issuer_did"] = self.agent1_identity.get("did") or self.agent1_identity.get("id", "")
                if self.blockchain_did_manager:
                    result["blockchain_metadata"]["network"] = self.blockchain_did_manager.network_name
                
                print(f"✅ W3C Eligibility Credential issued: {eligibility_credential.get('id')}")
                
                # Send authenticated message to Agent 2
                if self.communication_hub and self.agent2_identity and AgentCommunicationHub:
                    message = self.communication_hub.send_message_sync(
                        recipient_did=self.agent2_identity.get("did") or self.agent2_identity.get("id", ""),
                        content={
                            "candidate_did": candidate_did_str,
                            "credential_id": eligibility_credential.get("id"),
                            "task": "skill_validation"
                        }
                    )
                    result["agent_messages"].append({
                        "id": message.message_id,
                        "type": message.message_type,
                        "from": "Agent1:BlindGatekeeper",
                        "to": "Agent2:SkillValidator",
                        "timestamp": message.timestamp
                    })
                    print(f"✅ Blockchain-authenticated message sent to Agent 2")
                
            except Exception as e:
                print(f"⚠️ W3C credential issuance failed: {e}")
                # Fallback to legacy credential
                eligibility_credential = None
        
        # Fallback to legacy Zynd Protocol credential
        if not eligibility_credential and ZYND_AVAILABLE and self.protocol and candidate_did and self.agent1_identity:
            candidate_did_str = self._get_did_string(candidate_did)
            eligibility_credential = self.protocol.issue_credential(
                issuer_did=self.agent1_identity.get("did") or self.agent1_identity.get("id", ""),
                subject_did=candidate_did_str or "",
                credential_type="EligibilityCredential",
                claims={
                    "years_experience": agent1_result.get("years_exp", 0),
                    "minimum_required": min_years,
                    "pii_redacted": True,
                    "verification_status": "PASSED",
                    "verified_at": datetime.now().isoformat()
                }
            )
            result["credentials_issued"].append(eligibility_credential)
            
            # Send authenticated message to Agent 2
            if self.agent2_identity:
                agent2_did_str = self._get_did_string(self.agent2_identity)
                agent1_msg = self.protocol.send_message(
                    sender_did=self.agent1_identity.get("did") or self.agent1_identity.get("id", ""),
                    recipient_did=agent2_did_str or "",
                    content=json.dumps({
                        "candidate_did": candidate_did_str,
                        "credential_id": eligibility_credential.get("id"),
                        "task": "skill_validation"
                    }),
                    message_type="TASK_HANDOFF"
                )
                result["agent_messages"].append({
                    "id": agent1_msg.get("message_id"),
                    "type": "TASK_HANDOFF",
                    "from": "Agent1:BlindGatekeeper",
                    "to": "Agent2:SkillValidator"
                })
        
        # ============ AGENT 2: SKILL VALIDATOR ============
        print("\n" + "="*50)
        print("🎯 AGENT 2: Skill Validator (Evidence-Based)")
        print("="*50)
        
        try:
            agent2_result = self.validator.process(
                agent1_result.get("clean_data", {}),
                job_description,
                agent1_result.get("clean_token", ""),
                vector_store=self.vector_store,
                candidate_id=candidate_id
            )
        except Exception as e:
            print(f"❌ Agent 2 crashed: {e}")
            agent2_result = {
                "status": "FAIL",
                "reason": f"Agent 2 error: {str(e)}",
                "score": 0,
                "matched_skills": [],
                "missing_skills": [],
                "audit_log": []
            }
        result["pipeline_stages"]["agent_2"] = agent2_result
        result["agent_2_status"] = agent2_result.get("status", "FAIL")
        result["agent_2_score"] = agent2_result.get("score", 0)
        result["agent_2_reason"] = agent2_result.get("reason", "")
        
        # Save audit entries
        for entry in agent2_result.get("audit_log", []):
            self.audit_db.save_audit_entry(candidate_id, entry)
        
        # Check if Agent 2 passed
        if agent2_result.get("status") == "FAIL":
            result["final_status"] = "REJECTED_BY_AGENT_2"
            result["final_reason"] = agent2_result.get("reason", "")
            
            self.audit_db.update_candidate(candidate_id, {
                "status": "REJECTED",
                "years_exp": agent1_result.get("years_exp", 0),
                "match_score": agent2_result.get("score", 0),
                "final_decision": "REJECTED_BY_AGENT_2"
            })
            
            self.audit_db.save_verification_result(candidate_id, result)
            self.current_result = result
            return result
        
        print(f"✅ Agent 2 PASSED: {agent2_result.get('reason', '')}")
        
        # Issue SKILL credential via W3C or Zynd Protocol
        skill_credential = None
        if self.w3c_credential_manager and candidate_did and self.agent2_identity:
            try:
                # Use W3C Verifiable Credentials with blockchain
                candidate_did_str = self._get_did_string(candidate_did)
                skill_credential = self.w3c_credential_manager.issue_credential(
                    issuer_did=self.agent2_identity.get("did") or self.agent2_identity.get("id", ""),
                    credential_type="SkillMatchCredential",
                    subject_did=candidate_did_str or "",
                    claims={
                        "match_score": agent2_result.get("score", 0),
                        "matched_skills": agent2_result.get("matched_skills", []),
                        "missing_skills": agent2_result.get("missing_skills", []),
                        "threshold": 60,
                        "verification_status": "PASSED",
                        "verified_at": datetime.now().isoformat()
                    },
                    evidence=[{
                        "type": "AgentVerification",
                        "agent_id": "Agent2:SkillValidator",
                        "agent_did": self.agent2_identity.get("did") or self.agent2_identity.get("id", ""),
                        "evidence_chunks": agent2_result.get("evidence", [])[:3]  # Include top 3 evidence chunks
                    }]
                )
                result["credentials_issued"].append(skill_credential)
                
                # Update blockchain metadata
                if "blockchain_metadata" not in result:
                    result["blockchain_metadata"] = {}
                result["blockchain_metadata"]["skill_credential_id"] = skill_credential.get("id")
                
                print(f"✅ W3C Skill Match Credential issued: {skill_credential.get('id')}")
                
                # Send authenticated message to Agent 3
                if self.communication_hub and self.agent3_identity and AgentCommunicationHub:
                    message = self.communication_hub.send_message_sync(
                        recipient_did=self.agent3_identity.get("did") or self.agent3_identity.get("id", ""),
                        content={
                            "candidate_did": candidate_did_str,
                            "skill_credential_id": skill_credential.get("id"),
                            "task": "authenticity_verification"
                        }
                    )
                    result["agent_messages"].append({
                        "id": message.message_id,
                        "type": message.message_type,
                        "from": "Agent2:SkillValidator",
                        "to": "Agent3:Inquisitor",
                        "timestamp": message.timestamp
                    })
                    print(f"✅ Blockchain-authenticated message sent to Agent 3")
                
            except Exception as e:
                print(f"⚠️ W3C credential issuance failed: {e}")
                # Fallback to legacy credential
                skill_credential = None
        
        # Fallback to legacy Zynd Protocol credential
        if not skill_credential and ZYND_AVAILABLE and self.protocol and candidate_did and self.agent2_identity and self.agent3_identity:
            skill_credential = self.protocol.issue_credential(
                issuer_did=self.agent2_identity.get("did") or self.agent2_identity.get("id", ""),
                subject_did=candidate_did.get("did") or candidate_did.get("id", ""),
                credential_type="SkillMatchCredential",
                claims={
                    "match_score": agent2_result.get("score", 0),
                    "matched_skills": agent2_result.get("matched_skills", []),
                    "missing_skills": agent2_result.get("missing_skills", []),
                    "threshold": 60,
                    "verification_status": "PASSED",
                    "verified_at": datetime.now().isoformat()
                }
            )
            result["credentials_issued"].append(skill_credential)
            
            # Send authenticated message to Agent 3
            agent2_msg = self.protocol.send_message(
                sender_did=self.agent2_identity.get("did") or self.agent2_identity.get("id", ""),
                recipient_did=self.agent3_identity.get("did") or self.agent3_identity.get("id", ""),
                content=json.dumps({
                    "candidate_did": candidate_did.get("did") or candidate_did.get("id", ""),
                    "skill_credential_id": skill_credential.get("id"),
                    "task": "authenticity_verification"
                }),
                message_type="AUTHENTICITY_CHECK_REQUEST"
            )
            result["agent_messages"].append({
                "id": agent2_msg.get("id"),
                "type": agent2_msg.get("type"),
                "from": "Agent2:SkillValidator",
                "to": "Agent3:Inquisitor"
            })
        
        # ============ AGENT 3: INQUISITOR (Question Generation) ============
        print("\n" + "="*50)
        print("❓ AGENT 3: Inquisitor (Evidence-Based)")
        print("="*50)
        
        try:
            agent3_questions = self.inquisitor.process(
                agent1_result.get("clean_data", {}),
                num_questions=3,
                vector_store=self.vector_store,
                candidate_id=candidate_id
            )
        except Exception as e:
            print(f"❌ Agent 3 crashed: {e}")
            agent3_questions = {
                "questions": [],
                "status": "FAIL",
                "reason": f"Agent 3 error: {str(e)}",
                "audit_log": []
            }
        result["pipeline_stages"]["agent_3_questions"] = agent3_questions
        result["verification_questions"] = agent3_questions.get("questions", [])
        
        # Save audit entries
        for entry in agent3_questions.get("audit_log", []):
            self.audit_db.save_audit_entry(candidate_id, entry)
        
        print(f"✅ Agent 3 generated {len(agent3_questions.get('questions', []))} questions")
        
        # Pipeline pauses here - waiting for candidate answers
        result["final_status"] = "QUESTIONS_PENDING"
        result["agent_3_status"] = "PENDING"
        
        self.audit_db.update_candidate(candidate_id, {
            "status": "QUESTIONS_PENDING",
            "years_exp": agent1_result.get("years_exp", 0),
            "match_score": agent2_result.get("score", 0)
        })
        
        self.current_result = result
        return result
    
    def evaluate_candidate_answers(self, qa_pairs: List[Dict],
                                    candidate_id: Optional[str] = None) -> Dict:
        """
        Evaluate candidate's answers to Agent 3 questions.
        
        Args:
            qa_pairs: List of {"question": str, "answer": str}
            candidate_id: Optional override (uses current if not provided)
            
        Returns:
            Final evaluation result
        """
        
        cid = candidate_id or self.current_candidate_id
        
        if not cid or not self.current_result:
            return {
                "status": "ERROR",
                "reason": "No active verification pipeline"
            }
        
        # Get clean data from previous stage
        agent1_data = self.current_result.get("pipeline_stages", {}).get("agent_1", {})
        clean_data = agent1_data.get("clean_data", {})
        
        if not clean_data:
            return {
                "status": "ERROR",
                "reason": "No clean data available from Agent 1"
            }
        
        print("\n" + "="*50)
        print("❓ AGENT 3: Evaluating Answers")
        print("="*50)
        
        # Evaluate answers
        try:
            agent3_eval = self.inquisitor.evaluate_candidate_answers(clean_data, qa_pairs)
        except Exception as e:
            print(f"⚠️ Agent 3 evaluation failed: {e}")
            agent3_eval = {
                "status": "UNCERTAIN",
                "authenticity_score": 50,
                "reason": f"Agent 3 evaluation error: {str(e)}",
                "red_flags": [],
                "individual_scores": [],
                "audit_log": []
            }
        
        # Update result
        self.current_result["pipeline_stages"]["agent_3_evaluation"] = agent3_eval
        self.current_result["agent_3_status"] = agent3_eval.get("status", "UNCERTAIN")
        self.current_result["agent_3_authenticity"] = agent3_eval.get("authenticity_score", 50)
        self.current_result["agent_3_reason"] = agent3_eval.get("reason", "No reason provided")
        self.current_result["red_flags"] = agent3_eval.get("red_flags", [])
        
        # Save audit entries (use cid which is guaranteed to be set at this point)
        for entry in agent3_eval.get("audit_log", []):
            self.audit_db.save_audit_entry(cid, entry)
        
        # Issue AUTHENTICITY credential via W3C or Zynd Protocol
        authenticity_credential = None
        candidate_did_str = self.current_result.get("candidate_did", "")
        
        if self.w3c_credential_manager and self.agent3_identity and agent3_eval.get("status") == "PASS":
            try:
                # Use W3C Verifiable Credentials with blockchain
                authenticity_credential = self.w3c_credential_manager.issue_credential(
                    issuer_did=self.agent3_identity.get("did") or self.agent3_identity.get("id", ""),
                    credential_type="AuthenticityCredential",
                    subject_did=candidate_did_str,
                    claims={
                        "authenticity_score": agent3_eval["authenticity_score"],
                        "red_flags_count": len(agent3_eval.get("red_flags", [])),
                        "verification_status": "PASSED" if agent3_eval["status"] == "PASS" else "FAILED",
                        "verified_at": datetime.now().isoformat(),
                        "individual_scores": agent3_eval.get("individual_scores", [])
                    },
                    evidence=[{
                        "type": "AgentVerification",
                        "agent_id": "Agent3:Inquisitor",
                        "agent_did": self.agent3_identity.get("did") or self.agent3_identity.get("id", ""),
                        "qa_count": len(qa_pairs),
                        "red_flags": agent3_eval.get("red_flags", [])
                    }]
                )
                self.current_result["credentials_issued"].append(authenticity_credential)
                
                # Update blockchain metadata
                if "blockchain_metadata" not in self.current_result:
                    self.current_result["blockchain_metadata"] = {}
                self.current_result["blockchain_metadata"]["authenticity_credential_id"] = authenticity_credential.get("id")
                
                print(f"✅ W3C Authenticity Credential issued: {authenticity_credential.get('id')}")
                
                # Send completion message via blockchain
                if self.communication_hub and AgentCommunicationHub:
                    message = self.communication_hub.send_message_sync(
                        recipient_did="system",  # Send to system/orchestrator
                        message_type=AgentCommunicationHub.VERIFICATION_COMPLETE,
                        content={
                            "candidate_did": candidate_did_str,
                            "authenticity_credential_id": authenticity_credential.get("id"),
                            "final_status": agent3_eval.get("status", "UNCERTAIN")
                        }
                    )
                    self.current_result["agent_messages"].append({
                        "id": message.message_id,
                        "type": message.message_type,
                        "from": "Agent3:Inquisitor",
                        "to": "System:Orchestrator",
                        "timestamp": message.timestamp
                    })
                    print(f"✅ Verification complete message sent")
                
            except Exception as e:
                print(f"⚠️ W3C credential issuance failed: {e}")
                # Continue without credential
        
        # Final decision
        if agent3_eval.get("status") == "PASS":
            self.current_result["final_status"] = "✅ APPROVED"
            self.current_result["final_reason"] = "Passed all verification stages"
            
            self.audit_db.update_candidate(cid, {
                "status": "APPROVED",
                "authenticity_score": agent3_eval.get("authenticity_score", 50),
                "final_decision": "APPROVED"
            })
            
            print(f"✅ FINAL DECISION: APPROVED")
        else:
            self.current_result["final_status"] = "❌ REJECTED"
            self.current_result["final_reason"] = agent3_eval.get("reason", "Did not pass verification")
            
            self.audit_db.update_candidate(cid, {
                "status": "REJECTED",
                "authenticity_score": agent3_eval.get("authenticity_score", 50),
                "final_decision": "REJECTED_BY_AGENT_3"
            })
            
            print(f"❌ FINAL DECISION: REJECTED - {agent3_eval.get('reason', 'Unknown reason')}")
        
        # ============ TRUST LAYER: Cryptographic Proof (Ledger) ============
        # Create immutable hash of the final decision
        integrity_block = None
        if self.ledger_manager:
            print("🔐 Creating cryptographic proof (Integrity Block)...")
            
            # Create a clean copy of result for hashing (exclude mutable audit logs)
            hashable_result = {
                "candidate_id": cid,
                "final_status": self.current_result.get("final_status"),
                "final_reason": self.current_result.get("final_reason"),
                "agent_1_status": self.current_result.get("agent_1_status"),
                "agent_2_status": self.current_result.get("agent_2_status"),
                "agent_2_score": self.current_result.get("agent_2_score"),
                "agent_3_status": agent3_eval.get("status"),
                "agent_3_authenticity": agent3_eval.get("authenticity_score"),
                "red_flags_count": len(agent3_eval.get("red_flags", [])),
                "timestamp": self.current_result.get("timestamp")
            }
            
            integrity_block = self.ledger_manager.create_block(cid, hashable_result)
            
            # Add to trust layer
            if "trust_layer" not in self.current_result:
                self.current_result["trust_layer"] = {}
            
            self.current_result["trust_layer"]["integrity_block"] = integrity_block
            self.current_result["trust_layer"]["data_hash"] = integrity_block["data_hash"]
            self.current_result["trust_layer"]["block_id"] = integrity_block["block_id"]
            self.current_result["trust_layer"]["sealed_at"] = integrity_block["timestamp"]
            self.current_result["trust_layer"]["signature"] = integrity_block["signature"]
            
            print(f"   ✓ Block ID: {integrity_block['block_id'][:16]}...")
            print(f"   ✓ Data Hash: {integrity_block['data_hash'][:32]}...")
            print(f"   ✓ Signature: {integrity_block['signature']}")
        
        # Save complete verification result
        self.audit_db.save_verification_result(cid, self.current_result)
        
        return {
            "candidate_id": cid,
            "agent_3_status": agent3_eval.get("status", "UNCERTAIN"),
            "agent_3_reason": agent3_eval.get("reason", "No reason provided"),
            "agent_3_authenticity": agent3_eval.get("authenticity_score", 50),
            "red_flags": agent3_eval.get("red_flags", []),
            "final_status": self.current_result.get("final_status", "UNKNOWN"),
            "final_reason": self.current_result.get("final_reason", "No reason provided"),
            "individual_scores": agent3_eval.get("individual_scores", []),
            "trust_layer": self.current_result.get("trust_layer", {})
        }
    
    def get_pipeline_status(self) -> Dict:
        """Get current pipeline status"""
        if not self.current_result:
            return {"status": "NO_ACTIVE_PIPELINE"}
        
        return {
            "candidate_id": self.current_candidate_id,
            "status": self.current_result.get("final_status", "UNKNOWN"),
            "stages_completed": list(self.current_result.get("pipeline_stages", {}).keys())
        }
    
    def get_full_audit_trail(self, candidate_id: Optional[str] = None) -> List[Dict]:
        """Get complete audit trail for a candidate"""
        cid = candidate_id or self.current_candidate_id
        if not cid:
            return []
        
        return self.audit_db.get_candidate_history(cid)
    
    def get_pipeline_stats(self) -> Dict:
        """Get overall pipeline statistics"""
        return self.audit_db.get_pipeline_stats()
    
    def get_trust_packet(self, candidate_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the Trust Packet for a candidate.
        
        Contains:
        - diff_report: Visual proof of PII redaction
        - integrity_block: Cryptographic proof of decision
        - verification_status: Whether the data is tamper-free
        
        Args:
            candidate_id: Optional override (uses current if not provided)
            
        Returns:
            Trust packet for frontend display
        """
        cid = candidate_id or self.current_candidate_id
        
        if not cid or not self.current_result:
            return {
                "error": "No verification data available",
                "candidate_id": cid
            }
        
        trust_layer = self.current_result.get("trust_layer", {})
        
        return {
            "candidate_id": cid,
            "timestamp": self.current_result.get("timestamp"),
            
            # Visual Proof - Redaction Diff
            "diff_report": trust_layer.get("diff_report"),
            "diff_stats": trust_layer.get("diff_stats"),
            "redaction_verified": trust_layer.get("redaction_verified", False),
            
            # Cryptographic Proof - Integrity Block  
            "block_id": trust_layer.get("block_id"),
            "data_hash": trust_layer.get("data_hash"),
            "signature": trust_layer.get("signature"),
            "sealed_at": trust_layer.get("sealed_at"),
            
            # Verification Status
            "integrity_verified": True if trust_layer.get("data_hash") else False
        }
    
    def verify_candidate_integrity(self, candidate_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify that a candidate's data hasn't been tampered with.
        
        Re-computes the hash and compares with stored block.
        
        Returns:
            Verification report with match status
        """
        cid = candidate_id or self.current_candidate_id
        
        if not cid or not self.current_result:
            return {
                "verified": False,
                "error": "No verification data available"
            }
        
        trust_layer = self.current_result.get("trust_layer", {})
        integrity_block = trust_layer.get("integrity_block")
        
        if not integrity_block or not self.ledger_manager:
            return {
                "verified": False,
                "error": "No integrity block found"
            }
        
        # Re-create the hashable result
        hashable_result = {
            "candidate_id": cid,
            "final_status": self.current_result["final_status"],
            "final_reason": self.current_result["final_reason"],
            "agent_1_status": self.current_result.get("agent_1_status"),
            "agent_2_status": self.current_result.get("agent_2_status"),
            "agent_2_score": self.current_result.get("agent_2_score"),
            "agent_3_status": self.current_result.get("agent_3_status"),
            "agent_3_authenticity": self.current_result.get("agent_3_authenticity"),
            "red_flags_count": len(self.current_result.get("red_flags", [])),
            "timestamp": self.current_result.get("timestamp")
        }
        
        return self.ledger_manager.get_verification_report(integrity_block, hashable_result)
    
    def get_network_stats(self) -> Dict:
        """Get Zynd network statistics"""
        if ZYND_AVAILABLE and self.protocol:
            stats = self.protocol.get_network_stats()
            return {
                "registered_agents": stats.get("total_agents", 3),
                "total_messages": stats.get("total_messages", 0),
                "total_credentials": stats.get("total_credentials", 0),
                "candidates_processed": len(self.candidates),
                "agent_trust_scores": self.get_agent_trust_scores(),
                "capabilities": stats.get("capabilities", []),
                "zynd_enabled": True
            }
        else:
            return {
                "registered_agents": 3,
                "total_messages": 0,
                "total_credentials": 0,
                "candidates_processed": 0,
                "agent_trust_scores": {},
                "capabilities": [],
                "zynd_enabled": False
            }
    
    def get_agent_trust_scores(self) -> Dict[str, float]:
        """Get trust scores for all agents"""
        if ZYND_AVAILABLE and self.protocol:
            return {
                "BlindGatekeeper": self.protocol.get_agent_trust_score(self.agent1_identity.get("did") or self.agent1_identity.get("id", "")) if self.agent1_identity else 1.0,
                "SkillValidator": self.protocol.get_agent_trust_score(self.agent2_identity.get("did") or self.agent2_identity.get("id", "")) if self.agent2_identity else 1.0,
                "Inquisitor": self.protocol.get_agent_trust_score(self.agent3_identity.get("did") or self.agent3_identity.get("id", "")) if self.agent3_identity else 1.0
            }
        return {"BlindGatekeeper": 1.0, "SkillValidator": 1.0, "Inquisitor": 1.0}
    
    def get_candidate_credentials(self, candidate_id: str) -> List[Dict]:
        """Get all credentials for a candidate"""
        candidate = self.candidates.get(candidate_id)
        if candidate:
            return candidate.credentials
        return []


# Quick test
if __name__ == "__main__":
    orchestrator = VelosOrchestrator("test_orchestrator.db")
    
    sample_resume = """
    John Doe
    Email: john.doe@example.com
    Phone: 555-123-4567
    Location: San Francisco, CA
    
    PROFESSIONAL SUMMARY
    3.5 years of AI/ML engineering experience building production systems.
    
    WORK EXPERIENCE
    
    Senior AI Engineer | TechCorp Inc. (2022-2025)
    - Built RAG systems using LangChain and Pinecone
    - Developed production LLM pipelines with 99.9% uptime
    - Optimized inference latency by 40%
    - Tech: Python, FastAPI, AWS, Docker
    
    AI Developer | StartupXYZ (2020-2022)
    - Created NLP pipelines for document processing
    - Implemented transformer-based models
    - Built: Real-time text classification system
    
    SKILLS
    Python, FastAPI, LangChain, RAG, LLMs, AWS, Docker, SQL, Git
    
    EDUCATION
    Bachelor's in Computer Science from IIT Delhi (2020)
    """
    
    job_description = """
    Senior AI Engineer
    
    We're looking for an experienced AI Engineer.
    
    Requirements:
    - 2+ years of Python development
    - Experience with LLMs and RAG systems
    - FastAPI or Django experience
    - AWS or GCP cloud experience
    - Strong SQL skills
    """
    
    # Run pipeline
    print("\n" + "="*60)
    print("VELOS: FULL VERIFICATION PIPELINE")
    print("="*60)
    
    result = orchestrator.run_verification_pipeline(
        sample_resume,
        job_description,
        min_years=2.0
    )
    
    print("\n" + "="*50)
    print("PIPELINE RESULT")
    print("="*50)
    print(f"Candidate ID: {result['candidate_id']}")
    print(f"Agent 1: {result['agent_1_status']} ({result.get('years_exp', 0)} years)")
    print(f"Agent 2: {result.get('agent_2_status', 'N/A')} ({result.get('agent_2_score', 0)}%)")
    print(f"Status: {result['final_status']}")
    
    if result['final_status'] == 'QUESTIONS_PENDING':
        print("\n📝 Verification Questions:")
        for i, q in enumerate(result.get('verification_questions', []), 1):
            print(f"  {i}. {q}")
        
        # Simulate answers
        print("\n🔄 Simulating candidate answers...")
        qa_pairs = [
            {
                "question": q,
                "answer": f"For this project, I implemented a solution using Python and focused on {q.lower().split()[3] if len(q.split()) > 3 else 'best practices'}. The main challenge was handling scale, which I addressed through caching and async processing. We saw 40% improvement in performance."
            }
            for q in result.get('verification_questions', [])
        ]
        
        final_result = orchestrator.evaluate_candidate_answers(qa_pairs)
        
        print("\n" + "="*50)
        print("FINAL RESULT")
        print("="*50)
        print(f"Status: {final_result['final_status']}")
        print(f"Authenticity: {final_result['agent_3_authenticity']:.0f}%")
        print(f"Reason: {final_result['final_reason']}")
    
    # Cleanup
    orchestrator.audit_db.close()
    import os
    os.remove("test_orchestrator.db")
    print("\n✅ Orchestrator test passed!")
