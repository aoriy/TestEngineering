# ADR-0004: 简化变量替换引擎（非 Jinja2 全语法）

- **Status**: Accepted
- **Date**: 2026-08-12
- **Related**: architecture-review.md §六, AGENTS.md Architecture

## Context

变量引用 `{{var}}` 若用 Jinja2 全语法渲染，当变量值本身含 `{{` 或 `{%`（如某 API 返回的模板字符串、富文本）时会被当作模板语法执行 → 注入风险，可能执行任意代码/写坏模板。

## Decision

**用户变量渲染用简单的 `{{var}}` 正则替换引擎，不用 Jinja2 全语法。**

- 变量是"值"，不是"模板"——替换后直接当值用（填入 API body / Playwright 输入框 / 断言期望）
- Jinja2 仍然使用，但**仅限于代码生成模板**（`app/templates/pytest/*.j2`、`locustfile.j2`）等受控模板，不接触用户变量
- 渲染分两层：先用简化引擎替换用户变量出"最终值"，再用最终值喂 API/UI

## Consequences

**好处**
- 根除模板注入风险——值里含任何字符都不会当语法
- 实现极简（一个正则）
- 语义清晰：变量 = 值

**代价**
- 失去 Jinja2 的过滤器和逻辑表达式（如 `{{ x | upper }}`、`{% if %}`）——但用户变量场景不需要
- 复杂表达式由代码钩子（ADR-0003）兜底