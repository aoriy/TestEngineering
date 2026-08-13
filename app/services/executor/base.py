"""Executor abstraction (ADR-0002).

Every execution type (api/ui/perf) implements this interface. The runner
spawns worker subprocesses (ADR-0001) — the FastAPI process never runs tests.
"""

import abc
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.orm import Session


@dataclass
class RunRequest:
    run_id: str
    testcase_id: int | None = None
    environment_id: int | None = None
    params: dict = field(default_factory=dict)


@dataclass
class RunResult:
    run_id: str
    exit_code: int | None = None
    status: str = "pending"
    report_path: str = ""
    artifacts: dict = field(default_factory=dict)


class Executor(abc.ABC):
    key: str = "base"

    @abc.abstractmethod
    def generate_code(self, db: Session, request: RunRequest) -> Path:
        """Generate executable code into runs/<run_id>/generated/ and return its dir."""

    @abc.abstractmethod
    def build_command(self, request: RunRequest, generated_dir: Path) -> list[str]:
        """Return the subprocess command list (argv) to run the test."""

    def collect_result(self, request: RunRequest, exit_code: int) -> RunResult:
        """Map subprocess exit code to a RunResult (can be overridden)."""
        return RunResult(
            run_id=request.run_id,
            exit_code=exit_code,
            status="done" if exit_code == 0 else "failed",
        )
