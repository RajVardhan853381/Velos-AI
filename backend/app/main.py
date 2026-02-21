from contextlib import asynccontextmanager
from fastapi import FastAPI
import sys
import os

from backend.app.config import settings
from backend.app.core.middleware import setup_middlewares
from backend.app.core.exceptions import setup_exception_handlers
from backend.app.api.router import api_router

# Adjust python path to be able to import from root when running
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Events
    print(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode.")
    # Initialize DB connection pool (Phase 2)
    # Initialize Orchestrator/Agents (from server.py)
    
    yield
    
    # Shutdown Events
    print(f"Shutting down {settings.PROJECT_NAME}.")
    # Close DB connections and cleanup

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Decentralized Blind Hiring Platform - Enterprise SaaS Edition",
        lifespan=lifespan,
    )
    
    # Setup middlewares & exceptions
    setup_middlewares(app)
    setup_exception_handlers(app)
    
    # Mount V1 Routes
    app.include_router(api_router, prefix="/api")
    
    # Load v0 deprecated aliases from the existing prototype 
    # to guarantee zero breakage for the frontend.
    try:
        from server import app as prototype_app
        # We can either mount the prototype or include its router
        # By including its routes, we merge them into the new app
        for route in prototype_app.routes:
            app.router.routes.append(route)
        print("Successfully merged v0 prototype routes.")
    except ImportError as e:
        print(f"Warning: Could not import prototype routes. {e}")
        
    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:create_app", host="0.0.0.0", port=8000, reload=True, factory=True)
