import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check_returns_successfully(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data
    assert data["checks"]["database"]["status"] == "ok"

@pytest.mark.asyncio
async def test_metrics_endpoint_returns_data(client: AsyncClient):
    response = await client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "requests_processed" in response.json()
