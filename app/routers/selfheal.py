from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import SelfHealRecord
from app.schemas import SelfHealRequest
from app.services.selfheal import service

router = APIRouter(prefix="/selfheal", tags=["selfheal"])


@router.post("")
def self_heal(payload: SelfHealRequest, db: Session = Depends(get_db)):
    try:
        return service.self_heal(
            db,
            payload.shape_id,
            payload.old_locator,
            page_html=payload.page_html,
            old_meta=payload.old_meta,
            run_id=payload.run_id,
        )
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc


@router.post("/rollback")
def rollback(shape_id: int, db: Session = Depends(get_db)):
    try:
        return service.rollback(db, shape_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/records")
def list_records(shape_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(SelfHealRecord)
    if shape_id is not None:
        q = q.filter(SelfHealRecord.shape_id == shape_id)
    return q.order_by(SelfHealRecord.id.desc()).limit(100).all()
