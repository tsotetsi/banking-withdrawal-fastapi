from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional


@dataclass
class BankAccount:
    """A simple bank account model."""
    id: str
    balance: Decimal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WithdrawalStatus(Enum):
    """Status of a withdrawal transaction."""
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    PENDING = "PENDING"


@dataclass
class WithdrawalEvent:
    """Event representing a withdrawal transaction."""
    account_id: str
    amount: Decimal
    new_balance: Decimal
    status: WithdrawalStatus = WithdrawalStatus.PENDING
    timestamp: datetime = datetime.now(timezone.utc)
    error_message: Optional[str] = None