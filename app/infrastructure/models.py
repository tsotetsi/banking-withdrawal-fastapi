from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, Numeric, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class AccountModel(Base):
    """Account model for the accounts table."""
    __tablename__ = "accounts"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    account_number = Column(String(14), unique=True, nullable=False, index=True)
    balance = Column(Numeric(12, 2), nullable=False, default=0.00)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class TransactionModel(Base):
    """Transaction model for the transactions table."""
    __tablename__ = "transactions"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID, nullable=False, index=True)
    type = Column(String(10), nullable=False)  # "withdrawal"
    amount = Column(Numeric(12, 2), nullable=False)
    previous_balance = Column(Numeric(12, 2), nullable=False)
    new_balance = Column(Numeric(12, 2), nullable=False)
    correlation_id = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))