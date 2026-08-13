from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Project, Requirement
from app.schemas import (
    RequirementCreate,
    RequirementRead,
    RequirementUpdate,
)

router = APIRouter(prefix="/requirements", tags=["requirements"])


@router.get("", response_model=list[RequirementRead])
def list_requirements(project_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Requirement)
    if project_id is not None:
        q = q.filter(Requirement.project_id == project_id)
    return q.order_by(Requirement.id).all()


@router.post("", response_model=RequirementRead)
def create_requirement(payload: RequirementCreate, db: Session = Depends(get_db)):
    if db.get(Project, payload.project_id) is None:
        raise HTTPException(404, "project not found")
    obj = Requirement(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{requirement_id}", response_model=RequirementRead)
def get_requirement(requirement_id: int, db: Session = Depends(get_db)):
    obj = db.get(Requirement, requirement_id)
    if obj is None:
        raise HTTPException(404, "requirement not found")
    return obj


@router.patch("/{requirement_id}", response_model=RequirementRead)
def update_requirement(
    requirement_id: int, payload: RequirementUpdate, db: Session = Depends(get_db)
):
    obj = db.get(Requirement, requirement_id)
    if obj is None:
        raise HTTPException(404, "requirement not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{requirement_id}", status_code=204)
def delete_requirement(requirement_id: int, db: Session = Depends(get_db)):
    obj = db.get(Requirement, requirement_id)
    if obj is None:
        raise HTTPException(404, "requirement not found")
    db.delete(obj)
    db.commit()
