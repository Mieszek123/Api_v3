# FastAPI Users Template

A starter template for FastAPI projects with authentication already set up: **fastapi-users** (JWT), async SQLAlchemy, and **pytest** tests for register and login. Create a new repo from it and start building your own endpoints and models.

## What's included

- User registration and login (fastapi-users, JWT Bearer)
- Async SQLAlchemy with SQLite (easy to swap for PostgreSQL)
- Config through `.env`
- Pytest suite with a separate test database
- Dependencies managed with [uv](https://docs.astral.sh/uv/)

## Using this template

1. Click **Use this template** → **Create a new repository** on GitHub
2. Clone your new repo and set it up:

```bash
git clone https://github.com/YOUR_USERNAME/NEW_PROJECT.git
cd NEW_PROJECT

uv sync
cp .env.example .env     # then set your own SECRET_KEY
uv run python main.py
```

Docs: http://localhost:8000/docs

Or do the first step from the CLI:

```bash
gh repo create NEW_PROJECT --template YOUR_USERNAME/FastAPI-users_template --private --clone
```

## After creating a project

- [ ] Rename the project in `pyproject.toml` and this README
- [ ] Set your own `SECRET_KEY` in `.env` (never commit `.env`)
- [ ] Change `DATABASE_URL` if you don't want SQLite
- [ ] Run `uv run pytest` to check that everything works
- [ ] Delete the example parts you don't need

## Project structure

```
.
├── app/
│   ├── app.py        # FastAPI app, routers included here
│   ├── db.py         # engine, sessions, create_db_and_tables
│   ├── models.py     # Base and database models (User, ...)
│   ├── routes.py     # your own endpoints (APIRouter)
│   ├── schemas.py    # Pydantic schemas
│   └── users.py      # fastapi-users setup, JWT backend
├── test/
│   ├── conftest.py   # test client and test database
│   └── test_app.py   # register and login tests
├── main.py           # entry point
├── .env.example
├── pyproject.toml
└── uv.lock
```

## Extending the template

**Add endpoints:** create them in `app/routes.py` and include the router in `app/app.py`:

```python
from app.routes import router

app.include_router(router)
```

**Add a model:** define it in `app/models.py` under `Base`. Tables are created automatically on startup:

```python
class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
```

If you put models in separate files, import them in `db.py` so they register in `Base.metadata`.

> `create_all` only creates missing tables. After changing columns of an existing model, delete `database.db` (or use Alembic migrations).

## Auth endpoints

| Method | Path              | Description                                      |
|--------|-------------------|--------------------------------------------------|
| POST   | `/auth/register`  | Register (JSON: `email`, `password`)             |
| POST   | `/auth/jwt/login` | Log in (form data: `username` = email, `password`), returns `access_token` |

## Tests

```bash
uv run pytest
```

Tests run against a separate database (`test.db`), so dev data stays untouched.

- register: success (`201`), duplicate email (`400`)
- login: success (`200`), token returned, wrong password (`400`), unknown email (`400`)

Add new tests to `test/test_app.py` using the `client` fixture from `conftest.py`.

## Environment variables

| Variable       | Description                          | Example                                |
|----------------|--------------------------------------|----------------------------------------|
| `SECRET_KEY`   | Secret for signing JWT and tokens    | `change-me`                            |
| `DATABASE_URL` | Database connection string           | `sqlite+aiosqlite:///./database.db`    |

Generate a key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
