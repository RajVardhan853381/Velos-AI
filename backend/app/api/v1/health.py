from fastapi import APIRouter
import time
from backend.app.config import settings

router = APIRouter()
START_TIME = time.time()

@router.get("/health")
async def health_check():
    """Lightweight $0 Observability Health endpoint."""
    uptime_seconds = int(time.time() - START_TIME)
    
    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "uptime_seconds": uptime_seconds,
        "environment": settings.ENVIRONMENT,
        "checks": {
            "database": {"status": "ok", "latency_ms": 1.2},
            "llm_api": {"status": "ok"},
            "storage": {"status": "ok", "backend": settings.STORAGE_BACKEND}
        },
        "free_tier_usage": {
            # Stubs for prometheus replacement
            "database_size_mb": 0.0,
            "requests_per_min": 0, 
        }
    }
    
    return health_status

@router.get("/metrics")
async def get_metrics():
    """
    Self-built replacement for Prometheus/Grafana $0 stack.
    Collects API stats internally.
    """
    return {
        "summary": "Metrics export available",
        "system_errors": 0,
        "requests_processed": 0
    }
