from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.services import WithdrawalService
from app.domain.exceptions import InsufficientFundsError
from app.infrastructure.repository import InMemoryAccountRepository
from app.infrastructure.event_bus import InMemoryEventPublisher
from app.schemas.withdrawal import WithdrawalRequest


@pytest.fixture
def service():
    repo = InMemoryAccountRepository()
    publisher = InMemoryEventPublisher()
    return WithdrawalService(repository=repo, event_publisher=publisher)

def make_request(account_id: str, amount: str) -> WithdrawalRequest:
    return WithdrawalRequest(
        account_id=account_id,
        amount=Decimal(amount),
        correlation_id=uuid4(),
    )

def test_successful_withdrawal(service):
    request = make_request("1234567890", "200.00")
    event = service.withdraw(request)

    assert event.account_id == "1234567890"
    assert event.amount == Decimal("200.00")
    assert event.new_balance == Decimal("800.00")
    assert service.repository.get_account("1234567890").balance == Decimal("800.00")

def test_withdrawal_exact_balance(service):
    request = make_request("0987654321", "500.00")
    event = service.withdraw(request)

    assert event.amount == Decimal("500.00")
    assert event.new_balance == Decimal("0.00")
    assert service.repository.get_account("0987654321").balance == Decimal("0.00")

def test_withdrawal_insufficient_funds(service):
    request = make_request("1234567890", "2000.00")
    with pytest.raises(InsufficientFundsError):
        service.withdraw(request)

def test_withdrawal_account_not_found(service):
    request = make_request("9999999999", "50.00")
    with pytest.raises(ValueError, match="Account not found"):
        service.withdraw(request)

def test_event_publisher_called(service):
    request = make_request("1234567890", "100.00")
    event = service.withdraw(request)

    assert len(service.event_publisher.events) == 1
    published_event = service.event_publisher.events[0]
    assert published_event.account_id == "1234567890"
    assert published_event.amount == Decimal("100.00")
    assert published_event.new_balance == Decimal("900.00")
