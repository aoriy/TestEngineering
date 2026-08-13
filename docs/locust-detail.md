# Locust 性能测试细化

> 状态：阶段 4 实现
> 配套：ADR-0001 / ADR-0002 / nfr.md §二 / api-design.md

## 一、定位

性能测试复用 `ApiDefinition`（与 API/UI 共享），通过 TestCase → Flow → 步骤 → Shape → ApiDefinition 链路收集压测接口。Locust 在 **worker 子进程**跑（`--headless`），绝不在 FastAPI 进程内（ADR-0001）。

## 二、代码生成（`app/services/codegen/perf.py` + `app/templates/locust/locustfile.py.j2`）

- 遍历 TestCase 绑定 Flow 的所有节点步骤，收集**去重后**的 `api_definition_id`
- 每个唯一接口生成一个 `@task` 方法（`HttpUser` 子类，`wait_time = between(1, 3)`）
- `{{var}}` 在**代码生成时**预替换（环境变量 + 用例 `data_bindings`），产出固定 URL/headers/params/body
- body：JSON 可解析 → `json=`，否则 → `data=`

```python
# 生成示例
class ApiUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def task_0(self):
        self.client.request("GET", "/api/health", headers={}, params={}, name="health")
```

## 三、子进程 spawn（`PerfExecutor`）

| 参数 | 默认 | 说明 |
|------|------|------|
| `--host` | 环境 base_url | 从 codegen 回填到 request.params |
| `-u` users | 10 | 用户数 |
| `-r` spawn_rate | 1 | 每秒孵化数 |
| `-t` run_time | `30s` | 压测时长（支持 `5s`/`1m`/`2m30s`） |
| `--headless` | — | 无 UI |
| `--only-summary` | — | 日志只输出汇总表（控制 log 体积） |
| `--csv <runs>/<run_id>/stats` | — | 落盘 stats/failures/stats_history CSV |

**命令示例**
```
uv run locust -f runs/<run_id>/generated/locustfile.py --headless --only-summary \
  -u 10 -r 1 -t 30s --csv runs/<run_id>/stats --host http://example.com
```

## 四、结果收集

- 退出码 0 → `done`，否则 `failed`
- `TestRun.artifacts.csv` 存三份 CSV 路径（`stats_stats.csv` / `stats_failures.csv` / `stats_stats_history.csv`）
- 汇总表（# reqs / # fails / avg / req/s / 百分位）在 `log.txt` 尾部，前端日志弹窗直接可见

## 五、性能参数来源

`POST /api/runs` 的 `params`：
```json
{ "executor": "perf", "params": { "users": 10, "spawn_rate": 1, "run_time": "30s" } }
```

## 六、单机资源上限（NFR）

- 单机单 perf worker（并发压测任务串行，避免相互干扰）
- `run_time` 由用户控制，MVP 不设硬上限（后续可加保护）
- 压测目标与平台同机时会互相影响指标 —— 生产应分离，单机起步可接受

## 七、后续分布式升级口子

- Executor 接口不变（ADR-0002），换 `--master`/`--worker` 分布式即可
- `spawn` 换成 Redis+RQ（ADR-0001 预留），多机压测
