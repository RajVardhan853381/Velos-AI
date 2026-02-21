from fastapi import APIRouter
from backend.app.api.v1 import auth, health, billing, webhooks, dashboard

api_router = APIRouter()

# Register V1 Endpoints (Phase 1 placeholders)
v1_router = APIRouter()
v1_router.include_router(health.router, tags=["Health"])
v1_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
v1_router.include_router(billing.router, prefix="/billing", tags=["Monetization"])
v1_router.include_router(webhooks.router, prefix="/webhooks", tags=["Enterprise Integration"])
v1_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard Visibility"])

api_router.include_router(v1_router, prefix="/v1")

# Legacy V0 Prototype Aliases - Keep old prototype routes functional
# This will be populated by including the old server.py endpoints via main.py
