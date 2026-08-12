# 术语表

> 配套：requirements-analysis.md / architecture-review.md
> 用途：统一项目内术语，避免 Shape/Step/Flow/PageTemplate 等概念混用

## 顶层结构

| 术语 | 定义 |
|------|------|
| **Project** | 顶层容器。一个被测项目对应一个 Project，所有实体挂在其下 |
| **Module** | Project 下的分组单元，用于组织 PageTemplate / TestCase，可嵌套或扁平 |
| **Environment** | 环境配置（dev/staging/prod），含 base_url + headers + 默认变量；用例执行时绑定一个 |

## 测试资产

| 术语 | 定义 |
|------|------|
| **Requirement** | 需求条目，与 TestCase 多对多关联，用于追溯矩阵 |
| **TestCase** | 测试用例，绑定一个 Flow，带数据绑定、断言、优先级、标签 |
| **TestData** | 用例的数据驱动行（一组变量值，用例可批量执行） |

## 页面与流程（核心，易混）

| 术语 | 定义 |
|------|------|
| **PageTemplate** | **元素定义模板**（可复用）：页面"有什么字段/按钮"，存页面名/URL/所属模块 |
| **Shape** | PageTemplate 上的形状节点：类型/样式/画布位置/定位器/接口绑定/代码钩子/变量配置 |
| **Flow** | **流程实例**：由多个 FlowNode 拼接而成的完整业务流，跨页面 |
| **FlowNode** | Flow 中的节点，引用一个 PageTemplate + 实例级 `initial_vars` 覆盖 |
| **Step** | FlowNode 下的有序动作，**引用 `Shape`** + `order` + `action_type` + `action_params` |

**核心区分**：
- `PageTemplate` + `Shape` = "有什么"（定义层，跨流程复用）
- `Flow` + `FlowNode` + `Step` = "做什么、什么顺序"（实例层，引用 Shape）

## 简图与编排

| 术语 | 定义 |
|------|------|
| **简图** | 画布上用形状（正方形/粗边框/菱形…）直观组织的页面元素视图，**展示层**非执行层 |
| **流转图** | 多个 PageTemplate 实例（FlowNode）通过跳转边拼成的业务流总览 |
| **代码钩子** | 形状上的 Python 代码槽位：`before_code`（前置）/ `after_code`（后置），受 AST 护栏约束 |

## 接口与变量

| 术语 | 定义 |
|------|------|
| **ApiDefinition** | 接口定义：method/url/headers/body 模板/期望值，UI/API/性能复用 |
| **变量作用域** | 四级：global（整次运行）/ flow（整条流程）/ page（进页重置）/ local（形状内部） |
| **`{{var}}`** | 变量引用语法，由简化正则替换引擎渲染（非 Jinja2 全语法） |

## 执行与产出

| 术语 | 定义 |
|------|------|
| **Executor** | 执行抽象（`generate_code`/`spawn`/`collect_result`），api/ui/perf 三个实现，注册表管理 |
| **TestRun** | 一次执行记录，含状态/起止时间/退出码/环境/各产物路径 |
| **runs/<run_id>/** | 一次执行的所有产物目录（代码/日志/报告/截图/录像），gitignored，DB 关联路径 |

## 自愈

| 术语 | 定义 |
|------|------|
| **SelfHealRecord** | 自愈审计记录：旧→新定位器 + LLM 理由 + 页面状态 + 关联 run |
| **locator_history** | Shape 的定位器版本数组 + current 指针；自愈 append 新版本，回滚切 current |

## 扩展点

| 术语 | 定义 |
|------|------|
| **ShapeType** | 形状类型注册项：输入/按钮/接口/变量/代码/断言/等待/条件…，加类型=注册一条 |
| **Reporter** | 报告适配器：pytest-html / Allure / JUnit XML 各一实现，配置选 |