"""Executor abstraction (ADR-0002).

Every execution type (api/ui/perf) implements this interface. The runner
spawns worker subprocesses (ADR-0001) — the FastAPI process never runs tests.
"""

import abc
from dataclasses import dataclass, field


@dataclass
class RunRequest:
    run_id: str
    testcase_id: int | None
    environment: dict = field(default_factory=dict)
    variables: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)


@dataclass
class RunResult:
    run_id: str
    exit_code: int | None = None
    status: str = "pending"
    log_path: str = ""
    report_path: str = ""
    artifacts: dict = field(default_factory=dict)


class Executor(abc.ABC):
    key: str = "base"

    @abc.abstractmethod
    def generate_code(self, request: RunRequest) -> str:
        """Generate executable code under runs/<run_id>/generated/.

        Returns the directory path containing the generated files.
        """

    @abc.abstractmethod
    def build_command(self, request: RunRequest, generated_dir: str) -> list[str]:
        """Return the subprocess command list (argv) to run the test."""

    def collect_result(self, request: RunRequest, exit_code: int) -> RunResult:
        """Map subprocess exit code to a RunResult (can be overridden)."""
        return RunResult(
            run_id=request.run_id,
            exit_code=exit_code,
            status="done" if exit_code == 0 else "failed",
        )
