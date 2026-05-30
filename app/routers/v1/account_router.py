from fastapi import APIRouter, HTTPException, status
from app.core.dependencies import UserAuthenticationDep, AccountServiceDep
from app.schemas.v1.account_schema import (
    AccountCreateRequest,
    AccountPatchRequest,
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


@router.post("/", response_model=AccountCreateResponse)
async def create_account(
    current_user: UserAuthenticationDep,
    account_service: AccountServiceDep,
    account_data: AccountCreateRequest,
):
    try:
        created_account = account_service.create(
            name=account_data.name,
            initial_balance=account_data.initial_balance,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return AccountCreateResponse(
        created_item=AccountDetailResponse(
            id=created_account.id,
            user_id=created_account.user_id,
            name=created_account.name,
            initial_balance=created_account.initial_balance,
            total_balance=created_account.initial_balance,
        )
    )


@router.patch("/{account_id}", response_model=AccountDetailResponse)
async def update_account(
    current_user: UserAuthenticationDep,
    account_service: AccountServiceDep,
    account_id: int,
    account_data: AccountPatchRequest,
):
    try:
        updated_account, balance = account_service.update(
            account_id=account_id,
            user_id=current_user.id,
            name=account_data.name,
        )
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return AccountDetailResponse(
        id=updated_account.id,
        user_id=updated_account.user_id,
        name=updated_account.name,
        initial_balance=updated_account.initial_balance,
        total_balance=balance,
    )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    current_user: UserAuthenticationDep,
    account_service: AccountServiceDep,
    account_id: int,
) -> None:
    try:
        account_service.delete(account_id=account_id, user_id=current_user.id)
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
