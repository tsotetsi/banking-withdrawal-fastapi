from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4, UUID
from typing import Any

from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic.functional_serializers import model_serializer


class WithdrawalRequest(BaseModel):
    """Schema for a withdrawal request."""

    account_id: str = Field(
        ...,
        examples=["1234567", "12345678901234"],
        description="The account number to withdraw from. Must be 7-14 digits." # Tipical ZA account length.
    )

    amount: Decimal = Field(
        ...,
        gt=0, 
        examples=[50.00, 70.50, 1000],
        description="The amount to withdraw. Must be greater than zero."
    )

    correlation_id: UUID = Field(
        ...,
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        description="Unique identifier for tracking the request."
    )

    @field_validator("amount")
    def validate_amount_precision(cls, value: Decimal) -> Decimal:
        """Round to 2 decimal places for currency."""
        return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        """Custom serializer for Decimal and UUID fields."""
        return {
            "account_id": self.account_id,
            "amount": str(self.amount),
            "correlation_id": str(self.correlation_id)
        }

    model_config = ConfigDict(extra='forbid')


class WithdrawalResponse(BaseModel):
    """Schema for a withdrawal response."""

    transaction_id: UUID = Field(
        default_factory=uuid4,
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        description="Unique identifier for the transaction."
    )

    account_id: str = Field(
        ..., 
        examples=["1234567", "12345678901234"],
        description="The account number from which the amount was withdrawn."
    )

    amount: Decimal = Field(
        ..., 
        examples=[50.00, 70.50, 1000],
        description="The amount that was withdrawn."
    )

    balance: Decimal = Field(
        ..., 
        examples=[950.00, 1429.50, 5000],
        description="The remaining balance in the account after withdrawal."
    )

    correlation_id: UUID = Field(
        ..., 
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        description="Unique identifier for tracking the request."
    )

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        """Custom serializer for Decimal and UUID fields."""
        return {
            "transaction_id": str(self.transaction_id),
            "account_id": self.account_id,
            "amount": str(self.amount),
            "balance": str(self.balance),
            "correlation_id": str(self.correlation_id)
        }

    model_config = ConfigDict(extra='forbid')