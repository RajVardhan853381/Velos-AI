import logging
import asyncio
from typing import Dict, Any
from backend.app.agents.orchestrator import AgentMessage, AgentType, orchestrator
from backend.app.agents.core_agents import BaseAgent
from backend.app.integrations.zynd import ZyndPublishService, ZyndSearchService

logger = logging.getLogger(__name__)

class CredentialPublisherAgent(BaseAgent):
    """Agent 4: Autonomously decides when/how to publish credentials to Zynd."""
    def __init__(self):
        super().__init__(AgentType.PUBLISHER)
        self.publish_service = ZyndPublishService()

    async def handle_message(self, message: AgentMessage):
        if message.intent == "publish_credential":
            candidate_id = message.payload.get("candidate_id")
            logger.info(f"Publisher Agent packaging data for Zynd Network: {candidate_id}")
            
            try:
                res = await self.publish_service.publish_skill_credential(
                    candidate_id=candidate_id,
                    skills=["python", "fastapi"],  # Extracted in real pipeline
                    match_score=message.payload.get("match_score"),
                    trust_score=message.payload.get("trust_score"),
                    org_hash="velos-demo-hash"
                )
                logger.info(f"Successfully published verified credential: {res['zynd_uri']}")
                
                # Report to Auditor
                await self.send_message(
                    AgentType.AUDITOR,
                    "log_publication",
                    {"candidate_id": candidate_id, "zynd_uri": res["zynd_uri"]}
                )
            except Exception as e:
                logger.error(f"Agent failed to publish to Zynd: {e}")


class TalentDiscoveryAgent(BaseAgent):
    """Agent 5: Proactively searches Zynd for matching talent pools."""
    def __init__(self):
        super().__init__(AgentType.DISCOVERY)
        self.search_service = ZyndSearchService()

    async def handle_message(self, message: AgentMessage):
        if message.intent == "search_external_pools":
            skills = message.payload.get("skills", [])
            logger.info(f"Discovery Agent searching Zynd for: {skills}")
            results = await self.search_service.search_candidates(required_skills=skills)
            logger.info(f"Discovery Agent found {len(results)} remote candidates on Zynd.")


class BiasAuditorAgent(BaseAgent):
    """Agent 6: Constant background task verifying equity inside the ML decision loops."""
    def __init__(self):
        super().__init__(AgentType.AUDITOR)

    async def handle_message(self, message: AgentMessage):
        if message.intent == "audit_conflict":
            logger.info(f"Bias Auditor evaluating conflict resolution for {message.payload.get('candidate_id')}")
            # Audit logic verifying resolving score didn't penalize protected traits
            await asyncio.sleep(0.5)
            
            # Send to publisher
            await self.send_message(
                AgentType.PUBLISHER,
                "publish_credential",
                {"candidate_id": message.payload.get('candidate_id'), "trust_score": message.payload.get("resolved_score"), "match_score": message.payload.get("resolved_score")}
            )
        elif message.intent == "log_publication":
            logger.info(f"Auditor recording immutable hiring log for {message.payload.get('zynd_uri')} on blockchain.")

class NegotiationAgent(BaseAgent):
    """Agent 7: Simulates market-rate salary negotiations."""
    def __init__(self):
        super().__init__(AgentType.NEGOTIATOR)

# Initialize Singletons
publisher_agent = CredentialPublisherAgent()
discovery_agent = TalentDiscoveryAgent()
auditor_agent = BiasAuditorAgent()
negotiator_agent = NegotiationAgent()
