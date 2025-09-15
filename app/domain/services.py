import uuid
from datetime import datetime, timezone
from uuid import uuid4
import time

from prometheus_client import Counter, Histogram
import structlog

from .exceptions import InsufficientFundsError
from .models import WithdrawalEvent, WithdrawalStatus
from app.schemas.withdrawal import WithdrawalRequest
from app.infrastructure.event_bus import get_event_publisher


logger = structlog.get_logger()

# Business metrics.
WITHDRAWAL_COUNT = Counter(
    'withdrawal_requests_total',
    'Total withdrawal requests',
    ['status', 'account_id']
)

WITHDRAWAL_AMOUNT = Histogram(
    'withdrawal_amount',
    'Withdrawal amount distribution',
    ['status'],
    buckets=[10, 50, 100, 500, 1000, 5000]
)

TRANSACTION_LATENCY = Histogram(
    'transaction_processing_seconds',
    'Transaction processing time',
    ['type']
)

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
        start_time = time.time()

        try:
            account = self.repository.get_account(withdrawal_request.account_id)
            if not account:
                log.warning("account_not_found")
                raise ValueError("Account not found.")

            if account.balance < withdrawal_request.amount:
                log.warning("insufficient_funds", balance=account.balance)
                raise InsufficientFundsError("Insufficient funds.")
            previous_balance = account.balance
            account.balance -= withdrawal_request.amount
            self.repository.update_account(account)

            transaction_data = {
                'id': str(uuid.uuid4()),
                'account_id': account.id,
                'type': 'WITHDRAWAL',
                'amount': float(withdrawal_request.amount),
                'previous_balance': float(previous_balance),
                'new_balance': float(account.balance),
                'status': 'SUCCESSFUL',
                'correlation_id': str(withdrawal_request.correlation_id),
                'created_at': datetime.now(timezone.utc)
            }
            self.repository.create_transaction(transaction_data)

            event = WithdrawalEvent(
                account_id=account.id,
                amount=withdrawal_request.amount,
                status=WithdrawalStatus.SUCCESSFUL,
                new_balance=account.balance,
            )

            log = log.bind(transaction_id=str(uuid4()))
            log.info("withdrawal_success", amount=str(event.amount), new_balance=str(event.new_balance))

            self.event_publisher.publish(event)

            WITHDRAWAL_COUNT.labels(status='success', account_id=withdrawal_request.account_id).inc()
            WITHDRAWAL_AMOUNT.labels(status='success').observe(float(withdrawal_request.amount))
            
            return event
        except Exception as e:
            WITHDRAWAL_COUNT.labels(status='failed', account_id=withdrawal_request.account_id).inc()
            raise e
        finally:
            # Record processing time.
            processing_time = time.time() - start_time
            TRANSACTION_LATENCY.labels(type='withdrawal').observe(processing_time)