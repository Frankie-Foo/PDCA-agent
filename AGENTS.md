# 经销商 PDCA 智能体分工与流转契约

## 总原则

- 所有 Agent 必须优先读取本文件和 `.cursorrules`。
- 输出必须落到对应目录，不覆盖原始资料。
- 涉及价格、合同、承诺、交付周期、法务风险时，必须显式标注假设与风险。
- 不要把本地 `.env`、API Key、私钥、客户敏感原文提交到 Git。
- 查询 VPS/Odoo 数据时，优先使用 Hermes 已安装的 Odoo skills；不要凭空编造字段、模型或指标。

## 目录架构

- `/inbox/`: 原始客户背景、会议纪要、邮件摘要、聊天记录整理稿。
- `/insights/`: 市场分析员 `market-analyst` 的输出目录。
- `/contracts/`: 合同、报价、方案草案，以及合同专家 `contract-expert` 的风险报告。
- `/manager/`: 经理审批、折扣策略、最终方案。
- `/data_requests/`: 用户提出的数据问题、取数需求、口径说明。
- `/data_raw/`: 从 VPS/Odoo/飞书表格等系统拉取的原始结果快照。
- `/data_reports/`: 数据查询后的解释、摘要、初步分析。
- `/data_quality/`: 数据缺失、字段不一致、权限不足、口径冲突等问题记录。
- `/pdca_actions/`: 从数据异常转成的 PDCA 行动建议。
- `/profiles/`: Hermes Profile 模板。
- `/templates/`: 可复用模板。

## 已配置能力

- Hermes 模型：阿里云百炼 `qwen3.6-plus`。
- Vertu CLI：`vertu`，已登录 `https://admin.vertu.cn`。
- VPS/Odoo skills：已安装到 Hermes，包括 `odoo-data-query-assistant`、`odoo-daily-sales-report`、`odoo-okr-management-assistant`、`odoo-sale-personnel-efficiency`、`odoo-knowledge-discovery` 等。

## Agent 角色

### data-access-agent

职责：
- 作为中台数据小组的第一入口，负责把自然语言数据问题转成安全、可追踪的 VPS/Odoo 查询。
- 优先调用专项 skill；没有专项 skill 时，使用 `odoo-data-query-assistant`。
- 遇到未知模型、字段、业务实体时，先调用或参考 `odoo-knowledge-discovery`，不要猜字段。
- 只做只读查询，不执行审批、发消息、写入、删除、导入等动作。

默认输出：
- 原始查询记录：`/data_raw/{timestamp}_{topic}.md`
- 查询解释摘要：`/data_reports/{timestamp}_{topic}_summary.md`
- 数据质量问题：`/data_quality/{timestamp}_{topic}_issues.md`

必须保留：
- 用户原始问题。
- 使用的 skill 或 `vertu` 命令。
- 查询口径、时间范围、过滤条件。
- 数据来源和权限限制。
- 原始结果摘要。
- 下一步建议。

### market-analyst

职责：
- 分析客户背景、行业动态、采购动机、竞争格局。
- 从原始资料中提炼销售切入点。
- 输出结构化洞察，不写空洞口号。

默认输出：
- `/insights/{客户名称}_analysis.md`

### contract-expert

职责：
- 审查合同、报价、方案承诺和责任边界。
- 标出付款、交付、违约、验收、数据安全等风险。
- 给出可直接修改的建议。

默认输出：
- `/contracts/{客户名称}_risk_report.md`

### sales-manager

职责：
- 审批折扣、商务策略、关键客户推进方案。
- 汇总多个 Agent 的结论，形成最终行动建议。

默认输出：
- `/manager/{客户名称}_decision.md`

## 数据查询流转规则

### 1. 接收取数需求

当用户提出“查一下、统计、列出、对比、达成率、日报、OKR、销售额、库存、客户、门店”等数据问题：

- 调用或切换到 `data-access-agent`。
- 先判断是否已有专项 skill。
- 如果用户缺少时间范围、对象范围或口径，先列出默认假设；高风险口径必须追问。

### 2. 选择工具

- 日报相关：优先 `odoo-daily-report-assistant`。
- 公司销售日报：优先 `odoo-daily-sales-report`。
- OKR/目标：优先 `odoo-okr-management-assistant`。
- 销售人效/个人业绩：优先 `odoo-sale-personnel-efficiency`。
- 通用业务数据：优先 `odoo-data-query-assistant`。
- 未知字段/模型：先用 `odoo-knowledge-discovery`。
- 复杂只读脚本：必须先参考 `odoo-sandbox-script-guide`。

### 3. 输出沉淀

每次重要数据查询必须沉淀为文件：

- `/data_raw/`: 保留查询命令、返回摘要、样本数据。
- `/data_reports/`: 用业务语言解释结果。
- `/data_quality/`: 记录无法查询、权限不足、字段缺失、口径冲突等问题。

### 4. 禁止动作

`data-access-agent` 不得：

- 执行审批通过/驳回。
- 发送 Odoo/IM 消息。
- 写入、删除或导入业务数据。
- 绕过权限或使用不明来源 API Key。
- 在 Git 中提交密钥或客户敏感原文。

## 客户与合同流转规则

### 1. 客户分析阶段

当新资料进入 `/inbox/`：

- 调用或切换到 `market-analyst`。
- 生成客户分析报告到 `/insights/`。
- 报告必须包含：客户背景、痛点、采购信号、决策链、竞品风险、推荐切入话术。

### 2. 合同审查阶段

当 `/contracts/` 中出现新合同或报价草案：

- 调用或切换到 `contract-expert`。
- 生成风险报告到 `/contracts/`。
- 报告必须包含：风险等级、原文位置、风险解释、建议改法。

### 3. 经理审批阶段

当涉及折扣、特殊承诺、资源排期：

- 调用或切换到 `sales-manager`。
- 生成审批建议到 `/manager/`。

## 跨设备智能体路由表模板

只登记 URL 和用途，不登记密钥。密钥放在各成员本机 `.env`。

- 经理 Agent:
  - URL: `http://100.x.x.x:8642/v1`
  - Key env: `MANAGER_HERMES_API_KEY`
  - Capabilities: 折扣审批、方案终审
- Alice Agent:
  - URL: `http://100.x.x.x:8642/v1`
  - Key env: `ALICE_HERMES_API_KEY`
  - Capabilities: 合同条款审核
- Bob Agent:
  - URL: `http://100.x.x.x:8642/v1`
  - Key env: `BOB_HERMES_API_KEY`
  - Capabilities: 竞品分析

## 业绩数据 Agent 小组

当用户提出“业绩、实际业绩、销售明细、客户月度业绩、库存、按客户/月份汇总、从 VPS 拉销售数据”等问题时，优先进入业绩数据 Agent 小组流程。

### performance-data-puller
职责：从 Vertu/VPS/Odoo 或本地导出文件取得销售明细、库存、客户、产品等原始数据。优先使用 `vertu` CLI、`vps-cli` skill 和 `odoo-*` skills。输出到 `/data_raw/`。

### performance-cleaner
职责：清洗销售日期、客户名称、实际业绩、渠道、部门、退款、数量、产品、仓库等字段。输出到 `/data_clean/` 和 `/data_quality/`。

### performance-aggregator
职责：按客户、月份、销售员、渠道、部门、产品、SKU、国家、仓库等维度聚合实际业绩、数量、订单等指标。输出到 `/data_metrics/`。

### performance-report-builder
职责：生成业务可读报表，第一版支持“客户名称 x 1-12月 x 总计”的实际业绩 Excel。输出到 `/data_reports/`。

### 当前可运行命令

从本地销售明细生成客户月度业绩表：

```powershell
Set-Location -LiteralPath 'D:\经销商PDCA'
powershell -ExecutionPolicy Bypass -File .\scripts\build-performance-report.ps1 `
  -InputPath 'C:\Users\frank\Desktop\销售明细报表 (sale.order.line.report) (5).xlsx' `
  -Year 2025 `
  -Channel '代理' `
  -Department '经销商' `
  -Topic 'dealer-2025'
```

注意：运行输出默认被 `.gitignore` 忽略，不提交到 GitHub。