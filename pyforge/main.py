"""
AppGenerator CLI — A scaffolding tool for FastAPI and LangChain/LangGraph projects.
"""
import typer
from rich.console import Console

from pyforge.commands.create import create_app

app = typer.Typer(
    name="appgenerator",
    help="⚒️  AppGenerator — Scaffold production-ready Python projects instantly.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()

app.add_typer(create_app, name="create", help="Create a new project from a template.")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit."),
) -> None:
    if version:
        from pyforge import __version__
        console.print(f"[bold cyan]AppGenerator[/] version [bold]{__version__}[/]")
        raise typer.Exit()


if __name__ == "__main__":
    app()
