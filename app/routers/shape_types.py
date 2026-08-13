from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ShapeType
from app.schemas import ShapeTypeRead

router = APIRouter(prefix="/shape-types", tags=["shape-types"])

_DEFAULTS = [
    ("input", "输入框", {}),
    ("button", "按钮", {"strokeWidth": 3}),
    ("select", "下拉框", {"marker": "▼"}),
    ("checkbox", "复选框", {}),
    ("api", "接口调用", {"rx": 8, "ry": 8}),
    ("variable", "变量", {"diamond": True}),
    ("code", "代码钩子", {"code": True}),
    ("assert", "断言", {"assert": True}),
    ("wait", "等待", {}),
    ("condition", "条件", {}),
]


def _seed(db: Session) -> None:
    existing = {s.key for s in db.query(ShapeType).all()}
    for key, label, style in _DEFAULTS:
        if key not in existing:
            db.add(ShapeType(key=key, label=label, default_style=style))
    db.commit()


@router.get("", response_model=list[ShapeTypeRead])
def list_shape_types(db: Session = Depends(get_db)):
    _seed(db)
    return db.query(ShapeType).order_by(ShapeType.id).all()
