# AGENTS.md

Guidance for OpenCode agents working in this repository.

## Environment

- Python virtual environment is managed with **uv**, not pip/venv directly.
  - Create/sync the env: `uv sync` (creates `.venv/` and regenerates `uv.lock`)
  - Run anything in the env: `uv run <cmd>` (e.g. `uv run pytest`)
  - Add a dependency: `uv add <pkg>` (updates `pyproject.toml` + `uv.lock`)
  - Python is pinned via `.python-version` (currently 3.12)
- `.venv/` is gitignored; `uv.lock` is tracked — commit it after dependency changes.
- Windows: uv may warn "Failed to hardlink files; falling back to full copy" — harmless (cache and target on different filesystems). Silence with `export UV_LINK_MODE=copy` if noisy.

## Workflow

- Version control: git, default branch `main`. Remote `origin` tracked; **remote pushes are handled by the user** — agents commit to local only, do not run `git push`.
- **Commit every significant change** — after each major feature, refactor, or fix, stage and commit with a clear message. Do not let uncommitted work accumulate across unrelated changes.
- Line endings are not normalized (no `.gitattributes`); expect CRLF warnings on Windows — harmless, but prefer LF when editing.
- Tests are managed by pytest with `testpaths = ["tests"]` (configured in `pyproject.toml`). The `tests/` directory does not exist yet — create it when adding the first test.

## Architecture (see docs/architecture-review.md for full design)

- **Execution isolation iron law**: pytest / Playwright / Locust run in **worker subprocesses**, NEVER in the FastAPI process. FastAPI only orchestrates. Use `app/services/executor/` abstraction.
- **Code hooks safety**: user Python in shapes runs behind AST import whitelist + subprocess + controlled `ctx` (only `get_var/set_var/log/call_api/sleep/fail`). No `os`/`subprocess`/`open`.
- **Variables**: use the simple `{{var}}` regex substitution engine, NOT Jinja2 full syntax (injection-proof). Jinja2 is for code-gen templates only.
- **Generated code & run artifacts** go to `runs/<run_id>/` (gitignored); DB stores paths.
- **Plugins via registry**: `Executor` / `ShapeType` / `Reporter` are registry-based — add implementations, don't edit core.

## Coding conventions

### Python (backend, `app/`)

- Style: **black** formatting, **flake8** lint, **mypy** typecheck (all in `dev` extras). Run: `uv run black .`, `uv run flake8 app`, `uv run mypy app`.
- Use SQLAlchemy 2.0 style: `Mapped[...]` + `mapped_column(...)` (see `app/models/`).
- Pydantic v2: `model_config = ConfigDict(from_attributes=True)` for read models (see `app/schemas/schemas.py`).
- Routers live in `app/routers/` (one file per resource); schemas in `app/schemas/`; services (executor/codegen/selfheal/registry) in `app/services/`.
- New executor/shape-type/reporter = add an implementation + register it in the registry — do NOT edit core.

### Vue/TS (frontend, `frontend/`)

- Vue 3 `<script setup lang="ts">` + Composition API.
- Typecheck via `vue-tsc` (`npm run build` runs `vue-tsc -b && vite build`). Keep `noUnusedLocals`/`noUnusedParameters` clean.
- Element Plus components; state in `ref`/`reactive`; API calls via `fetch('/api/...')` (Vite proxy handles `/api`).
- Route pages live in `src/views/`; shared router in `src/router.ts`.

### General

- Commit messages: `<type>(<scope>): <summary>` where type ∈ `feat`/`docs`/`refactor`/`fix`; tag phases (`feat(phase0)`, `feat(phase1)`, ...).
- No comments unless they clarify a non-obvious "why" (architecture invariants excepted).

## Commands

| Task | Command |
|------|---------|
| Sync env | `uv sync` |
| Run tests | `uv run pytest` |
| Run a single test | `uv run pytest tests/test_foo.py::test_name` |
| Add dependency | `uv add <pkg>` |
| Add dev dependency | `uv add --dev <pkg>` |
| Backend dev server | `uv run uvicorn app.main:app --reload` |
| Frontend dev server | `cd frontend; npm run dev` |
| Frontend typecheck+build | `cd frontend; npm run build` |