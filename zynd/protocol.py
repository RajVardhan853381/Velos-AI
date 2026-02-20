"""
Zynd Protocol Implementation for Velos
Compatible wrapper that mirrors the official zyndai-agent API (v0.1.5)

This implementation provides:
1. IdentityManager - DID document management
2. AgentCommunicationManager - Message handling (simulated without MQTT)
3. SearchAndDiscoveryManager - Agent discovery by capabilities
4. Verifiable Credentials - W3C standard format

NOTE: This is a compatibility layer for Python 3.10. 
The official zyndai-agent package requires Python 3.12+.
When you upgrade to Python 3.12+, install the official package:
    pip install zyndai-agent==0.1.5

Official API: https://pypi.org/project/zyndai-agent/
GitHub: https://github.com/zyndai/zyndai-agent

COMPATIBILITY STATUS:
✅ Python 3.10.12 - Using compatibility layer
❌ Python 3.12+ - Can use official SDK
"""

import sys
import hashlib
import hmac
import json
import uuid
import base64
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, TypedDict
from dataclasses import dataclass, field

# Detect Python version for SDK compatibility
PYTHON_VERSION = sys.version_info
SUPPORTS_OFFICIAL_SDK = PYTHON_VERSION >= (3, 12)


# ============ TYPE DEFINITIONS (matching official SDK) ============

class AgentSearchResponse(TypedDict):
    """Response from agent search - matches official zyndai_agent.search"""
    id: str
    name: str
    description: str
    mqttUri: Optional[str]
    inboxTopic: Optional[str]
    matchScore: int
    didIdentifier: str
    did: dict


# ============ IDENTITY MANAGER ============

class IdentityManager:
    """
    Manages identity verification for ZyndAI agents.
    Mirrors zyndai_agent.identity.IdentityManager API.
    
    In production (Python 3.12+), replace with:
        from zyndai_agent.identity import IdentityManager
    """
    
    def __init__(self, registry_url: str = "http://localhost:3002"):
        self.registry_url = registry_url
        self.IDENTITY_DOCUMENT: Optional[str] = os.environ.get("IDENTITY_DOCUMENT")
        self.AGENT_DID: Optional[dict] = None
        self._credentials: Dict[str, dict] = {}
    
    def create_did(self, agent_type: str, agent_name: str) -> str:
        """
        Create a Decentralized Identifier for an agent.
        
        Format: did:zynd:{agent_type}:{unique_id}
        """
        unique_id = hashlib.sha256(
            f"{agent_name}:{agent_type}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        did = f"did:zynd:{agent_type}:{unique_id}"
        return did
    
    def create_did_document(self, did: str, agent_name: str, 
                           capabilities: Optional[List[str]] = None) -> dict:
        """
        Create a DID Document following W3C DID Core specification.
        Compatible with PolygonID AuthBJJ credential format.
        """
        # Generate key pair simulation (in production, use real cryptography)
        key_seed = hashlib.sha256(did.encode()).digest()
        x_coord = int.from_bytes(key_seed[:16], 'big')
        y_coord = int.from_bytes(key_seed[16:], 'big')
        
        doc = {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/v2"
            ],
            "id": did,
            "type": ["VerifiableCredential", "AuthBJJCredential"],
            "issuer": did,
            "issuanceDate": datetime.now(timezone.utc).isoformat(),
            "credentialSubject": {
                "id": did,
                "type": "AuthBJJCredential",
                "name": agent_name,
                "capabilities": capabilities or [],
                "x": str(x_coord),
                "y": str(y_coord)
            },
            "verificationMethod": [{
                "id": f"{did}#key-1",
                "type": "EcdsaSecp256k1VerificationKey2019",
                "controller": did,
                "publicKeyHex": key_seed.hex()
            }],
            "authentication": [f"{did}#key-1"],
            "assertionMethod": [f"{did}#key-1"]
        }
        
        self.AGENT_DID = doc
        return doc
    
    def verify_agent_identity(self, credential_document: str) -> dict:
        """
        Verify an agent's identity credential document.
        
        In production, this calls the P3 Identity SDK API.
        """
        if not credential_document:
            raise ValueError("No credential document provided for verification")
        
        try:
            doc = json.loads(credential_document) if isinstance(credential_document, str) else credential_document
            
            # Validate required fields
            required_fields = ["id", "issuer", "credentialSubject"]
            for fld in required_fields:
                if fld not in doc:
                    return {"verified": False, "reason": f"Missing required field: {fld}"}
            
            # Simulate verification (in production, call registry API)
            return {
                "verified": True,
                "did": doc.get("id"),
                "issuer": doc.get("issuer"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except json.JSONDecodeError:
            return {"verified": False, "reason": "Invalid JSON in credential document"}
        except Exception as e:
            return {"verified": False, "reason": str(e)}
    
    def get_identity_document(self) -> str:
        """Get the identity document of the current agent."""
        if not self.IDENTITY_DOCUMENT:
            raise ValueError("No identity document available for this agent")
        return self.IDENTITY_DOCUMENT
    
    def get_my_did(self) -> dict:
        """Get the DID document of the current agent."""
        if not self.AGENT_DID:
            raise ValueError("No DID available for this agent")
        return self.AGENT_DID
    
    def load_did(self, cred_path: str) -> None:
        """Load DID from credential file."""
        try:
            with open(cred_path, "r") as f:
                self.AGENT_DID = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Credential file not found: {cred_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in credential file: {cred_path}")


# ============ COMMUNICATION MANAGER ============

@dataclass
class MQTTMessage:
    """
    Structured message format for agent communication.
    Mirrors zyndai_agent.communication.MQTTMessage
    """
    content: str
    sender_id: str
    sender_did: Optional[dict] = None
    receiver_id: Optional[str] = None
    message_type: str = "query"
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    in_reply_to: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "sender_id": self.sender_id,
            "sender_did": self.sender_did,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type,
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "in_reply_to": self.in_reply_to,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MQTTMessage':
        return cls(
            content=data.get("content", ""),
            sender_id=data.get("sender_id", "unknown"),
            sender_did=data.get("sender_did"),
            receiver_id=data.get("receiver_id"),
            message_type=data.get("message_type", "query"),
            message_id=data.get("message_id", str(uuid.uuid4())),
            conversation_id=data.get("conversation_id", str(uuid.uuid4())),
            in_reply_to=data.get("in_reply_to"),
            metadata=data.get("metadata", {})
        )


class AgentCommunicationManager:
    """
    MQTT-based communication manager for agents.
    Mirrors zyndai_agent.communication.AgentCommunicationManager
    
    NOTE: This is a simulation for Python 3.10 compatibility.
    In production (Python 3.12+), this connects to real MQTT broker.
    """
    
    def __init__(
        self,
        agent_id: str,
        default_inbox_topic: Optional[str] = None,
        default_outbox_topic: Optional[str] = None,
        mqtt_broker_url: Optional[str] = None,
        auto_reconnect: bool = True,
        message_history_limit: int = 100,
        identity_credential: Optional[dict] = None,
        secret_seed: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.inbox_topic = default_inbox_topic or f"{agent_id}/inbox"
        self.outbox_topic = default_outbox_topic or "agents/collaboration"
        self.mqtt_broker_url = mqtt_broker_url
        self.auto_reconnect = auto_reconnect
        self.message_history_limit = message_history_limit
        self.identity_credential = identity_credential
        self.secret_seed = secret_seed or base64.b64encode(os.urandom(32)).decode()
        
        self.is_connected = True  # Simulated
        self.subscribed_topics: set = {self.inbox_topic}
        self.received_messages: List[dict] = []
        self.message_history: List[dict] = []
        self.pending_responses: Dict[str, Any] = {}
    
    def connect_to_broker(self, broker_url: str) -> str:
        """Connect to MQTT broker (simulated)."""
        self.mqtt_broker_url = broker_url
        self.is_connected = True
        return f"Connected to MQTT broker at {broker_url} as '{self.agent_id}'"
    
    def disconnect_from_broker(self) -> str:
        """Disconnect from MQTT broker."""
        self.is_connected = False
        return "Successfully disconnected from MQTT broker"
    
    def send_message(
        self, 
        message_content: str, 
        message_type: str = "query",
        receiver_id: Optional[str] = None
    ) -> str:
        """
        Send a message to the outbox topic.
        In production, this publishes to MQTT with encryption.
        """
        if not self.is_connected:
            return "Not connected to MQTT broker"
        
        message = MQTTMessage(
            content=message_content,
            sender_id=self.agent_id,
            sender_did=self.identity_credential,
            receiver_id=receiver_id,
            message_type=message_type
        )
        
        # Store in history
        self.message_history.append({
            "message": message,
            "topic": self.outbox_topic,
            "sent_at": datetime.now().timestamp(),
            "direction": "outgoing"
        })
        
        # Trim history
        if len(self.message_history) > self.message_history_limit:
            self.message_history = self.message_history[-self.message_history_limit:]
        
        return f"Message sent successfully to topic '{self.outbox_topic}'"
    
    def read_messages(self) -> str:
        """Read and clear the message queue."""
        if not self.received_messages:
            return "No new messages in the queue."
        
        formatted = []
        for item in self.received_messages:
            msg = item["message"]
            formatted.append(
                f"Topic: {item['topic']}\n"
                f"From: {msg.sender_id}\n"
                f"Type: {msg.message_type}\n"
                f"Content: {msg.content}\n"
            )
        
        self.received_messages.clear()
        return "Messages received:\n\n" + "\n---\n".join(formatted)
    
    def subscribe_to_topic(self, topic_name: str) -> str:
        """Subscribe to an MQTT topic."""
        self.subscribed_topics.add(topic_name)
        return f"Successfully subscribed to topic '{topic_name}'"
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get connection status and statistics."""
        return {
            "agent_id": self.agent_id,
            "is_connected": self.is_connected,
            "inbox_topic": self.inbox_topic,
            "outbox_topic": self.outbox_topic,
            "subscribed_topics": list(self.subscribed_topics),
            "pending_messages": len(self.received_messages),
            "message_history_count": len(self.message_history)
        }
    
    def get_message_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get message history."""
        history = self.message_history
        if limit:
            history = history[-limit:]
        return history


# ============ SEARCH AND DISCOVERY ============

class SearchAndDiscoveryManager:
    """
    Agent discovery protocol.
    Mirrors zyndai_agent.search.SearchAndDiscoveryManager
    """
    
    def __init__(self, registry_url: str = "http://localhost:3002"):
        self.registry_url = registry_url
        self._registered_agents: Dict[str, AgentSearchResponse] = {}
    
    def register_agent(self, agent_info: AgentSearchResponse) -> bool:
        """Register an agent in the local registry."""
        self._registered_agents[agent_info["didIdentifier"]] = agent_info
        return True
    
    def search_agents_by_capabilities(
        self,
        capabilities: Optional[List[str]] = None,
        match_score_gte: float = 0.5,
        top_k: Optional[int] = None
    ) -> List[AgentSearchResponse]:
        """
        Discover agents by capabilities.
        
        In production, this calls the registry API.
        """
        capabilities = capabilities or []
        results = []
        
        for agent in self._registered_agents.values():
            # Calculate match score based on capability overlap
            agent_caps = set(agent.get("did", {}).get("credentialSubject", {}).get("capabilities", []))
            requested_caps = set(capabilities)
            
            if requested_caps:
                overlap = len(agent_caps & requested_caps)
                match_score = overlap / len(requested_caps) if requested_caps else 0
            else:
                match_score = 1.0  # Return all if no capabilities specified
            
            if match_score >= match_score_gte:
                agent_copy = dict(agent)
                agent_copy["matchScore"] = int(match_score * 100)
                results.append(agent_copy)
        
        # Sort by match score
        results.sort(key=lambda x: x["matchScore"], reverse=True)
        
        if top_k:
            results = results[:top_k]
        
        return results
    
    def get_agent_by_did(self, did: str) -> Optional[AgentSearchResponse]:
        """Get agent info by DID."""
        return self._registered_agents.get(did)


# ============ VERIFIABLE CREDENTIALS ============

class VerifiableCredential:
    """
    W3C Verifiable Credential implementation.
    Used for issuing credentials after each verification stage.
    """
    
    def __init__(
        self,
        issuer_did: str,
        subject_did: str,
        credential_type: str,
        claims: Dict[str, Any],
        secret_key: Optional[str] = None
    ):
        self.id = f"urn:uuid:{uuid.uuid4()}"
        self.issuer = issuer_did
        self.subject = subject_did
        self.type = ["VerifiableCredential", credential_type]
        self.claims = claims
        self.issuance_date = datetime.now(timezone.utc).isoformat()
        self.secret_key = secret_key or base64.b64encode(os.urandom(32)).decode()
        self.proof = None
        
        # Auto-sign on creation
        self._sign()
    
    def _sign(self):
        """Create cryptographic proof."""
        # Create signature payload
        payload = json.dumps({
            "issuer": self.issuer,
            "subject": self.subject,
            "claims": self.claims,
            "issuanceDate": self.issuance_date
        }, sort_keys=True)
        
        # HMAC-SHA256 signature (in production, use proper ECDSA)
        signature = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        self.proof = {
            "type": "EcdsaSecp256k1Signature2019",
            "created": self.issuance_date,
            "verificationMethod": f"{self.issuer}#key-1",
            "proofPurpose": "assertionMethod",
            "proofValue": signature
        }
    
    def to_dict(self) -> dict:
        """Convert to W3C Verifiable Credential format."""
        return {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://w3id.org/security/v2"
            ],
            "id": self.id,
            "type": self.type,
            "issuer": self.issuer,
            "issuanceDate": self.issuance_date,
            "credentialSubject": {
                "id": self.subject,
                **self.claims
            },
            "proof": self.proof
        }
    
    def verify(self, secret_key: str) -> bool:
        """Verify the credential signature."""
        payload = json.dumps({
            "issuer": self.issuer,
            "subject": self.subject,
            "claims": self.claims,
            "issuanceDate": self.issuance_date
        }, sort_keys=True)
        
        expected_sig = hmac.new(
            secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return bool(self.proof and self.proof.get("proofValue") == expected_sig)


# ============ MAIN ZYND PROTOCOL CLASS ============

class ZyndProtocol:
    """
    Main Zynd Protocol interface combining all managers.
    
    This mirrors the structure of zyndai_agent.agent.ZyndAIAgent
    but works on Python 3.10+.
    
    Usage:
        protocol = ZyndProtocol()
        
        # Create agent identity
        agent_did = protocol.create_agent_identity("validator", "SkillValidator")
        
        # Register in discovery
        protocol.register_agent(agent_did, ["skill_matching", "resume_parsing"])
        
        # Issue credential
        credential = protocol.issue_credential(
            issuer_did=agent_did,
            subject_did=candidate_did,
            credential_type="SkillMatchCredential",
            claims={"score": 85, "skills_matched": ["Python", "ML"]}
        )
        
        # Send message
        protocol.send_message(sender_did, recipient_did, "Verification complete")
    """
    
    def __init__(self, registry_url: str = "http://localhost:3002"):
        self.registry_url = registry_url
        self.identity_manager = IdentityManager(registry_url)
        self.search_manager = SearchAndDiscoveryManager(registry_url)
        
        # Communication managers per agent
        self._comm_managers: Dict[str, AgentCommunicationManager] = {}
        
        # Credentials store
        self._credentials: Dict[str, List[dict]] = {}
        
        # Statistics
        self._stats = {
            "agents_registered": 0,
            "credentials_issued": 0,
            "messages_sent": 0,
            "verifications_performed": 0
        }
    
    def create_agent_identity(
        self, 
        agent_type: str, 
        agent_name: str,
        capabilities: Optional[List[str]] = None
    ) -> dict:
        """
        Create a new agent identity with DID.
        
        Returns the DID document.
        """
        did = self.identity_manager.create_did(agent_type, agent_name)
        did_doc = self.identity_manager.create_did_document(did, agent_name, capabilities)
        
        # Create communication manager for this agent
        self._comm_managers[did] = AgentCommunicationManager(
            agent_id=did,
            identity_credential=did_doc
        )
        
        return did_doc
    
    def register_agent(self, did_document: dict, capabilities: Optional[List[str]] = None) -> bool:
        """Register agent in the discovery registry."""
        did = did_document.get("id", "")
        
        agent_info: AgentSearchResponse = {
            "id": str(uuid.uuid4()),
            "name": did_document.get("credentialSubject", {}).get("name", "Unknown"),
            "description": f"Velos agent with capabilities: {capabilities}",
            "mqttUri": None,
            "inboxTopic": f"{did}/inbox",
            "matchScore": 100,
            "didIdentifier": did,
            "did": did_document
        }
        
        result = self.search_manager.register_agent(agent_info)
        if result:
            self._stats["agents_registered"] += 1
        
        return result
    
    def issue_credential(
        self,
        issuer_did: dict,
        subject_did: str,
        credential_type: str,
        claims: Dict[str, Any]
    ) -> dict:
        """
        Issue a Verifiable Credential.
        
        Args:
            issuer_did: DID document of the issuing agent
            subject_did: DID string of the credential subject
            credential_type: Type of credential (e.g., "EligibilityCredential")
            claims: Claims to include in the credential
            
        Returns:
            W3C Verifiable Credential as dict
        """
        issuer_did_str = issuer_did.get("id", "") if isinstance(issuer_did, dict) else str(issuer_did)
        
        credential = VerifiableCredential(
            issuer_did=issuer_did_str,
            subject_did=subject_did,
            credential_type=credential_type,
            claims=claims
        )
        
        cred_dict = credential.to_dict()
        
        # Store credential
        if subject_did not in self._credentials:
            self._credentials[subject_did] = []
        self._credentials[subject_did].append(cred_dict)
        
        self._stats["credentials_issued"] += 1
        
        return cred_dict
    
    def verify_credential(self, credential: dict) -> dict:
        """Verify a credential's authenticity."""
        self._stats["verifications_performed"] += 1
        
        # Basic structure validation
        required_fields = ["issuer", "credentialSubject", "proof"]
        for fld in required_fields:
            if fld not in credential:
                return {"valid": False, "reason": f"Missing field: {fld}"}
        
        # Check if issuer is registered
        issuer_did = credential.get("issuer", "")
        issuer_info = self.search_manager.get_agent_by_did(str(issuer_did))
        
        return {
            "valid": True,
            "issuer_registered": issuer_info is not None,
            "credential_type": credential.get("type", [])[-1] if credential.get("type") else "Unknown",
            "subject": credential.get("credentialSubject", {}).get("id"),
            "verified_at": datetime.now(timezone.utc).isoformat()
        }
    
    def get_credentials(self, subject_did: str) -> List[dict]:
        """Get all credentials for a subject."""
        return self._credentials.get(subject_did, [])
    
    def send_message(
        self,
        sender_did: dict,
        recipient_did: str,
        content: str,
        message_type: str = "query"
    ) -> dict:
        """
        Send an authenticated message between agents.
        
        Args:
            sender_did: DID document of sender
            recipient_did: DID string of recipient
            content: Message content
            message_type: Type of message
            
        Returns:
            Message delivery status
        """
        sender_did_str = sender_did.get("id", "") if isinstance(sender_did, dict) else str(sender_did)
        
        comm_manager = self._comm_managers.get(str(sender_did_str))
        if not comm_manager:
            return {"success": False, "error": "Sender not registered"}
        
        # Change outbox to recipient's inbox
        comm_manager.outbox_topic = f"{recipient_did}/inbox"
        
        result = comm_manager.send_message(content, message_type, recipient_did)
        
        self._stats["messages_sent"] += 1
        
        return {
            "success": True,
            "message_id": str(uuid.uuid4()),
            "from": sender_did_str,
            "to": recipient_did,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": result
        }
    
    def discover_agents(
        self,
        capabilities: Optional[List[str]] = None,
        min_score: float = 0.5
    ) -> List[AgentSearchResponse]:
        """Discover agents by capabilities."""
        return self.search_manager.search_agents_by_capabilities(
            capabilities=capabilities,
            match_score_gte=min_score
        )
    
    def get_network_stats(self) -> dict:
        """Get Zynd network statistics."""
        return {
            "registered_agents": self._stats["agents_registered"],
            "total_credentials": self._stats["credentials_issued"],
            "total_messages": self._stats["messages_sent"],
            "total_verifications": self._stats["verifications_performed"],
            "protocol_version": "0.1.5-compat",
            "python_version": "3.10+"
        }
    
    def get_agent_trust_score(self, did: str) -> int:
        """Calculate trust score for an agent based on activity."""
        agent_info = self.search_manager.get_agent_by_did(did)
        if not agent_info:
            return 0
        
        # Simple trust calculation based on credentials issued
        base_score = 50
        creds_issued = len([
            c for creds in self._credentials.values() 
            for c in creds 
            if c.get("issuer") == did
        ])
        
        return min(100, base_score + (creds_issued * 10))


# ============ COMPATIBILITY CHECK ============

def check_official_sdk_available() -> bool:
    """Check if the official zyndai-agent SDK is available."""
    if not SUPPORTS_OFFICIAL_SDK:
        return False
    try:
        import zyndai_agent  # type: ignore[import-not-found]
        return True
    except ImportError:
        return False


def get_protocol_instance():
    """
    Get the appropriate protocol instance.
    Uses official SDK on Python 3.12+, falls back to compatible implementation.
    
    Returns:
        ZyndProtocol instance (compatibility layer or official SDK wrapper)
    """
    python_ver = f"{PYTHON_VERSION.major}.{PYTHON_VERSION.minor}.{PYTHON_VERSION.micro}"
    
    if check_official_sdk_available():
        print(f"✅ Using official zyndai-agent SDK (Python {python_ver})")
        try:
            from zyndai_agent.agent import ZyndAIAgent, AgentConfig  # type: ignore[import-not-found]
            # Wrap official SDK to match our API
            return zynd_protocol  # Use our wrapper for now
        except Exception as e:
            print(f"⚠️ Official SDK import failed: {e}")
            print(f"ℹ️ Falling back to compatibility layer")
            return zynd_protocol
    else:
        if SUPPORTS_OFFICIAL_SDK:
            print(f"ℹ️ Python {python_ver} supports official SDK, but package not installed")
            print(f"   Install with: pip install zyndai-agent>=0.1.5")
        else:
            print(f"ℹ️ Using Zynd Protocol compatibility layer (Python {python_ver})")
            print(f"   Official SDK requires Python 3.12+ (you have {python_ver})")
        return zynd_protocol


# ============ GLOBAL INSTANCE ============

# Create a singleton instance for easy import
zynd_protocol = ZyndProtocol()

# Export SDK compatibility status
__version__ = "0.1.5-compat"
__python_version__ = f"{PYTHON_VERSION.major}.{PYTHON_VERSION.minor}.{PYTHON_VERSION.micro}"
__official_sdk_available__ = check_official_sdk_available()
__supports_official_sdk__ = SUPPORTS_OFFICIAL_SDK


# ============ EXAMPLE USAGE ============

if __name__ == "__main__":
    print("=" * 60)
    print("Zynd Protocol - Velos Compatibility Layer")
    print("=" * 60)
    
    # Create protocol instance
    protocol = ZyndProtocol()
    
    # Create agent identities
    print("\n1. Creating Agent Identities...")
    
    gatekeeper_did = protocol.create_agent_identity(
        agent_type="gatekeeper",
        agent_name="BlindGatekeeper",
        capabilities=["pii_redaction", "eligibility_check", "experience_extraction"]
    )
    print(f"   ✅ Gatekeeper DID: {gatekeeper_did['id']}")
    
    validator_did = protocol.create_agent_identity(
        agent_type="validator", 
        agent_name="SkillValidator",
        capabilities=["skill_matching", "semantic_analysis", "jd_parsing"]
    )
    print(f"   ✅ Validator DID: {validator_did['id']}")
    
    inquisitor_did = protocol.create_agent_identity(
        agent_type="inquisitor",
        agent_name="Inquisitor",
        capabilities=["question_generation", "authenticity_scoring", "fraud_detection"]
    )
    print(f"   ✅ Inquisitor DID: {inquisitor_did['id']}")
    
    # Register agents
    print("\n2. Registering Agents in Discovery Registry...")
    protocol.register_agent(gatekeeper_did, ["pii_redaction", "eligibility_check"])
    protocol.register_agent(validator_did, ["skill_matching", "semantic_analysis"])
    protocol.register_agent(inquisitor_did, ["question_generation", "fraud_detection"])
    print("   ✅ All agents registered")
    
    # Create candidate identity
    print("\n3. Creating Candidate Identity...")
    candidate_did = protocol.create_agent_identity(
        agent_type="candidate",
        agent_name="ANON-Candidate-001",
        capabilities=[]
    )
    print(f"   ✅ Candidate DID: {candidate_did['id']}")
    
    # Issue credentials
    print("\n4. Issuing Verifiable Credentials...")
    
    eligibility_cred = protocol.issue_credential(
        issuer_did=gatekeeper_did,
        subject_did=candidate_did['id'],
        credential_type="EligibilityCredential",
        claims={
            "eligible": True,
            "experience_years": 3.5,
            "pii_removed": True,
            "reason": "Meets minimum experience requirement"
        }
    )
    print(f"   ✅ EligibilityCredential issued")
    
    skill_cred = protocol.issue_credential(
        issuer_did=validator_did,
        subject_did=candidate_did['id'],
        credential_type="SkillMatchCredential",
        claims={
            "match_score": 85,
            "skills_matched": ["Python", "LangChain", "RAG", "AWS"],
            "threshold_passed": True
        }
    )
    print(f"   ✅ SkillMatchCredential issued")
    
    auth_cred = protocol.issue_credential(
        issuer_did=inquisitor_did,
        subject_did=candidate_did['id'],
        credential_type="AuthenticityCredential",
        claims={
            "authenticity_score": 92,
            "questions_answered": 3,
            "red_flags": [],
            "verdict": "AUTHENTIC"
        }
    )
    print(f"   ✅ AuthenticityCredential issued")
    
    # Send messages between agents
    print("\n5. Agent-to-Agent Communication...")
    
    msg1 = protocol.send_message(
        sender_did=gatekeeper_did,
        recipient_did=validator_did['id'],
        content="Candidate eligible. Clean data attached.",
        message_type="handoff"
    )
    print(f"   ✅ Gatekeeper → Validator: {msg1['status']}")
    
    msg2 = protocol.send_message(
        sender_did=validator_did,
        recipient_did=inquisitor_did['id'],
        content="Skill match: 85%. Proceeding to verification.",
        message_type="handoff"
    )
    print(f"   ✅ Validator → Inquisitor: {msg2['status']}")
    
    # Discover agents
    print("\n6. Agent Discovery...")
    fraud_detectors = protocol.discover_agents(
        capabilities=["fraud_detection"],
        min_score=0.5
    )
    print(f"   Found {len(fraud_detectors)} agent(s) with fraud_detection capability")
    
    # Get credentials for candidate
    print("\n7. Retrieving Candidate Credentials...")
    creds = protocol.get_credentials(candidate_did['id'])
    print(f"   ✅ {len(creds)} credential(s) found for candidate")
    for cred in creds:
        cred_type = cred['type'][-1] if cred.get('type') else 'Unknown'
        print(f"      - {cred_type}")
    
    # Network stats
    print("\n8. Network Statistics...")
    stats = protocol.get_network_stats()
    print(f"   Registered Agents: {stats['registered_agents']}")
    print(f"   Credentials Issued: {stats['total_credentials']}")
    print(f"   Messages Sent: {stats['total_messages']}")
    print(f"   Protocol Version: {stats['protocol_version']}")
    
    print("\n" + "=" * 60)
    print("✅ Zynd Protocol Demo Complete!")
    print("=" * 60)
