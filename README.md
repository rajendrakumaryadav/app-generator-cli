# ⚒ AppGenerator CLI

[![CI](https://github.com/rajendrakumaryadav/app-generator-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/rajendrakumaryadav/app-generator-cli/actions)
[![PyPI version](https://img.shields.io/pypi/v/app-generator-cli?cacheSeconds=60)](https://pypi.org/project/app-generator-cli/)
[![pytest](https://img.shields.io/badge/pytest-3.10%20%7C%203.11%20%7C%203.12-0A9EDC?logo=pytest)](https://github.com/rajendrakumaryadav/app-generator-cli/actions/workflows/ci.yml) 
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![GitHub issues](https://img.shields.io/github/issues/rajendrakumaryadav/app-generator-cli)](https://github.com/rajendrakumaryadav/app-generator-cli/issues)
[![GitHub license](https://img.shields.io/github/license/rajendrakumaryadav/app-generator-cli)](https://github.com/rajendrakumaryadav/app-generator-cli/blob/main/LICENSE)
> Scaffold production-ready Python projects in seconds — powered by `uv`.

CI runs `uv run pytest tests/ -v --tb=short` on Python `3.10`, `3.11`, and `3.12`.

```
$ app-generator-cli create fastapi my_api
$ app-generator-cli create fastapi-with-frontend my_web_app --docker
$ app-generator-cli create ai my_ai_app --docker --postgres
```

---

## Installation

```bash
pip install app-generator-cli
# or, with uv (recommended):
uv tool install app-generator-cli
```

Verify:
```bash
app-generator-cli --version
```

---

## Commands

### `app-generator-cli create fastapi <name>`

Scaffold a **FastAPI** backend.

| Flag | Description |
|------|-------------|
| `--docker` | Add `Dockerfile` + `docker-compose.yml` |
| `--postgres` | Use PostgreSQL (`asyncpg`) instead of SQLite |
| `--redis` | Add Redis client (`redis`) |
| `--output PATH` | Create the project in a custom directory |

**Example:**
```bash
app-generator-cli create fastapi my_api --docker --postgres --redis
cd my_api
cp .env.example .env
uv run uvicorn app.main:app --reload
```

### `app-generator-cli create fastapi-with-frontend <name>`

Scaffold a **FastAPI + Jinja2 frontend** project.

| Flag | Description |
|------|-------------|
| `--docker` | Add `Dockerfile` + `docker-compose.yml` |
| `--postgres` | Use PostgreSQL (`asyncpg`) instead of SQLite |
| `--redis` | Add Redis client (`redis`) |
| `--output PATH` | Create the project in a custom directory |

**Example:**
```bash
app-generator-cli create fastapi-with-frontend my_web_app --docker
cd my_web_app
cp .env.example .env
uv run uvicorn app.main:app --reload
# open http://localhost:8000/ and http://localhost:8000/docs
```

### `app-generator-cli create ai <name>`

Scaffold a **LangChain / LangGraph** AI application.

| Flag | Description |
|------|-------------|
| `--docker` | Add `Dockerfile` + `docker-compose.yml` |
| `--postgres` | Add pgvector PostgreSQL support |
| `--redis` | Add Redis semantic cache |
| `--output PATH` | Create the project in a custom directory |

**Example:**
```bash
app-generator-cli create ai my_assistant --docker
cd my_assistant
cp .env.example .env   # add your OPENAI_API_KEY
uv run python main.py
```

### `app-generator-cli create model --project-path <path>`

Interactively create a model inside an existing generated project.

| Prompt/Flag | Description |
|------|-------------|
| `--project-path`, `-p` | Existing project root to update |
| `--template` | Optional explicit template (`fastapi`, `fastapi-with-frontend`, `ai`) |
| `Model name` | Output file/class name (written to `app/models/`) |
| `Field prompts` | Add field name, type, required/nullable, and optional max_length |

**Examples:**
```bash
# SQLModel model in an existing FastAPI project
app-generator-cli create model --project-path ./my_api

# Pydantic model in an existing AI project
app-generator-cli create model --project-path ./my_assistant --template ai
```

---

## Generated Project Structure

### FastAPI

```
my_api/
├── app/
│   ├── main.py          # Application factory
│   ├── config.py        # Pydantic Settings
│   ├── dependencies.py  # FastAPI deps (DB session, etc.)
│   ├── api/v1/
│   │   └── health.py    # Health-check endpoint
│   ├── models/
│   │   └── base.py      # SQLModel base with timestamps
│   └── db/
│       └── session.py   # Async session factory
├── tests/
│   ├── conftest.py      # Async test client + DB fixtures
│   └── test_health.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── Dockerfile           # (--docker)
└── docker-compose.yml   # (--docker)
```

### AI (LangChain / LangGraph)

```
my_assistant/
├── main.py              # Interactive REPL
├── app/
│   ├── config.py        # Pydantic Settings
│   ├── agents/
│   │   └── assistant.py # LangGraph ReAct agent
│   ├── chains/
│   │   └── rag.py       # RAG chain example
│   └── tools/
│       ├── registry.py  # Tool registry
│       └── search.py    # Web search tool stub
├── tests/
│   └── test_agent.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── Dockerfile           # (--docker)
└── docker-compose.yml   # (--docker)
```

### FastAPI + Jinja Frontend

```
my_web_app/
├── app/
│   ├── main.py                    # App + homepage route
│   ├── templates/
│   │   ├── base.html              # Base layout
│   │   ├── index.html             # Homepage
│   │   └── partials/
│   │       ├── header.html        # Shared header
│   │       └── footer.html        # Shared footer
│   ├── api/v1/
│   │   └── health.py
│   └── ...                        # config/db/models/dependencies
├── tests/
│   ├── test_health.py
│   └── test_frontend.py
├── .env.example
├── pyproject.toml
├── Dockerfile                     # (--docker)
└── docker-compose.yml             # (--docker)
```

---

## Packaging & Publishing to PyPI

### 1. Build

```bash
# Install build tools
pip install build twine

# Build wheel + sdist
python -m build
# Outputs: dist/app-generator-cli-0.1.0-py3-none-any.whl
#          dist/app-generator-cli-0.1.0.tar.gz
```

### 2. Test on TestPyPI

```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ app-generator-cli
```

### 3. Publish to PyPI

```bash
twine upload dist/*
```

Or with uv:

```bash
uv build
uv publish
```

---

## Development Setup

```bash
git clone https://github.com/yourname/app-generator-cli
cd app-generator-cli

uv venv
uv sync --dev

# Run locally
uv run app-generator-cli --help

# Tests
uv run pytest

# Lint
uv run ruff check .
uv run ruff format .
```

---

## Requirements

- Python ≥ 3.10
- [`uv`](https://docs.astral.sh/uv/) installed on the system (for generated project env management)

---

## License

MIT
