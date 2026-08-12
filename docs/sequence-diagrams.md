# 关键时序图（Mermaid）

> 3 个最关键运行时场景的时序视图
> 配套：container-view.md / architecture-review.md / ADR-0001/0005/0006

## 1. 执行流转时序

```mermaid
sequenceDiagram
    autonumber
    participant U as 测试员
    participant SPA as Frontend (Vue3)
    participant API as Backend (FastAPI)
    participant EX as Executor
    participant WK as Worker (子进程)
    participant DB as SQLite
    participant FS as runs/&lt;run_id&gt;/

    U->>SPA: 点击"执行" (选 TestCase + Environment)
    SPA->>API: POST /runs {testcase_id, env_id}
    API->>DB: INSERT TestRun (status=running)
    API->>EX: Executor.generate_code(testcase, env)
    EX->>FS: 写 generated/*.py + conftest.py
    EX->>FS: 写 locustfile.py (若 perf) / POM 文件 (若 UI)
    EX->>WK: subprocess.Popen (uv run pytest ..., cwd=runs/&lt;run_id&gt;/)
    WK-->>FS: stdout 流式写 log.txt
    WK-->>FS: 失败截图/录像/trace 落盘
    loop 轮询 (每 1-2s)
        SPA->>API: GET /runs/{id}
        API->>DB: SELECT status
        API-->>SPA: {status, progress}
    end
    WK-->>EX: 退出码 0/1/超时
    EX->>DB: UPDATE TestRun (status, exit_code,finished_at, paths)
    EX->>FS: 报告落盘 report.html
```

**关键约束**：FastAPI 进程自始至终不跑测试，只 spawn 与轮询；Worker 隔离崩溃不影响编排层。

## 2. 自愈流程时序

```mermaid
sequenceDiagram
    autonumber
    participant WK as Worker (Playwright)
    participant API as Backend
    participant SH as selfheal service
    participant DS as DeepSeek v4-pro
    participant DB as SQLite

    WK->>WK: 元素定位失败 (旧 xpath 超时/无匹配)
    WK->>API: POST /selfheal {shape_id, old_locator, page_html, screenshot}
    API->>SH: 触发自愈
    SH->>SH: 1. 检查缓存 (page_sign+old_locator) 命中则返回
    SH->>DS: messages=[system:自愈专家, user:旧xpath+HTML片段], thinking=enabled, reasoning_effort=high
    DS-->>SH: JSON {locators:[...], confidence:0.92, reasoning:"..."}
    SH->>SH: 2. 验证层: Playwright 试跑每个候选 (唯一/可见/可点击)
    SH->>SH: 3. 语义指纹校验: 新旧元素 innerText/aria-label/role 相似度
    SH->>SH: 4. 置信度门限: 0.92 >= 0.8 → 通过
    alt 验证+指纹+置信度都通过
        SH->>DB: INSERT locator_history (新版本, current=新)
        SH->>DB: INSERT SelfHealRecord (旧→新, 理由, run_id)
        SH-->>API: auto-applied (auto)
        API-->>WK: 用新 locator 重试当前步骤
    else 任一未达阈值
        SH->>DB: INSERT SelfHealRecord (status=suggest)
        SH-->>API: suggest (需人工确认)
        API-->>WK: 失败/跳过当前步骤
    end
```

**关键约束**：三层防线（验证/指纹/置信度）是核心投入点；只有三层全过才自动改，否则降级为建议（ADR-0005）。回滚 = 切回 locator_history 旧版本 current。

## 3. 录制导入时序（阶段 5）

```mermaid
sequenceDiagram
    autonumber
    participant U as 测试员
    participant SPA as Frontend
    participant API as Backend
    participant CG as Playwright codegen (子进程)
    participant SUT as 被测系统
    participant DB as SQLite

    U->>SPA: 选择目标 PageTemplate, 启动录制
    SPA->>API: POST /record/start {page_template_id, env_id}
    API->>CG: subprocess.Popen (playwright codegen --target=python, base_url=env.base_url)
    CG->>SUT: 打开浏览器, 用户在 SUT 上操作
    CG->>SUT: 每次动作: 记录 (action_type, locator, getBoundingClientRect 坐标)
    CG-->>API: 实时上报 (或批次回传) 操作序列
    API->>API: 1. 为每动作建/复用 Shape (按 locator 去重)
    API->>API: 2. 用 Playwright 真实坐标 → 区域吸附映射画布 (缩放比例)
    API->>API: 3. 按顺序建 Step (shape_id, order, action_type, action_params)
    loop 用户继续操作
        CG->>SUT: ...
        CG-->>API: ...
    end
    U->>SPA: 停止录制
    SPA->>API: POST /record/stop {run_id}
    API->>CG: 终止子进程
    API->>DB: 批量 INSERT Shape/Step, 画布坐标已吸附
    API-->>SPA: 返回画布预览 (形状已排版)
```

**关键约束**：录制在子进程跑（ADR-0001）；区域吸附用 Playwright 真实坐标缩放上画布，不调用 AI（避免布局不稳定、过度工程）；坐标取不到（iframe 内）降级为时间序排列。