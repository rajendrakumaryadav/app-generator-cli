# {{ project_name }}

A production-ready FastAPI backend with a clean Jinja2 frontend, scaffolded by [AppGenerator](https://github.com/yourname/appgenerator-cli).

## Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** — high-performance async web framework
- **[Jinja2](https://jinja.palletsprojects.com/)** — server-rendered HTML templates
- **[SQLModel](https://sqlmodel.tiangolo.com/)** — type-safe ORM (built on SQLAlchemy + Pydantic)
- **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** — typed config from env
- **[Alembic](https://alembic.sqlalchemy.org/)** — database migrations
- **[uv](https://docs.astral.sh/uv/)** — blazing-fast package management
{% if postgres %}- **PostgreSQL** — relational database
{% endif %}{% if redis %}- **Redis** — caching layer
{% endif %}{% if docker %}- **Docker** — containerisation
{% endif %}

## Getting Started

```bash
# 1. Copy and fill in your environment variables
cp .env.example .env

# 2. Run the development server
uv run uvicorn app.main:app --reload

# 3. Open the frontend and docs
# http://localhost:8000/
# http://localhost:8000/docs
```

## Project Structure

```
{{ project_name }}/
├── app/
│   ├── main.py                    # FastAPI app + homepage route
│   ├── config.py                  # Typed settings (pydantic-settings)
│   ├── dependencies.py            # Shared FastAPI dependencies
│   ├── templates/
│   │   ├── base.html              # Base layout
│   │   ├── index.html             # Homepage template
│   │   └── partials/
│   │       ├── header.html        # Shared header
│   │       └── footer.html        # Shared footer
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── health.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py
│   └── db/
│       ├── __init__.py
│       └── session.py
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   └── test_frontend.py
├── .env.example
├── .gitignore
└── pyproject.toml
```

## Running Tests

```bash
uv run pytest
```

## Linting

```bash
uv run ruff check .
uv run ruff format .
```
