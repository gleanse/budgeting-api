from pydantic import BaseModel, Field
from decimal import Decimal


class AccountCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    initial_balance: Decimal = Field(ge=0)


class AccountPatchRequest(BaseModel):
    name: str | None = None


class AccountListResponse(BaseModel):
    id: int
    name: str
    total_balance: Decimal


class AccountDetailResponse(BaseModel):
    id: int
    user_id: int
    name: str
    initial_balance: Decimal
    total_balance: Decimal


class OverallBalanceResponse(BaseModel):
    user: str
    total_balance: Decimal


class AccountCreateResponse(BaseModel):
    message: str = "Account created successfully"
    created_item: AccountDetailResponse
