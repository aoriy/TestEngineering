from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Environment, Module, Project
from app.schemas import (
    EnvironmentCreate,
    EnvironmentRead,
    ModuleCreate,
    ModuleRead,
    ProjectCreate,
    ProjectRead,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.id).all()


@router.post("", response_model=ProjectRead)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    obj = Project(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    obj = db.get(Project, project_id)
    if obj is None:
        raise HTTPException(404, "project not found")
    return obj


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    obj = db.get(Project, project_id)
    if obj is None:
        raise HTTPException(404, "project not found")
    db.delete(obj)
    db.commit()


@router.post("/{project_id}/modules", response_model=ModuleRead)
def create_module(
    project_id: int, payload: ModuleCreate, db: Session = Depends(get_db)
):
    if db.get(Project, project_id) is None:
        raise HTTPException(404, "project not found")
    obj = Module(project_id=project_id, name=payload.name, parent_id=payload.parent_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{project_id}/modules", response_model=list[ModuleRead])
def list_modules(project_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Module)
        .filter(Module.project_id == project_id)
        .order_by(Module.id)
        .all()
    )


@router.post("/{project_id}/environments", response_model=EnvironmentRead)
def create_environment(
    project_id: int, payload: EnvironmentCreate, db: Session = Depends(get_db)
):
    if db.get(Project, project_id) is None:
        raise HTTPException(404, "project not found")
    obj = Environment(project_id=project_id, **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{project_id}/environments", response_model=list[EnvironmentRead])
def list_environments(project_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Environment)
        .filter(Environment.project_id == project_id)
        .order_by(Environment.id)
        .all()
    )
