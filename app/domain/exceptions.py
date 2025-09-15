class InsufficientFundsError(Exception):
    """There are no sufficient founds in the account."""
    pass

class AccountNotFoundError(Exception):
    """Account does not exist in the system."""
    pass