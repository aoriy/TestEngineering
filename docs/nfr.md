# 质量需求（NFR）

> 非功能需求量化指标，分阶段目标
> 配套：feasibility-analysis.md / architecture-review.md / ADR-0001/0003/0005

## 一、性能

| 指标 | 量化 | 阶段目标 | 说明/验收 |
|------|------|---------|----------|
| 单用例启动延迟 | codegen+spawn→首个动作执行 | ≤ 3s (MVP) / ≤ 1.5s (优化) | 排除 SUT 响应时间 |
| API 用例执行 | 10 个接口用例总耗时 | ≤ 10s (MVP) | 同等 SUT 响应对比 |
| UI 用例执行 | 10 步 Playwright 流程 | ≤ 30s (MVP) | 受 SUT 响应影响 |
| 自愈调用延迟 | 单次失败自愈 p95 | ≤ 5s (含 DeepSeek + 三层验证) | 命中缓存 ≤ 200ms |
| 前端首屏 | SPA 加载 | ≤ 2s (dev mode) | Vite 下 |

## 二、并发与资源

| 指标 | 量化 | 阶段目标 | 约束机制 |
|------|------|---------|---------|
| 单机 worker 并发浏览器 | MVP 1 / 目标 4 | MVP 串行 | Executor 浏览器池上限 |
| 单次执行自愈调用上限 | ≤ 30 次/单次 run | 防雪崩烧钱 | selfheal 配额 |
| 单步钩子超时 | 60s | 防 exec 卡死 | worker 进程级 kill (ADR-0003) |
| 用例执行超时 | 可配置，默认 1800s | 防长跑锁死 | subprocess timeout |
| 压测 worker 上限 | 1 | MVP 单机单 perf | 子进程隔离 (ADR-0001) |

## 三、安全

| 指标 | 量化 | 机制 |
|------|------|------|
| 钩子 import 白名单违规 | 0 价外（应拒绝的全拒绝） | AST 静态检查 (ADR-0003) |
| 危险 builtins 屏蔽 | 100% (`__import__/eval/exec/open` 不可达) | globals 注入 |
| 变量模板注入 | 0 例（变量值含 `{{`/`{%` 不当语法） | 简化替换引擎 (ADR-0004) |
| API key 泄漏 | 0（绝不 commit / 不回日志） | .env + 日志脱敏 |
| 自愈自动通过率语义正确 | ≥ 80% | 三层防线 (ADR-0005) |

## 四、可观测性

| 指标 | 量化 | 说明 |
|------|------|------|
| 执行日志覆盖 | 100% run必有 log.txt | stdout 流式落盘 runs/&lt;run_id&gt;/ |
| 失败截图 | 失败用例 100% 有截图 | Playwright screenshot |
| 失败录像 | 失败 UI 用例 100% 有 video | Playwright video |
| 失败 trace | 失败 UI 用例 100% 有 trace.zip | Playwright trace |
| 自愈审计 | 100% 自愈事件留 SelfHealRecord | 关联 run_id + locator_history |
| TestRun 字段完整 | 100% (起止/状态/码/路径必填) | DB NOT NULL |

## 五、可维护 / 可扩展

| 指标 | 量化 | 机制 |
|------|------|------|
| 新增执行器/形状/报告类型 | 仅加实现，不改核心 | 注册表模式 (ADR-0002) |
| 代码生成模板独立 | 加新执行器只增加 .j2 文件，不改 codegen 核心 | templates/ 目录隔离 |
| 切换 LLM 供应商 | 改 base_url/model/api_key，不改 selfheal 逻辑 | 适配器 |
| 切换 DB | 改连接串（SQLite→MySQL） | SQLAlchemy ORM 隔离 |
| 切换执行调度 | 改 spawn 实现为 Redis+RQ | Executor 接口不变 |

## 六、存储与清理（暂列目标，后续补策略）

| 指标 | 量化 | 说明 |
|------|------|------|
| 单次 run 目录上限 | ≤ 50MB（截图/录像过多需聚簇压缩） | 建议 NFR 守门阈值 |
| 总 runs/ 增长 | 人工清理（MVP）；后续自动保留 N 天 | 待补策略 |
| DB 大小 | < 100MB（SQLite 单机不上量） | 自愈审计膨胀时清理 |

## 七、可用性 / 可移植

| 指标 | 量化 | 说明 |
|------|------|------|
| 主开发平台 | Windows | 用户环境 |
| 可移植到 | Linux | FastAPI/Playwright/Locust 都跨平台，预期无障碍 |
| 启动依赖 | uv sync + (前端) npm install 后可跑 | 无外网/无代理可跑（ DeepSeek 自愈需外网，关闭后降级为失败） |
| 离线降级 | 关 AI 自搜后用例正常跑，仅定位失败时不自动修 | 配置开关 SELFHEAL_MODE=off |