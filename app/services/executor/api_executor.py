from pathlib import Path

from sqlalchemy.orm import Session

from app.core.paths import PROJECT_ROOT
from app.services.codegen.generator import generate_api_test
from app.services.executor.base import Executor, RunRequest


def _generated_dir(run_id: str) -> Path:
    return PROJECT_ROOT / "runs" / run_id / "generated"


def _report_path(run_id: str) -> Path:
    return PROJECT_ROOT / "runs" / run_id / "report.html"


class ApiExecutor(Executor):
    key = "api"

    def generate_code(self, db: Session, request: RunRequest) -> Path:
        if request.testcase_id is None:
            raise ValueError("testcase_id is required for the api executor")
        code = generate_api_test(db, request.testcase_id)
        out = _generated_dir(request.run_id)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"test_case_{request.testcase_id}.py").write_text(code, encoding="utf-8")
        return out

    def build_command(self, request: RunRequest, generated_dir: Path) -> list[str]:
        return [
            "uv",
            "run",
            "python",
            "-m",
            "pytest",
            str(generated_dir),
            "--html",
            str(_report_path(request.run_id)),
            "--self-contained-html",
            "-q",
        ]


class UiExecutor(Executor):
    key = "ui"

    def generate_code(self, db: Session, request: RunRequest) -> Path:
        # Phase 3.x: Playwright POM codegen. Requires `playwright install`.
        raise NotImplementedError("UI executor codegen is not implemented yet")

    def build_command(self, request: RunRequest, generated_dir: Path) -> list[str]:
        return ["uv", "run", "python", "-m", "pytest", str(generated_dir), "-q"]


class PerfExecutor(Executor):
    key = "perf"

    def generate_code(self, db: Session, request: RunRequest) -> Path:
        # Phase 4: locustfile.py from ApiDefinition.
        raise NotImplementedError("perf executor codegen is not implemented yet")

    def build_command(self, request: RunRequest, generated_dir: Path) -> list[str]:
        return ["uv", "run", "locust", "-f", str(generated_dir), "--headless"]
