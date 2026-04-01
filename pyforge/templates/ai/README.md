# {{ project_name }}

A production-ready LangChain / LangGraph AI application, scaffolded by [AppGenerator](https://github.com/yourname/appgenerator-cli).

## Tech Stack

- **[LangChain](https://python.langchain.com/)** — LLM orchestration framework
- **[LangGraph](https://langchain-ai.github.io/langgraph/)** — stateful agent graphs
- **[LangChain-OpenAI](https://python.langchain.com/docs/integrations/chat/openai)** — OpenAI chat models
- **[LangChain-Ollama](https://python.langchain.com/docs/integrations/chat/ollama)** — local Ollama models
- **[ChromaDB](https://docs.trychroma.com/)** — local vector store for RAG
- **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** — typed config from env
- **[uv](https://docs.astral.sh/uv/)** — blazing-fast package management
{% if postgres %}- **pgvector** — PostgreSQL vector extension
{% endif %}{% if redis %}- **Redis** — semantic caching layer
{% endif %}{% if docker %}- **Docker** — containerisation
{% endif %}

## Project Structure

```
{{ project_name }}/
├── main.py                  # Interactive REPL entry point
├── app/
│   ├── config.py            # Typed settings (pydantic-settings)
│   ├── agents/
│   │   ├── __init__.py
│   │   └── assistant.py     # LangGraph ReAct agent
│   ├── chains/
│   │   ├── __init__.py
│   │   └── rag.py           # RAG chain example
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py      # Tool registry (add tools here)
│   │   └── search.py        # Web search tool stub
├── tests/
│   ├── conftest.py
│   ├── test_agent.py
│   └── __init__.py
├── .env.example
├── .gitignore
└── pyproject.toml
```

## Getting Started

```bash
# 1. Copy and configure your secrets
cp .env.example .env
# Edit .env — add your OPENAI_API_KEY

# 2. Run the interactive assistant
uv run python main.py
```

## Using Ollama (Local Models)

```bash
# Install Ollama: https://ollama.com
ollama pull llama3.2

# Update .env
OLLAMA_MODEL=llama3.2
```

Then swap the LLM in `app/agents/assistant.py`:

```python
from langchain_ollama import ChatOllama
self._llm = ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url)
```

## Adding Tools

Edit `app/tools/registry.py` and add your tools to `get_tools()`:

```python
from app.tools.my_tool import my_custom_tool

def get_tools():
    return [web_search_tool, my_custom_tool]
```

## Running Tests

```bash
uv run pytest
```

## LangSmith Tracing (optional)

```bash
# .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_key
LANGCHAIN_PROJECT={{ project_name }}
```
