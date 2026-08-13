"""Turn recorded actions into Shape + Step (region-snap fallback: time-order layout)."""

from sqlalchemy.orm import Session

from app.models import FlowNode, Shape, Step
from app.services.recorder.parser import RecordedAction

_SHAPE_TYPE = {"click": "button", "input": "input", "select": "select"}


def import_recording(
    db: Session,
    page_template_id: int,
    actions: list[RecordedAction],
    flow_id: int | None = None,
) -> dict:
    existing = {
        (s.locator_type, s.locator_value): s
        for s in db.query(Shape)
        .filter(Shape.page_template_id == page_template_id)
        .all()
    }

    node = None
    if flow_id is not None:
        node = (
            db.query(FlowNode)
            .filter(
                FlowNode.flow_id == flow_id,
                FlowNode.page_template_id == page_template_id,
            )
            .first()
        )
        if node is None:
            node = FlowNode(
                flow_id=flow_id, page_template_id=page_template_id, x=40, y=40
            )
            db.add(node)
            db.flush()

    shape_ids: list[int] = []
    step_ids: list[int] = []
    for i, act in enumerate(actions):
        key = (act.locator_type, act.locator_value)
        shape = existing.get(key)
        if shape is None:
            shape = Shape(
                page_template_id=page_template_id,
                shape_type=_SHAPE_TYPE.get(act.action, "button"),
                label=act.locator_value[:30] or act.action,
                locator_type=act.locator_type,
                locator_value=act.locator_value,
                value=act.value,
                x=40,
                y=40 + i * 60,
            )
            db.add(shape)
            db.flush()
            existing[key] = shape
            shape_ids.append(shape.id)
        if node is not None:
            step = Step(
                flow_node_id=node.id,
                shape_id=shape.id,
                order=i,
                action_type=act.action,
            )
            db.add(step)
            step_ids.append(step.id)
    db.commit()

    return {
        "shapes_created": len(shape_ids),
        "shape_ids": shape_ids,
        "steps_created": len(step_ids),
        "node_id": node.id if node else None,
    }
