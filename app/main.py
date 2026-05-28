from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
from app.database import engine
from app.routers.v1 import (
    auth_router,
    category_router,
    account_router,
    expense_router,
    income_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("SERVER - Server running...")
    print(f"Models registered: {SQLModel.metadata.tables.keys()}")
    SQLModel.metadata.create_all(engine)
    print("DATABASE - All database tables created")
    yield
    print("SERVER - Shutting down...")


app = FastAPI(
    title="Budgeting App API",
    version="1.0.0",
    description="API for managing personal finances - incomes, expenses, categories, and balance",
    lifespan=lifespan,
)

app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(income_router.router, prefix="/api/v1")
app.include_router(expense_router.router, prefix="/api/v1")
app.include_router(category_router.router, prefix="/api/v1")
app.include_router(account_router.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Budgeting App v0.1"}
