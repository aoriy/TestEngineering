from pathlib import Path

from sqlalchemy.orm import Session

from app.core.paths import PROJECT_ROOT
from app.services.codegen.generator import generate_api_test
from app.services.codegen.perf import generate_locustfile
from app.services.executor.base import Executor, RunRequest, RunResult


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
        if request.testcase_id is None:
            raise ValueError("testcase_id is required for the perf executor")
        code, host = generate_locustfile(db, request.testcase_id)
        out = _generated_dir(request.run_id)
        out.mkdir(parents=True, exist_ok=True)
        (out / "locustfile.py").write_text(code, encoding="utf-8")
        request.params["host"] = host
        return out

    def build_command(self, request: RunRequest, generated_dir: Path) -> list[str]:
        params = request.params or {}
        host = params.get("host", "")
        users = str(params.get("users", 10))
        spawn_rate = str(params.get("spawn_rate", 1))
        run_time = str(params.get("run_time", "30s"))
        csv_prefix = str(PROJECT_ROOT / "runs" / request.run_id / "stats")
        cmd = [
            "uv",
            "run",
            "locust",
            "-f",
            str(generated_dir / "locustfile.py"),
            "--headless",
            "--only-summary",
            "-u",
            users,
            "-r",
            spawn_rate,
            "-t",
            run_time,
            "--csv",
            csv_prefix,
        ]
        if host:
            cmd += ["--host", host]
        return cmd

    def collect_result(self, request: RunRequest, exit_code: int) -> RunResult:
        result = RunResult(
            run_id=request.run_id,
            exit_code=exit_code,
            status="done" if exit_code == 0 else "failed",
        )
        stats_dir = PROJECT_ROOT / "runs" / request.run_id
        result.artifacts = {
            "csv": {
                name: str(stats_dir / f"stats_{name}.csv")
                for name in ("stats", "failures", "stats_history")
            }
        }
        return result
