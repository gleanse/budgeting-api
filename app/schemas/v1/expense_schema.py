from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class ExpenseCreateRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    category_id: int | None = None
    account_id: int
    description: str | None = None
    date_time: datetime | None = None


class ExpenseUpdateRequest(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    category_id: int | None = None
    account_id: int | None = None
    description: str | None = None
    date_time: datetime | None = None


class ExpenseListResponse(BaseModel):
    id: int
    amount: Decimal
    category_name: str
    account_name: str
    date_time: datetime


class ExpenseDetailResponse(BaseModel):
    id: int
    amount: Decimal
    category_id: int | None
    category_name: str
    account_id: int
    account_name: str
    description: str | None
    date_time: datetime


class ExpenseCreateResponse(BaseModel):
    message: str = "Expense created successfully"
    created_item: ExpenseDetailResponse
