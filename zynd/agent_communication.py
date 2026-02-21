"""
ZeroMQ-based Agent Communication for Velos AI
Real-time, asynchronous P2P messaging between agents with DID authentication

Features:
- Async ZeroMQ pub/sub messaging
- DID-signed messages
- Message authentication
- Real-time event streaming for UI
- Message history and replay
"""

import zmq
import zmq.asyncio
import json
import asyncio
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from eth_account import Account
from eth_account.messages import encode_defunct


@dataclass
class AgentMessage:
    """
    Authenticated agent-to-agent message with DID signature.
    """
    message_id: str
    sender_did: str
    recipient_did: str
    message_type: str  # TASK_HANDOFF, CREDENTIAL_ISSUED, VERIFICATION_REQUEST, etc.
    content: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    signature: Optional[str] = None
    conversation_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentMessage':
        """Create from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentMessage':
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


class AgentCommunicationHub:
    """
    ZeroMQ-based communication hub for multi-agent coordination.
    
    Uses pub/sub pattern for scalable, real-time messaging.
    """
    
    # Message types
    TASK_HANDOFF = "TASK_HANDOFF"
    CREDENTIAL_ISSUED = "CREDENTIAL_ISSUED"
    VERIFICATION_REQUEST = "VERIFICATION_REQUEST"
    VERIFICATION_COMPLETE = "VERIFICATION_COMPLETE"
    AGENT_STATUS = "AGENT_STATUS"
    ERROR = "ERROR"
    
    def __init__(
        self,
        agent_id: str,
        agent_did: str,
        private_key: Optional[str] = None,
        publisher_port: int = 5555,
        subscriber_port: int = 5556
    ):
        """
        Initialize communication hub.
        
        Args:
            agent_id: Agent identifier
            agent_did: Agent's DID
            private_key: Ethereum private key for signing messages
            publisher_port: ZMQ publisher port
            subscriber_port: ZMQ subscriber port
        """
        self.agent_id = agent_id
        self.agent_did = agent_did
        
        # Setup Ethereum account for signing
        if private_key:
            self.account = Account.from_key(private_key)
        else:
            self.account = Account.create()
        
        # ZMQ setup
        self.context = zmq.asyncio.Context()
        self.publisher_port = publisher_port
        self.subscriber_port = subscriber_port
        
        # Publisher socket (sends messages)
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://*:{publisher_port}")
        
        # Subscriber socket (receives messages)
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(f"tcp://localhost:{subscriber_port}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all
        
        # Message history
        self.sent_messages: List[AgentMessage] = []
        self.received_messages: List[AgentMessage] = []
        
        # Callbacks for message handling
        self.message_handlers: Dict[str, List[Callable]] = {}
        
        # Running flag
        self.running = False
        
        print(f"📡 Agent Communication Hub initialized for {agent_id}")
        print(f"   Publisher: tcp://*:{publisher_port}")
        print(f"   Subscriber: tcp://localhost:{subscriber_port}")
    
    def _sign_message(self, message: AgentMessage) -> str:
        """
        Sign a message with Ethereum private key.
        
        Args:
            message: Message to sign
            
        Returns:
            Hex signature
        """
        # Create canonical message representation
        message_dict = message.to_dict()
        message_dict.pop('signature', None)  # Remove signature if exists
        canonical = json.dumps(message_dict, sort_keys=True)
        
        # Sign
        message_hash = encode_defunct(text=canonical)
        signed = Account.sign_message(message_hash, private_key=self.account.key)
        
        return signed.signature.hex()
    
    def _verify_signature(self, message: AgentMessage, expected_address: Optional[str] = None) -> bool:
        """
        Verify message signature.
        
        Args:
            message: Message to verify
            expected_address: Expected signer address (optional)
            
        Returns:
            True if signature is valid
        """
        if not message.signature:
            return False
        
        try:
            # Reconstruct signed message
            message_dict = message.to_dict()
            message_dict.pop('signature', None)
            canonical = json.dumps(message_dict, sort_keys=True)
            
            # Verify
            message_hash = encode_defunct(text=canonical)
            recovered_address = Account.recover_message(
                message_hash,
                signature=message.signature
            )
            
            # Check against expected address if provided
            if expected_address:
                return recovered_address.lower() == expected_address.lower()
            
            return True
            
        except Exception as e:
            print(f"❌ Signature verification failed: {e}")
            return False
    
    async def send_message(
        self,
        recipient_did: str,
        message_type: str,
        content: Dict[str, Any],
        conversation_id: Optional[str] = None,
        in_reply_to: Optional[str] = None
    ) -> AgentMessage:
        """
        Send authenticated message to another agent.
        
        Args:
            recipient_did: Recipient's DID
            message_type: Type of message
            content: Message content
            conversation_id: Conversation ID for threading
            in_reply_to: ID of message being replied to
            
        Returns:
            Sent message
        """
        # Generate message ID
        message_id = self._generate_message_id()
        
        # Create message
        message = AgentMessage(
            message_id=message_id,
            sender_did=self.agent_did,
            recipient_did=recipient_did,
            message_type=message_type,
            content=content,
            conversation_id=conversation_id,
            in_reply_to=in_reply_to
        )
        
        # Sign message
        message.signature = self._sign_message(message)
        
        # Publish via ZMQ
        await self.publisher.send_string(message.to_json())
        
        # Store in history
        self.sent_messages.append(message)
        
        # Trim history if too long
        if len(self.sent_messages) > 1000:
            self.sent_messages = self.sent_messages[-1000:]
        
        print(f"📤 Sent {message_type} message to {recipient_did[:20]}...")
        
        return message
    
    def send_message_sync(
        self,
        recipient_did: str,
        message_type: str,
        content: Dict[str, Any],
        conversation_id: Optional[str] = None,
        in_reply_to: Optional[str] = None
    ) -> 'AgentMessage':
        """
        Synchronous version of send_message.
        Skips ZMQ publish (not available in sync context) but stores in history.
        Used by the synchronous run_verification_pipeline().
        """
        message_id = self._generate_message_id()
        message = AgentMessage(
            message_id=message_id,
            sender_did=self.agent_did,
            recipient_did=recipient_did,
            message_type=message_type,
            content=content,
            conversation_id=conversation_id,
            in_reply_to=in_reply_to
        )
        message.signature = self._sign_message(message)
        # Store in history (ZMQ publish skipped in sync context)
        self.sent_messages.append(message)
        if len(self.sent_messages) > 1000:
            self.sent_messages = self.sent_messages[-1000:]
        print(f"📤 [sync] Sent {message_type} message to {recipient_did[:20]}...")
        return message

    async def receive_messages(self):
        """
        Async loop to receive and process incoming messages.
        Should run in background task.
        """
        self.running = True
        print(f"👂 Listening for messages on port {self.subscriber_port}...")
        
        while self.running:
            try:
                # Receive message (non-blocking with timeout)
                if await self.subscriber.poll(timeout=100):  # 100ms timeout
                    message_json = await self.subscriber.recv_string()
                    
                    # Parse message
                    message = AgentMessage.from_json(message_json)
                    
                    # Verify signature
                    if not self._verify_signature(message):
                        print(f"⚠️ Invalid signature on message {message.message_id}")
                        continue
                    
                    # Store in history
                    self.received_messages.append(message)
                    
                    # Trim history
                    if len(self.received_messages) > 1000:
                        self.received_messages = self.received_messages[-1000:]
                    
                    print(f"📥 Received {message.message_type} from {message.sender_did[:20]}...")
                    
                    # Trigger handlers
                    await self._handle_message(message)
                
                else:
                    # No message, yield control
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                print(f"❌ Error receiving message: {e}")
                await asyncio.sleep(0.1)
    
    async def _handle_message(self, message: AgentMessage):
        """
        Handle received message by calling registered handlers.
        
        Args:
            message: Received message
        """
        handlers = self.message_handlers.get(message.message_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                print(f"❌ Handler error for {message.message_type}: {e}")
    
    def on_message(self, message_type: str, handler: Callable):
        """
        Register a message handler.
        
        Args:
            message_type: Type of message to handle
            handler: Callback function (can be async)
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        
        self.message_handlers[message_type].append(handler)
        print(f"✅ Registered handler for {message_type}")
    
    def stop(self):
        """Stop the communication hub."""
        self.running = False
        self.publisher.close()
        self.subscriber.close()
        self.context.term()
        print(f"🛑 Communication hub stopped for {self.agent_id}")
    
    def get_message_history(self, limit: int = 100) -> Dict[str, List[Dict]]:
        """
        Get message history.
        
        Args:
            limit: Max messages to return
            
        Returns:
            Dict with sent and received messages
        """
        sent_dicts = []
        for msg in self.sent_messages[-limit:]:
            if hasattr(msg, "to_dict"):
                sent_dicts.append(msg.to_dict())
            elif isinstance(msg, dict):
                sent_dicts.append(msg)
            else:
                sent_dicts.append({"message": str(msg)})
                
        recv_dicts = []
        for msg in self.received_messages[-limit:]:
            if hasattr(msg, "to_dict"):
                recv_dicts.append(msg.to_dict())
            elif isinstance(msg, dict):
                recv_dicts.append(msg)
            else:
                recv_dicts.append({"message": str(msg)})
                
        return {
            "sent": sent_dicts,
            "received": recv_dicts
        }
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID."""
        unique_str = f"{self.agent_did}:{datetime.now().isoformat()}"
        message_hash = hashlib.sha256(unique_str.encode()).hexdigest()[:16]
        return f"msg:{message_hash}"


# Quick test
if __name__ == "__main__":
    print("🧪 Testing Agent Communication Hub\n")
    
    async def test_communication():
        # Create two agents
        agent1 = AgentCommunicationHub(
            agent_id="agent1_gatekeeper",
            agent_did="did:ethr:optimism-sepolia:0x111",
            publisher_port=5555,
            subscriber_port=5556
        )
        
        agent2 = AgentCommunicationHub(
            agent_id="agent2_validator",
            agent_did="did:ethr:optimism-sepolia:0x222",
            publisher_port=5556,
            subscriber_port=5555
        )
        
        # Register message handler for agent2
        def handle_task_handoff(message: AgentMessage):
            print(f"\n✅ Agent 2 received task handoff:")
            print(f"   Content: {message.content}")
        
        agent2.on_message(AgentCommunicationHub.TASK_HANDOFF, handle_task_handoff)
        
        # Start agent2 receiver in background
        receiver_task = asyncio.create_task(agent2.receive_messages())
        
        # Give subscriber time to connect
        await asyncio.sleep(0.5)
        
        # Agent1 sends message to Agent2
        print("\n📤 Agent 1 sending task handoff to Agent 2...")
        await agent1.send_message(
            recipient_did="did:ethr:optimism-sepolia:0x222",
            message_type=AgentCommunicationHub.TASK_HANDOFF,
            content={
                "candidate_id": "CAND-ABC123",
                "task": "skill_validation",
                "eligibility_credential_id": "cred:elig:001"
            }
        )
        
        # Wait for message to be received
        await asyncio.sleep(1)
        
        # Check history
        print("\n📊 Agent 1 message history:")
        history = agent1.get_message_history()
        print(f"   Sent: {len(history['sent'])} messages")
        
        print("\n📊 Agent 2 message history:")
        history = agent2.get_message_history()
        print(f"   Received: {len(history['received'])} messages")
        
        # Cleanup
        agent2.stop()
        receiver_task.cancel()
        agent1.stop()
        
        print("\n✅ Communication test completed!")
    
    # Run test
    asyncio.run(test_communication())
