import pytest
from httpx import AsyncClient
from backend.app.main import create_app

@pytest.mark.asyncio
async def test_health_simple():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.get("/api/v1/health")
        assert res.status_code == 200
