import hmac
import hashlib
import httpx
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

async def dispatch_webhook(
    url: str, 
    secret: str, 
    event_type: str, 
    payload: Dict[str, Any], 
    max_retries: int = 3
):
    """
    Enterprise Webhook Dispatcher ($0 Cost using asyncio BackgroundTasks).
    Includes HMAC-SHA256 signatures for security and exponential backoff retries.
    """
    body = json.dumps({"event": event_type, "data": payload}).encode('utf-8')
    
    # Calculate Signature
    signature = hmac.new(
        key=secret.encode('utf-8'),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Velos-Signature": f"sha256={signature}",
        "X-Velos-Event": event_type
    }
    
    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(url, content=body, headers=headers, timeout=10.0)
                if response.status_code < 400:
                    logger.info(f"Webhook {event_type} delivered to {url}")
                    return True
                
                logger.warning(f"Webhook {url} returned {response.status_code}. Retrying...")
            except Exception as e:
                logger.warning(f"Webhook delivery failed: {e}")
                
            # Exponential backoff (2^attempt seconds)
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep(2 ** attempt)
                
    logger.error(f"Webhook {event_type} to {url} failed after {max_retries} attempts.")
    return False
