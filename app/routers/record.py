from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Environment, PageTemplate
from app.schemas import RecordStart, RecordStop
from app.services.recorder import controller, parser, service

router = APIRouter(prefix="/record", tags=["record"])


@router.post("/start")
def start_recording(payload: RecordStart, db: Session = Depends(get_db)):
    tpl = db.get(PageTemplate, payload.page_template_id)
    if tpl is None:
        raise HTTPException(404, "page template not found")
    env = (
        db.get(Environment, payload.environment_id) if payload.environment_id else None
    )
    base = env.base_url if env else ""
    url = base + (tpl.url or "")
    record_id = controller.start(
        payload.page_template_id, payload.environment_id, url, payload.flow_id
    )
    return {"record_id": record_id, "url": url}


@router.post("/stop")
def stop_recording(payload: RecordStop, db: Session = Depends(get_db)):
    try:
        result = controller.stop(payload.record_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

    actions = parser.parse_recorded_code(result["code"])
    imported = service.import_recording(
        db,
        result["page_template_id"],
        actions,
        flow_id=result.get("flow_id"),
    )
    return {
        "url": result["url"],
        "actions": [asdict(a) for a in actions],
        **imported,
    }
