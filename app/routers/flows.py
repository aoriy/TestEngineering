from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Flow, FlowEdge, FlowNode, PageTemplate, Project, Step
from app.schemas import (
    FlowCreate,
    FlowEdgeCreate,
    FlowEdgeRead,
    FlowNodeCreate,
    FlowNodeRead,
    FlowNodeUpdate,
    FlowRead,
    StepCreate,
    StepRead,
    StepReorder,
    StepUpdate,
)

router = APIRouter(prefix="/flows", tags=["flows"])


@router.get("", response_model=list[FlowRead])
def list_flows(project_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Flow)
    if project_id is not None:
        q = q.filter(Flow.project_id == project_id)
    return q.order_by(Flow.id).all()


@router.post("", response_model=FlowRead)
def create_flow(payload: FlowCreate, db: Session = Depends(get_db)):
    if db.get(Project, payload.project_id) is None:
        raise HTTPException(404, "project not found")
    obj = Flow(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{flow_id}", response_model=FlowRead)
def get_flow(flow_id: int, db: Session = Depends(get_db)):
    obj = db.get(Flow, flow_id)
    if obj is None:
        raise HTTPException(404, "flow not found")
    return obj


@router.delete("/{flow_id}", status_code=204)
def delete_flow(flow_id: int, db: Session = Depends(get_db)):
    obj = db.get(Flow, flow_id)
    if obj is None:
        raise HTTPException(404, "flow not found")
    db.delete(obj)
    db.commit()


# --- nodes ---


@router.post("/{flow_id}/nodes", response_model=FlowNodeRead)
def create_node(flow_id: int, payload: FlowNodeCreate, db: Session = Depends(get_db)):
    if db.get(Flow, flow_id) is None:
        raise HTTPException(404, "flow not found")
    if db.get(PageTemplate, payload.page_template_id) is None:
        raise HTTPException(404, "page template not found")
    obj = FlowNode(flow_id=flow_id, **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{flow_id}/nodes/{node_id}", response_model=FlowNodeRead)
def update_node(
    flow_id: int, node_id: int, payload: FlowNodeUpdate, db: Session = Depends(get_db)
):
    obj = db.get(FlowNode, node_id)
    if obj is None or obj.flow_id != flow_id:
        raise HTTPException(404, "flow node not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{flow_id}/nodes/{node_id}", status_code=204)
def delete_node(flow_id: int, node_id: int, db: Session = Depends(get_db)):
    obj = db.get(FlowNode, node_id)
    if obj is None or obj.flow_id != flow_id:
        raise HTTPException(404, "flow node not found")
    db.delete(obj)
    db.commit()


# --- steps ---


@router.post("/{flow_id}/nodes/{node_id}/steps", response_model=StepRead)
def create_step(
    flow_id: int, node_id: int, payload: StepCreate, db: Session = Depends(get_db)
):
    node = db.get(FlowNode, node_id)
    if node is None or node.flow_id != flow_id:
        raise HTTPException(404, "flow node not found")
    order = payload.order
    if order is None:
        max_order = db.query(Step).filter(Step.flow_node_id == node_id).count()
        order = max_order
    obj = Step(
        flow_node_id=node_id,
        shape_id=payload.shape_id,
        order=order,
        action_type=payload.action_type,
        action_params=payload.action_params,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{flow_id}/nodes/{node_id}/steps/{step_id}", response_model=StepRead)
def update_step(
    flow_id: int,
    node_id: int,
    step_id: int,
    payload: StepUpdate,
    db: Session = Depends(get_db),
):
    obj = db.get(Step, step_id)
    if obj is None or obj.flow_node_id != node_id:
        raise HTTPException(404, "step not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{flow_id}/nodes/{node_id}/steps/{step_id}", status_code=204)
def delete_step(
    flow_id: int, node_id: int, step_id: int, db: Session = Depends(get_db)
):
    obj = db.get(Step, step_id)
    if obj is None or obj.flow_node_id != node_id:
        raise HTTPException(404, "step not found")
    db.delete(obj)
    db.commit()


@router.post("/{flow_id}/nodes/{node_id}/steps/reorder", response_model=list[StepRead])
def reorder_steps(
    flow_id: int, node_id: int, payload: StepReorder, db: Session = Depends(get_db)
):
    steps = db.query(Step).filter(Step.flow_node_id == node_id).all()
    by_id = {s.id: s for s in steps}
    for idx, sid in enumerate(payload.ordered_ids):
        if sid in by_id:
            by_id[sid].order = idx
    db.commit()
    return (
        db.query(Step).filter(Step.flow_node_id == node_id).order_by(Step.order).all()
    )


# --- edges ---


@router.post("/{flow_id}/edges", response_model=FlowEdgeRead)
def create_edge(flow_id: int, payload: FlowEdgeCreate, db: Session = Depends(get_db)):
    if db.get(Flow, flow_id) is None:
        raise HTTPException(404, "flow not found")
    obj = FlowEdge(flow_id=flow_id, **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{flow_id}/edges/{edge_id}", status_code=204)
def delete_edge(flow_id: int, edge_id: int, db: Session = Depends(get_db)):
    obj = db.get(FlowEdge, edge_id)
    if obj is None or obj.flow_id != flow_id:
        raise HTTPException(404, "edge not found")
    db.delete(obj)
    db.commit()
