"""
`appgenerator create` subcommand group.
Delegates to template-specific generators.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from pyforge.generator import ProjectGenerator

create_app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
console = Console()


def _run_generator(
    template: str,
    project_name: str,
    output_dir: Optional[Path],
    docker: bool,
    postgres: bool,
    redis: bool,
) -> None:
    target = (output_dir or Path.cwd()) / project_name
    if target.exists():
        console.print(f"[bold red]✗[/] Directory [bold]{target}[/] already exists.")
        raise typer.Exit(code=1)

    generator = ProjectGenerator(
        template=template,
        project_name=project_name,
        target_dir=target,
        options={"docker": docker, "postgres": postgres, "redis": redis},
    )
    generator.run()


@create_app.command("fastapi", help="Scaffold a [bold]FastAPI[/] backend project.")
def create_fastapi(
    project_name: str = typer.Argument(..., help="Name of the new project."),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Parent directory."),
    docker: bool = typer.Option(False, "--docker", help="Add Dockerfile & docker-compose.yml."),
    postgres: bool = typer.Option(False, "--postgres", help="Add PostgreSQL support."),
    redis: bool = typer.Option(False, "--redis", help="Add Redis support."),
) -> None:
    _run_generator("fastapi", project_name, output_dir, docker, postgres, redis)


@create_app.command(
    "fastapi-with-frontend",
    help="Scaffold a [bold]FastAPI + Jinja frontend[/] project.",
)
def create_fastapi_with_frontend(
    project_name: str = typer.Argument(..., help="Name of the new project."),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Parent directory."),
    docker: bool = typer.Option(False, "--docker", help="Add Dockerfile & docker-compose.yml."),
    postgres: bool = typer.Option(False, "--postgres", help="Add PostgreSQL support."),
    redis: bool = typer.Option(False, "--redis", help="Add Redis support."),
) -> None:
    _run_generator("fastapi-with-frontend", project_name, output_dir, docker, postgres, redis)


@create_app.command("ai", help="Scaffold a [bold]LangChain / LangGraph[/] AI project.")
def create_ai(
    project_name: str = typer.Argument(..., help="Name of the new project."),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Parent directory."),
    docker: bool = typer.Option(False, "--docker", help="Add Dockerfile & docker-compose.yml."),
    postgres: bool = typer.Option(False, "--postgres", help="Add PostgreSQL vector DB support."),
    redis: bool = typer.Option(False, "--redis", help="Add Redis cache support."),
) -> None:
    _run_generator("ai", project_name, output_dir, docker, postgres, redis)
