# 需求分析与方案设计

> 文档版本：v1.0 (2026-08-10)
> 配套文档：[market-research.md](./market-research.md)、[feasibility-analysis.md](./feasibility-analysis.md)

---

## 一、需求背景

我是一个测试员，工作中遇到的实际痛点：
- 纯列表式管理工具（用例 / 步骤 / 元素都是平铺列表）**无法直观感受到页面上下文**，理解复杂业务流吃力
- 接口测试和 UI 测试割裂，同一个业务的 UI 操作和底层接口重复维护
- 关联字段（A 字段输入后带出 B 字段）的联动逻辑散落在脚本里，难复用、难理解
- 页面变化时定位器失效，纯脚本维护成本高

本项目旨在构建一个**个人测试工程管理平台**，覆盖需求分析、用例管理、自动化测试（接口 + UI）、性能测试，并用一种直观的"页面简图画布"作为差异化核心。

---

## 二、需求范围

### 2.1 四大功能模块

| 模块 | 范围定位 | 说明 |
|------|---------|------|
| 需求分析 | **轻量** | 需求 CRUD + 需求 ↔ 用例追溯矩阵 |
| 用例管理 | **轻量** | 用例 CRUD、标签、优先级、执行记录 |
| 自动化 - UI | **重做（核心）** | 页面简图画布 + 步骤列表 + 代码钩子 + 变量系统 + 录制导入 + Playwright 执行 |
| 自动化 - API | **轻量** | requests 直接跑，复用接口定义 |
| 性能测试 | **最轻** | Locust 复用接口定义，启动按钮 + 报告 |

> 范围策略：**收缩范围，聚焦差异化**。把火力集中在独特点（画布 + 钩子 + 变量 + 自愈），其余模块做够用版，不做花活。

### 2.2 核心痛点 → 功能映射

| 痛点 | 功能 |
|------|------|
| 列表不直观 | 页面简图画布（展示层） |
| UI / API 割裂 | 一份模型双执行（Playwright + requests 同源生成） |
| 关联字段联动难复用 | 接口返回值驱动 + 页面公共变量 + `{{var}}` 引用 |
| 动态逻辑难表达 | 形状上的 Python 代码钩子（before/after） |
| 定位器失效 | AI 自愈（DeepSeek 适配器，验证后自动修复） |

---

## 三、核心概念定义

### 3.1 简图（画布）

**简图 ≠ 页面模型，简图 = 可视化的组织层（展示容器）**。

- 每个页面一张画布，画布上的形状 = 该页面的元素 / 步骤
- 用基础形状一比一示意真实页面（线框图），但不追求还原：
  - 输入框 = 普通正方形
  - 按钮 = **粗边框**正方形
  - 下拉 = 正方形带 ▼
  - 复选框 = 小方块带 ✓
  - 接口调用 = 圆角方框
  - 变量 = 菱形
  - Python 代码 = 带 `</>` 图标的方块
  - 断言 = 带 ⚖ 图标的方块
- **执行靠定位器**（xpath / data-testid 优先），Playwright 定位时根本不看简图
- 页面变了 → 重新录一遍、重新放形状即可，**不需要维护图与页面的对应关系** → 绕开"模型漂移"死穴

### 3.2 形状（Shape）

每个形状是一个可视化节点，可绑定：
- 类型（输入 / 按钮 / 下拉 / 复选框 / 接口 / 变量 / 代码 / 断言 / 等待 / 条件）
- 视觉样式（普通 / 粗边框 / 圆角等，按类型自动）
- 定位器（data-testid 优先，xpath / css / 文本兜底）
- 接口绑定（method / url / 入参映射 / 响应提取）
- 代码钩子（before_code / after_code，Python 代码）
- 变量读写（值来源 / 提取规则）

### 3.3 代码钩子

每个形状有两个可选 Python 代码槽位：
- **前置 `before_code`**：处理入参、造数据、调用工具函数
- **后置 `after_code`**：解析响应、提取变量、临时断言
- 运行时 API：`ctx.get_var('x')`、`ctx.set_var('x', v)`、`ctx.log()`、`ctx.call_api()`

### 3.4 变量系统

三级作用域：
```
全局变量(global) → 流程变量(flow) → 页面公共变量(page)   ← 重点
```
- 页面公共变量：进页时**重置**，页面内所有形状 / 代码 / 接口都可见可读写
- 引用语法：`{{变量名}}`，支持嵌套
- 提取语法：接口响应 → JSONPath / 正则 / XPATH → 变量名

### 3.5 流转图

- 节点 = 页面画布实例，边 = 跳转操作（点击某按钮 → 进入某页）
- 拖拽拼接多个页面画布 = 完整业务流
- 跨页数据传递 = 流程变量 / 全局变量

### 3.6 录制导入

- 用 Playwright codegen 捕获操作和定位器
- 自动生成步骤列表 + 自动排版成简图形状
- **录制为主，手动添加形状兜底**
- 用户可在简图上拖拽重排 / 连线，重排即改执行顺序

### 3.7 执行顺序

- **列表为默认执行源**（录制生成有序步骤）
- 简图上拖拽重排 / 连线 = 修改执行顺序
- 列表与简图双向联动

---

## 四、端到端执行示例（关联字段场景）

页面「客户详情」画布中的形状序列：
```
① 输入框「客户编号」  值={{数据行.customer_id}}
② 按钮「查询」  before_code: 取①的值→requests 调 GET /api/customer/{id}
                 after_code:  response.json()['data']['name'] → set_var('客户姓名')
③ 输入框「客户姓名」  值={{客户姓名}}   ← 自动带出
④ 按钮「保存」 → 断言「保存成功」提示
```

生成代码后：
- UI 模式：Playwright 真实执行 ①②③④
- 接口模式：直接发请求

**一份画布，双执行路径**（保留 Tricentis Tosca 理念，但用页面线框图承载）。

---

## 五、AI 自愈模块

### 5.1 工作流程（定位失败时触发）

```
执行失败(元素未找到/超时)
   ↓
采集现场: 页面HTML片段 + 截图 + 旧定位器
   ↓
调用第三方LLM(DeepSeek): "旧xpath失效了,分析下面HTML,给出新定位器"
   ↓
LLM返回候选定位器 (结构化JSON)
   ↓
自动验证: Playwright试跑新定位器
   ↓
通过 → 自动更新元素定位器 + 记录自愈日志
失败 → 作为"建议修复"留存,人工确认
```

### 5.2 关键设计

1. **适配器抽象**：`LlmAdapter` 支持 OpenAI 兼容协议，`base_url` 可配 → 兼容 DeepSeek / Qwen / GLM / OpenAI 任意一家
2. **默认配置**：DeepSeek（实证：`base_url=https://api.deepseek.com`，模型 `deepseek-v4-pro` / `v4-flash`，OpenAI 兼容协议 `client.chat.completions.create`），api_key 走 `.env`（沿用 `OPENAI_API_KEY` 约定）
3. **模型选型（实证）**：自愈用 **`deepseek-v4-pro` + 开启 `thinking` mode + `reasoning_effort: high`**。自愈是"错一次比贵一万次更糟"的场景，质量优先于成本；thinking 模式让模型显式推理 XPath，可解释性强，正好填进自愈审计日志
4. **成本无忧**：自愈只在定位失败时触发（健康代码库失败率 < 10%），单次 3-4k 入 + 1k 出 tokens，按 DeepSeek 公开量级是分钱级，一天回归数十次自愈约月几元级
5. **三档动作**：`auto`(置信度高自动改) / `suggest`(建议待确认) / `off`(关闭)
6. **审计**：每次自愈记录"旧 → 新定位器 + 页面状态 + LLM 理由"，可回滚
7. **自动化程度**：验证后自动修复（推荐路线）
8. **配额与缓存**：相同页面 + 旧定位器缓存自愈结果，不重复调；单次执行内自愈调用上限（防雪崩烧钱）；`.env` 的 `SELFHEAL_MODE=auto/suggest/off`，高危页面单独标 `suggest`

### 5.3 防误判三层防线（核心投入点）

LLM 自愈真正的风险不是成本，是**"看着对但语义错"**——找到页面里另一个相似按钮，自动修复后用例假绿。三层防线：

1. **验证层**：Playwright 试跑新定位器，必须**唯一匹配 + 可见 + 可点击**才接受
2. **语义指纹校验**：对比新旧定位器所在元素的 `innerText` / `aria-label` / `role` 相似度，低于阈值（如 0.6）降级为建议。这一层决定了"修的是同一个东西"
3. **置信度门限**：要求 LLM 返回 JSON `{locators:[...], confidence:0.0-1.0}`，低于 0.8 转人工

**工程重点投在这三层而非省钱**——成本无忧，质量才是自愈可用与否的分水岭。

### 5.3 AI 能力范围

- **自愈**：定位器自愈（核心）
- **分析建议**：报告分析 + 用例建议（沿用并升级 `ai_helper.py` 现有能力）
- 不做：自然语言生成用例等重量功能

---

## 六、技术架构

### 6.1 总体架构

> 架构评审后修订：见 [architecture-review.md](./architecture-review.md) 第三、四、五、六章

```
┌─ Frontend: Vue3 + X6 画布 + Monaco ─┐
└──────────────┬───────────────────────┘
               │ REST (轮询)
┌──────────────▼───────────────────────┐
│ Backend: FastAPI (编排层，不跑测试)   │
│  services/: codegen/executor/selfheal │
│  executor/: base/api/ui/perf + runner │
└──────────────┬───────────────────────┘
               │ subprocess.spawn
┌──────────────▼───────────────────────┐
│ Worker 子进程 (隔离执行)              │
│  pytest+requests / pytest+Playwright │
│  locust --headless / exec 钩子(AST)   │
│  → DeepSeek 自愈                      │
└──────────────────────────────────────┘
DB: Project→Module→PageTemplate→Shape
    Environment / Flow→FlowNode→Step
    TestRun / SelfHealRecord
生成代码: runs/<run_id>/ (gitignored)
```

**铁律**：pytest/Playwright/Locust 一律子进程，绝不在 FastAPI 进程内跑。

### 6.2 技术栈

| 层 | 选型 | 备注 |
|----|------|------|
| 后端 | FastAPI + SQLAlchemy + SQLite（预留 MySQL） | — |
| 前端 | Vue3 + Vite + Element Plus + **AntV X6**（画布）+ **Monaco Editor**（代码钩子） | — |
| 变量模板 | **简化 `{{var}}` 正则替换引擎** | 修订：去掉 Jinja2 全语法，根除注入；Jinja2 仅用于受控的代码生成模板 |
| 响应提取 | jsonpath-ng | — |
| UI 执行 | Playwright（子进程） | — |
| API 执行 | requests / httpx（子进程） | — |
| 性能 | Locust（`--headless` 子进程 + Stats API） | 子进程隔离，绝不 in-process |
| 代码生成 | Jinja2 模板（受控，非用户变量） | `app/templates/pytest/*.j2` |
| AI | OpenAI 兼容协议适配器，DeepSeek v4-pro + thinking | — |
| **执行隔离** | **subprocess + Executor 抽象** | FastAPI 不跑测试，一律子进程；Executor 接口预留 Redis+RQ |
| **代码钩子护栏** | **AST 白名单 + subprocess + 受控 ctx** | 单步超时 60s |

### 6.3 代码组织

```
TestEngineering/
├── pyproject.toml        # 后端 + 执行引擎 (uv 管理)
├── app/                  # FastAPI 应用
│   ├── models/           # SQLAlchemy 实体
│   ├── schemas/          # Pydantic
│   ├── routers/          # API 路由
│   ├── services/
│   │   ├── codegen/      # Jinja2 代码生成
│   │   ├── executor/     # 执行抽象 + api/ui/perf 实现 + runner
│   │   ├── selfheal/     # DeepSeek 适配器 + 防误判三层
│   │   └── registry/     # Executor/ShapeType/Reporter 注册表
│   ├── templates/        # pytest/locust Jinja2 模板 (受控)
│   └── core/             # config/db/安全/变量引擎
├── runs/                 # 生成代码+日志+报告 (gitignored，按 run_id)
├── frontend/             # Vue3 + Vite + AntV X6 (npm)
├── tests/                # 平台自身 pytest 测试
├── docs/                 # 设计文档
└── AGENTS.md
```

---

## 七、数据模型

> 架构评审后修订：见 [architecture-review.md](./architecture-review.md) 第四章

### 7.1 实体层级（修订后）

```
Project (顶层容器)
  ├─ Module (分组)
  ├─ Environment: base_url + vars + headers，用例执行绑环境
  ├─ Requirement
  ├─ TestCase (加 environment_id, flow_id)
  ├─ ApiDefinition (挂 project_id，UI/API/性能复用)
  └─ Flow (挂 project_id)
       └─ FlowNode (引用 PageTemplate + initial_vars 实例级覆盖)
            └─ Step (引用 Shape + order + action_type + action_params)
PageTemplate (挂 Project + Module)
  └─ Shape (locator_history 版本数组 + current 指针)
Requirement ↔ TestCase (多对多，追溯矩阵)
TestData (挂 TestCase，数据驱动行)
TestRun (加 environment_id, log_path, report_path, exit_code)
SelfHealRecord (关联 Shape 版本 + run_id，可回滚)
```

### 7.2 关键归属厘清：Shape vs Step

- **`PageTemplate` + `Shape` = 元素定义（可复用）**：页面"有什么字段/按钮"，跨流程共享
- **`Flow` + `FlowNode` + `Step` = 流程实例的有序动作**：这条流程里"做哪些动作、什么顺序"，`Step.shape_id → Shape` + `Step.order`
- **机制落地**：
  - 简图画布 = PageTemplate 的 Shapes 按位置渲染
  - 步骤列表 = FlowNode 的 Steps 按 order 排序
  - 拖拽重排 = 改 `Step.order`
  - 同一页模板在不同流程带不同步骤/初始变量 → `FlowNode.initial_vars`

### 7.3 自愈版本化

- `Shape.locator_history`：版本数组 + current 指针，不再简单覆盖
- 自愈 append 新版本并标记 current，回滚 = 切回旧版本 current
- `SelfHealRecord` 关联 Shape 版本 + run_id + 旧→新定位器 + 理由 + 页面状态

### 7.4 生成代码与报告落盘

- `runs/<run_id>/` 目录结构（test 文件 + log + 报告 + 截图/录像/trace）
- gitignored，DB 存路径 + 关键 artifacts 路径，可追溯不丢

### 7.5 变量作用域

| 作用域 | 生命周期 | 用途 |
|--------|---------|------|
| global | 整次运行 | 跨用例共享配置 |
| flow | 整条流程 | 跨页面传值 |
| page | 进页重置 | 关联字段联动（核心） |
| local | 形状内部 | 临时变量 |

变量渲染用简化 `{{var}}` 正则替换引擎（不用 Jinja2 全语法，根除注入；Jinja2 仅用于受控代码生成模板）。

---

## 八、实施阶段（每阶段提交本地 git）

| 阶段 | 内容 | 交付物 |
|------|------|--------|
| **0** | 骨架：FastAPI 建表 + Vue3 前端 + X6 画布可跑 | 可启动的前后端 |
| **1** | 需求管理 + 用例管理（够用版 CRUD + 追溯矩阵） | 最先用起来 |
| **2** | 页面简图画布 + 步骤列表 + 流转图（拖拽 / 重排 / 连线） | 简图核心落地 |
| **3** | 代码钩子 + 变量系统 + 执行引擎 + 报告（先接口后 UI） | 拖图重排即可运行 |
| **3.5** | AI 自愈（DeepSeek 适配器）+ 报告 / 用例 AI 建议 | 补齐定位器维护短板 |
| **4** | Locust 性能测试（复用接口定义） | 压测可复用用例 |
| **5** | 录制导入（Playwright codegen）+ 数据驱动 + 完善 | 闭环可用 |

### 提交约定
- 每阶段结束提交**本地** git，远程推送由用户处理
- API key 只在 `.env`，绝不 commit

---

## 九、关键决策记录

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 页面简图形态 | 结构化页面编辑器 | 可靠，避免截图标注的坐标脆弱 |
| 部署形态 | 单机起步预留扩展 | 开发快，先用起来 |
| 流转图执行方式 | 先生成代码后续升级 | 可调试、可维护，兜底 |
| 性能测试方案 | Locust | Python 原生，复用接口定义 |
| 页面公共变量重置时机 | 进页重置 | 避免脏状态，符合字段联动语义 |
| 形状代码钩子粒度 | 前后置钩子 | 够用且清晰 |
| UI 定位器策略 | data-testid 优先 | 最可靠，需开发协作埋点 |
| 执行顺序来源 | 列表为默认 + 简图可重排 | 录制生成有序，重排即改序 |
| 简图组织粒度 | 每页一画布 + 流转图 | 与真实页面结构对齐 |
| 元素录入方式 | 录制导入 + 手动添加 | 录制为主提效，手动兜底 |
| LLM 供应商 | DeepSeek（OpenAI 兼容） | 国内可达、便宜、协议通用 |
| 自愈自动化程度 | 验证后自动修复 | 平衡效率与安全 |
| AI 能力范围 | 自愈 + 分析建议 | 聚焦核心痛点，不做重量功能 |
| 范围取舍（决策补充）| 全自研外围轻做（路线 C）| HttpRunner(Go)/MeterSphere(Java) 不同栈，借力反而强化割裂；"Python 全栈+画布"是差异化生态位 |
| AI 自愈模型选型 | DeepSeek v4-pro + thinking | 自愈是"错一次比贵一万次更糟"，质量优先；thinking 可解释性强，填进审计日志 |
| 自愈防误判 | 验证层 + 语义指纹 + 置信度门限 | 修"对的东西"比省钱重要，三层决定可用性 |
| 简图自动生成 | 区域吸附为主 + 时间序兜底 | Playwright 真实坐标缩放上画布，匹配"一比一示意"初衷，不用 AI 布局 |
| 接口用例形态 | 数据流走画布 + 顺序走列表，共享 ApiDefinition | 与 HttpRunner 统一格式理念一致，但画布形态升级 |
| 报告方案 | MVP 用 pytest-html，Allure 可选开关 | 个人工具无需 Allure 的汇报价值；Allure 依赖已留 |
| 多人协作预留 | 预留 owner/project 字段 + X-User header | 不实现鉴权，单人阶段权限纯负担；补 import/export 导出 |

---

## 十、开放问题收敛结论（实证补充调研后）

以下 6 个开放问题经第二轮实证调研（代理已通）后全部收敛：

### 1. 范围取舍——路线 C 全自研外围轻做

**结论**：不借力 MeterSphere / HttpRunner。理由：HttpRunner v5（4295 stars，Go）虽覆盖一致但栈不同；MeterSphere（Java）亦不同栈。**你的痛点是"用例/元素/步骤/执行彼此割裂"，借力不同栈工具恰恰强化割裂**——用例去别处跑，画布在 Python 端，绑定断了。**只有自研一条路能让画布↔执行↔自愈全打通，且"Python 全栈+Web 画布"在开源里暂无人占位**。

### 2. AI 自愈成本——DeepSeek v4-pro + thinking，成本无忧

**实证**：DeepSeek `base_url=https://api.deepseek.com`，模型 `deepseek-v4-pro`/`v4-flash`，支持 `thinking` mode + `reasoning_effort: high`，OpenAI 兼容协议。自愈只在定位失败时触发（< 10%），单次分钱级，月几元级。**重点不在省钱而在防误判**，采用 v4-pro + thinking 让可解释性填进审计日志。三层防线（验证 + 语义指纹 + 置信度门限）是核心投入点。

### 3. 多人协作——预留到字段级，不实现鉴权

**结论**：预留 `owner`/`project` 字段 + `X-User` header 占位，不画登录页、不做 RBAC、不做并发锁。单人阶段权限是纯负担，真要多人时改造成本可控。**补一项 import/export**（项目/用例/画布整体导出 JSON），低工作量、高未来弹性。

### 4. 简图自动生成——区域吸附为主，时间序兜底

**结论**：录制每个元素时 Playwright 已通过 `getBoundingClientRect` 拿到真实坐标，缩放映射到画布坐标系，形状自动落在贴近真实页面的位置。Users 手动微调即可。**正好匹配"简图一比一示意真实页面"的初衷，不用 AI 布局**（AI 布局不稳定且过度工程）。坐标无法获取（如 iframe 内）降级为时间序排列。录制结束给"自动排版"重跑按钮。

### 5. 接口测试 UI 形态——双视图共享 ApiDefinition

**结论**：复杂数据流（取数→创建→断言）用画布画，享受变量联动；轻量顺序用例走列表页。二者共用 `ApiDefinition` + 变量系统，是同一数据的不同视图。**与 HttpRunner v5 统一格式理念一致，但画布形态升级**——HttpRunner 是 GoTest/YAML/JSON/Text/pytest 多格式统一，本项目是"画布/列表双视图 + 共享定义"，形态差异即差异化。

### 6. 报告方案——MVP 用 pytest-html，Allure 可选开关

**实证**：Allure（Python 适配 813 stars + allure2 5494 stars，需 Java 二进制）vs pytest-html（775 stars，纯 Python 一键单文件）。**MVP 用 pytest-html**（零额外依赖、栈一致），`TestRun` 表存原始结果，渲染"有 Allure 用 Allure，否则 pytest-html"。Allure 作为可选开关（`allure-pytest` 依赖已留），需要汇报场景时再装命令行。