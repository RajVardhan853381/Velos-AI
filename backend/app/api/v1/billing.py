import os
from fastapi import APIRouter, Depends, HTTPException, Request

router = APIRouter()

class PlanLimits:
    FREE = {"runs": 25, "users": 2, "storage_mb": 100}
    STARTER = {"runs": 250, "users": 10, "storage_mb": 1024}
    PRO = {"runs": 2500, "users": 50, "storage_mb": 10240}
    
    @classmethod
    def enforce_usage_limits(cls, org_plan: str, metrics: dict):
        """Hard validation against plan limits to avoid runaway free-tier costs."""
        plan = getattr(cls, org_plan.upper(), cls.FREE)
        if metrics.get("runs", 0) >= plan["runs"]:
            raise HTTPException(402, "Monthly pipeline run limit reached. Please upgrade plan.")

# Stripe Stub Initialization
@router.post("/create-checkout")
async def create_checkout_session(request: Request):
    """
    $0 Zero Cost implementation: Stripe creates zero structural cost until usage.
    However, we return 'coming soon' during the Free Tier scale out phase to defer complexity.
    """
    # Verify User logic placeholder
    return {
        "status": "coming_soon",
        "message": "Payment system disabled as everyone is on the Free trial tier.",
        "url": None
    }

@router.get("/usage")
async def get_usage_stats(request: Request):
    """
    Returns the metric limit stats consumed by the Org to display in UI.
    """
    # Fetch from DB usage_records
    return {
        "plan": "FREE",
        "runs": {
            "used": 4, # mock
            "limit": PlanLimits.FREE["runs"]
        },
        "storage_mb": {
            "used": 1.2, # mock
            "limit": PlanLimits.FREE["storage_mb"] 
        }
    }
