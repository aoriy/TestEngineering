"""Code generation for execution (Jinja2 templates, ADR-0004: templates only)."""

from pathlib import Path

from jinja2 import Environment as JinjaEnvironment, FileSystemLoader
from sqlalchemy.orm import Session

from app.models import ApiDefinition, Environment, Flow, FlowNode, Shape, TestCase

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

_env = JinjaEnvironment(loader=FileSystemLoader(str(TEMPLATES_DIR / "pytest")))


def _normalize_rules(rules) -> list[dict]:
    if not rules:
        return []
    if isinstance(rules, dict):
        return [
            {"path": path, "var": var, "scope": "page"} for var, path in rules.items()
        ]
    result = []
    for r in rules:
        result.append(
            {
                "path": r.get("path"),
                "var": r.get("var"),
                "scope": r.get("scope", "page"),
            }
        )
    return result


def _collect_api_defs(db: Session, steps: list[dict]) -> dict:
    api_defs: dict = {}
    for step in steps:
        api_id = step["api_definition_id"]
        if api_id is None or str(api_id) in api_defs:
            continue
        api = db.get(ApiDefinition, api_id)
        if api is None:
            continue
        api_defs[str(api_id)] = {
            "method": api.method,
            "url": api.url,
            "headers": api.headers,
            "params": api.params,
            "body_template": api.body_template,
        }
    return api_defs


def generate_api_test(db: Session, testcase_id: int) -> str:
    tc = db.get(TestCase, testcase_id)
    if tc is None:
        raise ValueError(f"testcase {testcase_id} not found")

    env = db.get(Environment, tc.environment_id) if tc.environment_id else None
    base_url = env.base_url if env else ""
    env_vars = env.variables if env else {}

    steps: list[dict] = []
    flow_vars: dict = dict(tc.data_bindings or {})

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
                flow_vars.update(node.initial_vars or {})
                for step in sorted(node.steps, key=lambda s: s.order):
                    shape = db.get(Shape, step.shape_id)
                    if shape is None:
                        continue
                    steps.append(
                        {
                            "label": shape.label or f"shape#{shape.id}",
                            "api_definition_id": shape.api_definition_id,
                            "api_params": shape.api_params or {},
                            "extraction_rules": _normalize_rules(
                                shape.extraction_rules
                            ),
                            "before_code": shape.before_code or "",
                            "after_code": shape.after_code or "",
                        }
                    )

    template = _env.get_template("api_test.py.j2")
    data_rows = list(tc.data_rows or [])
    param_rows = [r.row or {} for r in data_rows]
    row_ids = [r.name or f"row_{i}" for i, r in enumerate(data_rows)]
    return template.render(
        test_name=f"case_{tc.id}",
        base_url=base_url,
        env_vars=env_vars,
        flow_vars=flow_vars,
        api_defs=_collect_api_defs(db, steps),
        steps=steps,
        assertions=tc.assertions or [],
        param_rows=param_rows,
        row_ids=row_ids,
    )
