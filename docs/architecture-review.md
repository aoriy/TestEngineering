# 架构评审与修订

> 文档版本：v1.0 (2026-08-12)
> 配套文档：[requirements-analysis.md](./requirements-analysis.md)、[feasibility-analysis.md](./feasibility-analysis.md)、[market-research.md](./market-research.md)
> 评审范围：合理性 / 健壮性 / 扩展性三维检视，聚焦"开工前必决"的关键问题

## 相关文档索引（arc42 最小说闭环）

| 文档 | 类型 | 内容 |
|------|------|------|
| [system-context.md](./system-context.md) | C4 L1 | 系统与外部边界（SUT/浏览器/DeepSeek/Locust） |
| [container-view.md](./container-view.md) | C4 L2 | 容器部署单元与数据流 |
| [sequence-diagrams.md](./sequence-diagrams.md) | 时序 | 执行/自愈/录制导入 3 张 Mermaid 时序图 |
| [nfr.md](./nfr.md) | 质量需求 | 性能/并发/安全/可观测/可维护 量化指标 |
| [glossary.md](./glossary.md) | 术语表 | Shape/Step/Flow/PageTemplate/作用域 等定义 |
| `adr/ADR-0001~0007` | 决策记录 | 7 条关键架构决策登记 |
| [requirements-analysis.md](./requirements-analysis.md) | 需求分析 | 完整方案设计主文档 |
| [feasibility-analysis.md](./feasibility-analysis.md) | 可行性 | 技术/市场/工程三维评估 |
| [market-research.md](./market-research.md) | 市场调研 | 同类产品实证对标 |
| [data-model-detail.md](./data-model-detail.md) | 数据模型 | 字段级设计 + 索引（阶段 0/1 落定） |
| [api-design.md](./api-design.md) | API 设计 | 端点清单 + 响应格式 + 错误码（阶段 0/1 已实现部分） |
| [deployment.md](./deployment.md) | 部署 | 单机启动 + .env 配置清单（阶段 0/1） |
| [selfheal-prompt-design.md](./selfheal-prompt-design.md) | AI 自愈 | Prompt 模板 + 三层防线 + 回滚（阶段 3.5） |
| [locust-detail.md](./locust-detail.md) | 性能 | Locust codegen + spawn + CSV 指标（阶段 4） |

### 待补文档（到对应阶段自动提示，见 smart notes）

- 测试策略 — 阶段 0 末（待 tests/ 出现 test_*.py）
- 画布交互细节 — 阶段 2
- 录制导入细化 — 阶段 5

> 编码规范已并入 AGENTS.md「Coding conventions」章节；字段级数据模型 / API 设计 / 部署文档 / AI 自愈 Prompt 设计 / Locust 细化已随对应阶段补全。

---

## 一、评审结论速览

| 维度 | 修订前评分 | 修订后 | 核心修订 |
|------|----------|--------|---------|
| 合理性 | B+ | A- | 执行层与后端解耦，数据模型补 Project/Environment，FlowNode/PageTemplate 关系厘清 |
| 健壮性 | B- | A- | exec 护栏、Locust 隔离、Playwright 并发、自愈版本化、Jinja2 注入根除 |
| 扩展性 | B | A- | Executor/ShapeType/Reporter 插件化 |

**开工前必决的 3 件事已全部定稿**（见第三、四、五章）。

---

## 二、修订前的 9 个问题清单

### 合理性问题（4）

1. **执行引擎与后端进程耦合**——FastAPI 进程内直接跑 pytest/Playwright/Locust，UI 测试阻塞 API 进程、Locust 吃 CPU 拖垮服务、浏览器崩溃波及后端
2. **生成代码落盘隐患**——`app/generated/` gitignore 后丢追溯，单机调试要断点、多人重新生成要全 DB 状态
3. **数据模型缺 Project/Environment**——没有顶层 Project，也没有 Environment（dev/staging/prod 配置）
4. **Flow vs PageTemplate 关系未定**——"节点=页面实例"未定义，同模板在不同流程带不同数据怎么存不清楚

### 健壮性问题（3 高 + 2 中）

5. **🔴 exec 用户代码安全性**——`import os; os.system(...)` 可毁机，无限循环卡死，写巨大对象爆内存
6. **🔴 Locust 压测与后端互斥**——in-process 跑会拖垮 FastAPI
7. **🔴 Playwright 并发与资源**——多用例并发开多浏览器内存爆炸
8. **🟡 自愈回滚机制**——需保留旧定位器历史版本
9. **🟡 Jinja2 模板注入**——变量值含 `{{`/`{%` 被当模板语法

### 扩展性问题（3 待补）

10. **执行引擎插件化**——写死 pytest+Playwright+requests+Locust，加移动端/桌面会侵入代码生成器
11. **形状类型扩展**——加"上传/拖拽/键盘/网络拦截"需改核心
12. **报告输出插件化**——pytest-html/Allure 写死，CI 集成常需 JUnit XML

---

## 三、关键修订 1：执行层独立 worker 进程

### 方案（MVP = subprocess + Executor 抽象，预留队列升级）

```
FastAPI 进程 (编排层，不跑测试)         Worker 子进程 (隔离执行)
  ├─ POST /runs → 写 TestRun              ├─ uv run pytest runs/<run_id>/...
  ├─ 调 Executor.spawn()                  ├─ 边跑边写 runs/<run_id>/log.txt
  ├─ subprocess.Popen + 超时监控          ├─ 报告落盘 runs/<run_id>/report.html
  └─ GET /runs/{id} 轮询状态             └─ 退出码 → 更新 TestRun.status
```

### 新增 `app/services/executor/` 包

- `base.py`：`Executor` 抽象（`generate_code()` / `spawn()` / `collect_result()`）
- `api_executor.py`：接口用例执行（pytest + requests）
- `ui_executor.py`：UI 用例执行（pytest + Playwright POM）
- `perf_executor.py`：性能执行（`locust --headless` 子进程 + Stats API 抓指标）
- `runner.py`：`subprocess.Popen` spawn（cwd/env/timeout，stdout 流式写日志）
- `registry.py`：Executor 注册表（按用例类型选实现，未来加 Appium/WinAppDriver 只加实现）

### 铁律

- pytest / Playwright / Locust **一律子进程**，绝不在 FastAPI 进程内跑
- Locust 必须独立进程：后端只生成 locustfile 并 spawn，绝不 in-process
- Playwright 并发上限：执行 worker 设浏览器池上限，MVP 串行，后续固定并发度（如 4）；失败截图/录像/trace 落盘进 TestRun
- 前端轮询 `GET /runs/{id}`，SSE 实时流留作升级点

### 预留升级

Executor 接口不变，后续把 spawn 换成 Redis+RQ 即可分布式；MVP 用 subprocess 零额外依赖。

---

## 四、关键修订 2：数据模型补全 + Shape/Step 归属厘清

### 4.1 关键澄清：Shapes vs Steps 的归属

评审里最模糊的一点，定清楚：

- **`PageTemplate` + `Shape` = 元素定义（可复用）**：页面"有什么字段/按钮"，跨流程共享
- **`Flow` + `FlowNode` + `Step` = 流程实例的有序动作**：这条流程里"做哪些动作、什么顺序"
- **`Step` 挂 `FlowNode`，引用 `Shape`**：`step.shape_id → Shape` + `step.order` + `action_type` + `action_params`

这样"列表为默认执行源 + 简图可重排"天然落地：
- 简图画布 = PageTemplate 的 Shapes 按位置渲染
- 步骤列表 = FlowNode 的 Steps 按 order 排序
- 拖拽重排 = 改 `Step.order`
- 同一页模板在不同流程带不同步骤/初始变量 → `FlowNode.initial_vars`（实例级覆盖）

### 4.2 实体层级（修订后）

```
Project (新增顶层)
  ├─ Module (分组，保留)
  ├─ Environment (新增): base_url + vars + headers，用例执行绑环境
  ├─ Requirement
  ├─ TestCase (加 environment_id, flow_id)
  ├─ ApiDefinition (加 project_id)
  └─ Flow (加 project_id)
       └─ FlowNode (引用 PageTemplate + initial_vars)
            └─ Step (引用 Shape + order + action)
PageTemplate (挂 Project + Module)
  └─ Shape (locator_history 版本数组 + current 指针)
SelfHealRecord (关联 Shape 版本 + run_id)
TestRun (加 environment_id, log_path, report_path, exit_code)
TestData (挂 TestCase)
```

### 4.3 关键修正点

1. **补 `Project` 顶层 + `Environment`**（多环境是测试平台刚需，dev/staging/prod 不同 base_url/账号；缺它会卡到执行）
2. **保留 `Module`** 分组（挂 Project 下，PageTemplate/TestCase 分组用）
3. **`Shape.locator_history` 版本化**（自愈回滚基础，不再简单覆盖；append 新版本 + current 指针；回滚 = 切回旧版本 current）
4. **`FlowNode` vs `PageTemplate` 关系**：FlowNode 引用 PageTemplate + initial_vars 实例级覆盖，PageTemplate 可跨 Flow 复用
5. **生成代码落盘 `runs/<run_id>/`**（gitignored），DB 存路径 + 关键 artifacts 路径，可追溯不丢

### 4.4 变量作用域（不变）

| 作用域 | 生命周期 | 用途 |
|--------|---------|------|
| global | 整次运行 | 跨用例共享配置 |
| flow | 整条流程 | 跨页面传值 |
| page | 进页重置 | 关联字段联动（核心） |
| local | 形状内部 | 临时变量 |

变量渲染方式见第六章修订。

---

## 五、关键修订 3：exec 用户代码安全护栏

### 方案（AST 白名单 + subprocess 隔离 + 受控 ctx）

```
代码钩子字符串
  ↓ ast.parse + walk
  → 检查 Import/ImportFrom：只允许白名单模块
  → 检查危险 builtins：屏蔽 __import__/eval/exec/open
  ↓ 通过则在 worker 子进程内 exec
  → globals 只注入: 白名单模块 + 受控 ctx + 安全内建
  → 单步超时 60s（worker 进程级 kill）
  → ctx 只暴露: get_var/set_var/log/call_api/sleep/fail
```

### 白名单

- **允许**：`requests` `httpx` `json` `re` `jsonpath_ng` `datetime` `random` `faker` `decimal` `hashlib`
- **禁止**：`os` `subprocess` `shutil` `open` `socket` `ctypes` `importlib` `__builtins__` 深层访问

### 为什么不用 RestrictedPython

- 限制太死，合法代码常被拒
- AST 白名单足够且可控
- worker 子进程已经隔离崩溃风险
- 单人 Windows 机上 Docker 沙箱不现实

### 受控 ctx API

| 方法 | 用途 |
|------|------|
| `ctx.get_var(name)` | 读变量（任意作用域） |
| `ctx.set_var(name, value, scope='page')` | 写变量 |
| `ctx.log(msg)` | 写日志（进 run log） |
| `ctx.call_api(api_id, params)` | 调接口定义 |
| `ctx.sleep(seconds)` | 等待 |
| `ctx.fail(reason)` | 主动失败并记原因 |

---

## 六、次要问题收尾（开工前一并定）

| 次要问题 | 处理 |
|---------|------|
| 生成代码落盘 | `runs/<run_id>/` 目录结构（test 文件 + log + 报告），DB 存路径，gitignore |
| 自愈版本化 | `Shape.locator_history`（版本数组 + current 指针），自愈 append 新版本，回滚=切 current |
| **Jinja2 注入** | **不用全语法 Jinja2**，改简单 `{{var}}` 正则替换引擎；变量是值不是模板，根除注入 |
| Executor 插件化 | `Executor` 抽象 + 注册表，新执行类型=加实现 |
| ShapeType 插件化 | `ShapeType` 枚举 + 每类型 handler 模块 + 注册表，加类型=注册一条 |
| Reporter 插件化 | `Reporter` 适配器，pytest-html/Allure/JUnit XML 各一，配置选 |

### 变量渲染修订

- **修订前**：Jinja2（`{{var}}` 天然支持）
- **修订后**：简化 `{{var}}` 正则替换引擎（不用 Jinja2 全语法）
- **理由**：变量值含 `{{`/`{%` 会被 Jinja2 当模板语法 → 注入风险。简化替换引擎把变量当值处理，根除注入
- **仍用 Jinja2 的地方**：代码生成模板（`app/templates/pytest/*.j2`）——这是受控的模板，不是用户变量

---

## 七、修订后的技术栈表

| 层 | 选型 | 修订 |
|----|------|------|
| 后端 | FastAPI + SQLAlchemy + SQLite（预留 MySQL） | — |
| 前端 | Vue3 + Vite + Element Plus + AntV X6 + Monaco | — |
| 变量模板 | **简化 `{{var}}` 正则替换引擎** | 修订：去掉 Jinja2 全语法，根除注入 |
| 响应提取 | jsonpath-ng | — |
| UI 执行 | Playwright | — |
| API 执行 | requests / httpx | — |
| 性能 | Locust（`--headless` 子进程） | 修订：子进程隔离，不 in-process |
| 代码生成 | Jinja2 模板（受控，非用户变量） | — |
| AI | OpenAI 兼容协议适配器，DeepSeek v4-pro + thinking | — |
| **执行隔离** | **subprocess + Executor 抽象** | 新增：FastAPI 不跑测试，一律子进程 |
| **代码钩子护栏** | **AST 白名单 + subprocess + 受控 ctx** | 新增 |

---

## 八、修订后的架构图

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

### 代码组织（修订后）

```
TestEngineering/
├── pyproject.toml        # 后端 + 执行引擎 (uv 管理)
├── app/                  # FastAPI 应用
│   ├── models/           # SQLAlchemy 实体
│   ├── schemas/          # Pydantic
│   ├── routers/          # API 路由
│   ├── services/
│   │   ├── codegen/      # Jinja2 代码生成
│   │   ├── executor/     # 执行抽象 + 三个实现 + runner
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

## 九、已确认的取舍决策

本轮评审的 5 个取舍点已全部按推荐路线决定：

| 取舍点 | 决策 |
|--------|------|
| 执行 worker 模式 | **subprocess 优先**（Executor 接口预留 Redis+RQ） |
| 代码钩子护栏 | **AST 白名单** + subprocess + 受控 ctx |
| 变量模板渲染 | **简化替换引擎**（`{{var}}` 正则，不用 Jinja2 全语法） |
| Module 分组 | **保留 Module**（挂 Project 下） |
| 落盘目录 | `runs/<run_id>/`（gitignored，DB 存路径） |

---

## 十、对实施阶段的影响

阶段计划主体不变，但需依修订调整：

| 阶段 | 调整 |
|------|------|
| **0** | 骨架要含 `services/executor/` 抽象 + 数据模型全表（含 Project/Environment/FlowNode/Step） |
| **1** | 用例管理 CRUD 要带 Project/Environment 上下文 |
| **2** | 简图画布渲染 Shape，步骤列表渲染 Step（按 order），重排=改 order |
| **3** | Executor 子进程跑 + runs/<run_id>/ 落盘 + exec 护栏 + 简化变量引擎 |
| **3.5** | 自愈写入 Shape.locator_history 版本，回滚=切 current |
| **报告** | Reporter 插件化，MVP 用 pytest-html，Allure/JUnit XML 可选 |