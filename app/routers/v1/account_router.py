from fastapi import APIRouter, HTTPException, status
from app.core.dependencies import UserAuthenticationDep, AccountServiceDep
from app.schemas.v1.account_schema import (
    AccountCreateRequest,
    AccountCreateResponse,
    AccountListResponse,
    AccountDetailResponse,
    OverallBalanceResponse,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=list[AccountListResponse])
async def get_accounts(
    current_user: UserAuthenticationDep, account_service: AccountServiceDep
) -> list[AccountListResponse]:
    accounts = account_service.list_by_user_with_balance(current_user.id)

    return [
        AccountListResponse(
            id=account.id,
            name=account.name,
            total_balance=total_balance,
        )
        for account, total_balance in accounts
    ]


@router.get("/balance/overall", response_model=OverallBalanceResponse)
async def get_total_balance_across_accounts(
    current_user: UserAuthenticationDep, account_service: AccountServiceDep
) -> OverallBalanceResponse:
    accounts_total_balance = account_service.total_balance_on_all_accounts(
        current_user.id
    )

    return OverallBalanceResponse(
        user=current_user.username,
        total_balance=accounts_total_balance,
    )


@router.get("/{account_id}", response_model=AccountDetailResponse)
async def get_account(
    current_user: UserAuthenticationDep,
    account_service: AccountServiceDep,
    account_id: int,
) -> AccountDetailResponse:
    try:
        account, balance = account_service.get_by_id_and_user_with_balance(
            account_id, current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return AccountDetailResponse(
        id=account.id,
        user_id=current_user.id,
        name=account.name,
        initial_balance=account.initial_balance,
        total_balance=balance,
    )
