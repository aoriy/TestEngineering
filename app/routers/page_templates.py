from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import PageTemplate, Project, Shape
from app.schemas import (
    PageTemplateCreate,
    PageTemplateRead,
    ShapeCreate,
    ShapeRead,
    ShapeUpdate,
)

router = APIRouter(prefix="/page-templates", tags=["page-templates"])


@router.get("", response_model=list[PageTemplateRead])
def list_templates(project_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(PageTemplate)
    if project_id is not None:
        q = q.filter(PageTemplate.project_id == project_id)
    return q.order_by(PageTemplate.id).all()


@router.post("", response_model=PageTemplateRead)
def create_template(payload: PageTemplateCreate, db: Session = Depends(get_db)):
    if db.get(Project, payload.project_id) is None:
        raise HTTPException(404, "project not found")
    obj = PageTemplate(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{template_id}", response_model=PageTemplateRead)
def get_template(template_id: int, db: Session = Depends(get_db)):
    obj = db.get(PageTemplate, template_id)
    if obj is None:
        raise HTTPException(404, "page template not found")
    return obj


@router.delete("/{template_id}", status_code=204)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    obj = db.get(PageTemplate, template_id)
    if obj is None:
        raise HTTPException(404, "page template not found")
    db.delete(obj)
    db.commit()


# --- shapes ---


@router.post("/{template_id}/shapes", response_model=ShapeRead)
def create_shape(template_id: int, payload: ShapeCreate, db: Session = Depends(get_db)):
    if db.get(PageTemplate, template_id) is None:
        raise HTTPException(404, "page template not found")
    obj = Shape(page_template_id=template_id, **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{template_id}/shapes/{shape_id}", response_model=ShapeRead)
def update_shape(
    template_id: int, shape_id: int, payload: ShapeUpdate, db: Session = Depends(get_db)
):
    obj = db.get(Shape, shape_id)
    if obj is None or obj.page_template_id != template_id:
        raise HTTPException(404, "shape not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{template_id}/shapes/{shape_id}", status_code=204)
def delete_shape(template_id: int, shape_id: int, db: Session = Depends(get_db)):
    obj = db.get(Shape, shape_id)
    if obj is None or obj.page_template_id != template_id:
        raise HTTPException(404, "shape not found")
    db.delete(obj)
    db.commit()
