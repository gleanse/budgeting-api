<div align="center">

# Budgeting API

A personal finance REST API built with FastAPI and SQLModel.
JWT auth, versioned endpoints, and database migrations.



![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)




![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)




![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)




![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)



</div>

---

## Features

- JWT authentication with bcrypt password hashing
- Accounts with computed balances
- Income and expense tracking
- User-defined categories
- Alembic migrations
- Versioned endpoints under `/api/v1`
- Interactive docs via Swagger UI and ReDoc

## Endpoints

All routes are prefixed with `/api/v1` and, except auth, require a bearer token.

| Resource | Routes |
| -------- | ------ |
| `/auth` | `POST /register` `POST /login` `POST /logout` |
| `/accounts` | `GET /` `GET /{id}` `POST /` `PATCH /{id}` `DELETE /{id}` `GET /balance/overall` |
| `/incomes` | `GET /` `GET /{id}` `POST /` `PATCH /{id}` `DELETE /{id}` |
| `/expenses` | `GET /` `GET /{id}` `POST /` `PATCH /{id}` `DELETE /{id}` |
| `/categories` | `GET /` `GET /{id}` `POST /` `PATCH /{id}` `DELETE /{id}` |

Full request and response schemas are in the interactive docs at `/docs`.

## Tech Stack

| | |
| --- | --- |
| Framework | FastAPI |
| ORM | SQLModel (SQLAlchemy + Pydantic) |
| Database | PostgreSQL |
| Migrations | Alembic |
| Auth | python-jose, bcrypt |
| Config | python-decouple |
| Containers | Docker Compose (database) |

## Getting Started

**1. Clone the repo**

```bash
git clone https://github.com/gleanse/budgeting-api.git
cd budgeting-api
```

**2. Create your environment file**

```bash
cp .env.example .env
```

```env
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database_name>
JWT_KEY=your-secret-jwt-key-here
```

**3. Start PostgreSQL**

With Docker:

```bash
docker compose up -d
```

Or point `DATABASE_URL` at any PostgreSQL instance you already run.

**4. Install dependencies**

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**5. Run migrations**

```bash
alembic upgrade head
```

**6. Start the server**

```bash
fastapi dev app/main.py
```

The API runs at `http://localhost:8000`, with docs at `/docs` and `/redoc`.

## Testing

The test database is created by `init.sql` on container init. Apply migrations to it by overriding `DATABASE_URL`:

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/budgeting_fastapi_db_test alembic upgrade head
```

Then run the suite:

```bash
pytest
```

## Known Limitations

- No pagination on list endpoints
- Logout is stateless, so tokens are not blacklisted
- Budget and transfer models exist but are not exposed through endpoints yet
