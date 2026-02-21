import pytest
import asyncio
from backend.app.agents.orchestrator import AgentOrchestrator, AgentMessage, AgentType
from backend.app.agents.core_agents import BaseAgent

class DummyAgent(BaseAgent):
    def __init__(self, agent_type: AgentType, orchestrator_instance: AgentOrchestrator):
        self.agent_type = agent_type
        self.received_messages = []
        orchestrator_instance.register_agent(agent_type, self)
        self.orchestrator = orchestrator_instance

    async def handle_message(self, message: AgentMessage):
        self.received_messages.append(message)

@pytest.mark.asyncio
async def test_agent_orchestrator_message_routing():
    test_orchestrator = AgentOrchestrator()
    
    # We use GATEKEEPER and INQUISITOR just for enum validity
    sender = DummyAgent(AgentType.GATEKEEPER, test_orchestrator)
    receiver = DummyAgent(AgentType.INQUISITOR, test_orchestrator)
    
    # Start the event loop briefly
    task = asyncio.create_task(test_orchestrator.start_listening())
    
    # Dispatch
    msg = AgentMessage(
        id="test-msg",
        sender=AgentType.GATEKEEPER,
        receiver=AgentType.INQUISITOR,
        intent="ping",
        payload={"data": "hello"}
    )
    
    await test_orchestrator.dispatch(msg)
    
    # Allow event loop to process
    await asyncio.sleep(0.1)
    test_orchestrator.stop()
    await task
    
    assert len(receiver.received_messages) == 1
    assert receiver.received_messages[0].intent == "ping"
    assert receiver.received_messages[0].payload["data"] == "hello"

@pytest.mark.asyncio
async def test_agent_orchestrator_drops_unregistered_receivers(caplog):
    test_orchestrator = AgentOrchestrator()
    sender = DummyAgent(AgentType.GATEKEEPER, test_orchestrator)
    
    # Receiver not registered!
    task = asyncio.create_task(test_orchestrator.start_listening())
    
    msg = AgentMessage(
        id="test-msg-drop",
        sender=AgentType.GATEKEEPER,
        receiver=AgentType.INQUISITOR,
        intent="ping",
        payload={}
    )
    await test_orchestrator.dispatch(msg)
    await asyncio.sleep(0.1)
    
    test_orchestrator.stop()
    await task
    
    assert "not registered" in caplog.text
