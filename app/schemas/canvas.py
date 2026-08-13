from pydantic import BaseModel

from app.schemas.schemas import ORMModel


# --- PageTemplate ---


class PageTemplateBase(BaseModel):
    name: str
    url: str = ""
    description: str | None = None


class PageTemplateCreate(PageTemplateBase):
    project_id: int
    module_id: int | None = None


class PageTemplateRead(PageTemplateBase, ORMModel):
    id: int
    project_id: int
    module_id: int | None
    shapes: list["ShapeRead"] = []


# --- Shape ---


class ShapeBase(BaseModel):
    shape_type: str
    label: str = ""
    x: float = 0.0
    y: float = 0.0
    width: float = 120.0
    height: float = 40.0
    style: dict = {}
    locator_type: str = "data-testid"
    locator_value: str = ""
    api_definition_id: int | None = None
    api_params: dict = {}
    extraction_rules: dict = {}
    value_source: str = "literal"
    value: str = ""
    before_code: str = ""
    after_code: str = ""


class ShapeCreate(ShapeBase):
    pass


class ShapeUpdate(BaseModel):
    shape_type: str | None = None
    label: str | None = None
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None
    style: dict | None = None
    locator_type: str | None = None
    locator_value: str | None = None
    api_definition_id: int | None = None
    api_params: dict | None = None
    extraction_rules: dict | None = None
    value_source: str | None = None
    value: str | None = None
    before_code: str | None = None
    after_code: str | None = None


class ShapeRead(ShapeBase, ORMModel):
    id: int
    page_template_id: int


class ShapeTypeRead(ORMModel):
    id: int
    key: str
    label: str
    default_style: dict = {}


# --- Flow / FlowNode / Step / FlowEdge ---


class FlowBase(BaseModel):
    name: str
    description: str | None = None


class FlowCreate(FlowBase):
    project_id: int


class FlowRead(FlowBase, ORMModel):
    id: int
    project_id: int
    nodes: list["FlowNodeRead"] = []
    edges: list["FlowEdgeRead"] = []


class FlowNodeBase(BaseModel):
    page_template_id: int
    x: float = 0.0
    y: float = 0.0
    initial_vars: dict = {}


class FlowNodeCreate(FlowNodeBase):
    pass


class FlowNodeUpdate(BaseModel):
    x: float | None = None
    y: float | None = None
    initial_vars: dict | None = None


class StepRead(ORMModel):
    id: int
    flow_node_id: int
    shape_id: int
    order: int
    action_type: str
    action_params: dict


class FlowNodeRead(FlowNodeBase, ORMModel):
    id: int
    flow_id: int
    page_template_name: str = ""
    steps: list[StepRead] = []


class StepCreate(BaseModel):
    shape_id: int
    order: int | None = None
    action_type: str = "click"
    action_params: dict = {}


class StepUpdate(BaseModel):
    action_type: str | None = None
    action_params: dict | None = None
    order: int | None = None


class StepReorder(BaseModel):
    ordered_ids: list[int]


class FlowEdgeCreate(BaseModel):
    source_node_id: int
    target_node_id: int
    trigger: str = ""


class FlowEdgeRead(FlowEdgeCreate, ORMModel):
    id: int
    flow_id: int
