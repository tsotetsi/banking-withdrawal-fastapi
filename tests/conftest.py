import pytest

from app.infrastructure.repository import reset_mock_accounts


@pytest.fixture(autouse=True)
def setup_test_data():
    """Reset repository accounts before each test."""
    reset_mock_accounts()
    yield
    reset_mock_accounts()