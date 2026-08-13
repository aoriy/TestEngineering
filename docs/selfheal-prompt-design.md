# AI 自愈 Prompt 设计

> 状态：阶段 3.5 实现
> 配套：ADR-0005 / ADR-0001 / sequence-diagrams.md §2 / nfr.md

## 一、触发与流程

定位器失败（超时/无匹配/不唯一）时由执行器调用 `POST /api/selfheal`，服务编排如下：

```
失败定位器 + 页面 HTML
  → LlmAdapter (DeepSeek v4-pro + thinking)
  → 候选定位器 [{locator_type, locator_value, inner_text, aria_label, role}]
  → 三层防线评估
  → 通过且 mode=auto → 写 locator_history 新版本 + SelfHealRecord(auto_applied)
  → 未通过 → SelfHealRecord(suggest) 降级人工
```

## 二、Prompt 模板（`app/services/selfheal/prompts.py`）

**System**
```
You are a UI test locator repair expert. Given a broken locator and the
surrounding page HTML, propose 1-3 alternative locators (xpath/css) that
uniquely identify the SAME element, plus a confidence score. Return JSON only.
```

**User**（含失败定位器 + 截断 HTML + JSON 格式约束）
```
The locator `{old_locator}` failed to match (or is not unique/visible).

Page HTML (truncated):
{truncated_html}

Return a JSON object with shape: {"locators": [{"locator_type": "xpath"|"css"|"data-testid",
"locator_value": "...", "inner_text": "...", "aria_label": "...", "role": "..."}],
"confidence": 0.0-1.0}. No prose.
```

**关键设计**
- `response_format: {"type": "json_object"}` 强制 JSON 输出，避免解析歧义
- 要求 LLM 同时返回候选元素的 `inner_text`/`aria_label`/`role` → 供第二层语义指纹比对
- `confidence` 是**整体**置信度（非每个候选），对应第三层门限

## 三、HTML 截断策略（控成本）

- 阈值 `_MAX_HTML_CHARS = 8000`，超出时**首尾各半**截断（保留开头 DOM 结构 + 结尾目标元素区），中间插 `<!-- ...truncated... -->`
- SelfHealRecord 存 `page_snapshot` 时用更小阈值 2000（审计只需足够上下文）
- 截断优先保留旧定位器周边 DOM（后续阶段可改为「按旧定位器定位 DOM 子集」精确定位截断）

## 四、thinking 输出 → 审计日志

- DeepSeek `thinking: true` 开启推理，`reasoning_content` 字段回传
- `SelfHealRecord.reasoning` 存完整推理文本 → 回滚/排查时有据可查
- `SelfHealRecord.confidence` / `locator_version` / `old_locator` / `new_locator` 全留痕

## 五、三层防误判防线（`app/services/selfheal/defense.py`）

| 层 | 检查 | 阈值 | 说明 |
|----|------|------|------|
| 3 置信度 | `confidence >= CONFIDENCE_THRESHOLD` | **0.8** | LLM 整体置信度，低于 → 转人工 |
| 1 验证层 | 候选定位器唯一匹配 + 可见 + 可点击 | 唯一/可见/可点 | Playwright 试跑，`verify` 回调注入（API 切片暂缺，UI 执行器实现后接入） |
| 2 语义指纹 | 新旧元素 `innerText`/`aria-label`/`role` 相似度 | **0.6** | `0.3*role匹配 + 0.4*innerText相似 + 0.3*aria相似`，用 difflib.SequenceMatcher |

**执行顺序**：先置信度（最便宜）→ 再验证层（最贵）→ 最后语义指纹。任一不过即 `suggest`。

## 六、缓存键

- 键：`(shape_id, old_locator)` + `status=auto_applied`
- 查最近一条 `SelfHealRecord` 命中即返回 `cached`，避免同一失败重复烧 token
- 命中返回缓存的 `new_locator` + `locator_version`

## 七、配额与降级

| 配置 | 默认 | 说明 |
|------|------|------|
| `SELFHEAL_MODE` | `suggest` | auto（自动应用）/ suggest（只建议）/ off（关闭） |
| `SELFHEAL_CALL_LIMIT` | 30 | 单次 run 自愈调用上限（防雪崩烧钱，NFR） |
| `DEEPSEEK_MODEL` | `deepseek-v4-pro` | v4-pro + thinking，质量优先 |

- `off`：定位失败直接报错，不自愈（离线降级，NFR）
- 无 `DEEPSEEK_API_KEY` 时 `/api/selfheal` 返回 `503`
- `suggest` 模式下即使候选通过防线也不自动改，只落建议

## 八、回滚

- `POST /api/selfheal/rollback?shape_id=`：`locator_current` 前移一版，恢复上一版 `locator_type/value`
- `Shape.locator_history` 版本数组 + `locator_current` 指针，自愈 append 新版本（ADR-0007）

## 九、API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/selfheal` | 触发自愈 `{shape_id, old_locator, page_html, old_meta, run_id}` |
| POST | `/api/selfheal/rollback?shape_id=` | 回滚定位器 |
| GET | `/api/selfheal/records?shape_id=` | 审计记录列表 |
