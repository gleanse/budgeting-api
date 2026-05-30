from sqlmodel import create_engine, Session
from decouple import config

DATABASE_URL = config("DATABASE_URL")

# railway injects postgresql:// but sqlalchemy requires an explicit driver
# so we replace it with postgresql+psycopg2:// to avoid implicit fallback behavior
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL)


# automatically open the database connection session and then automatically close it after using it
def get_session():
    with Session(engine) as session:
        yield session
