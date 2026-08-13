# 录制导入细化

> 状态：阶段 5 实现
> 配套：ADR-0001 / ADR-0006 / sequence-diagrams.md §3

## 一、定位

录制导入是「录制回放 + 简图」理念的入口：用户在实际浏览器里操作，平台把操作序列转成**形状（元素定义）+ 步骤（有序动作）**，落到页面简图画布和流转图上。

- 简图 = 展示层（直观组织），定位器才是执行依据 —— 录制只负责把元素和定位器抓进来，不维护图与页面的强对应
- 录制在 **worker 子进程**跑（`playwright codegen`，ADR-0001）

## 二、流程（`app/services/recorder/`）

```
POST /api/record/start {page_template_id, environment_id?, flow_id?}
  → 拼 url = base_url + template.url
  → subprocess.Popen(playwright codegen --target=python <url>, stdout→runs/records/<id>/recorded.py)
  → 返回 record_id

用户在浏览器操作（codegen 实时生成 Python 脚本）

POST /api/record/stop {record_id}
  → terminate 子进程
  → 读 recorded.py → parse_recorded_code() 提取动作
  → import_recording() 建 Shape + Step
```

## 三、解析（`parser.py`）

`playwright codegen --target=python` 输出行形如：
```python
page.get_by_test_id("username").click()
page.get_by_placeholder("Username").fill("admin")
page.locator("#password").fill("secret")
page.get_by_role("button", name="Log in").click()
```

| codegen 方法 | 解析为 locator_type / value |
|-------------|-----------------------------|
| `get_by_test_id("X")` | `data-testid` / `X` |
| `get_by_text("X")` | `text` / `X` |
| `get_by_placeholder("X")` | `css` / `[placeholder="X"]` |
| `get_by_role("R", name="X")` | `text` / `X`（name 优先） |
| `locator("X")` | `css` / `X`（`//` 或 `xpath=` 前缀 → `xpath`） |

| codegen 动作 | 解析为 action / value |
|-------------|----------------------|
| `click()/check()/dblclick()/tap()` | `click` |
| `fill("X")/type("X")/press("X")` | `input` / `X` |
| `select_option("X")` | `select` / `X` |

`goto` / `expect` / 导入语句等跳过。

## 四、区域吸附（降级版：时间序布局）

- 主方案（区域吸附）：录制时 Playwright `getBoundingClientRect` 拿真实坐标 → 缩放到画布。**当前用 codegen CLI 拿不到坐标**，故 MVP 采用时间序兜底
- 兜底：形状按录制顺序垂直排列（`x=40, y=40+i*60`），用户再在画布拖拽微调
- 升级口子：改为自研录制器（Playwright API 直驱 + 实时坐标上报）即可实现真·区域吸附

## 五、导入（`service.py`）

- **Shape 去重**：同一页面模板内按 `(locator_type, locator_value)` 去重，重复元素复用
- **shape_type 映射**：click→button / input→input / select→select
- **Step 顺序**：按录制顺序 `order=i`，`action_type` 直接用解析出的 action
- 传入 `flow_id` 时自动找/建对应 FlowNode 并生成步骤；否则只建形状

## 六、API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/record/start` | `{page_template_id, environment_id?, flow_id?}` → `{record_id, url}` |
| POST | `/api/record/stop` | `{record_id}` → `{actions, shapes_created, steps_created, node_id}` |

## 七、前置条件

- 首次运行需 `uv run playwright install chromium` 下载浏览器（~150MB）
- 录制是交互式流程（打开浏览器窗口），需人工操作
