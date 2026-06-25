from sqlmodel import Session
from datetime import datetime
from decimal import Decimal
from app.models import Income, Expense
from app.repositories.income_repository import IncomeRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.account_repository import AccountRepository


class TransactionService:
    def __init__(self, session: Session):
        self.income_repo = IncomeRepository(session)
        self.expense_repo = ExpenseRepository(session)
        self.category_repo = CategoryRepository(session)
        self.account_repo = AccountRepository(session)

    def list_by_user(
        self, transaction_type: str, user_id: int
    ) -> list[tuple[Income | Expense, str | None, str | None]]:
        if transaction_type == "income":
            return self.income_repo.get_all_by_user_with_category_and_account(user_id)
        else:
            return self.expense_repo.get_all_by_user_with_category_and_account(user_id)

    def get_detail_by_id_and_user(
        self, transaction_type: str, transaction_id: int, user_id: int
    ) -> tuple[Income | Expense, str | None, str | None]:
        if transaction_type == "income":
            transaction = self.income_repo.get_by_id_and_user_with_category_and_account(
                transaction_id, user_id
            )
        else:
            transaction = (
                self.expense_repo.get_by_id_and_user_with_category_and_account(
                    transaction_id, user_id
                )
            )
        if transaction is None:
            raise ValueError(f"{transaction_type} not found")

        return transaction

    def create(
        self,
        transaction_type: str,
        amount: Decimal,
        category_id: int,
        account_id: int,
        description: str,
        user_id: int,
        date_time: datetime | None = None,
    ) -> tuple[Income | Expense, str, str]:
        category = self.category_repo.get_by_id_and_user(category_id, user_id)
        if category is None:
            raise ValueError("Category not found")

        account = self.account_repo.get_by_id_and_user(account_id, user_id)
        if account is None:
            raise ValueError("Account not found")

        if category.type != transaction_type:
            raise ValueError(f"Invalid category, use a {transaction_type} category")

        if transaction_type == "income":
            new_transaction = Income(
                amount=amount,
                category_id=category_id,
                account_id=account_id,
                description=description,
                user_id=user_id,
                date_time=date_time,
            )
            self.income_repo.save(new_transaction)
        else:
            new_transaction = Expense(
                amount=amount,
                category_id=category_id,
                account_id=account_id,
                description=description,
                user_id=user_id,
                date_time=date_time,
            )
            self.expense_repo.save(new_transaction)

        return new_transaction, category.name, account.name

    def update(
        self, transaction_id: int, user_id: int, **kwargs
    ) -> tuple[Income | Expense, str | None, str | None]:
        result = self.income_repo.get_by_id_and_user_with_category_and_account(
            transaction_id, user_id
        )
        is_income = True

        if result is None:
            result = self.expense_repo.get_by_id_and_user_with_category_and_account(
                transaction_id, user_id
            )
            is_income = False

        if result is None:
            raise ValueError("Transaction not found")

        # unpack tuple result
        transaction, category_name, account_name = result

        # check if category type is changing
        new_category_id = kwargs.get("category_id")
        if new_category_id is not None:
            new_category = self.category_repo.get_by_id_and_user(
                new_category_id, user_id
            )
            if new_category is None:
                raise ValueError("Category not found")

            expected_type = "income" if is_income else "expense"

            if new_category.type != expected_type:
                # if transaction type detected change by its new update category, delete old create new on opposite transaction type
                return self._convert_transaction(
                    transaction, new_category, user_id, **kwargs
                )

        # for normal update (if category that will update is just same type)
        for key, value in kwargs.items():
            if value is not None:
                setattr(transaction, key, value)

        if is_income:
            saved = self.income_repo.save(transaction)
        else:
            saved = self.expense_repo.save(transaction)

        return saved, category_name, account_name

    def delete(self, transaction_type: str, transaction_id: int, user_id: int) -> None:
        if transaction_type == "income":
            transaction = self.income_repo.get_by_id_and_user(transaction_id, user_id)
            if transaction is None:
                raise ValueError("Income not found")
            self.income_repo.delete(transaction)
        else:
            transaction = self.expense_repo.get_by_id_and_user(transaction_id, user_id)
            if transaction is None:
                raise ValueError("Expense not found")
            self.expense_repo.delete(transaction)

    # PRIVATE helper methods
    def _convert_transaction(
        self, old_transaction, new_category, user_id, **kwargs
    ) -> tuple[Income | Expense, str | None, str | None]:
        """convert transaction to opposite type"""
        # NOTE: ignore the unhighlighted words as my linter is dumb
        # extract data (new category already validated)
        amount = kwargs.get("amount", old_transaction.amount)
        account_id = kwargs.get("account_id", old_transaction.account_id)
        description = kwargs.get("description", old_transaction.description)
        date_time = kwargs.get("date_time", old_transaction.date_time)

        # delete old
        if isinstance(old_transaction, Income):
            self.income_repo.delete(old_transaction)
            new_type = "expense"
        else:
            self.expense_repo.delete(old_transaction)
            new_type = "income"

        # create new
        if new_type == "income":
            new_transaction = Income(
                amount=amount,
                category_id=new_category.id,
                account_id=account_id,
                description=description,
                date_time=date_time,
                user_id=user_id,
            )
            self.income_repo.save(new_transaction)

            result = self.income_repo.get_by_id_and_user_with_category_and_account(
                new_transaction.id, user_id
            )
            if result is not None:
                new_transaction, category_name, account_name = result
            else:
                category_name = None
                account_name = None
        else:
            new_transaction = Expense(
                amount=amount,
                category_id=new_category.id,
                account_id=account_id,
                description=description,
                date_time=date_time,
                user_id=user_id,
            )
            self.expense_repo.save(new_transaction)

            result = self.expense_repo.get_by_id_and_user_with_category_and_account(
                new_transaction.id, user_id
            )
            if result is not None:
                new_transaction, category_name, account_name = result
            else:
                category_name = None
                account_name = None

        return new_transaction, category_name, account_name
