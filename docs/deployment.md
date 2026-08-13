# 单机部署文档

> 状态：阶段 0/1 单机起步
> 目标平台：Windows（主开发）；Linux 可移植

## 一、前置条件

| 依赖 | 版本 | 说明 |
|------|------|------|
| uv | 0.11+ | Python 环境与依赖管理 |
| Python | 3.12（`.python-version` 固定） | uv 自动读取 |
| Node.js + npm | Node 22+ / npm 10+ | 前端构建 |

## 二、后端启动

```powershell
# 首次或依赖变更后同步环境
uv sync

# 启动（开发，热重载）
uv run uvicorn app.main:app --reload --port 8000
```

- 首次启动自动建表（`init_db`，SQLAlchemy `create_all`），无需手动迁移
- 健康检查：`http://127.0.0.1:8000/api/health`

## 三、前端启动

```powershell
cd frontend
npm install
npm run dev      # 开发，http://localhost:5173
npm run build    # 生产构建（vue-tsc + vite build）
npm run preview  # 预览构建产物
```

- 开发模式 Vite proxy 将 `/api` 反代到 `127.0.0.1:8000`
- 生产模式（build 后）需自行将 `/api` 反代到后端（nginx 或后端托管静态文件，后续阶段补）

## 四、数据与产物目录

| 路径 | 内容 | 是否入库 |
|------|------|---------|
| `data.db` | SQLite 数据库 | gitignored（`*.db`） |
| `runs/<run_id>/` | 生成代码/日志/报告/截图/录像 | gitignored |
| `.env` | 环境变量（含 API key） | gitignored |
| `app/templates/` | Jinja2 代码生成模板 | 入库 |
| `docs/` | 设计文档 | 入库 |

## 五、.env 配置项清单

| 键 | 默认值 | 说明 |
|----|--------|------|
| `DATABASE_URL` | `sqlite:///./data.db` | 数据库连接串 |
| `DEBUG` | `false` | 调试模式 |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | CORS 白名单 |
| `DEEPSEEK_API_KEY` | 空 | AI 自愈密钥（阶段 3.5 用） |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | LLM 端点 |
| `DEEPSEEK_MODEL` | `deepseek-v4-pro` | 模型 |
| `SELFHEAL_MODE` | `suggest` | auto / suggest / off |
| `RUNS_DIR` | `runs` | 产物根目录 |
| `STEP_TIMEOUT_SECONDS` | `60` | 单步钩子超时 |
| `RUN_TIMEOUT_SECONDS` | `1800` | 单次执行超时 |
| `SELFHEAL_CALL_LIMIT` | `30` | 单次执行自愈上限 |

> 配置由 `app/core/config.py`（pydantic-settings）读取，字段名与上表对应。`.env` 不入库，模板可参考上表手写。

## 六、一键启动（开发）

```powershell
# 终端 1：后端
uv run uvicorn app.main:app --reload

# 终端 2：前端
cd frontend; npm run dev
```

浏览器访问 `http://localhost:5173`，侧边栏含项目管理/需求/用例/追溯矩阵四页。

## 七、故障排查

| 现象 | 处理 |
|------|------|
| 前端 `/api` 404 | 确认后端在 8000 端口已启动；检查 vite proxy target |
| 建表失败 | 删除 `data.db` 重新启动（SQLite 本地） |
| uv 提示 hardlink 警告 | 无害；`$env:UV_LINK_MODE='copy'` 可静默 |
| CRLF 警告 | 无害，Windows 行尾，偏好 LF 编辑 |

## 八、待补（后续阶段）

- 生产模式 nginx 反代 `/api` 配置示例
- Linux/Docker 部署（当前仅 Windows 主开发）
- 性能压测（Locust）与 Playwright 浏览器安装说明（`playwright install`）
