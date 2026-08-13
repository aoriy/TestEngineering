from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    owner: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime


class ModuleBase(BaseModel):
    name: str
    parent_id: int | None = None


class ModuleCreate(ModuleBase):
    pass


class ModuleRead(ModuleBase, ORMModel):
    id: int
    project_id: int


class EnvironmentBase(BaseModel):
    name: str
    base_url: str = ""
    headers: dict = {}
    variables: dict = {}


class EnvironmentCreate(EnvironmentBase):
    pass


class EnvironmentRead(EnvironmentBase, ORMModel):
    id: int
    project_id: int


class RequirementBase(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"
    status: str = "draft"


class RequirementCreate(RequirementBase):
    project_id: int
    module_id: int | None = None


class RequirementUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None
    module_id: int | None = None


class RequirementRead(RequirementBase, ORMModel):
    id: int
    project_id: int
    module_id: int | None
    testcase_ids: list[int] = []


class TestDataBase(BaseModel):
    name: str = ""
    row: dict = {}


class TestDataRead(TestDataBase, ORMModel):
    id: int


class TestCaseBase(BaseModel):
    name: str
    priority: str = "medium"
    status: str = "draft"
    data_bindings: dict = {}
    assertions: list = []
    tags: str = ""


class TestCaseCreate(TestCaseBase):
    project_id: int
    flow_id: int | None = None
    environment_id: int | None = None


class TestCaseUpdate(BaseModel):
    name: str | None = None
    priority: str | None = None
    status: str | None = None
    flow_id: int | None = None
    environment_id: int | None = None
    data_bindings: dict | None = None
    assertions: list | None = None
    tags: str | None = None


class TestCaseRead(TestCaseBase, ORMModel):
    id: int
    project_id: int
    flow_id: int | None
    environment_id: int | None
    requirement_ids: list[int] = []
    data_rows: list[TestDataRead] = []


class RunCreate(BaseModel):
    testcase_id: int
    environment_id: int | None = None
    executor: str = "api"
    params: dict = {}


class TestRunRead(ORMModel):
    id: int
    run_id: str
    testcase_id: int | None
    environment_id: int | None
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    exit_code: int | None
    runs_dir: str
    log_path: str
    report_path: str
    artifacts: dict = {}


class ApiDefinitionBase(BaseModel):
    name: str
    method: str = "GET"
    url: str
    headers: dict = {}
    params: dict = {}
    body_template: str = ""
    expected: dict = {}


class ApiDefinitionCreate(ApiDefinitionBase):
    project_id: int


class ApiDefinitionRead(ApiDefinitionBase, ORMModel):
    id: int
    project_id: int


class SelfHealRequest(BaseModel):
    shape_id: int
    old_locator: str
    page_html: str = ""
    old_meta: dict | None = None
    run_id: str = ""
