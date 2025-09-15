from decimal import Decimal
from contextlib import contextmanager
from datetime import datetime, timezone
import uuid
import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.domain.models import BankAccount
from app.infrastructure.models import Base, AccountModel, TransactionModel


class PostgresRepository:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        
        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def init_db(self):
        """Initialize database tables."""
        Base.metadata.create_all(bind=self.engine)
        
    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def get_account(self, account_number: str) -> Optional[BankAccount]:
        with self.get_session() as session:
            account_model = session.query(AccountModel).filter_by(account_number=account_number).first()
            if account_model:
                return BankAccount(
                    id=str(account_model.id),
                    account_number=str(account_model.account_number),
                    balance=Decimal(account_model.balance), # type: ignore
                    created_at=account_model.created_at, # type: ignore
                    updated_at=account_model.updated_at # type: ignore
                )
            return None

    def create_transaction(self, transaction_data: dict) -> None:
        with self.get_session() as session:
            transaction = TransactionModel(**transaction_data)
            session.add(transaction)

    def update_account(self, account: BankAccount) -> None:
        """Update an existing account in the database."""
        with self.get_session() as session:
            account_model = session.query(AccountModel).filter_by(id=uuid.UUID(account.id)).first()
            if account_model:
                account_model.balance = float(account.balance) # type: ignore
                account_model.updated_at = datetime.now(timezone.utc) # type: ignore
                session.add(account_model)

# Singleton instance
_repository = None

def get_repository():
    global _repository
    if _repository is None:
        _repository = PostgresRepository()
        _repository.init_db()  # Initialize tables on first call
    return _repository

def reset_mock_accounts():
    """Initialize with some test accounts (for development onlyy)"""
    repo = get_repository()
    with repo.get_session() as session:
        # Clear existing data.
        session.query(TransactionModel).delete()
        session.query(AccountModel).delete()
        
        # Create test accounts.
        test_accounts = [
            AccountModel(account_number="1234567", balance=1000.00),
            AccountModel(account_number="7654321", balance=5000.00),
            AccountModel(account_number="1111111", balance=250.50),
        ]
        
        session.add_all(test_accounts)
        session.commit()