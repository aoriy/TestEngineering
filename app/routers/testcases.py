from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Project, Requirement, TestCase, TestData
from app.schemas import TestCaseCreate, TestCaseRead, TestCaseUpdate

router = APIRouter(prefix="/testcases", tags=["testcases"])


@router.get("", response_model=list[TestCaseRead])
def list_testcases(project_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(TestCase)
    if project_id is not None:
        q = q.filter(TestCase.project_id == project_id)
    return q.order_by(TestCase.id).all()


@router.post("", response_model=TestCaseRead)
def create_testcase(payload: TestCaseCreate, db: Session = Depends(get_db)):
    if db.get(Project, payload.project_id) is None:
        raise HTTPException(404, "project not found")
    obj = TestCase(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{testcase_id}", response_model=TestCaseRead)
def get_testcase(testcase_id: int, db: Session = Depends(get_db)):
    obj = db.get(TestCase, testcase_id)
    if obj is None:
        raise HTTPException(404, "testcase not found")
    return obj


@router.patch("/{testcase_id}", response_model=TestCaseRead)
def update_testcase(
    testcase_id: int, payload: TestCaseUpdate, db: Session = Depends(get_db)
):
    obj = db.get(TestCase, testcase_id)
    if obj is None:
        raise HTTPException(404, "testcase not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{testcase_id}", status_code=204)
def delete_testcase(testcase_id: int, db: Session = Depends(get_db)):
    obj = db.get(TestCase, testcase_id)
    if obj is None:
        raise HTTPException(404, "testcase not found")
    db.delete(obj)
    db.commit()


# --- traceability (Requirement <-> TestCase) ---


@router.post(
    "/{testcase_id}/requirements/{requirement_id}", response_model=TestCaseRead
)
def link_requirement(
    testcase_id: int, requirement_id: int, db: Session = Depends(get_db)
):
    tc = db.get(TestCase, testcase_id)
    req = db.get(Requirement, requirement_id)
    if tc is None or req is None:
        raise HTTPException(404, "testcase or requirement not found")
    if req not in tc.requirements:
        tc.requirements.append(req)
        db.commit()
        db.refresh(tc)
    return tc


@router.delete(
    "/{testcase_id}/requirements/{requirement_id}", response_model=TestCaseRead
)
def unlink_requirement(
    testcase_id: int, requirement_id: int, db: Session = Depends(get_db)
):
    tc = db.get(TestCase, testcase_id)
    req = db.get(Requirement, requirement_id)
    if tc is None or req is None:
        raise HTTPException(404, "testcase or requirement not found")
    if req in tc.requirements:
        tc.requirements.remove(req)
        db.commit()
        db.refresh(tc)
    return tc


# --- data rows ---


@router.post("/{testcase_id}/data", response_model=TestCaseRead)
def add_data_row(
    testcase_id: int,
    name: str = "",
    row: dict | None = None,
    db: Session = Depends(get_db),
):
    tc = db.get(TestCase, testcase_id)
    if tc is None:
        raise HTTPException(404, "testcase not found")
    db.add(TestData(testcase_id=testcase_id, name=name, row=row or {}))
    db.commit()
    db.refresh(tc)
    return tc
