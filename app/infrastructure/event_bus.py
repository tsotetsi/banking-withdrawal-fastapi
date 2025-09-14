from app.domain.models import WithdrawalEvent


class InMemoryEventPublisher:
    """Simple in-memory event publisher for testing."""

    def __init__(self):
        self.events: list[WithdrawalEvent] = []

    def publish(self, event: WithdrawalEvent) -> None:
        if not isinstance(event.amount, (int, float)) and event.amount is None:
            raise ValueError("WithdrawalEvent.amount cannot be None.")
        if event.new_balance is None:
            raise ValueError("WithdrawalEvent.new_balance cannot be None.")

        self.events.append(event)
        print(f"[EVENT] Published: {event}")