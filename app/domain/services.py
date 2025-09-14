import structlog
from uuid import uuid4

from .models import WithdrawalEvent, WithdrawalStatus
from .exceptions import InsufficientFundsError
from app.schemas.withdrawal import WithdrawalRequest
from app.infrastructure.event_bus import get_event_publisher


logger = structlog.get_logger()


class WithdrawalService:
    """Service to handle withdrawal operations."""

    def __init__(self, repository, event_publisher):
        self.repository = repository
        self.event_publisher = event_publisher or get_event_publisher()

    def withdraw(self, withdrawal_request: WithdrawalRequest) -> WithdrawalEvent:
        """Process a withdrawal and send an event."""

        log = logger.bind(
            account_id=withdrawal_request.account_id,
            amount=str(withdrawal_request.amount),
            correlation_id=withdrawal_request.correlation_id,
        )

        account = self.repository.get_account(withdrawal_request.account_id)
        if not account:
            log.warning("account_not_found")
            raise ValueError("Account not found.")

        if account.balance < withdrawal_request.amount:
            log.warning("insufficient_funds", balance=account.balance)
            raise InsufficientFundsError("Insufficient funds.")

        account.balance -= withdrawal_request.amount
        self.repository.update_account(account)

        event = WithdrawalEvent(
            account_id=account.id,
            amount=withdrawal_request.amount,
            status=WithdrawalStatus.SUCCESSFUL,
            new_balance=account.balance,
        )

        log = log.bind(transaction_id=str(uuid4()))
        log.info("withdrawal_success", amount=str(event.amount), new_balance=str(event.new_balance))


        self.event_publisher.publish(event)
        return event
