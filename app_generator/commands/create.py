"""
`appgenerator create` subcommand group.
Delegates to template-specific generators.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from app_generator.generator import (
    ModelFieldSpec,
    ProjectGenerator,
    create_model_file,
    detect_project_template,
)

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


@create_app.command("model", help="Interactively create a model in an existing project.")
def create_model(
    project_path: Path = typer.Option(..., "--project-path", "-p", help="Existing project root path."),
    template: Optional[str] = typer.Option(
        None,
        "--template",
        help="Template type: fastapi | fastapi-with-frontend | ai. Auto-detected if omitted.",
    ),
) -> None:
    resolved = project_path.resolve()
    try:
        detected = detect_project_template(resolved)
    except ValueError as exc:
        console.print(f"[bold red]✗[/] {exc}")
        raise typer.Exit(code=1) from exc
    selected_template = template or detected
    if template and template != detected:
        console.print(
            f"[bold red]✗[/] Template mismatch. Detected [bold]{detected}[/], got [bold]{template}[/]."
        )
        raise typer.Exit(code=1)

    console.print(f"[cyan]Project:[/] {resolved}")
    console.print(f"[cyan]Template:[/] {selected_template}")

    model_name = typer.prompt("Model name", type=str).strip()
    fields: list[ModelFieldSpec] = []

    type_choices = "str/int/float/bool/datetime"
    while typer.confirm("Add a field?", default=not fields):
        field_name = typer.prompt("Field name", type=str).strip().lower().replace("-", "_")
        data_type = typer.prompt(f"Field type ({type_choices})", type=str).strip().lower()
        if data_type not in {"str", "int", "float", "bool", "datetime"}:
            console.print(f"[bold red]✗[/] Unsupported field type: {data_type}")
            raise typer.Exit(code=1)
        required = typer.confirm("Required?", default=True)
        nullable = typer.confirm("Nullable?", default=not required)
        max_length: Optional[int] = None
        if data_type == "str" and typer.confirm("Set max_length?", default=False):
            max_length = typer.prompt("max_length", type=int)

        fields.append(
            ModelFieldSpec(
                name=field_name,
                data_type=data_type,
                required=required,
                nullable=nullable,
                max_length=max_length,
            )
        )

    console.print("\n[bold]Planned output:[/]")
    console.print(f"- app/models/{model_name.lower().replace(' ', '_').replace('-', '_')}.py")
    if not typer.confirm("Continue and create model file?", default=True):
        console.print("[yellow]Aborted. No files were changed.[/]")
        raise typer.Exit(code=1)

    try:
        out = create_model_file(
            project_root=resolved,
            template=selected_template,
            model_name=model_name,
            fields=fields,
        )
    except ValueError as exc:
        console.print(f"[bold red]✗[/] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[bold green]✓[/] Created model: [bold]{out}[/]")


