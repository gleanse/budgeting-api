from sqlmodel import Session, select, func
from decimal import Decimal
from app.models import Account, Income, Expense


class AccountRepository:
    def __init__(self, session: Session):
        self.session = session

    def exists_by_name_and_user(self, name, user_id) -> bool:
        """Check if account name already exists for user"""
        statement = select(Account).where(
            Account.name == name, Account.user_id == user_id
        )
        return self.session.exec(statement).first() is not None

    def get_all_by_user_with_balance(
        self, user_id: int
    ) -> list[tuple[Account, Decimal]]:
        """list of all accounts with their total balance"""
        income_subq = (
            select(
                Income.account_id,
                func.coalesce(func.sum(Income.amount), 0).label("total_income"),
            )
            .group_by(Income.account_id)
            .subquery()
        )
        expense_subq = (
            select(
                Expense.account_id,
                func.coalesce(func.sum(Expense.amount), 0).label("total_expense"),
            )
            .group_by(Expense.account_id)
            .subquery()
        )
        statement = (
            select(
                Account,
                (
                    Account.initial_balance
                    + func.coalesce(income_subq.c.total_income, 0)
                    - func.coalesce(expense_subq.c.total_expense, 0)
                ).label("total_balance"),
            )
            .outerjoin(income_subq, income_subq.c.account_id == Account.id)
            .outerjoin(expense_subq, expense_subq.c.account_id == Account.id)
            .where(Account.user_id == user_id)
        )
        return self.session.exec(statement).all()

    def get_by_id_and_user(self, account_id: int, user_id: int) -> Account | None:
        statement = select(Account).where(
            Account.id == account_id, Account.user_id == user_id
        )
        return self.session.exec(statement).first()

    def get_total_initial_balance_by_user(self, user_id: int) -> Decimal:
        statement = select(func.sum(Account.initial_balance)).where(
            Account.user_id == user_id
        )
        result = self.session.exec(statement).first()

        return result or Decimal("0")

    def save(self, account: Account) -> Account:
        """insert or update account"""
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)

        return account

    def delete(self, account: Account) -> None:
        self.session.delete(account)
        self.session.commit()
