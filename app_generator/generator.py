"""
Core project generation engine.
Handles file rendering, uv init, and dependency installation.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
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
