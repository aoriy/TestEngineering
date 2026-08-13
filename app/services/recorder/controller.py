"""Recording controller: spawn `playwright codegen` subprocess (ADR-0001)."""

import subprocess
import uuid
from typing import IO

from app.core.paths import PROJECT_ROOT

_sessions: dict[str, dict] = {}


def start(
    page_template_id: int,
    environment_id: int | None,
    url: str,
    flow_id: int | None,
) -> str:
    record_id = uuid.uuid4().hex[:12]
    out_dir = PROJECT_ROOT / "runs" / "records" / record_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "recorded.py"
    fh: IO[str] = out_file.open("w", encoding="utf-8")
    cmd = ["uv", "run", "playwright", "codegen", "--target", "python", url]
    proc = subprocess.Popen(
        cmd,
        cwd=str(PROJECT_ROOT),
        stdout=fh,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    _sessions[record_id] = {
        "proc": proc,
        "fh": fh,
        "out_file": out_file,
        "page_template_id": page_template_id,
        "environment_id": environment_id,
        "flow_id": flow_id,
        "url": url,
    }
    return record_id


def stop(record_id: str) -> dict:
    session = _sessions.pop(record_id, None)
    if session is None:
        raise ValueError(f"record {record_id} not found")
    proc: subprocess.Popen = session["proc"]
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    session["fh"].close()
    code = session["out_file"].read_text(encoding="utf-8", errors="replace")
    return {
        "code": code,
        "page_template_id": session["page_template_id"],
        "flow_id": session["flow_id"],
        "url": session["url"],
    }
