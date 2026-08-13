from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ApiDefinition, Project
from app.schemas import ApiDefinitionCreate, ApiDefinitionRead

router = APIRouter(prefix="/api-definitions", tags=["api-definitions"])


@router.get("", response_model=list[ApiDefinitionRead])
def list_definitions(project_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(ApiDefinition)
    if project_id is not None:
        q = q.filter(ApiDefinition.project_id == project_id)
    return q.order_by(ApiDefinition.id).all()


@router.post("", response_model=ApiDefinitionRead)
def create_definition(payload: ApiDefinitionCreate, db: Session = Depends(get_db)):
    if db.get(Project, payload.project_id) is None:
        raise HTTPException(404, "project not found")
    obj = ApiDefinition(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{definition_id}", response_model=ApiDefinitionRead)
def get_definition(definition_id: int, db: Session = Depends(get_db)):
    obj = db.get(ApiDefinition, definition_id)
    if obj is None:
        raise HTTPException(404, "api definition not found")
    return obj


@router.delete("/{definition_id}", status_code=204)
def delete_definition(definition_id: int, db: Session = Depends(get_db)):
    obj = db.get(ApiDefinition, definition_id)
    if obj is None:
        raise HTTPException(404, "api definition not found")
    db.delete(obj)
    db.commit()
