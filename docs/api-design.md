# API 设计草案

> 状态：阶段 0/1 已实现部分（projects/requirements/testcases/traceability），阶段 2+ 端点待补
> 配套：architecture-review.md / sequence-diagrams.md / data-model-detail.md

## 一、通用约定

- 前缀：`/api`
- 数据格式：JSON
- 前端开发经 Vite proxy `/api → http://127.0.0.1:8000`（见 `frontend/vite.config.ts`）
- 端口：后端 `8000`，前端 `5173`

## 二、统一响应格式

**成功**
- 返回资源对象或数组（FastAPI `response_model` 直接序列化 Pydantic）
- `DELETE` 返回 `204 No Content`
- 列表返回 `200` + 数组

**失败**（FastAPI 默认错误体）
```json
{ "detail": "错误信息" }
```
- `404` 资源不存在、`422` 参数校验失败、`500` 服务异常
- 错误码规范（后续阶段细化）：
  - 404：资源未找到
  - 422：请求体校验失败（含字段定位 `loc`）

## 三、已实现端点（阶段 0/1）

### health
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查，返回 `{status, app, executors}` |

### projects 项目
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/projects` | 项目列表 |
| POST | `/api/projects` | 创建项目 |
| GET | `/api/projects/{id}` | 项目详情 |
| DELETE | `/api/projects/{id}` | 删除项目（级联） |

### modules 模块（嵌套在项目下）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/projects/{project_id}/modules` | 模块列表 |
| POST | `/api/projects/{project_id}/modules` | 创建模块 |

### environments 环境（嵌套在项目下）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/projects/{project_id}/environments` | 环境列表 |
| POST | `/api/projects/{project_id}/environments` | 创建环境 |

### requirements 需求
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/requirements?project_id={id}` | 需求列表（按项目过滤） |
| POST | `/api/requirements` | 创建需求 |
| GET | `/api/requirements/{id}` | 需求详情 |
| PATCH | `/api/requirements/{id}` | 更新需求（部分字段） |
| DELETE | `/api/requirements/{id}` | 删除需求 |

### testcases 用例
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/testcases?project_id={id}` | 用例列表（按项目过滤） |
| POST | `/api/testcases` | 创建用例 |
| GET | `/api/testcases/{id}` | 用例详情 |
| PATCH | `/api/testcases/{id}` | 更新用例（部分字段） |
| DELETE | `/api/testcases/{id}` | 删除用例 |
| POST | `/api/testcases/{id}/data` | 添加数据行 `{name, row}` |
| POST | `/api/testcases/{tc_id}/requirements/{req_id}` | 关联需求 |
| DELETE | `/api/testcases/{tc_id}/requirements/{req_id}` | 解除关联 |

### traceability 追溯矩阵
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/traceability?project_id={id}` | 返回 `{requirements:[{id,title,status,testcase_ids}], testcases:[{id,name,status,requirement_ids}]}` |

## 四、待实现端点（阶段 2+）

| 阶段 | 资源 | 端点前缀 |
|------|------|---------|
| 2 | 页面模板/形状 | `/api/page-templates`、`/api/page-templates/{id}/shapes` |
| 2 | 流转图 | `/api/flows`、`/api/flows/{id}/nodes`、`/api/flows/{id}/edges` |
| 2 | 步骤 | `/api/flows/{flow_id}/nodes/{node_id}/steps`（含 order 重排） |
| 3 | 接口定义 | `/api/api-definitions` |
| 3 | 执行 | `POST /api/runs`（spawn worker）、`GET /api/runs/{id}`（轮询状态） |
| 3.5 | 自愈 | `POST /api/selfheal`、`GET /api/selfheal?shape_id=` |
| 4 | 性能 | `POST /api/runs`（executor=perf）复用 run 端点 |
| 5 | 录制 | `POST /api/record/start`、`POST /api/record/stop` |

## 五、分页/过滤约定（后续统一）

- 列表默认不分页（单机量级）；数据量大时加 `?limit=&offset=`
- 过滤用 query 参数（已用 `project_id` 作示范）
- 排序默认按 `id` 升序

## 六、与前端 SPA 对接

- 前端 `src/views/*.vue` 直接用 `fetch('/api/...')`（经 Vite proxy）
- 类型定义在各 view 的 `interface` 内联，后续阶段抽到 `src/api/` 共享模块
- 追溯矩阵页依赖 `/api/traceability` 的聚合结构，避免前端多次请求拼装
