"""
Tests for the PyForge generator and CLI.
These are unit tests that mock filesystem and subprocess calls.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


# ── Generator unit tests ─────────────────────────────────────────────────────

class TestProjectGenerator:
    def _make_generator(self, template: str, tmp_path: Path, **opts):
        from pyforge.generator import ProjectGenerator

        return ProjectGenerator(
            template=template,
            project_name="test_proj",
            target_dir=tmp_path / "test_proj",
            options={"docker": False, "postgres": False, "redis": False, **opts},
        )

    def test_fastapi_template_renders(self, tmp_path):
        gen = self._make_generator("fastapi", tmp_path)
        with (
            patch.object(gen, "_uv_init"),
            patch.object(gen, "_install_deps"),
        ):
            gen.run()

        project = tmp_path / "test_proj"
        assert (project / "pyproject.toml").exists()
        assert (project / "app" / "main.py").exists()
        assert (project / "app" / "config.py").exists()
        assert (project / "app" / "db" / "session.py").exists()
        assert (project / "app" / "models" / "base.py").exists()
        assert (project / "app" / "api" / "v1" / "health.py").exists()
        assert (project / "tests" / "conftest.py").exists()
        assert (project / ".env.example").exists()
        assert (project / ".gitignore").exists()
        assert (project / "README.md").exists()

        pyproject = (project / "pyproject.toml").read_text()
        assert 'build-backend = "uv_build"' in pyproject
        assert 'module-name = "app"' in pyproject
        assert "tool.setuptools" not in pyproject
        assert "tool.hatch" not in pyproject

        env_example = (project / ".env.example").read_text()
        assert "{%" not in env_example
        assert "{{" not in env_example

    def test_ai_template_renders(self, tmp_path):
        gen = self._make_generator("ai", tmp_path)
        with (
            patch.object(gen, "_uv_init"),
            patch.object(gen, "_install_deps"),
        ):
            gen.run()

        project = tmp_path / "test_proj"
        assert (project / "pyproject.toml").exists()
        assert (project / "main.py").exists()
        assert (project / "app" / "config.py").exists()
        assert (project / "app" / "agents" / "assistant.py").exists()
        assert (project / "app" / "chains" / "rag.py").exists()
        assert (project / "app" / "tools" / "registry.py").exists()
        assert (project / "tests" / "test_agent.py").exists()
        assert not (project / "app" / "config" / "__init__.py").exists()

        pyproject = (project / "pyproject.toml").read_text()
        assert 'build-backend = "uv_build"' in pyproject
        assert 'module-name = "app"' in pyproject
        assert "tool.setuptools" not in pyproject
        assert "tool.hatch" not in pyproject

        env_example = (project / ".env.example").read_text()
        assert "{%" not in env_example
        assert "{{" not in env_example

    def test_fastapi_with_frontend_template_renders(self, tmp_path):
        gen = self._make_generator("fastapi-with-frontend", tmp_path)
        with (
            patch.object(gen, "_uv_init"),
            patch.object(gen, "_install_deps"),
        ):
            gen.run()

        project = tmp_path / "test_proj"
        assert (project / "app" / "main.py").exists()
        assert (project / "app" / "templates" / "base.html").exists()
        assert (project / "app" / "templates" / "index.html").exists()
        assert (project / "app" / "templates" / "partials" / "header.html").exists()
        assert (project / "app" / "templates" / "partials" / "footer.html").exists()
        assert (project / "tests" / "test_frontend.py").exists()

        main_py = (project / "app" / "main.py").read_text()
        assert "Jinja2Templates" in main_py
        assert "@application.get(\"/\"" in main_py

    def test_install_deps_uses_no_sync_then_sync(self, tmp_path):
        gen = self._make_generator("fastapi", tmp_path, postgres=True)
        gen.target_dir.mkdir(parents=True, exist_ok=True)

        with patch("pyforge.generator.shutil.which", return_value="uv"), patch.object(
            gen, "_run"
        ) as run_mock:
            gen._install_deps()

        assert run_mock.call_args_list[0].args[0][:3] == ["uv", "add", "--no-sync"]
        assert "aiosqlite" in run_mock.call_args_list[0].args[0]
        assert run_mock.call_args_list[1].args[0][:4] == ["uv", "add", "--no-sync", "--dev"]
        assert run_mock.call_args_list[2].args[0] == ["uv", "sync", "--no-install-project"]

    def test_docker_files_excluded_by_default(self, tmp_path):
        gen = self._make_generator("fastapi", tmp_path, docker=False)
        with (
            patch.object(gen, "_uv_init"),
            patch.object(gen, "_install_deps"),
        ):
            gen.run()

        project = tmp_path / "test_proj"
        assert not (project / "Dockerfile").exists()
        assert not (project / "docker-compose.yml").exists()

    def test_docker_files_included_with_flag(self, tmp_path):
        gen = self._make_generator("fastapi", tmp_path, docker=True)
        with (
            patch.object(gen, "_uv_init"),
            patch.object(gen, "_install_deps"),
        ):
            gen.run()

        project = tmp_path / "test_proj"
        assert (project / "Dockerfile").exists()
        assert (project / "docker-compose.yml").exists()

    def test_project_name_in_pyproject(self, tmp_path):
        gen = self._make_generator("fastapi", tmp_path)
        with (
            patch.object(gen, "_uv_init"),
            patch.object(gen, "_install_deps"),
        ):
            gen.run()

        content = (tmp_path / "test_proj" / "pyproject.toml").read_text()
        assert "test_proj" in content

    def test_context_package_name_sanitises_hyphens(self, tmp_path):
        from pyforge.generator import ProjectGenerator

        gen = ProjectGenerator(
            template="fastapi",
            project_name="my-cool-api",
            target_dir=tmp_path / "my-cool-api",
            options={"docker": False, "postgres": False, "redis": False},
        )
        ctx = gen._build_context()
        assert ctx["package_name"] == "my_cool_api"

    def test_existing_directory_raises(self, tmp_path):
        from typer.testing import CliRunner
        from pyforge.main import app

        (tmp_path / "existing_proj").mkdir()
        runner = CliRunner()
        result = runner.invoke(
            app, ["create", "fastapi", "existing_proj", "--output", str(tmp_path)]
        )
        assert result.exit_code != 0


# ── CLI smoke tests ───────────────────────────────────────────────────────────

class TestCLI:
    def test_help(self):
        from typer.testing import CliRunner
        from pyforge.main import app

        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "create" in result.output

    def test_version(self):
        from typer.testing import CliRunner
        from pyforge.main import app
        from pyforge import __version__

        runner = CliRunner()
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_create_help(self):
        from typer.testing import CliRunner
        from pyforge.main import app

        runner = CliRunner()
        result = runner.invoke(app, ["create", "--help"])
        assert result.exit_code == 0
        assert "fastapi" in result.output
        assert "fastapi-with-frontend" in result.output
        assert "ai" in result.output
