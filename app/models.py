from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

import bcrypt
from sqlalchemy import (
    CHAR,
    CheckConstraint,
    Column,
    DateTime,
    Index,
    SmallInteger,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class AccountType(str, Enum):
    cash = "cash"
    bank = "bank"
    ewallet = "ewallet"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )

    transactions: list["Transaction"] = Relationship(back_populates="user")
    categories: list["Category"] = Relationship(back_populates="user")
    accounts: list["Account"] = Relationship(back_populates="user")
    transfers: list["Transfer"] = Relationship(back_populates="user")
    budgets: list["Budget"] = Relationship(back_populates="user")

    # hash password and store it
    def set_password(self, password: str):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode(
            "utf-8"
        )

    # verify if password matches the hash
    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )


class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_accounts_user_id_name"),
    )

    id: int | None = Field(default=None, primary_key=True)
    name: str
    type: AccountType = Field(
        default=AccountType.cash,
        sa_column=Column(
            SAEnum(AccountType, name="account_type"),
            nullable=False,
            server_default="cash",
        ),
    )
    currency: str = Field(
        default="PHP",
        sa_type=CHAR(3),
        sa_column_kwargs={"server_default": "PHP"},
    )
    initial_balance: Decimal = Field(
        default=Decimal("0.00"),
        max_digits=14,
        decimal_places=2,
        sa_column_kwargs={"server_default": "0"},
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")

    user: User = Relationship(back_populates="accounts")
    transactions: list["Transaction"] = Relationship(back_populates="account")
    transfers_out: list["Transfer"] = Relationship(
        back_populates="from_account",
        sa_relationship_kwargs={"foreign_keys": "[Transfer.from_account_id]"},
    )
    transfers_in: list["Transfer"] = Relationship(
        back_populates="to_account",
        sa_relationship_kwargs={"foreign_keys": "[Transfer.to_account_id]"},
    )


class Category(SQLModel, table=True):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "type", "name", name="uq_categories_user_id_type_name"
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    name: str
    type: TransactionType = Field(
        sa_column=Column(
            SAEnum(TransactionType, name="transaction_type"), nullable=False
        )
    )
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")

    user: User = Relationship(back_populates="categories")
    transactions: list["Transaction"] = Relationship(back_populates="category")
    budgets: list["Budget"] = Relationship(back_populates="category")


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        Index("ix_transactions_user_id_date_time", "user_id", "date_time"),
    )

    id: int | None = Field(default=None, primary_key=True)
    type: TransactionType = Field(
        sa_column=Column(
            SAEnum(TransactionType, name="transaction_type"), nullable=False
        )
    )
    amount: Decimal = Field(max_digits=14, decimal_places=2, gt=0)
    description: str | None = Field(default=None)
    date_time: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now(), "onupdate": utc_now},
    )
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    account_id: int = Field(foreign_key="accounts.id", ondelete="RESTRICT", index=True)
    category_id: int | None = Field(
        default=None, foreign_key="categories.id", ondelete="SET NULL", index=True
    )

    user: User = Relationship(back_populates="transactions")
    account: Account = Relationship(back_populates="transactions")
    category: Category | None = Relationship(back_populates="transactions")


class Transfer(SQLModel, table=True):
    __tablename__ = "transfers"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transfers_amount_positive"),
        CheckConstraint(
            "from_account_id <> to_account_id",
            name="ck_transfers_different_accounts",
        ),
        Index("ix_transfers_user_id_date_time", "user_id", "date_time"),
    )

    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal = Field(max_digits=14, decimal_places=2, gt=0)
    description: str | None = Field(default=None)
    date_time: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    from_account_id: int = Field(foreign_key="accounts.id", ondelete="RESTRICT")
    to_account_id: int = Field(foreign_key="accounts.id", ondelete="RESTRICT")

    user: User = Relationship(back_populates="transfers")
    from_account: Account = Relationship(
        back_populates="transfers_out",
        sa_relationship_kwargs={"foreign_keys": "[Transfer.from_account_id]"},
    )
    to_account: Account = Relationship(
        back_populates="transfers_in",
        sa_relationship_kwargs={"foreign_keys": "[Transfer.to_account_id]"},
    )


# NOTE: month/year for now for simplicity later prolly use period start/end
class Budget(SQLModel, table=True):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "category_id",
            "month",
            "year",
            name="uq_budgets_user_id_category_id_month_year",
        ),
        CheckConstraint("limit_amount > 0", name="ck_budgets_limit_positive"),
        CheckConstraint("month between 1 and 12", name="ck_budgets_month_range"),
    )

    id: int | None = Field(default=None, primary_key=True)
    limit_amount: Decimal = Field(max_digits=14, decimal_places=2, gt=0)
    month: int = Field(ge=1, le=12, sa_type=SmallInteger)
    year: int = Field(ge=2000, le=2100, sa_type=SmallInteger)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    category_id: int = Field(foreign_key="categories.id", ondelete="CASCADE")

    user: User = Relationship(back_populates="budgets")
    category: Category = Relationship(back_populates="budgets")
