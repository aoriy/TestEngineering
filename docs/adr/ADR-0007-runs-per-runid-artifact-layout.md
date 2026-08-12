# ADR-0007: runs/<run_id>/ 落盘布局

- **Status**: Accepted
- **Date**: 2026-08-12
- **Related**: architecture-review.md §六, requirements-analysis.md §7.4

## Context

执行产生的代码、日志、报告、截图、录像、trace 需要落盘。最初写在 `app/generated/` 后整体 gitignore，问题：
- 不按 run 隔离 → 多次执行互相覆盖，无法回溯
- DB 不存路径 → 丢失与 run 的关联
- 单机调试要看代码/断点，散落工作区目录难找

## Decision

**按 `runs/<run_id>/` 目录隔离，gitignored，DB 存路径。**

- 目录结构：
  ```
  runs/<run_id>/
    ├─ generated/       # 生成的 pytest 文件、conftest、locustfile
    ├─ log.txt          # stdout 流式日志
    ├─ report.html      # pytest-html 报告
    ├─ screenshots/     # 失败截图
    ├─ video/           # 录像
    └─ trace/           # Playwright trace
  ```
- `.gitignore` 加 `runs/` 与 `app/generated/`
- `TestRun` 表存：`run_id` / `log_path` / `report_path` / `artifacts_dir` / `exit_code` / `status` 等
- 可追溯不丢：DB 关联路径，文件按 run 隔离

## Consequences

**好处**
- 一次 run 的所有产物聚一处，排查快
- 多次执行互不覆盖
- 不污染仓库（gitignored）但 DB 可追溯

**代价**
- 文件需管理生命周期（暂不清理，后续可加保留策略/按 run 清理）
- 单机硬盘会累积，需定期手动清理（NFR 已列存储量上限）