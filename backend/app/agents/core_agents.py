import logging
import asyncio
import uuid
from typing import Dict, Any, Optional
from backend.app.services.llm_client import llm_client
from backend.app.agents.orchestrator import (
    AgentMessage, AgentType, orchestrator
)

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        orchestrator.register_agent(self.agent_type, self)

    async def send_message(self, receiver: AgentType, intent: str, payload: Dict[str, Any]):
        msg = AgentMessage(
            id=uuid.uuid4().hex,
            sender=self.agent_type,
            receiver=receiver,
            intent=intent,
            payload=payload
        )
        await orchestrator.dispatch(msg)

    async def handle_message(self, message: AgentMessage):
        """Override this in specific agents to handle incoming orchestrator payloads."""
        pass


class GatekeeperAgent(BaseAgent):
    """Stage 1: Extracts PII, redacts it, and verifies baseline eligibility."""
    def __init__(self):
        super().__init__(AgentType.GATEKEEPER)

    async def handle_message(self, message: AgentMessage):
        if message.intent == "start_screening":
            candidate_id = message.payload.get("candidate_id")
            logger.info(f"Gatekeeper redacting PII for {candidate_id}")
            # Mock delay representing PII removal & parsing
            await asyncio.sleep(1)
            
            # Pass to Validator
            await self.send_message(
                AgentType.VALIDATOR, 
                "validate_skills", 
                {"candidate_id": candidate_id, "anonymized_resume": "Mock Redacted Resume Text"}
            )


class SkillValidatorAgent(BaseAgent):
    """Stage 2: Compares anonymized resume against Job Description."""
    def __init__(self):
        super().__init__(AgentType.VALIDATOR)

    async def handle_message(self, message: AgentMessage):
        if message.intent == "validate_skills":
            candidate_id = message.payload.get("candidate_id")
            logger.info(f"SkillValidator assessing {candidate_id}")
            
            # Simulate heavy LLM operations
            await asyncio.sleep(2)
            match_score = 85.0 # Mocked for compilation
            
            # Pass to Inquisitor
            await self.send_message(
                AgentType.INQUISITOR,
                "deep_analysis",
                {"candidate_id": candidate_id, "match_score": match_score}
            )
            
        elif message.intent == "negotiate_score":
            candidate_id = message.payload.get("candidate_id")
            inquisitor_score = message.payload.get("trust_score")
            logger.warning(f"Validator negotiating score for {candidate_id}. Inquisitor gave: {inquisitor_score}")
            # In a real app, this re-prompts the LLM with the Inquisitor's context
            await asyncio.sleep(1)
            
            # Request Auditor review
            await self.send_message(
                AgentType.AUDITOR,
                "audit_conflict",
                {"candidate_id": candidate_id, "resolved_score": (85.0 + inquisitor_score) / 2}
            )


class InquisitorAgent(BaseAgent):
    """Stage 3: Analyzes claims, detects fraud via LLM probing."""
    def __init__(self):
        super().__init__(AgentType.INQUISITOR)

    async def handle_message(self, message: AgentMessage):
        if message.intent == "deep_analysis":
            candidate_id = message.payload.get("candidate_id")
            match_score = message.payload.get("match_score")
            logger.info(f"Inquisitor probing {candidate_id} built logic...")
            
            await asyncio.sleep(1)
            trust_score = 60.0 # Intentionally low to trigger negotiation
            
            if abs(match_score - trust_score) > 20:
                logger.warning(f"Discrepancy detected! Match {match_score} vs Trust {trust_score}.")
                await self.send_message(
                    AgentType.VALIDATOR,
                    "negotiate_score",
                    {"candidate_id": candidate_id, "trust_score": trust_score}
                )
            else:
                await self.send_message(
                    AgentType.PUBLISHER,
                    "publish_credential",
                    {"candidate_id": candidate_id, "trust_score": trust_score, "match_score": match_score}
                )

# Initialize singletons to bind to Orchestrator memory bus
gatekeeper = GatekeeperAgent()
skill_validator = SkillValidatorAgent()
inquisitor = InquisitorAgent()
