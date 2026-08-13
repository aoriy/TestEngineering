# 字段级数据模型设计

> 状态：阶段 0/1 落定，与 `app/models/` 的 SQLAlchemy 模型一一对应
> 配套：architecture-review.md §四 / ADR-0006 / ADR-0007 / glossary.md

所有实体继承 `TimestampMixin`（`created_at`、`updated_at`，见 `app/models/base.py`）。主键统一 `id: int` 自增。JSON 字段用 SQLite 的 JSON 类型（SQLAlchemy `JSON`）。

## 一、顶层结构

### project 项目
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| name | str(255) | NOT NULL | 项目名 |
| description | text | NULL | |
| owner | str(255) | NULL | 预留多人（ADR：预留不实现鉴权） |

### module 模块
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| project_id | int | FK→project.id, CASCADE | |
| name | str(255) | NOT NULL | |
| parent_id | int | FK→module.id, SET NULL | 扁平分组，暂不递归展开 |

### environment 环境
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| project_id | int | FK→project.id, CASCADE | |
| name | str(255) | NOT NULL | dev/staging/prod |
| base_url | str(512) | 默认 '' | |
| headers | JSON | 默认 {} | 环境级请求头 |
| variables | JSON | 默认 {} | 环境级默认变量 |

## 二、需求与用例

### requirement 需求
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| project_id | int | FK→project.id, CASCADE | |
| module_id | int | FK→module.id, SET NULL | |
| title | str(255) | NOT NULL | |
| description | text | NULL | |
| priority | str(32) | 默认 'medium' | high/medium/low |
| status | str(32) | 默认 'draft' | |

关联：`Requirement.testcases` ↔ `TestCase.requirements`，经关联表 `requirement_testcase`（`requirement_id` + `testcase_id`，双主键，均 CASCADE）。

### testcase 用例
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| project_id | int | FK→project.id, CASCADE | |
| flow_id | int | FK→flow.id, SET NULL | 阶段 2 起绑定流转图 |
| environment_id | int | FK→environment.id, SET NULL | 执行环境 |
| name | str(255) | NOT NULL | |
| priority | str(32) | 默认 'medium' | |
| status | str(32) | 默认 'draft' | |
| data_bindings | JSON | 默认 {} | 数据绑定 |
| assertions | JSON(list) | 默认 [] | 断言列表 |
| tags | str(512) | 默认 '' | 逗号分隔 |

### test_data 数据行
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| testcase_id | int | FK→testcase.id, CASCADE | |
| name | str(255) | 默认 '' | |
| row | JSON | 默认 {} | 一行数据驱动值 |

## 三、页面模板与形状（核心，ADR-0006）

### page_template 页面模板
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| project_id | int | FK→project.id, CASCADE | |
| module_id | int | FK→module.id, SET NULL | |
| name | str(255) | NOT NULL | |
| url | str(512) | 默认 '' | 支持 `{{env.base_url}}` 前缀或相对路径 |
| description | text | NULL | |

### shape 形状
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| page_template_id | int | FK→page_template.id, CASCADE | |
| shape_type | str(32) | NOT NULL | input/button/select/checkbox/api/variable/code/assert/wait/condition |
| label | str(255) | 默认 '' | 显示名 |
| x / y | float | 默认 0 | 画布坐标 |
| width / height | float | 默认 120/40 | 形状尺寸 |
| style | JSON | 默认 {} | 视觉样式（普通/粗边框等） |
| locator_type | str(32) | 默认 'data-testid' | data-testid/xpath/css/text |
| locator_value | str(1024) | 默认 '' | 定位器值 |
| locator_history | JSON(list) | 默认 [] | 版本数组（ADR-0007） |
| locator_current | int | 默认 0 | current 指针 |
| api_definition_id | int | FK→api_definition.id, SET NULL | 接口绑定 |
| api_params | JSON | 默认 {} | 入参映射（字段值→接口参数） |
| extraction_rules | JSON | 默认 {} | 响应提取（JSONPath/正则→变量） |
| value_source | str(32) | 默认 'literal' | literal/variable/data_row/from_api |
| value | text | 默认 '' | 值或 `{{var}}` 引用 |
| before_code | text | 默认 '' | 前置钩子（AST 护栏，ADR-0003） |
| after_code | text | 默认 '' | 后置钩子 |

### shape_type 形状类型注册表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| key | str(32) | UNIQUE NOT NULL | |
| label | str(255) | NOT NULL | |
| default_style | JSON | 默认 {} | |

## 四、流转图（ADR-0006）

### flow 流程
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| project_id | int | FK→project.id, CASCADE | |
| name | str(255) | NOT NULL | |
| description | text | NULL | |

### flow_node 流程节点（页面实例）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| flow_id | int | FK→flow.id, CASCADE | |
| page_template_id | int | FK→page_template.id, CASCADE | 引用模板 |
| x / y | float | 默认 0 | 流转图画布坐标 |
| initial_vars | JSON | 默认 {} | 实例级初始变量覆盖 |

### step 步骤（实例有序动作）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| flow_node_id | int | FK→flow_node.id, CASCADE | |
| shape_id | int | FK→shape.id, CASCADE | 引用形状 |
| order | int | NOT NULL | 执行顺序（拖拽重排=改 order） |
| action_type | str(32) | 默认 'click' | click/input/select/assert/api_call/wait/condition/custom |
| action_params | JSON | 默认 {} | |

### flow_edge 流转边
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| flow_id | int | FK→flow.id, CASCADE | |
| source_node_id | int | FK→flow_node.id, CASCADE | |
| target_node_id | int | FK→flow_node.id, CASCADE | |
| trigger | str(255) | 默认 '' | 跳转操作（按钮名） |

## 五、接口定义

### api_definition 接口定义
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| project_id | int | FK→project.id, CASCADE | |
| name | str(255) | NOT NULL | |
| method | str(16) | 默认 'GET' | |
| url | str(1024) | NOT NULL | 支持 `{{var}}` |
| headers | JSON | 默认 {} | |
| params | JSON | 默认 {} | query 参数 |
| body_template | text | 默认 '' | body（支持 `{{var}}`） |
| expected | JSON | 默认 {} | 期望值 |

## 六、执行与自愈

### test_run 执行记录
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| testcase_id | int | FK→testcase.id, SET NULL | |
| environment_id | int | FK→environment.id, SET NULL | |
| run_id | str(64) | UNIQUE NOT NULL | 对应 runs/<run_id>/ |
| status | str(32) | 默认 'pending' | pending/running/done/failed/timeout/cancelled |
| started_at / finished_at | datetime | NULL | |
| exit_code | int | NULL | |
| runs_dir | str(1024) | 默认 '' | 产物目录 |
| log_path | str(1024) | 默认 '' | log.txt |
| report_path | str(1024) | 默认 '' | report.html |
| artifacts | JSON | 默认 {} | 截图/录像/trace 路径清单 |

### self_heal_record 自愈审计
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | |
| run_id | str(64) | 默认 '' | 关联 run |
| shape_id | int | FK→shape.id, SET NULL | |
| old_locator / new_locator | text | 默认 '' | |
| confidence | float | 默认 0 | LLM 置信度 |
| reasoning | text | 默认 '' | LLM thinking 输出 |
| page_snapshot | text | 默认 '' | HTML 片段 |
| locator_version | int | 默认 0 | 写入的 locator_history 版本 |
| status | str(32) | 默认 'suggest' | auto_applied/suggest/rejected |

## 七、索引建议（SQLite 单机量级，按需）

| 表 | 建议索引 | 理由 |
|----|---------|------|
| requirement | (project_id) | 按项目过滤 |
| testcase | (project_id) | 按项目过滤 |
| shape | (page_template_id) | 画布加载形状 |
| step | (flow_node_id, order) | 按节点+顺序取步骤 |
| flow_node | (flow_id) | 取流程节点 |
| test_run | (run_id UNIQUE) | 轮询状态 |
| self_heal_record | (shape_id) | 查某形状自愈历史 |

> SQLite 单机量级下这些索引非必需，但预留便于切换 MySQL 后复用。
