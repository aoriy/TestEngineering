import subprocess
from pathlib import Path
from typing import Iterator

from app.core.config import settings
from app.services.executor.base import Executor, RunRequest, RunResult


def run_dir_for(run_id: str) -> Path:
    return Path(settings.runs_dir) / run_id


def spawn_and_stream(
    executor: Executor, request: RunRequest
) -> tuple[RunResult, Iterator[str]]:
    """Generate code, spawn a worker subprocess, yield log lines.

    The FastAPI process never runs tests — this is the ADR-0001 boundary.
    """
    generated_dir = executor.generate_code(request)
    cmd = executor.build_command(request, generated_dir)
    log_path = run_dir_for(request.run_id) / "log.txt"

    proc = subprocess.Popen(
        cmd,
        cwd=str(run_dir_for(request.run_id)),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    def _lines() -> Iterator[str]:
        assert proc.stdout is not None
        with log_path.open("w", encoding="utf-8") as fh:
            for line in proc.stdout:
                fh.write(line)
                yield line
        proc.wait()
        proc.stdout.close()

    return (
        RunResult(run_id=request.run_id, log_path=str(log_path)),
        _lines(),
    )
