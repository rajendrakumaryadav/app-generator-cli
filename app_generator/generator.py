"""
Core project generation engine.
Handles file rendering, uv init, and dependency installation.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

# Package root — templates live here
TEMPLATES_DIR = Path(__file__).parent / "templates"


class ProjectGenerator:
    """Renders a project template and initialises it with uv."""

    FASTAPI_DEPS = [
        "fastapi",
        "uvicorn[standard]",
        "sqlmodel",
        "aiosqlite",
        "pydantic",
        "pydantic-settings",
        "python-dotenv",
        "alembic",
        "httpx",
    ]
    FASTAPI_DEV_DEPS = ["pytest", "pytest-asyncio", "httpx", "ruff", "mypy"]

    FASTAPI_FRONTEND_DEPS = FASTAPI_DEPS + ["jinja2"]
    FASTAPI_FRONTEND_DEV_DEPS = FASTAPI_DEV_DEPS

    AI_DEPS = [
        "langchain",
        "langgraph",
        "langchain-community",
        "langchain-openai",
        "langchain-ollama",
        "langchain-chroma",
        "chromadb",
        "openai",
        "tiktoken",
        "python-dotenv",
        "pydantic",
        "pydantic-settings",
        "httpx",
    ]
    AI_DEV_DEPS = ["pytest", "pytest-asyncio", "ruff", "mypy"]

    TEMPLATE_DEPS: dict[str, list[str]] = {
        "fastapi": FASTAPI_DEPS,
        "fastapi-with-frontend": FASTAPI_FRONTEND_DEPS,
        "ai": AI_DEPS,
    }
    TEMPLATE_DEV_DEPS: dict[str, list[str]] = {
        "fastapi": FASTAPI_DEV_DEPS,
        "fastapi-with-frontend": FASTAPI_FRONTEND_DEV_DEPS,
        "ai": AI_DEV_DEPS,
    }

    OPTIONAL_DEPS: dict[str, list[str]] = {
        "postgres": ["asyncpg", "psycopg2-binary"],
        "redis": ["redis", "hiredis"],
    }

    MODEL_TEMPLATES = {"fastapi", "fastapi-with-frontend", "ai"}

    def __init__(
        self,
        template: str,
        project_name: str,
        target_dir: Path,
        options: dict[str, Any],
    ) -> None:
        self.template = template  # "fastapi" | "ai"
        self.project_name = project_name
        self.target_dir = target_dir
        self.options = options
        self.template_dir = TEMPLATES_DIR / template
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            keep_trailing_newline=True,
        )

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    def run(self) -> None:
        console.print()
        console.print(
            Panel.fit(
                f"[bold cyan]⚒  AppGenerator[/]  ·  Creating [bold]{self.project_name}[/] "
                f"([italic]{self.template}[/] template)",
                border_style="cyan",
            )
        )
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            t = progress.add_task("Rendering template files …", total=None)
            self._render_template()
            progress.update(t, description="[green]✓[/] Template files written")

            progress.update(t, description="Initialising uv project …", completed=None)
            self._uv_init()
            progress.update(t, description="[green]✓[/] uv project initialised")

            progress.update(t, description="Installing dependencies …", completed=None)
            self._install_deps()
            progress.update(t, description="[green]✓[/] Dependencies installed")

        self._print_success()

    # ------------------------------------------------------------------ #
    #  Steps
    # ------------------------------------------------------------------ #

    def _render_template(self) -> None:
        """Walk the template directory, render Jinja files, copy static files."""
        ctx = self._build_context()

        for src in self.template_dir.rglob("*"):
            if src.is_dir():
                continue

            rel = src.relative_to(self.template_dir)
            dest = self.target_dir / rel

            # Skip optional files based on flags
            if self._should_skip(rel):
                continue

            dest.parent.mkdir(parents=True, exist_ok=True)

            if src.suffix in {".py", ".toml", ".env", ".yml", ".yaml", ".md", ".txt", ".cfg", ".ini", ".dockerfile", ""} or src.name == ".env.example":
                try:
                    template = self.env.get_template(str(rel).replace("\\", "/"))
                    dest.write_text(template.render(**ctx), encoding="utf-8")
                except Exception:
                    # Binary or unparseable — just copy
                    shutil.copy2(src, dest)
            else:
                shutil.copy2(src, dest)

    def _uv_init(self) -> None:
        """Run `uv init` inside the target directory (no-op if uv not found)."""
        if not shutil.which("uv"):
            console.print(
                "[yellow]⚠[/]  [bold]uv[/] not found — skipping venv initialisation. "
                "Install uv: [link=https://docs.astral.sh/uv/]https://docs.astral.sh/uv/[/link]"
            )
            return

        # uv init creates a pyproject.toml — we already created ours, so just create the venv
        self._run(["uv", "venv"], cwd=self.target_dir)

    def _install_deps(self) -> None:
        """Write dependencies into pyproject.toml and sync the venv.

        Uses --no-sync on `uv add` so uv only updates pyproject.toml + uv.lock
        without trying to build/install the generated project itself as an
        editable package.

        The actual installation is done by a follow-up
        `uv sync --no-install-project`.
        """
        if not shutil.which("uv"):
            return

        deps = self.TEMPLATE_DEPS.get(self.template)
        dev_deps = self.TEMPLATE_DEV_DEPS.get(self.template)
        if deps is None or dev_deps is None:
            console.print(f"[red]Unknown template:[/] {self.template}")
            sys.exit(1)

        for flag, pkgs in self.OPTIONAL_DEPS.items():
            if self.options.get(flag):
                deps = deps + pkgs

        # --no-sync: only pin versions into pyproject.toml / uv.lock, don't build project
        self._run(["uv", "add", "--no-sync"] + deps, cwd=self.target_dir)
        self._run(["uv", "add", "--no-sync", "--dev"] + dev_deps, cwd=self.target_dir)

        # Install all pinned deps into .venv, skipping the project root package
        self._run(["uv", "sync", "--no-install-project"], cwd=self.target_dir)

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def _build_context(self) -> dict[str, Any]:
        pkg = self.project_name.lower().replace("-", "_").replace(" ", "_")
        return {
            "project_name": self.project_name,
            "package_name": pkg,
            "template": self.template,
            "docker": self.options.get("docker", False),
            "postgres": self.options.get("postgres", False),
            "redis": self.options.get("redis", False),
            "fastapi_deps": self.FASTAPI_DEPS,
            "ai_deps": self.AI_DEPS,
        }

    def _should_skip(self, rel: Path) -> bool:
        name = rel.name
        parts = set(rel.parts)
        if name in {"Dockerfile", "docker-compose.yml"} and not self.options.get("docker"):
            return True
        if "postgres" in parts and not self.options.get("postgres"):
            return True
        if "redis" in parts and not self.options.get("redis"):
            return True
        return False

    def _run(self, cmd: list[str], cwd: Path) -> None:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            console.print(f"[red]Command failed:[/] {' '.join(cmd)}")
            console.print(result.stderr)
            sys.exit(result.returncode)

    def _print_success(self) -> None:
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold green")
        table.add_column()

        rel = self.target_dir.resolve()
        run_cmd = (
            "uvicorn app.main:app --reload"
            if self.template in {"fastapi", "fastapi-with-frontend"}
            else "python main.py"
        )

        table.add_row("Project:", str(rel))
        table.add_row("Template:", self.template)
        table.add_row("venv:", str(rel / ".venv"))
        table.add_row("", "")
        table.add_row("Next steps:", f"cd {self.project_name}")
        table.add_row("", "cp .env.example .env  # fill in your secrets")
        table.add_row("", f"uv run {run_cmd}")

        console.print(
            Panel(table, title="[bold green]✓  Project created[/]", border_style="green")
        )
        console.print()


@dataclass(slots=True)
class ModelFieldSpec:
    name: str
    data_type: str
    required: bool = True
    nullable: bool = False
    max_length: int | None = None


def detect_project_template(project_root: Path) -> str:
    if (project_root / "app" / "templates").exists() and (project_root / "app" / "models" / "base.py").exists():
        return "fastapi-with-frontend"
    if (project_root / "app" / "models" / "base.py").exists():
        return "fastapi"
    if (project_root / "app" / "agents").exists() and (project_root / "app" / "chains").exists():
        return "ai"
    raise ValueError(f"Unable to detect template type for existing project: {project_root}")


def validate_model_generation(project_root: Path, template: str) -> None:
    if not project_root.exists() or not project_root.is_dir():
        raise ValueError(f"Project path does not exist: {project_root}")
    if template not in ProjectGenerator.MODEL_TEMPLATES:
        raise ValueError(f"Unsupported template for model generation: {template}")
    if not (project_root / "app").exists():
        raise ValueError("Project must contain an app/ directory")
    if template in {"fastapi", "fastapi-with-frontend"} and not (project_root / "app" / "models" / "base.py").exists():
        raise ValueError("FastAPI project missing app/models/base.py; expected scaffolded FastAPI structure")


def create_model_file(
    project_root: Path,
    template: str,
    model_name: str,
    fields: list[ModelFieldSpec],
) -> Path:
    validate_model_generation(project_root, template)

    models_dir = (project_root / "app" / "models").resolve()
    models_dir.mkdir(parents=True, exist_ok=True)

    safe_model_file = f"{_to_snake(model_name)}.py"
    dest = (models_dir / safe_model_file).resolve()
    if models_dir not in dest.parents:
        raise ValueError("Model file path must stay within app/models")

    source = _build_sqlmodel_source(model_name, fields) if template in {"fastapi", "fastapi-with-frontend"} else _build_pydantic_source(model_name, fields)
    dest.write_text(source, encoding="utf-8")
    return dest


def _to_snake(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in name.strip())
    out = []
    prev_lower = False
    for ch in cleaned:
        if ch.isupper() and prev_lower:
            out.append("_")
        out.append(ch.lower())
        prev_lower = ch.isalpha() and ch.islower()
    return "".join(out).strip("_") or "model"


def _to_class(name: str) -> str:
    parts = [p for p in _to_snake(name).split("_") if p]
    return "".join(part.capitalize() for part in parts) or "Model"


def _field_annotation(data_type: str, required: bool) -> str:
    return data_type if required else f"{data_type} | None"


def _build_sqlmodel_source(model_name: str, fields: list[ModelFieldSpec]) -> str:
    class_name = _to_class(model_name)
    imports: list[str] = []
    if any(field.data_type == "datetime" for field in fields):
        imports.extend(["from datetime import datetime", ""])
    imports.extend(["from sqlmodel import Field", "", "from app.models.base import BaseModel", ""])
    lines = [f"class {class_name}(BaseModel, table=True):", f"    __tablename__ = \"{_to_snake(model_name)}s\"", ""]

    if not fields:
        lines.append("    pass")
        return "\n".join(imports + lines) + "\n"

    for field in fields:
        safe_field_name = _to_snake(field.name)
        annotation = _field_annotation(field.data_type, field.required)
        args: list[str] = []
        if not field.required:
            args.append("default=None")
        args.append(f"nullable={field.nullable}")
        if field.max_length is not None and field.data_type == "str":
            args.append(f"max_length={field.max_length}")
        lines.append(f"    {safe_field_name}: {annotation} = Field({', '.join(args)})")

    return "\n".join(imports + lines) + "\n"


def _build_pydantic_source(model_name: str, fields: list[ModelFieldSpec]) -> str:
    class_name = _to_class(model_name)
    lines: list[str] = []
    if any(field.data_type == "datetime" for field in fields):
        lines.extend(["from datetime import datetime", ""])
    lines.extend(["from pydantic import BaseModel, Field", "", f"class {class_name}(BaseModel):"])

    if not fields:
        lines.append("    pass")
        return "\n".join(lines) + "\n"

    for field in fields:
        safe_field_name = _to_snake(field.name)
        annotation = _field_annotation(field.data_type, field.required)
        if field.required:
            default_expr = "Field(...)"
        else:
            extras: list[str] = ["default=None"]
            if field.max_length is not None and field.data_type == "str":
                extras.append(f"max_length={field.max_length}")
            default_expr = f"Field({', '.join(extras)})"
        lines.append(f"    {safe_field_name}: {annotation} = {default_expr}")

    return "\n".join(lines) + "\n"


