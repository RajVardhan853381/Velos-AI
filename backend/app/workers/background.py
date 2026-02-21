from fastapi import BackgroundTasks
import asyncio
from typing import Callable, Any

# Rather than a full robust queue like Celery that needs Redis
# We provide a wrapper for BackgroundTasks that can orchestrate async execution

class BackgroundWorker:
    """
    Background worker orchestrator built on FastAPI's BackgroundTasks.
    For $0 scale. Can run simple awaitables without holding the request cycle.
    """
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    def dispatch(self, func: Callable, *args: Any, **kwargs: Any):
        """Dispatches a task to FastAPI BackgroundTasks pool."""
        self.background_tasks.add_task(func, *args, **kwargs)

async def example_pipeline_run(candidate_id: str):
    """Example simulated task for AI pipeline evaluation lifecycle"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Pipeline started for {candidate_id}")
    await asyncio.sleep(2)
    logger.info(f"Agent 1 passed for {candidate_id}")
    await asyncio.sleep(2)
    logger.info(f"Pipeline finished for {candidate_id}")
