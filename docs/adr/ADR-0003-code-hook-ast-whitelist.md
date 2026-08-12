# ADR-0003: 代码钩子 AST 白名单 + 受控 ctx

- **Status**: Accepted
- **Date**: 2026-08-12
- **Related**: architecture-review.md §五, requirements-analysis.md §5.2-5.3

## Context

形状的 before_code / after_code 是用户 Python 字符串，运行时 exec。风险：
- `import os; os.system(...)` 可毁机/删库
- 无限循环卡死执行
- `ctx.set_var` 写巨型对象爆内存/爆序列化
- 恶意/误用 `open` 读写磁盘敏感文件

## Decision

**AST 检查 import 白名单 + subprocess 隔离 + 受控 ctx + 单步超时。**

- `ast.parse` 后 walk：只允许白名单模块 import
  - 允许：`requests httpx json re jsonpath_ng datetime random faker decimal hashlib`
  - 禁止：`os subprocess shutil open socket ctypes importlib __builtins__` 深层
- 通过后在 worker 子进程内 exec（配合 ADR-0001）
- 单步超时 60s，进程级 kill
- `globals` 只注入白名单模块 + 受控 `ctx` + 安全内建
- `ctx` 只暴露：`get_var / set_var / log / call_api / sleep / fail`（不暴露进程内对象）

## Consequences

**好处**
- 防住最常见的危险操作（文件/进程/网络层）
- 子进程隔离崩溃风险
- 受控 ctx 控制内存与副作用

**代价**
- 白名单需维护（新库要加）；AST 检查对极少数合法代码可能误拒
- 不是真沙箱（无法防内存级攻击），但单人工具场景够用

## Alternatives Considered

- **RestrictedPython**：限制太死，合法代码常被拒，pass
- **不加护栏信任自己**：误操作一样能删库，pass
- **Docker 沙箱**：单人 Windows 机不现实，pass（留升级口）