"""Locust codegen for performance tests (reuses ApiDefinition via flow steps)."""

import json
from pathlib import Path

from jinja2 import Environment as JinjaEnvironment, FileSystemLoader
from sqlalchemy.orm import Session

from app.core.varlib import VariableStore, substitute
from app.models import ApiDefinition, Environment, Flow, FlowNode, Shape, TestCase

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

_env = JinjaEnvironment(loader=FileSystemLoader(str(TEMPLATES_DIR / "locust")))


def generate_locustfile(db: Session, testcase_id: int) -> tuple[str, str]:
    """Generate a locustfile for the test case's API steps.

    Returns (locustfile_code, host).
    """
    tc = db.get(TestCase, testcase_id)
    if tc is None:
        raise ValueError(f"testcase {testcase_id} not found")

    env = db.get(Environment, tc.environment_id) if tc.environment_id else None
    host = env.base_url if env else ""

    store = VariableStore()
    store.global_vars = env.variables if env else {}
    store.flow_vars = dict(tc.data_bindings or {})

    api_ids: list[int] = []
    seen: set[int] = set()
    if tc.flow_id:
        flow = db.get(Flow, tc.flow_id)
        if flow:
            nodes = (
                db.query(FlowNode)
                .filter(FlowNode.flow_id == flow.id)
                .order_by(FlowNode.id)
                .all()
            )
            for node in nodes:
                for step in sorted(node.steps, key=lambda s: s.order):
                    shape = db.get(Shape, step.shape_id)
                    if (
                        shape is not None
                        and shape.api_definition_id is not None
                        and shape.api_definition_id not in seen
                    ):
                        seen.add(shape.api_definition_id)
                        api_ids.append(shape.api_definition_id)

    tasks: list[dict] = []
    for i, api_id in enumerate(api_ids):
        api = db.get(ApiDefinition, api_id)
        if api is None:
            continue
        body_str = substitute(api.body_template or "", store)
        body: object = None
        body_kind = "none"
        if body_str:
            try:
                body = json.loads(body_str)
                body_kind = "json"
            except ValueError:
                body = body_str
                body_kind = "data"
        tasks.append(
            {
                "func_name": f"task_{i}",
                "method": api.method,
                "url": substitute(api.url, store),
                "headers": {
                    substitute(str(k), store): substitute(str(v), store)
                    for k, v in (api.headers or {}).items()
                },
                "params": {
                    substitute(str(k), store): substitute(str(v), store)
                    for k, v in (api.params or {}).items()
                },
                "body": body,
                "body_kind": body_kind,
                "name": api.name,
            }
        )

    code = _env.get_template("locustfile.py.j2").render(tasks=tasks)
    return code, host
