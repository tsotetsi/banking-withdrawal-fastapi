# from typing import Optional
# from datetime import datetime, timezone
# from decimal import Decimal
# from app.domain.models import BankAccount


# # Default seeded accounts for testing
# DEFAULT_ACCOUNTS: dict[str, BankAccount] = {
#     "1234567890": BankAccount(id="1234567890",
#                               account_number="1234567890",
#                               balance=Decimal("1000.00"),
#                               created_at=datetime.now(timezone.utc),
#                               updated_at=datetime.now(timezone.utc)
#                               ),
#     "0987654321": BankAccount(id="0987654321",
#                               account_number="0987654321",
#                               balance=Decimal("500.00"),
#                               created_at=datetime.now(timezone.utc),
#                               updated_at=datetime.now(timezone.utc)
#                               ),
#     "1111111111": BankAccount(id="1111111111",
#                               account_number="1111111111",
#                               balance=Decimal("0.00"),
#                               created_at=datetime.now(timezone.utc),
#                               updated_at=datetime.now(timezone.utc)
#                               ),
# }


# class InMemoryAccountRepository:
#     """In-memory account repository for testing."""

#     def __init__(self):
#         self.reset()

#     def reset(self):
#         # copy defaults fresh for each test run
#         self.accounts: dict[str, BankAccount] = {
#             k: BankAccount(
#                 id=v.id,
#                 account_number=v.account_number, 
#                 balance=Decimal(v.balance),
#                 created_at=datetime.now(timezone.utc),
#                 updated_at=datetime.now(timezone.utc)
#             )
#             for k, v in DEFAULT_ACCOUNTS.items()
#         }

#     def get_account(self, account_id: str) -> BankAccount | None:
#         return self.accounts.get(account_id)

#     def update_account(self, account: BankAccount) -> None:
#         if not isinstance(account.balance, Decimal):
#             raise TypeError("Account balance must be a Decimal.")
#         self.accounts[account.id] = account

# # Helper for tests
# _repo_instance: InMemoryAccountRepository | None = None


# def get_repository() -> InMemoryAccountRepository:
#     global _repo_instance
#     if _repo_instance is None:
#         _repo_instance = InMemoryAccountRepository()
#     return _repo_instance


# def reset_mock_accounts() -> None:
#     global _repo_instance
#     if _repo_instance is not None:
#         _repo_instance.reset()

from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.domain.models import BankAccount
from app.infrastructure.models import Base, AccountModel, TransactionModel
import os
from contextlib import contextmanager
from decimal import Decimal

class PostgresRepository:
    def __init__(self):
        db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def init_db(self):
        """Initialize database tables"""
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
                    id=str(account_model.id),  # Convert UUID to string
                    account_number=str(account_model.account_number),  # Explicit conversion
                    balance=Decimal(account_model.balance), # type: ignore
                    created_at=account_model.created_at, # type: ignore
                    updated_at=account_model.updated_at # type: ignore
                )
            return None

    def update_account_balance(self, account_id: str, new_balance: Decimal) -> None:
        with self.get_session() as session:
            account = session.query(AccountModel).filter_by(id=account_id).first()
            if account:
                account.balance = new_balance
                session.add(account)

    def create_transaction(self, transaction_data: dict) -> None:
        with self.get_session() as session:
            transaction = TransactionModel(**transaction_data)
            session.add(transaction)

# Singleton instance
_repository = None

def get_repository():
    global _repository
    if _repository is None:
        _repository = PostgresRepository()
        _repository.init_db()  # Initialize tables on first call
    return _repository

def reset_mock_accounts():
    """Initialize with some test accounts (for development)"""
    repo = get_repository()
    with repo.get_session() as session:
        # Clear existing data
        session.query(TransactionModel).delete()
        session.query(AccountModel).delete()
        
        # Create test accounts
        test_accounts = [
            AccountModel(account_number="1234567", balance=1000.00),
            AccountModel(account_number="7654321", balance=5000.00),
            AccountModel(account_number="1111111", balance=250.50),
        ]
        
        session.add_all(test_accounts)
        session.commit()