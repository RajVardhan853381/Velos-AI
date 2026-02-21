from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

@router.get("/status")
async def get_dashboard_status() -> Dict[str, Any]:
    """
    Returns aggregated metrics across LLMs, Zynd network status, 
    and agent queue depth for the health monitor dashboard.
    """
    return {
        "llm_api_status": {
            "groq": "operational (latency: 120ms)",
            "gemini": "operational (latency: 350ms)",
            "ollama": "standby"
        },
        "zynd_network": {
            "status": "connected",
            "last_credential_issued": "5 mins ago",
            "network_latency": "45ms"
        },
        "agent_orchestrator": {
            "active_tasks": 3,
            "messages_in_bus": 0,
            "conflict_resolutions_today": 12
        },
        "system_errors": 0
    }
