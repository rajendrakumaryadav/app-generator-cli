# ⚒ AppGenerator CLI

[![CI](https://github.com/rajendrakumaryadav/pyforge/actions/workflows/ci.yml/badge.svg)](https://github.com/rajendrakumaryadav/pyforge/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/appgenerator-cli)](https://pypi.org/project/appgenerator-cli/)
[![pytest](https://img.shields.io/badge/pytest-3.10%20%7C%203.11%20%7C%203.12-0A9EDC?logo=pytest)](https://github.com/rajendrakumaryadav/pyforge/actions/workflows/ci.yml) 

> Scaffold production-ready Python projects in seconds — powered by `uv`.

CI runs `uv run pytest tests/ -v --tb=short` on Python `3.10`, `3.11`, and `3.12`.

```
$ appgenerator create fastapi my_api
$ appgenerator create ai my_ai_app --docker --postgres
```

---

## Installation

```bash
pip install appgenerator-cli
# or, with uv (recommended):
uv tool install appgenerator-cli
```

Verify:
```bash
appgenerator --version
```

---

## Commands

### `appgenerator create fastapi <name>`

Scaffold a **FastAPI** backend.

| Flag | Description |
|------|-------------|
| `--docker` | Add `Dockerfile` + `docker-compose.yml` |
| `--postgres` | Use PostgreSQL (`asyncpg`) instead of SQLite |
| `--redis` | Add Redis client (`redis`) |
| `--output PATH` | Create the project in a custom directory |

**Example:**
```bash
appgenerator create fastapi my_api --docker --postgres --redis
cd my_api
cp .env.example .env
uv run uvicorn app.main:app --reload
```

### `appgenerator create ai <name>`

Scaffold a **LangChain / LangGraph** AI application.

| Flag | Description |
|------|-------------|
| `--docker` | Add `Dockerfile` + `docker-compose.yml` |
| `--postgres` | Add pgvector PostgreSQL support |
| `--redis` | Add Redis semantic cache |
| `--output PATH` | Create the project in a custom directory |

**Example:**
```bash
appgenerator create ai my_assistant --docker
cd my_assistant
cp .env.example .env   # add your OPENAI_API_KEY
uv run python main.py
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

---

## Packaging & Publishing to PyPI

### 1. Build

```bash
# Install build tools
pip install build twine

# Build wheel + sdist
python -m build
# Outputs: dist/appgenerator_cli-0.1.0-py3-none-any.whl
#          dist/appgenerator_cli-0.1.0.tar.gz
```

### 2. Test on TestPyPI

```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ appgenerator-cli
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
git clone https://github.com/yourname/pyforge-cli
cd pyforge-cli

uv venv
uv sync --dev

# Run locally
uv run appgenerator --help

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
