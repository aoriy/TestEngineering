# ADR-0005: DeepSeek v4-pro + thinking 自愈

- **Status**: Accepted
- **Date**: 2026-08-12
- **Related**: requirements-analysis.md §5.2-5.3, ADR-0001

## Context

定位器自愈的目标是用 LLM 推断新 xpath/copy，替代人工重抓。可选模型供应商：DeepSeek（国内可达、便宜、OpenAI 兼容）、OpenAI（国内需代理）、Qwen/GLM 等。可选量级：pro（强）或 flash（便宜快）。

自愈是**"错一次比费一万次更糟"**的场景——返回的定位器看着对但语义错（找到另一个相似按钮），自动修复后用例假绿，比失败更危险。

## Decision

**用 DeepSeek `deepseek-v4-pro` + 开启 `thinking` mode + `reasoning_effort: high`。**

- base_url `https://api.deepseek.com`，OpenAI 兼容协议 `client.chat.completions.create`
- 选 pro 不选 flash：自愈频率低（只在定位失败时触发，健康库 < 10%），单次贵一点点可接受，质量直接决定误判率
- thinking 模式让模型显式推理 XPath，可解释性强，正好填进自愈审计日志便于回溯
- 成本无忧：单次约 3-4k 入 + 1k 出 tokens，分钱级，月几元

**配合三层防误判防线**（重点投入）：
1. **验证层**：Playwright 试跑新定位器，必须唯一匹配 + 可见 + 可点击
2. **语义指纹校验**：对比新旧定位器元素的 `innerText` / `aria-label` / `role` 相似度，低于阈值降级为建议
3. **置信度门限**：LLM 返回 JSON `{locators, confidence}`，低于 0.8 转人工

## Consequences

**好处**
- 国内可达，无需代理
- thinking 可解释性填审计日志，回滚有据
- OpenAI 兼容，切供应商只改 base_url/model

**代价**
- 自愈单次比 flash 稍贵，但量级仍是分钱，无忧
- 三层防线是真正的工程投入点（不是省钱）