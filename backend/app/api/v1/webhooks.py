from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import List

router = APIRouter()

class WebhookEndpointModel(BaseModel):
    url: str
    secret: str
    events: List[str]

@router.post("/endpoints")
async def register_webhook(webhook: WebhookEndpointModel, request: Request):
    """
    Registers a Webhook Endpoint for an Organization.
    Actual implementation stores in org DB. (Phase 13)
    """
    return {"message": "Webhook registered.", "id": "wh-mock-id"}

@router.delete("/endpoints/{id}")
async def delete_webhook(id: str, request: Request):
    return {"message": "Webhook removed."}
