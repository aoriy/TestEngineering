import threading
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.models import TestCase, TestRun
from app.schemas import RunCreate, TestRunRead
from app.services.executor.runner import run_dir_for, spawn, stream_to_log
from app.services.registry import executor_registry

router = APIRouter(prefix="/runs", tags=["runs"])


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("", response_model=list[TestRunRead])
def list_runs(db: Session = Depends(get_db)):
    return db.query(TestRun).order_by(TestRun.id.desc()).limit(50).all()


@router.get("/{run_id}", response_model=TestRunRead)
def get_run(run_id: str, db: Session = Depends(get_db)):
    obj = db.query(TestRun).filter(TestRun.run_id == run_id).first()
    if obj is None:
        raise HTTPException(404, "run not found")
    return obj


@router.get("/{run_id}/log", response_class=PlainTextResponse)
def get_run_log(run_id: str, db: Session = Depends(get_db)):
    obj = db.query(TestRun).filter(TestRun.run_id == run_id).first()
    if obj is None or not obj.log_path:
        raise HTTPException(404, "run or log not found")
    try:
        return (run_dir_for(run_id) / "log.txt").read_text(
            encoding="utf-8", errors="replace"
        )
    except FileNotFoundError:
        return ""


@router.get("/{run_id}/report")
def get_run_report(run_id: str, db: Session = Depends(get_db)):
    obj = db.query(TestRun).filter(TestRun.run_id == run_id).first()
    if obj is None:
        raise HTTPException(404, "run not found")
    report = run_dir_for(run_id) / "report.html"
    if not report.exists():
        raise HTTPException(404, "report not found")
    return FileResponse(report, media_type="text/html")


@router.post("", response_model=TestRunRead)
def create_run(payload: RunCreate, db: Session = Depends(get_db)):
    tc = db.get(TestCase, payload.testcase_id)
    if tc is None:
        raise HTTPException(404, "testcase not found")
    if payload.executor not in executor_registry.keys():
        raise HTTPException(422, f"unknown executor: {payload.executor}")

    run_id = uuid.uuid4().hex[:16]
    obj = TestRun(
        run_id=run_id,
        testcase_id=payload.testcase_id,
        environment_id=payload.environment_id,
        status="pending",
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)

    _launch(obj.id, run_id, payload)
    return obj


def _launch(run_db_id: int, run_id: str, payload: RunCreate) -> None:
    def work() -> None:
        db = SessionLocal()
        try:
            run = db.get(TestRun, run_db_id)
            if run is None:
                return
            run.status = "running"
            run.started_at = _now()
            run.runs_dir = str(run_dir_for(run_id))
            run.log_path = str(run_dir_for(run_id) / "log.txt")
            run.report_path = str(run_dir_for(run_id) / "report.html")
            db.commit()

            executor = executor_registry.get(payload.executor)
            request = _request(run_id, payload)
            generated_dir = executor.generate_code(db, request)
            command = executor.build_command(request, generated_dir)

            proc = spawn(command, run_id, run_dir_for(run_id) / "log.txt")
            for _ in stream_to_log(proc, run_dir_for(run_id) / "log.txt"):
                pass

            result = executor.collect_result(request, proc.returncode)
            run.status = result.status
            run.exit_code = proc.returncode
            run.finished_at = _now()
            if result.artifacts:
                run.artifacts = result.artifacts
            db.commit()
        except Exception as exc:  # noqa: BLE001
            run = db.get(TestRun, run_db_id)
            if run is not None:
                run.status = "failed"
                run.exit_code = -1
                run.finished_at = _now()
                run.artifacts = {"error": str(exc)}
                db.commit()
        finally:
            db.close()

    threading.Thread(target=work, daemon=True).start()


def _request(run_id: str, payload: RunCreate):
    from app.services.executor.base import RunRequest

    return RunRequest(
        run_id=run_id,
        testcase_id=payload.testcase_id,
        environment_id=payload.environment_id,
        params=dict(payload.params or {}),
    )
