# 经销商 PDCA 工作台项目设计与功能说明

## 1. 项目定位

经销商 PDCA 工作台是面向海外经销商团队的本地化经营管理工具，目标是把销售业绩、客户周期、物流核查、每日待办、Agent 调度和 PDCA 复盘放到同一个工作台中。

当前阶段优先满足本地汇报和团队试用，核心目标是：

- 让非技术用户通过网页入口使用，不依赖命令行。
- 把 VPS/Odoo 中的正式业绩数据拉下来，生成看板、Excel 和日报。
- 把客户管理从“零散表格”升级为“客户全周期管理”。
- 让 Hermes / Agent 成为任务入口，而不是让用户自己判断该跑哪个脚本。
- 保证本地演示稳定、快速，避免现场重复拉数或长时间等待。

## 2. 设计思路

### 2.1 本地优先，先跑通闭环

项目当前采用本地 Web 工作台模式：

- 主工作台运行在 `http://127.0.0.1:8765`。
- 客户周期管理模块运行在 `http://127.0.0.1:8787`。
- 数据、报告、看板、Excel 都落到本地目录。
- Git 暂作为临时数据中台和版本保护手段。

这样做的好处是实施速度快、对现有 VPS/Hermes/本地脚本兼容度高，适合当前汇报和 MVP 验证。

### 2.2 正式数据只认 VPS/Odoo

业绩数据的正式口径来自 VPS/Odoo，不以临时 Excel 作为正式来源。

当前正式业绩口径：

- 数据表：`sale_order_line_report`
- 组织范围：海外事业部 / 经销商
- 销售类型：`agent_sale`、`agent_sale_replacement`、`agent_sale_return`
- 拉数方式：`vertu odoo data sandbox`

Excel 只作为输出物或离线调试使用，不作为正式业绩口径。

### 2.3 一个入口，多 Agent 分工

用户日常只需要面对工作台和 Hermes 任务入口。内部由不同 Agent 或脚本完成分工：

- 数据出表 Agent：拉 VPS 数据、生成 Excel 和汇总。
- 物流核查 Agent：识别物流单号，调用官网或浏览器核查。
- 市场调研 Agent：根据自然语言问题输出 Markdown 调研报告。
- PDCA Agent：生成每日 Check / Act / 明日行动清单。
- 客户管理 Agent：辅助客户资料完善、跟进、任务分派。

### 2.4 演示稳定优先

因为当前马上要汇报，项目对本地演示做了专门处理：

- 已生成的 5 月 29 日看板可直接打开。
- `data_sources.json` 本地可指向已缓存 VPS JSON，避免现场重复慢拉数。
- 工作台请求有超时和异常兜底。
- Hermes 和浏览器自动化限制最大执行时间和最大步骤数。
- 客户管理、看板、首页都已做健康检查。

## 3. 总体架构

```text
用户浏览器
  |
  |-- 8765 主工作台 pdca_workbench.py
  |     |-- 首页 / 今日待办 / Hermes 任务入口
  |     |-- 业绩驾驶舱 dashboard.html
  |     |-- Excel / Markdown 结果查看与打开
  |     |-- 客户管理 iframe 入口
  |
  |-- 8787 客户周期管理 server.py
        |-- 客户漏斗
        |-- 客户资料
        |-- 今日任务
        |-- 管理大盘
        |-- Vemory 会议复盘

本地脚本层
  |
  |-- run_data_role_pdca_daily.ps1
  |-- pull_vps_sales_data.ps1
  |-- data_role_pdca_daily.py
  |-- pull_dealer_sales_month_to_date.py

外部能力
  |
  |-- VPS/Odoo via vertu CLI
  |-- Hermes Agent
  |-- Playwright / 浏览器物流核查
```

## 4. 主要模块

### 4.1 主工作台

文件：

- `scripts/pdca_workbench.py`
- `数据岗位PDCA工作台.bat`

实现功能：

- 提供本地 Web 首页。
- 展示今日待办、IM 未读、数据看板、客户管理入口。
- 支持一键运行当天 PDCA。
- 支持向 Hermes 派任务。
- 对“从vps”类问题直接走 VPS-CLI 数据路径。
- 支持 Excel / Markdown / HTML 结果打开和预览。
- 支持客户管理模块自动拉起。

设计重点：

- 非技术用户优先，入口尽量按钮化。
- 慢任务加超时，失败时返回可读错误。
- 对重复演示使用缓存，避免每次重新拉 VPS。

### 4.2 业绩驾驶舱

文件：

- `templates/dashboard_template.html`
- `scripts/data_role_pdca_daily.py`
- `outputs/YYYY-MM-DD/dashboard.html`
- `outputs/YYYY-MM-DD/chart_data.json`

实现功能：

- 月报、周报、日报视角。
- 销售员业绩排名。
- 产品业绩排名。
- 客户 / 经销商业绩排名。
- 日、周、月业绩数据注入。
- 当天无业绩时，日报自动回退到最近有数据日，并显示提示。
- 门店页展示销售详情和大区门店分析。

关键指标：

- 业绩金额
- 提货数量
- 产品维度
- 客户维度
- 销售员维度
- 大区 / 国家 / 门店维度

当前策略：

- 有真实 VPS 数据的字段展示真实值。
- 暂未接入 VPS 的字段显示“暂未接入VPS”，避免编造数据。

### 4.3 VPS 数据拉取与 Excel 输出

文件：

- `scripts/pull_vps_sales_data.ps1`
- `system_queries/pull_dealer_sales_month_to_date.py`
- `scripts/data_role_pdca_daily.py`

实现功能：

- 从 VPS/Odoo 拉取经销商业绩数据。
- 支持按日期或月累周期拉取。
- 生成销售员、团队、产品、客户汇总。
- 生成 Excel 工作簿。
- 生成 Markdown 数据汇总报告。
- 生成 `chart_data.json` 供看板注入。

性能策略：

- 本地有新鲜原始 JSON 时优先复用。
- 汇报时可固定到已拉好的 5 月 29 日数据。
- 数据出表类问题尽量绕过 Hermes 对话，直接生成 Excel。

### 4.4 客户全周期管理

路径：

- `C:\Users\frank\Documents\Codex\2026-05-27\pdca-codex-1-guru-electronics-singapore\he-haiwen-dealer-workbench`

主要文件：

- `server.py`
- `index.html`
- `dealer-adapter.js`

实现功能：

- 用户视角切换：总监、组长、销售。
- 今日任务。
- 六阶段漏斗看板。
- 客户管理列表。
- 应收管理。
- 管理大盘。
- 客户资料编辑。
- Vemory 每日会议复盘。
- VPS 客户数据读取。

漏斗阶段：

```text
潜在 -> 触达中 -> 已回复 -> 约见 -> 意向 -> 成交
```

客户资料字段包括：

- 客户名称
- 联系人
- 电话
- 区域 / 国家 / 城市
- 客户等级
- 跟进阶段
- 门店数量
- 陈列情况
- 月采购潜力
- 下一步动作
- 备注

当前集成方式：

- 主工作台通过 `/customer-mgmt` 嵌入 8787 客户管理页面。
- 如果 8787 未启动，主工作台会尝试自动启动。

### 4.5 Hermes / Agent 任务入口

文件：

- `scripts/pdca_workbench.py`
- `scripts/invoke-data-access-agent.ps1`
- `agents/research-agent.md`
- `data_platform/hermes_skills/data-role-pdca-mvp/SKILL.md`

实现功能：

- 用户在工作台输入自然语言任务。
- 系统识别任务类型。
- 数据类任务优先直接出 Excel。
- 调研类任务进入 research-agent。
- 物流类任务进入物流核查流程。
- 其他复杂任务交给 Hermes。

当前任务路由：

```text
包含“从vps” -> VPS-CLI 直接拉数/出表
销售/业绩/产品/客户/团队 -> 读取最新 VPS 数据并生成 Excel
物流单号 -> 物流核查 Agent
调研/市场/竞品/客户背景 -> research-agent
其他 -> Hermes data-access-agent
```

稳定性控制：

- Hermes 单次执行超时限制。
- 调研 Agent 输出限制在合理范围。
- 浏览器查物流最多 15 步，避免无限重试。
- API key / 模型错误会返回明确提示。

### 4.6 物流核查

文件：

- `scripts/pdca_workbench.py`
- `agents/logistics-browser-agent.md`

实现功能：

- 识别物流单号。
- 推断承运商。
- 生成官网核查链接。
- DHL 已接入 Playwright 浏览器核查。
- 读取官网页面文本，提取状态、更新时间、始发地、目的地。
- 查询失败时标记“待人工确认”或“官网浏览器核查失败”。

设计原则：

- 不编造物流状态。
- 官网无法读取时，给出人工核查入口。
- 浏览器核查有步骤上限和超时限制。

### 4.7 每日 PDCA

文件：

- `inputs/todos/`
- `inputs/questionnaires/`
- `outputs/YYYY-MM-DD/pdca_daily_check.md`
- `outputs/YYYY-MM-DD/todo_reminder.md`
- `outbox/YYYY-MM-DD_im_message.md`

实现功能：

- 汇总昨日未完成和今日待办。
- 生成今日必须完成 / 应完成 / 可延后事项。
- 读取每日问卷。
- 生成每日 Check 报告。
- 生成次日 Act 行动建议。
- 输出 IM 消息草稿。

每日闭环：

```text
早上拉待办
白天处理客户 / 数据 / 物流 / 临时需求
晚上填写问卷
系统生成 Check / Act
次日继续滚动
```

## 5. 已实现功能清单

### 工作台层

- 本地 Web 首页。
- 数据看板入口。
- 客户管理入口。
- 今日待办入口。
- IM 未读入口。
- Hermes 任务入口。
- Agent 编辑入口。
- Markdown / Excel / HTML 结果查看。
- 各页面返回按钮。
- 执行任务时按钮置灰和 thinking 动画。

### 数据层

- VPS/Odoo 正式业绩拉取。
- 销售员汇总。
- 团队汇总。
- 产品汇总。
- 客户汇总。
- Excel 输出。
- Markdown 报告输出。
- 图表 JSON 输出。
- 数据解析兼容 `execution.result`、`result`、`ai.result`。
- 本地缓存复用。

### 看板层

- 月报 / 周报 / 日报。
- 销售员排名。
- 产品排名。
- 客户排名。
- 门店数据页。
- 大区门店分析。
- 日报无数据时回退并说明。
- 真实数据和“暂未接入VPS”占位并存。

### 客户管理层

- 总监 / 组长 / 销售视角。
- 客户漏斗。
- 客户资料编辑。
- 客户完善度。
- 今日任务。
- 管理大盘。
- Vemory 会议复盘入口。
- VPS 客户数据读取。

### Agent 层

- 数据出表 Agent。
- 物流官网核查 Agent。
- 市场调研 Agent。
- Hermes 总入口。
- “从vps”关键词直连 VPS-CLI。

## 6. 关键输出物

每天运行后主要输出：

```text
outputs/YYYY-MM-DD/todo_reminder.md
outputs/YYYY-MM-DD/data_summary_report.md
outputs/YYYY-MM-DD/YYYY-MM-DD_data_summary.xlsx
outputs/YYYY-MM-DD/dashboard.html
outputs/YYYY-MM-DD/chart_data.json
outputs/YYYY-MM-DD/logistics_check_report.md
outputs/YYYY-MM-DD/pdca_daily_check.md
outbox/YYYY-MM-DD_im_message.md
```

## 7. 稳定性设计

当前已经做的稳定性处理：

- 工作台服务使用 `ThreadingHTTPServer`，避免单个请求完全阻塞所有页面。
- 慢任务设置超时时间。
- 浏览器物流核查设置 15 步上限。
- Hermes 调用失败会返回错误说明。
- VPS 拉数失败时优先使用已有缓存。
- 工作台输出页面时处理浏览器断连异常。
- 客户管理 API 增加异常兜底。
- 本地演示使用已缓存 VPS JSON，避免现场重复拉数。

演示前建议：

- 先确认 `8765` 和 `8787` 都在监听。
- 先打开 5 月 29 日看板。
- 不在现场强制刷新 VPS。
- 不在现场跑长时间物流官网核查。
- 调研任务尽量输入明确问题。

## 8. 性能设计

当前性能优化点：

- VPS 原始 JSON 可缓存复用。
- 数据出表绕过 Hermes 直接生成 Excel。
- 已生成看板直接读取静态 HTML。
- 5 月 29 日汇报数据已预生成。
- 客户管理接口有内存缓存。

后续可继续优化：

- 把客户管理和主工作台合并为同一服务。
- 把 ECharts、Tailwind、Alpine 等前端依赖本地化。
- 使用 SQLite / Redis 缓存 VPS 结果。
- 慢任务改为后台队列 + 前端轮询。
- 生成看板和拉 VPS 分离，避免打开页面时触发慢任务。

## 9. 当前边界与注意事项

当前仍是本地 MVP，不是正式生产系统。

需要注意：

- 客户管理模块目前在独立目录和独立端口。
- 部分前端依赖仍来自 CDN，离线环境可能影响首次加载。
- Playwright 查物流依赖本机 Chrome / Edge。
- Hermes 依赖本机配置和 API key。
- `data_sources.json` 中的本地绝对路径只适合本机演示，不适合提交远端。
- 一些字段如 IoT、Walk In、入库、激活等尚未全部接入 VPS，当前按“暂未接入VPS”处理。

## 10. 后续规划

### 第一阶段：本地汇报稳定版

目标：今天汇报稳定、快速、可演示。

重点：

- 固定 5 月 29 日数据。
- 保证工作台和客户管理可打开。
- 保证看板和 Excel 可展示。
- 避免现场慢拉数。

### 第二阶段：团队内测版

目标：让销售团队和组长真实试用。

重点：

- 主工作台和客户管理合并。
- 增加统一缓存。
- 增加任务执行状态。
- 完善客户资料写回 VPS。
- 完善 Vemory、应收、物流数据接入。

### 第三阶段：网页部署版

目标：部署成内网或公网 Web 服务。

重点：

- 去掉本机路径依赖。
- 后端服务化 VPS、Hermes、物流核查。
- 文件打开改为浏览器下载和在线预览。
- 增加登录、权限、审计和监控。
- 引入数据库和任务队列。

## 11. 一句话总结

经销商 PDCA 工作台当前已经从“脚本和零散文件”升级为“本地 Web 工作台 + 业绩驾驶舱 + 客户周期管理 + Hermes Agent 入口”的 MVP 闭环。它已经可以支撑本地汇报和初步试用，下一步重点是把本地依赖服务化、缓存化和权限化，逐步演进为稳定的团队级经营管理系统。
