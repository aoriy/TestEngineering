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

## Commands

| Task | Command |
|------|---------|
| Sync env | `uv sync` |
| Run tests | `uv run pytest` |
| Run a single test | `uv run pytest tests/test_foo.py::test_name` |
| Add dependency | `uv add <pkg>` |
| Add dev dependency | `uv add --dev <pkg>` |