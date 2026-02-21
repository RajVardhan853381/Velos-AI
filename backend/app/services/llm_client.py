import os
import time
import httpx
import logging
import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from backend.app.config import settings

logger = logging.getLogger(__name__)

class LLMResponse(BaseModel):
    content: str
    tokens_used: int
    provider: str
    duration_ms: int

class RateLimiter:
    """Token bucket rate limiter logic."""
    def __init__(self, rpm_limit: int):
        self.rpm_limit = rpm_limit
        self.tokens = rpm_limit
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        async with self.lock:
            now = time.time()
            # Refill logic
            time_passed = now - self.last_refill
            new_tokens = time_passed * (self.rpm_limit / 60.0)
            self.tokens = min(self.rpm_limit, self.tokens + new_tokens)
            self.last_refill = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

class LLMClient:
    """
    Abstract LLM Client managing failovers between $0 tier pipelines:
    1. Groq (Free: 30 RPM) -> Fastest.
    2. Gemini (Free: 60 RPM) -> Reliable Fallback.
    3. Ollama (Local: Unlimited) -> Last Resort Fallback.
    """
    def __init__(self):
        self.groq_limiter = RateLimiter(30)
        self.gemini_limiter = RateLimiter(60)
        
        self.clients = {
            "groq": httpx.AsyncClient(
                base_url="https://api.groq.com/openai/v1",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                timeout=30.0
            ),
            "gemini": httpx.AsyncClient(
                base_url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}",
                timeout=30.0
            ) if settings.GEMINI_API_KEY else None,
            "ollama": httpx.AsyncClient(
                base_url=f"{settings.OLLAMA_BASE_URL}/api",
                timeout=60.0
            )
        }

    async def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        start_time = time.time()
        
        # 1. Try Groq
        if await self.groq_limiter.acquire():
            try:
                result = await self._call_groq(prompt, system_prompt)
                return LLMResponse(**result, duration_ms=int((time.time() - start_time) * 1000))
            except Exception as e:
                logger.warning(f"Groq failed: {e}. Failing over to Gemini.")
        
        # 2. Try Gemini
        if self.clients["gemini"] and await self.gemini_limiter.acquire():
            try:
                result = await self._call_gemini(prompt, system_prompt)
                return LLMResponse(**result, duration_ms=int((time.time() - start_time) * 1000))
            except Exception as e:
                logger.warning(f"Gemini failed: {e}. Failing over to Ollama.")

        # 3. Try Ollama (No rate limit)
        try:
            result = await self._call_ollama(prompt, system_prompt)
            return LLMResponse(**result, duration_ms=int((time.time() - start_time) * 1000))
        except Exception as e:
            logger.error(f"All LLM providers failed. Last logic: {e}")
            raise RuntimeError("LLM Pipeline Exhausted.")

    async def _call_groq(self, prompt: str, system: str) -> Dict[str, Any]:
        response = await self.clients["groq"].post("/chat/completions", json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        })
        response.raise_for_status()
        data = response.json()
        return {
            "content": data["choices"][0]["message"]["content"],
            "tokens_used": data.get("usage", {}).get("total_tokens", 0),
            "provider": "groq"
        }

    async def _call_gemini(self, prompt: str, system: str) -> Dict[str, Any]:
        # Gemini specific payload
        payload = {
            "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}],
            "generationConfig": {"temperature": 0.1}
        }
        response = await self.clients["gemini"].post("", json=payload)
        response.raise_for_status()
        data = response.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        return {
            "content": content,
            "tokens_used": 0, # Requires parsing token metrics from response
            "provider": "gemini"
        }

    async def _call_ollama(self, prompt: str, system: str) -> Dict[str, Any]:
        response = await self.clients["ollama"].post("/generate", json={
            "model": "llama3",
            "prompt": f"{system}\n\n{prompt}",
            "stream": False,
            "options": {"temperature": 0.1}
        })
        response.raise_for_status()
        data = response.json()
        return {
            "content": data["response"],
            "tokens_used": data.get("eval_count", 0) + data.get("prompt_eval_count", 0),
            "provider": "ollama"
        }

    async def close(self):
        for client in self.clients.values():
            if client:
                await client.aclose()

llm_client = LLMClient()
