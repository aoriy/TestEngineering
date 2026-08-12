# 系统上下文（C4 Level 1）

> C4 模型第 1 层：本系统与外部系统/人员的边界关系
> 配套：container-view.md（L2）/ sequence-diagrams.md / architecture-review.md

## 图

```mermaid
C4Context
title TestEngineering 系统上下文

Person(tester, "测试员", "使用平台编排与执行测试")
System(te, "TestEngineering", "测试工程管理平台：编排+执行+自愈")

System(sut, "被测系统 (SUT)", "Web 应用/接口服务")
System_Ext(browser, "浏览器", "Playwright 驱动的 Chromium/WebKit/Firefox")
System_Ext(deepseek, "DeepSeek API", "v4-pro + thinking，定位器自愈")
System_Ext(locust, "Locust Worker", "性能压测子进程")

Rel(tester, te, "浏览器访问 (Vue3 SPA)")
Rel(te, sut, "HTTP/HTTPS (API 用例)")
Rel(te, browser, "Playwright 协议 (UI 用例)")
Rel(browser, sut, "HTTP/HTTPS (真实操作)")
Rel(te, deepseek, "OpenAI 兼容协议 (自愈)")
Rel(te, locust, "subprocess spawn")
Rel(locust, sut, "HTTP/HTTPS (压测)")
```

## 边界说明

| 边界 | 协议/方式 | 说明 |
|------|---------|------|
| 测试员 ↔ TestEngineering | HTTP（浏览器） | Vue3 SPA，FastAPI 提供 REST |
| TestEngineering ↔ SUT | HTTP/HTTPS | API 用例直接发请求；UI 用例经浏览器 |
| TestEngineering ↔ 浏览器 | Playwright 协议 | 子进程内驱动浏览器，浏览器再访问 SUT |
| TestEngineering ↔ DeepSeek | HTTPS（OpenAI 兼容）| 仅定位失败时调用，触发率 < 10% |
| TestEngineering ↔ Locust | subprocess | Locust 在 worker 子进程跑（`locust --headless`），Stats API 抓指标 |

## 关键约束（来自 ADR）

- TestEngineering 内部分两层：FastAPI 编排 + Worker 子进程执行（ADR-0001）
- 浏览器、Locust 都不与 SUT 直接经 TestEngineering 转发，由 worker 子进程驱动
- DeepSeek 仅自愈调用，不在执行主路径