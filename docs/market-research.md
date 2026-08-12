# 市场调研报告

> 调研时间：2026-08-10
> 调研方式：官方资料实证抓取（代理已通） + GitHub 仓库实测
> 调研目的：为本项目的功能取舍提供市场对标依据

---

## 一、调研背景

本项目（TestEngineering）期望开发一个测试工程管理平台，覆盖需求分析、用例管理、自动化测试（接口 + UI）、性能测试。其中**自动化测试**采用一种特殊方案——用页面"简图"（简化图形）直观组织页面元素和操作，通过拖拽、代码钩子和接口返回值驱动完成自动化。

为判断方案的独创性、可行性和市场定位，对同类产品做了实证调研。

---

## 二、调研结论速览

| 维度 | 市场现状 |
|------|---------|
| 页面图形化建模（线框图） | **市面没有**——所有产品都是元素列表/步骤列表 |
| 图形 + 代码钩子 + 变量联动 | **市面没有**——Katalon 的 Custom Keywords 是代码级，非图形级 |
| 跨字段接口返回值驱动 | 各平台需手写关联/断言，无"字段联动"概念 |
| 一份模型双执行（UI + API） | Tricentis Tosca 理念接近，但无线框图 |
| 完整四大模块平台 | Katalon / MeterSphere 有，但都**缺本项目的核心差异化** |

**核心结论**：本项目的方案是 **MBT 状态机 + 页面对象仓库 + 数据流编排** 三者的图形化融合，这个具体形态在开源和商业产品里都没有现成对标。差异化真实存在，但工程量大。

---

## 三、实证调研的产品资料

### 3.1 Katalon Studio（商业 / 免费版）

**来源**：实测官网 https://katalon.com/katalon-studio

**核心能力**：
- Web / API / Mobile / Desktop **四端 + 性能**全覆盖
- 用例管理（TestOps）+ AI 辅助
- **对象仓库（Object Repository）**：页面元素 + 定位器，可 Spy 抓取、AI 智能 XPath 自愈
- No-code / Low-code / Full-code 三档
- AI self-healing、smart XPath、intelligent object spying

**与本项目的异同**：
- 范围最全（四大模块全覆盖）
- 但对象是**列表式仓库**，步骤是**列表式编排**——没有"页面图形化建模"
- 本项目用画布式简图组织元素，这是与 Katalon 的核心差异

### 3.2 MeterSphere（国内开源）

**来源**：实测 GitHub https://github.com/metersphere/metersphere

**核心数据**：
- stars: 13,422
- 语言: Java（后端 Spring Boot + 前端 Vue.js）
- 中间件: MySQL + Kafka + MinIO + Redis
- Docker 部署，JMeter 做性能
- 更新日期: 2026-08-09（活跃维护）

**核心能力**：
- AI 辅助（AI 生成用例、推荐、报告分析）
- 测试跟踪：用例管理、测试计划执行、缺陷管理、测试报告
- 接口测试：Postman 风格 + JMeter 风格融合，接口调试、接口定义、接口 Mock、接口自动化
- 团队协作：系统-组织-项目分层

**与本项目的异同**：
- 范围接近本项目的四大模块，但**没有 UI 自动化模块**（v3 README 中无 UI 测试）
- 它的"拖拽"是步骤列表拖拽，不是页面图形化建模
- 国内一站式开源对标，可作为用例/接口/性能模块的参考

### 3.3 GraphWalker（开源 MBT）

**来源**：实测 GitHub https://github.com/GraphWalker/graphwalker-project

**核心数据**：
- stars: 369
- 语言: Java
- MIT license

**核心能力**：
- 状态机图模型（`图` = 页面/状态，`边` = 操作）→ 自动生成测试路径
- 有 GraphWalker Studio（图形编辑器）
- 模型是抽象的页面状态，无字段/元素/代码钩子

**与本项目的异同**：
- 只做"流转图自动生成路径"那一部分，模型是抽象状态机
- 无页面元素、无代码钩子、无变量联动——是本项目方案的"骨架子集"

### 3.4 Tricentis Tosca（企业级商业）

**来源**：实测官网 https://www.tricentis.com/products/automate-continuous-testing-tosca

**核心能力**：
- "model-based approach ensures scalable integration with minimum maintenance effort"
- 智能无代码测试自动化，企业级（SAP / Salesforce / Web）
- Agentic AI、Elastic execution、云端执行
- 旗下还有 Testim（已收购）、qTest、NeoLoad、SeaLights 等品牌

**与本项目的异同**：
- 理念最贴近"一份模型多执行"，但重、贵、面向大企业
- 无页面线框图建模
- 是本项目"双执行路径"理念的最接近商业对标

### 3.5 Testim（已被 Tricentis 收购）

**来源**：实测 GitHub 搜索

**核心能力**：
- AI-powered functional and end-to-end test automation platform
- "records, runs, and stabilises codeless and code-based UI tests using AI-driven Smart Locators that learn DOM changes and reduce flakiness"
- 2022 年被 Tricentis 收购

**与本项目的异同**：
- 主打 AI Smart Locator 自愈——这正是本项目想通过第三方 API key 加的 AI 自愈能力
- 录制 + AI 自愈的成熟组合验证了本项目的执行核心可行

### 3.6 Fastbot（字节跳动开源）

**来源**：实测 GitHub https://github.com/bytedance/Fastbot_Android

**核心数据**：
- stars: 1,196
- 语言: C++

**核心能力**：
- "Model-based testing tool for modeling GUI transitions to discover app stability problems"
- 移动端 GUI 状态机模型，自动遍历发现稳定性问题

**与本项目的异同**：
- 只做移动端 GUI 状态机遍历，非业务用例编排
- 再次印证"GUI 状态机模型"路径是有大厂投入的方向

### 3.7 HttpRunner v5（开源，All-in-One）

**来源**：实测 GitHub https://github.com/HttpRunner/HttpRunner （README 实证）

**核心数据**：
- stars: 4,295
- 语言: Go（v5 起 Python 版迁移到 `httprunner/httprunner.py`）
- 自 2017 年起，2022 年扩展支持 UI 自动化

**核心能力**：
- "All-in-One Testing Solution"——API + UI（Android/iOS/Harmony/Browser）+ 性能（boomer 并发跑 API testcase）**全模块**都有
- **LLM 驱动**："Natural language driven test scenarios powered by LLM" + 大模型驱动用例生成
- MCP server for UI automation + mcphost chat session 交互
- testcase 格式统一：GoTest / YAML / JSON / Text / pytest
- hrp CLI，跨平台 macOS/Linux/Windows
- CI/CD 友好（JSON 日志 + HTML 报告）

**与本项目的异同**：
- **最强开源对标**：覆盖范围与你完全一致（API+UI+性能+AI），且已在 AI 方向发力
- UI 自动化"采用大模型驱动 + OCR/CV/VLM"与本项目"录制 + AI 自愈"思路异曲同工
- 但形态完全不同：HttpRunner 是 **Go 栈 + CLI（hrp）**，本项目是 **Python 栈 + Web 画布**
- 形态差异决定两者生态位不冲突：HttpRunner 适合命令行/CI 场景，本项目适合可视化编排场景

### 3.8 其他参考

- **Spec Explorer（微软）**：实测 Wikipedia — MBT 工具，**最后版本停在 2013 年，微软放弃**。MBT 路径在业界的历史失败案例。
- **RobotFramework RIDE**：stars 1,011，Python 的测试数据编辑器（树状 / 列表式可视化）。
- **Postman Flows**：可视化拖拽接口编排 + 变量，但只做 API。
- **Airtest / Poco（网易）**：图像识别视觉建模，面向移动端 / 游戏。
- **SikuliX**：截图图像识别驱动，视觉但非页面模板。
- **mabl / Rainforest QA**：无代码 AI 驱动，无页面建模。

---

## 四、为什么市场不做"页面图形化建模"的深度分析

### 4.1 历史：不是没人做，是做过的失败了

**微软 Spec Explorer**（实证确认）：90 年代起的官方 MBT 工具，在 VS 里建模 → 自动生成测试。**最后版本停在 2013 年，微软放弃了**。这不是技术不成熟，是**市场证明这条路走不通**。

MBT（模型驱动测试）这个概念 30 年前就有，学术界反复研究。结局是：**图模型生成测试 → 从没有成为主流**。Katalon / MeterSphere / Tosca 没有重蹈覆辙，是有原因的。

### 4.2 核心死因：维护成本 > 收益（ROI 倒挂）

图形化建模最大的敌人是"**模型漂移**"——页面一改，图形就得跟着改。而页面是天天变的。
- 写一条 Playwright 脚本：页面改 → 改一行定位器
- 维护一张页面图形：页面改 → 移动形状位置、改字段绑定、改连线……**比改代码还累**
- 测试工具的第一 KPI 是"省维护"，图形化恰恰在维护上最费

### 4.3 映射问题（mapping problem）——抽象层和真实层的鸿沟

这是 MBT 的经典死穴（Wikipedia 实证确认）：图形是抽象层，但执行必须落到真实 DOM 元素 / 定位器 / 接口。**图形和真实页面之间没有自动对应关系**，每一层都靠人工。图形越精美，这个鸿沟越宽——你画得再像，Playwright 还是需要 `data-testid` 才能找到元素。图形本身**不产生任何执行能力**，它只是"视觉层"，真本事全在绑定的定位器和代码里。

### 4.4 替代路径已经更便宜（录制 + AI 自愈）

- 市场真正验证的是：**录制回放**（点一下就能生成脚本）+ **AI 智能定位自愈**（Testim 被 Tricentis 收购、Katalon AI XPath，均已实证）
- 对商业产品来说，"打开浏览器录一遍"比"拖拖拽拽画页面模型"**快一个数量级**，还零建模成本
- 既然录制 + AI 已覆盖 90% 场景，谁还愿意为"页面图形"付钱？

### 4.5 目标用户与学习成本

- 图形化建模的服务对象是"不会写代码的测试员"，但恰恰是这批人维护模型更吃力、更容易画错
- 会写代码的工程师 → 直接写 Playwright 更高效，不需要图
- **"会写代码但又想用图形"的中间人群太小**，撑不起一个商业产品的 ROI

### 4.6 结论：是"实现难"还是"不值得"？

**两者都有，但"不值得"是主因：**
- 实现难是**真的难**，但难点不在"画图"（画布库 AntV X6 很成熟）。难在**语义设计**：图形节点 → 运行时动作的翻译、变量流、错误处理、动态页面状态
- 但更根本的是：**就算做出来了，用户不买单**。因为图形的执行价值 ≈ 0，纯靠绑定的定位器和代码撑着，而这部分恰恰是列表式 / 代码式工具已经做得更好、更省维护的

---

## 五、本项目的差异化定位

### 5.1 本项目最终定位

经过澄清收敛，本项目的核心定位是：

> **录制回放 + 直观简图展示层 + 代码钩子 + 变量联动 + AI 自愈增强**

关键澄清：
- **简图 ≠ 页面模型，简图 = 可视化的组织层（展示容器）**
- 简图只是用形状把元素 / 步骤按页面组织起来，不追求还原真实页面
- **执行靠定位器**（xpath / data-testid），Playwright 定位时根本不看简图
- 页面变了 → 重新录一遍、重新放形状即可，不需要维护图与页面的对应关系 → **绕开了"模型漂移"这个 MBT 死因**

这个定位恰好是市场验证过的路（录制回放），同时差异化在"直观展示层"。

### 5.2 三个差异化点（市面没有）

1. **页面本身就是画布**——用线框图还原真实页面，每个形状既是视觉又是可编程节点。现有产品都是"元素列表"或"步骤列表"，没有"页面图形化建模"
2. **跨字段联动靠接口返回值驱动**：A 字段输入 → 调接口 → 返回值存页面公共变量 → B 字段自动带出。Postman Flows 也只有列表式，没有这个
3. **Python 代码钩子嵌入图形**——不是 Groovy / JS，是 Python（团队技术栈）

**新增定位（实证后）**：与最强开源对标 HttpRunner v5（Go + CLI + LLM 驱动）相比，本项目走"**Python 全栈 + Web 画布**"生态位——两者覆盖一致但形态不冲突，HttpRunner 适合 CI/命令行场景，本项目适合可视化编排场景。**这一生态位在开源里暂时无人占位**。

### 5.3 化解 MBT 死路的三个救命点

本项目的设计里有三个救命点，避免了重蹈 Spec Explorer 的覆辙：
1. **代码钩子 = 逃生舱**：图形画不出的动态逻辑，用 Python 钩子兜底 → 补上"映射问题"
2. **接口返回值驱动变量联动**：图形工具里真正有价值的差异点
3. **简图是组织层不是模型层**：不与页面强绑定，无模型漂移

---

## 六、市场对标总表

| 产品 | 形态 | 与本项目的异同 |
|------|------|---------------|
| **Katalon Studio** | 对象仓库（列表式）+ 低代码 + 全代码 + 四端 + 性能 | 范围最全，但无页面图形化建模；有 AI 自愈 + 录制，本项目可对标 |
| **MeterSphere** | 一站式（用例 + 接口 + 性能，无 UI） | 国内开源对标，可参考用例 / 接口 / 性能模块 |
| **Tricentis Tosca** | 模型驱动，统一 API/UI/数据库 | 理念最接近"一份模型多执行"，但无页面线框图 |
| **GraphWalker** | 状态机图模型 → 自动生成测试路径 | 本项目"流转图"那部分的子集，无元素 / 钩子 / 变量 |
| **Testim** | 录制 + AI Smart Locator 自愈 | 验证"录制 + AI 自愈"组合的成熟性 |
| **Fastbot** | 移动端 GUI 状态机遍历 | 大厂投入"GUI 状态机"方向的存在感 |
| **HttpRunner v5** | All-in-One（API+UI+性能），Go 栈 + CLI + LLM 驱动 | **最强开源对标**，覆盖一致但形态不同（CLI vs Web 画布，生态位不冲突）|
| **Spec Explorer** | 微软 MBT，2013 年放弃 | MBT 路径的历史失败教训 |
| **RobotFramework RIDE** | Python 测试数据编辑器（树状 / 列表） | 列表式可视化的开源对标 |
| **Postman Flows** | 可视化拖拽接口编排 + 变量 | 仅 API，可参考变量联动设计 |
| **Airtest / SikuliX** | 图像识别视觉建模 | 视觉但非页面模板，方向不同 |

---

## 七、对本项目的建议

1. **收缩范围，聚焦差异化**：资源全部压在"页面简图画布 + 代码钩子 + 变量系统 + AI 自愈"这个独特点上，其余模块做轻量版够用即可
2. **不要重做 MBT**：保持"简图是组织层"的定位，不追求图形与页面的 1:1 映射，避免模型漂移死穴
3. **AI 自愈弥补最大短板**：单人做不出完整 AI 自愈，但用第三方 API key（DeepSeek）即可补上 Katalon / Testim 的核心能力
4. **借鉴而非照抄**：用例 / 接口 / 性能模块参考 MeterSphere 的结构，但代码用 Python 栈（FastAPI + Playwright + Locust）
5. **对标 HttpRunner 而非重复造轮**：HttpRunner 在 API/UI/性能/LLM 上覆盖一致，本项目以"Web 画布可视化编排"差异化，与 HttpRunner 的 CLI 形态正交互补——后续可考虑兼容 HttpRunner 的 testcase 格式导入导出