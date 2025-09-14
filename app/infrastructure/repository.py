from decimal import Decimal
from app.domain.models import BankAccount


# Default seeded accounts for testing
DEFAULT_ACCOUNTS: dict[str, BankAccount] = {
    "1234567890": BankAccount(id="1234567890", balance=Decimal("1000.00")),
    "0987654321": BankAccount(id="0987654321", balance=Decimal("500.00")),
    "1111111111": BankAccount(id="1111111111", balance=Decimal("0.00")),
}


class InMemoryAccountRepository:
    """In-memory account repository for testing."""

    def __init__(self):
        self.reset()

    def reset(self):
        # copy defaults fresh for each test run
        self.accounts: dict[str, BankAccount] = {
            k: BankAccount(id=v.id, balance=Decimal(v.balance))
            for k, v in DEFAULT_ACCOUNTS.items()
        }

    def get_account(self, account_id: str) -> BankAccount | None:
        return self.accounts.get(account_id)

    def update_account(self, account: BankAccount) -> None:
        if not isinstance(account.balance, Decimal):
            raise TypeError("Account balance must be a Decimal.")
        self.accounts[account.id] = account

# Helper for tests
_repo_instance: InMemoryAccountRepository | None = None


def get_repository() -> InMemoryAccountRepository:
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = InMemoryAccountRepository()
    return _repo_instance


def reset_mock_accounts() -> None:
    global _repo_instance
    if _repo_instance is not None:
        _repo_instance.reset()