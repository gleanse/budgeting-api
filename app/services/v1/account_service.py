from sqlmodel import Session
from app.models import Account
from decimal import Decimal
from app.repositories.account_repository import AccountRepository
from app.repositories.income_repository import IncomeRepository
from app.repositories.expense_repository import ExpenseRepository


class AccountService:
    def __init__(self, session: Session):
        self.account_repo = AccountRepository(session)
        self.income_repo = IncomeRepository(session)
        self.expense_repo = ExpenseRepository(session)

    def list_by_user_with_balance(self, user_id: int) -> list[tuple[Account, Decimal]]:
        return self.account_repo.get_all_by_user_with_balance(user_id)

    def get_by_id_and_user_with_balance(
        self, account_id: int, user_id: int
    ) -> tuple[Account, Decimal]:
        account = self.account_repo.get_by_id_and_user(account_id, user_id)
        if account is None:
            raise ValueError("Account not found")

        total_income = self.income_repo.get_total_balance_by_account(account_id)
        total_expense = self.expense_repo.get_total_balance_by_account(account_id)
        balance = account.initial_balance + total_income - total_expense

        return account, balance

    def total_balance_on_all_accounts(self, user_id: int) -> Decimal:
        total_income = self.income_repo.get_total_balance_across_accounts_by_user(
            user_id
        )
        total_expense = self.expense_repo.get_total_balance_across_accounts_by_user(
            user_id
        )
        total_initial_balance = self.account_repo.get_total_initial_balance_by_user(
            user_id
        )

        return total_initial_balance + total_income - total_expense

    def create(self, name: str, initial_balance: Decimal, user_id: int) -> Account:
        if self.account_repo.exists_by_name_and_user(name, user_id):
            raise ValueError(f"Account '{name}' already exists")

        new_account = Account(
            name=name,
            initial_balance=initial_balance,
            user_id=user_id,
        )

        return self.account_repo.save(new_account)

    def update(
        self, account_id: int, user_id: int, name: str | None
    ) -> tuple[Account, Decimal]:
        account = self.account_repo.get_by_id_and_user(account_id, user_id)

        if account is None:
            raise ValueError("Account not found")

        if name is not None and name != account.name:
            if self.account_repo.exists_by_name_and_user(name, user_id):
                raise ValueError(f"Account '{name}' already exists")
            account.name = name

        updated_account = self.account_repo.save(account)
        total_income = self.income_repo.get_total_balance_by_account(account_id)
        total_expense = self.expense_repo.get_total_balance_by_account(account_id)
        balance = updated_account.initial_balance + total_income - total_expense

        return updated_account, balance

    def delete(self, account_id: int, user_id: int) -> None:
        account = self.account_repo.get_by_id_and_user(account_id, user_id)

        if account is None:
            raise ValueError("Account not found")

        if self.income_repo.exists_by_account(
            account_id
        ) or self.expense_repo.exists_by_account(account_id):
            raise ValueError("Cannot delete account that is in use")

        self.account_repo.delete(account)
