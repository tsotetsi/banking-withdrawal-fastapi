from decimal import Decimal
from uuid import uuid4

from fastapi import status
from httpx import AsyncClient, ASGITransport
import pytest

from app.main import app
from app.api.v1.withdrawal import reset_mock_accounts


@pytest.fixture(autouse=True)
def setup_test_data():
    """Reset mock data before each test."""
    reset_mock_accounts()
    yield
    # Clean up after test.
    reset_mock_accounts()

@pytest.fixture
async def async_client():
    """Reusable async client fixture."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client

@pytest.mark.asyncio
async def test_withdrawal_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        correlation_id = str(uuid4())
        payload = {
            "account_id": "1234567890",
            "amount": "200.50",
            "correlation_id": correlation_id,
        }
        response = await ac.post("/api/v1/withdrawal", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "transaction_id" in data
    assert data["account_id"] == payload["account_id"]
    assert data["amount"] == payload["amount"]
    assert "balance" in data
    assert data["correlation_id"] == payload["correlation_id"]
    assert Decimal(data["balance"]) == Decimal("799.50")

@pytest.mark.asyncio
async def test_withdrawal_insufficient_funds():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        correlation_id = str(uuid4())
        payload = {
            "account_id": "1234567890",
            "amount": "2000.00",  # larger than mock balance of 1000.00
            "correlation_id": correlation_id,
        }
        response = await ac.post("/api/v1/withdrawal", json=payload)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"] == "Insufficient funds."

@pytest.mark.asyncio
async def test_withdrawal_account_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        correlation_id = str(uuid4())
        payload = {
            "account_id": "9999999999",  # non-existent account
            "amount": "50.00",
            "correlation_id": correlation_id,
        }
        response = await ac.post("/api/v1/withdrawal", json=payload)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Account not found."

@pytest.mark.asyncio
async def test_withdrawal_zero_balance_account():
    """Test withdrawal from account with zero balance."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        correlation_id = str(uuid4())
        payload = {
            "account_id": "1111111111",  # account with 0.00 balance
            "amount": "10.00",
            "correlation_id": correlation_id,
        }
        response = await ac.post("/api/v1/withdrawal", json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Insufficient funds."


@pytest.mark.asyncio
async def test_withdrawal_exact_balance():
    """Test withdrawal of exact account balance."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        correlation_id = str(uuid4())
        payload = {
            "account_id": "0987654321",  # account with 500.00 balance
            "amount": "500.00",
            "correlation_id": correlation_id,
        }
        response = await ac.post("/api/v1/withdrawal", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert Decimal(data["balance"]) == Decimal("0.00")


@pytest.mark.asyncio
async def test_withdrawal_success_with_fixture(async_client):
    correlation_id = str(uuid4())
    payload = {
        "account_id": "1234567890",
        "amount": "100.00",
        "correlation_id": correlation_id,
    }
    response = await async_client.post("/api/v1/withdrawal", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "transaction_id" in data
    assert data["account_id"] == payload["account_id"]
    assert data["amount"] == payload["amount"]
    assert Decimal(data["balance"]) == Decimal("900.00")


@pytest.mark.asyncio
async def test_multiple_withdrawals_update_balance(async_client):
    """Test that multiple withdrawals properly update the balance."""
    correlation_id1 = str(uuid4())
    correlation_id2 = str(uuid4())
    
    # First withdrawal
    payload1 = {
        "account_id": "1234567890",
        "amount": "300.00",
        "correlation_id": correlation_id1,
    }
    response1 = await async_client.post("/api/v1/withdrawal", json=payload1)
    assert response1.status_code == status.HTTP_200_OK
    data1 = response1.json()
    assert Decimal(data1["balance"]) == Decimal("700.00")
    
    # Second withdrawal
    payload2 = {
        "account_id": "1234567890",
        "amount": "200.00",
        "correlation_id": correlation_id2,
    }
    response2 = await async_client.post("/api/v1/withdrawal", json=payload2)
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()
    assert Decimal(data2["balance"]) == Decimal("500.00")