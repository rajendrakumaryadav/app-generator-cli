# AGENTS.md

## Purpose
- `pyforge` is a Typer CLI that scaffolds complete project directories from in-repo templates (`fastapi`, `ai`) and optionally bootstraps deps with `uv`.
- Primary goal when editing: keep generated output stable and predictable for CLI users.

## Architecture At A Glance
- CLI entrypoint: `pyforge/main.py` (`app`), with `appgenerator` and `pyforge` console scripts defined in `pyproject.toml` under `[project.scripts]`.
- Command routing: `pyforge/commands/create.py` exposes `create fastapi` and `create ai`, both delegating to `_run_generator(...)`.
- Generation engine: `pyforge/generator.py` (`ProjectGenerator`) handles render + optional `uv` setup + dependency install.
- Template boundary: all scaffold content lives under `pyforge/templates/<template>/...`; generator should stay generic.

## Critical Data Flow
- User command (`appgenerator create ...`; alias: `pyforge create ...`) -> `_run_generator(...)` -> `ProjectGenerator.run()`.
- `run()` executes in order: `_render_template()` -> `_uv_init()` -> `_install_deps()` -> `_print_success()`.
- Render context is built in `_build_context()` (`project_name`, `package_name`, `docker`, `postgres`, `redis`, etc.) and fed into Jinja templates.
- Optional file inclusion is controlled by `_should_skip(...)`; `Dockerfile` and `docker-compose.yml` are skipped unless `--docker`, and `postgres` / `redis` paths are skipped unless their flags are enabled.

## Repo-Specific Conventions
- Edit `pyforge/generator.py` as the single active generation engine used by CLI commands.
- `TEMPLATES_DIR` in active generator points to `pyforge/templates`; preserve this package-relative behavior.
- Treat text-like files as Jinja-renderable (see suffix list in `_render_template()`), with binary fallback via `shutil.copy2`.
- Package name normalization is expected: hyphens/spaces -> underscores (`tests/test_generator.py::test_context_package_name_sanitises_hyphens`).

## Developer Workflows (Validated From Repo Docs)
- Local install/dev sync (from root): `uv sync --dev`
- Run CLI locally: `uv run appgenerator --help` (alias: `uv run pyforge --help`)
- Run tests: `uv run pytest`
- Lint/format: `uv run ruff check .` and `uv run ruff format .`

## Testing Priorities For Changes
- Main safety net: `tests/test_generator.py` (template render assertions, Docker flag behavior, CLI smoke tests).
- If changing output structure, update both template files and tests that assert exact generated paths.
- If changing version behavior, align `tests/test_generator.py::test_version` with package metadata exposed via `pyforge/__init__.py`.

## Integration Notes
- External runtime dependency is `uv`; generator intentionally no-ops uv steps when missing (`_uv_init`, `_install_deps`).
- Dependency bootstrap flow is `uv add --no-sync` (runtime/dev deps) followed by `uv sync --no-install-project`; keep this behavior aligned with `tests/test_generator.py::test_install_deps_uses_no_sync_then_sync`.
- Generated template READMEs under `pyforge/templates/{fastapi,ai}/README.md` define user-facing post-scaffold run paths; keep them aligned with actual generated files.
