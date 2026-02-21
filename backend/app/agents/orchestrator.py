from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class AgentType(str, Enum):
    GATEKEEPER = "Gatekeeper"
    VALIDATOR = "SkillValidator"
    INQUISITOR = "Inquisitor"
    PUBLISHER = "CredentialPublisher"
    DISCOVERY = "TalentDiscovery"
    AUDITOR = "BiasAuditor"
    NEGOTIATOR = "NegotiationAgent"
    ORCHESTRATOR = "Orchestrator"

class AgentMessage(BaseModel):
    id: str
    sender: AgentType
    receiver: AgentType
    intent: str  # e.g. "request_validation", "escalate_fraud", "negotiate_score"
    payload: Dict[str, Any]
    requires_response: bool = False
    
class AgentOrchestrator:
    """
    The central intelligence hub handling message passing and coordination 
    between autonomous agents.
    """
    def __init__(self):
        self.message_bus: asyncio.Queue = asyncio.Queue()
        self.agents: Dict[AgentType, Any] = {}
        self._running = False
        
    def register_agent(self, agent_type: AgentType, agent_instance: Any):
        self.agents[agent_type] = agent_instance
        logger.info(f"Registered Agent: {agent_type}")
        
    async def dispatch(self, message: AgentMessage):
        """Put a message onto the orchestrator's event bus."""
        await self.message_bus.put(message)
        logger.debug(f"Message dispatched from {message.sender} -> {message.receiver} (Intent: {message.intent})")

    async def start_listening(self):
        """Starts the main message parsing loop in the background."""
        self._running = True
        while self._running:
            try:
                msg: AgentMessage = await asyncio.wait_for(self.message_bus.get(), timeout=1.0)
                await self._route_message(msg)
                self.message_bus.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Orchestrator error routing message: {e}")

    async def _route_message(self, msg: AgentMessage):
        """Routes a message to the target agent for processing."""
        if msg.receiver in self.agents:
            target_agent = self.agents[msg.receiver]
            if hasattr(target_agent, 'handle_message'):
                # Fire and forget / background the agent processing to allow parallel evaluation
                asyncio.create_task(target_agent.handle_message(msg))
            else:
                logger.warning(f"Agent {msg.receiver} does not implement handle_message")
        else:
            logger.warning(f"Message dropped. Receiver {msg.receiver} not registered.")
            
    def stop(self):
        self._running = False

orchestrator = AgentOrchestrator()
