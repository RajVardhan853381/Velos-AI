import pytest
import os
from unittest.mock import AsyncMock, patch
from backend.app.integrations.zynd import (
    ZyndSearchService, ZyndPublishService, ZyndPayService
)

@pytest.mark.asyncio
async def test_zynd_publish_credential():
    publisher = ZyndPublishService()
    candidate_id = "test-candidate-1"
    
    # We test the mock responses baked in for the hackathon
    res = await publisher.publish_skill_credential(
        candidate_id, ["python"], 95.0, 90.0, "org-hash"
    )
    assert res["status"] == "success"
    assert "zynd://" in res["zynd_uri"]

@pytest.mark.asyncio
async def test_zynd_talent_search():
    searcher = ZyndSearchService()
    results = await searcher.search_candidates(
        required_skills=["fastapi", "docker"], limit=3
    )
    
    # Randomly mocked inside implementation to return 2-3 items
    assert len(results) >= 2
    assert "zynd_did" in results[0]
    assert results[0]["trust_score"] >= 80.0

@pytest.mark.asyncio
async def test_zynd_payment_invoice_generation():
    payer = ZyndPayService()
    invoice = await payer.create_premium_credential_invoice(
        candidate_did="did:zynd:test-user", amount_usd=10.0
    )
    
    assert invoice["status"] == "pending"
    assert "pay.zynd.io" in invoice["payment_url"]
    
@pytest.mark.asyncio
async def test_zynd_payment_verification():
    payer = ZyndPayService()
    status = await payer.verify_payment_status("inv_test")
    assert status == "paid"
