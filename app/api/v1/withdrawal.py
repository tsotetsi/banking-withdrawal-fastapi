from fastapi import APIRouter, HTTPException, Depends, status

from app.domain.exceptions import InsufficientFundsError
from app.domain.services import WithdrawalService
from app.infrastructure.event_bus import InMemoryEventPublisher
from app.infrastructure.repository import get_repository, reset_mock_accounts
from app.schemas.withdrawal import WithdrawalRequest, WithdrawalResponse


router = APIRouter(tags=["withdrawals"])


# Dependency injection factory
def get_withdrawal_service() -> WithdrawalService:
    repo = get_repository()
    publisher = InMemoryEventPublisher()
    return WithdrawalService(repository=repo, event_publisher=publisher)


@router.post(
    "/withdrawal",
    response_model=WithdrawalResponse,
    status_code=status.HTTP_200_OK,
    summary="Withdraw funds from an account.",
    response_description="Details of the withdrawal transaction.",
)
async def withdraw(
    request: WithdrawalRequest,
    service: WithdrawalService = Depends(get_withdrawal_service),
) -> WithdrawalResponse:
    """
    Withdraw funds from an account using the WithdrawalService.
    """
    try:
        event = service.withdraw(request)

        return WithdrawalResponse(
            account_id=event.account_id,
            amount=event.amount,
            balance=event.new_balance,
            correlation_id=request.correlation_id,
        )

    except InsufficientFundsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValueError as e:  # e.g. account not found.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
