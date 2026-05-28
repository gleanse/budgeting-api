from sqlmodel import Session, select
from app.models import Category


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_by_user(self, user_id: int) -> list[Category]:
        statement = select(Category).where(
            Category.user_id == user_id,
        )
        return self.session.exec(statement).all()

    def get_by_id_and_user(self, category_id: int, user_id: int) -> Category | None:
        statement = select(Category).where(
            Category.id == category_id,
            Category.user_id == user_id,
        )

        return self.session.exec(statement).first()

    def exists_by_name_and_user(self, name, user_id) -> bool:
        """Check if category name already exists for user"""
        statement = select(Category).where(
            Category.name == name, Category.user_id == user_id
        )
        return self.session.exec(statement).first() is not None

    def save(self, category: Category) -> Category:
        """insert or update category"""
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)

        return category

    def delete(self, category: Category) -> None:
        self.session.delete(category)
        self.session.commit()
