from sqlmodel import Session
from app.models import Category
from app.repositories.category_repository import CategoryRepository
from app.repositories.income_repository import IncomeRepository
from app.repositories.expense_repository import ExpenseRepository


class CategoryService:
    def __init__(self, session: Session):
        self.category_repo = CategoryRepository(session)
        self.income_repo = IncomeRepository(session)
        self.expense_repo = ExpenseRepository(session)

    def list_by_user(self, user_id: int) -> list[Category]:
        return self.category_repo.get_all_by_user(user_id)

    def get_by_id_and_user(self, category_id: int, user_id: int) -> Category:
        category = self.category_repo.get_by_id_and_user(category_id, user_id)

        if category is None:
            raise ValueError("Category not found")

        return category

    def create(self, name: str, type: str, user_id: int) -> Category:
        if self.category_repo.exists_by_name_and_user(name, user_id):
            raise ValueError(f"Category '{name}' already exists")

        new_category = Category(
            name=name,
            type=type,
            user_id=user_id,
        )

        return self.category_repo.save(new_category)

    def update(
        self, category_id: int, user_id: int, name: str | None, type: str | None
    ) -> Category:
        category = self.category_repo.get_by_id_and_user(category_id, user_id)

        if category is None:
            raise ValueError("Category not found")

        if type is not None and type != category.type:
            if self.income_repo.exists_by_category(
                category_id
            ) or self.expense_repo.exists_by_category(category_id):
                raise ValueError(
                    "Cannot change category type as it is already used by existing transactions"
                )

        if name is not None and name != category.name:
            if self.category_repo.exists_by_name_and_user(
                name, user_id, exclude_id=category_id
            ):
                raise ValueError(f"Category '{name}' already exists")
            category.name = name

        if type is not None:
            category.type = type

        return self.category_repo.save(category)

    def delete(self, category_id: int, user_id: int) -> None:
        category = self.category_repo.get_by_id_and_user(category_id, user_id)

        if category is None:
            raise ValueError("Category not found")

        if self.income_repo.exists_by_category(
            category_id
        ) or self.expense_repo.exists_by_category(category_id):
            raise ValueError("Cannot delete category that is in use")

        self.category_repo.delete(category)
