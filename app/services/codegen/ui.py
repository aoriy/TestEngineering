"""Playwright POM codegen for UI test cases."""

from pathlib import Path

from jinja2 import Environment as JinjaEnvironment, FileSystemLoader
from sqlalchemy.orm import Session

from app.models import (
    ApiDefinition,
    Environment,
    Flow,
    FlowNode,
    PageTemplate,
    Shape,
    TestCase,
)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

_env = JinjaEnvironment(loader=FileSystemLoader(str(TEMPLATES_DIR / "pytest")))


def _locator_expr(shape: Shape) -> str:
    lt = shape.locator_type or "data-testid"
    v = shape.locator_value or ""
    if lt == "data-testid":
        return f"page.get_by_test_id({v!r})"
    if lt == "xpath":
        return f"page.locator('xpath=' + {v!r})"
    if lt == "text":
        return f"page.get_by_text({v!r})"
    return f"page.locator({v!r})"


def _render_step(action_type: str, shape: Shape, action_params: dict) -> dict:
    locator = _locator_expr(shape)
    value = action_params.get("value") or shape.value or ""
    common = {
        "label": shape.label or f"shape#{shape.id}",
        "locator": locator,
        "value": value,
        "before": shape.before_code or "",
        "after": shape.after_code or "",
        "api_definition_id": shape.api_definition_id,
    }
    if action_type == "input":
        return {**common, "action": "input"}
    if action_type == "select":
        return {**common, "action": "select"}
    if action_type == "assert":
        return {**common, "action": "assert_text" if value else "assert_visible"}
    if action_type == "wait":
        return {**common, "action": "wait"}
    if action_type == "click":
        return {**common, "action": "click"}
    return {**common, "action": "skip"}


def generate_ui_test(db: Session, testcase_id: int) -> str:
    tc = db.get(TestCase, testcase_id)
    if tc is None:
        raise ValueError(f"testcase {testcase_id} not found")

    env = db.get(Environment, tc.environment_id) if tc.environment_id else None
    base_url = env.base_url if env else ""
    env_vars = env.variables if env else {}

    flow_vars: dict = dict(tc.data_bindings or {})
    steps: list[dict] = []
    goto_url = ""
    api_defs: dict = {}

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
                tpl = db.get(PageTemplate, node.page_template_id)
                if tpl is not None and not goto_url:
                    goto_url = tpl.url or ""
                flow_vars.update(node.initial_vars or {})
                for step in sorted(node.steps, key=lambda s: s.order):
                    shape = db.get(Shape, step.shape_id)
                    if shape is None:
                        continue
                    steps.append(
                        _render_step(step.action_type, shape, step.action_params or {})
                    )
                    if shape.api_definition_id is not None:
                        api = db.get(ApiDefinition, shape.api_definition_id)
                        if api is not None and str(api.id) not in api_defs:
                            api_defs[str(api.id)] = {
                                "method": api.method,
                                "url": api.url,
                                "headers": api.headers,
                                "params": api.params,
                                "body_template": api.body_template,
                            }

    template = _env.get_template("ui_test.py.j2")
    return template.render(
        test_name=f"case_{tc.id}",
        base_url=base_url,
        goto_url=goto_url,
        env_vars=env_vars,
        flow_vars=flow_vars,
        steps=steps,
        api_defs=api_defs,
    )
