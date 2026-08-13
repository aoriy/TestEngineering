import subprocess
from pathlib import Path
from typing import Iterator

from app.core.config import settings
from app.core.paths import PROJECT_ROOT


def run_dir_for(run_id: str) -> Path:
    return PROJECT_ROOT / settings.runs_dir / run_id


def spawn(command: list[str], run_id: str, log_path: Path) -> subprocess.Popen:
    """Spawn a worker subprocess rooted at the project dir (ADR-0001)."""
    run_dir_for(run_id).mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(
        command,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def stream_to_log(proc: subprocess.Popen, log_path: Path) -> Iterator[str]:
    """Consume stdout lines into the log file; yields each line."""
    assert proc.stdout is not None
    with log_path.open("w", encoding="utf-8") as fh:
        for line in proc.stdout:
            fh.write(line)
            yield line
        proc.wait()
        proc.stdout.close()
