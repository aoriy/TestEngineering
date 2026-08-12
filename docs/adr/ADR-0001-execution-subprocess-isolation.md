# ADR-0001: 执行层 worker 子进程隔离

- **Status**: Accepted
- **Date**: 2026-08-12
- **Related**: architecture-review.md §三, requirements-analysis.md §6.1

## Context

自动化工(UI/API/性能)需要跑 pytest / Playwright / Locust。若在 FastAPI 进程内直接跑：
- UI 测试阻塞 API 进程，界面卡死
- Locust 压测吃 CPU/内存，拖垮后端服务
- Playwright 浏览器崩溃可能波及后端进程
- 无超时控制，长跑用例能锁死整个平台

业界测试平台（Katalon Studio、MeterSphere）都把执行与编排分进程。

## Decision

**执行层独立成 worker 子进程。FastAPI 只编排，不跑测试。**

- `app/services/executor/` 抽象：`base.Executor` 接口（`generate_code` / `spawn` / `.collect_result`）+ api/ui/perf 三个实现 + `runner.py` 用 `subprocess.Popen`（cwd/env/timeout，stdout 流式写日志）
- pytest / Playwright / Locust **一律子进程**
- 前端轮询 `GET /runs/{id}` 取状态；SSE 留作升级点
- MVP 用 subprocess（零额外依赖）；Executor 接口不变，后续可换 Redis+RQ 分布式

## Consequences

**好处**
- 编排与执行隔离，崩溃互不波及
- 资源上限可控（Playwright 并发、Locust CPU）
- 超时可在进程级 kill
- Executor 接口预留下沉到队列
- 单机零额外依赖

**代价**
- MVP 单机串行（多并发需自建池）
- 状态用轮询（简单但延迟比 SSE/WebSocket 高，单机可接受）
- 需管理 runs/&lt;run_id&gt;/ 目录的生命周期

## Alternatives Considered

- **直接在 FastAPI 进程内跑**：危险，pass
- **一上来上 Redis+RQ**：MVP 增加部署复杂度依赖，pass（留升级口）