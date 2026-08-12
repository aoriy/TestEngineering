# ADR-0006: FlowNode/Step 与 PageTemplate 的归属分离

- **Status**: Accepted
- **Date**: 2026-08-12
- **Related**: architecture-review.md §四, requirements-analysis.md §7

## Context

最初设计里"流转图节点 = 页面实例"语义模糊：同一个页面模板能不能在不同流转图里复用？同一页在不同流程带不同数据怎么存？执行顺序是看简图位置还是看列表？"列表为默认执行源 + 简图可重排"如何落地？

## Decision

**分离"元素定义"与"流程实例有序动作"两类实体。**

- **`PageTemplate` + `Shape` = 元素定义（可复用）**：页面"有什么字段/按钮"，跨流程共享
- **`Flow` + `FlowNode` + `Step` = 流程实例的有序动作**：这条流程里"做哪些动作、什么顺序"
- **`Step` 挂 `FlowNode`，引用 `Shape`**：`step.shape_id → Shape` + `step.order` + `action_type` + `action_params`
- **`FlowNode` 引用 `PageTemplate` + `initial_vars`**：实例级覆盖（同一页模板在不同流程带不同初始变量）

落地机制：
- 简图画布 = `PageTemplate` 的 `Shape`s 按位置渲染
- 步骤列表 = `FlowNode` 的 `Step`s 按 `order` 排序
- 拖拽重排 = 改 `Step.order`
- `Shape.locator_history` 版本化（自愈 append，回滚切 current）

## Consequences

**好处**
- "列表为执行源 + 简图可重排"天然落地（重排 = 改 order）
- 模板可跨 Flow 复用（一处改定位器，多流程受益）
- 实例与定义隔离，符合大多数测试平台的设计共识

**代价**
- 实体数量多（PageTemplate/Flow/FlowNode/Step/Shape），需在文档里反复澄清
- 录制导入时要同时建 Shape 和 Step