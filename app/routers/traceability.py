from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Requirement, TestCase

router = APIRouter(prefix="/traceability", tags=["traceability"])


@router.get("")
def matrix(project_id: int, db: Session = Depends(get_db)):
    requirements = (
        db.query(Requirement).filter(Requirement.project_id == project_id).all()
    )
    testcases = db.query(TestCase).filter(TestCase.project_id == project_id).all()

    req_rows = [
        {
            "id": r.id,
            "title": r.title,
            "status": r.status,
            "testcase_ids": [tc.id for tc in r.testcases],
        }
        for r in requirements
    ]
    tc_rows = [
        {
            "id": t.id,
            "name": t.name,
            "status": t.status,
            "requirement_ids": [r.id for r in t.requirements],
        }
        for t in testcases
    ]

    return {"requirements": req_rows, "testcases": tc_rows}
