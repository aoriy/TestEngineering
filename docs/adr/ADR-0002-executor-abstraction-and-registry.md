# ADR-0002: Executor 抽象 + 注册表

- **Status**: Accepted
- **Date**: 2026-08-12
- **Related**: architecture-review.md §三/§六, ADR-0001

## Context

执行引擎写死"pytest+Playwright / pytest+requests / Locust"会让后续扩展（移动端 Appium、桌面 WinAppDriver、协议 gRPC）侵入代码生成器与 runner，每加一种就改核心。

## Decision

**把执行抽象成 `Executor` 接口 + 注册表模式。**

- `app/services/executor/base.py`：`Executor` 抽象（`generate_code()` / `spawn()` / `collect_result()`）
- `api_executor.py` / `ui_executor.py` / `perf_executor.py`：三个实现
- `app/services/registry/executor_registry.py`：按"用例类型"选实现
- 新执行类型 = 加一个实现 + 注册一条，不改核心
- ShapeType / Reporter 同样采用注册表（见 ADR-0006 / NFR）

## Consequences

**好处**
- 加 Appium/WireMock/JMeter 只加实现，核心稳
- 三类执行差异隔离在一处，易测试
- 配合 ADR-0001 子进程隔离，Executor 是 spawn 的边界

**代价**
- 一次抽象成本（接口设计需想清）
- 极简用例可能感觉 over-engineered，但扩展性收益大于此成本