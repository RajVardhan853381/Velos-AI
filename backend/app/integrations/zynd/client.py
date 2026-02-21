import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ZyndClient:
    """
    Base asynchronous HTTP client for the Zynd Protocol API.
    Handles authentication, retries, and rate-limiting.
    """
    def __init__(self, api_key: str, base_url: str = "https://api.zynd.io/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def _request(
        self, method: str, endpoint: str, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None, max_retries: int = 3
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            for attempt in range(max_retries):
                try:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=self.headers,
                        json=json_data,
                        params=params,
                        timeout=15.0
                    )
                    
                    if response.status_code == 429:
                        logger.warning(f"Zynd API rate limit hit. Retrying {attempt+1}/{max_retries}")
                        import asyncio
                        await asyncio.sleep(2 ** attempt)
                        continue
                        
                    response.raise_for_status()
                    return response.json()
                
                except httpx.HTTPStatusError as e:
                    logger.error(f"Zynd HTTP error on {method} {endpoint}: {e.response.text}")
                    raise
                except httpx.RequestError as e:
                    logger.error(f"Zynd Request error on {method} {endpoint}: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                    
        raise RuntimeError(f"Failed to execute Zynd API request after {max_retries} attempts.")

from backend.app.config import settings

zynd_client_instance = None

def get_zynd_client(api_key: Optional[str] = None) -> ZyndClient:
    global zynd_client_instance
    if not zynd_client_instance:
         # Use the explicit key, or fallback to the .env settings key
         resolved_key = api_key or settings.ZYND_API_KEY
         zynd_client_instance = ZyndClient(api_key=resolved_key)
    return zynd_client_instance
