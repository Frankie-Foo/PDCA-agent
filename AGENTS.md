# 销售团队智能体分工与流转契约

## 总原则

- 所有 Agent 必须优先读取本文件和 `.cursorrules`。
- 输出必须落到对应目录，不要覆盖原始资料。
- 涉及价格、合同、承诺、交付周期、法务风险时，必须显式标注假设与风险。
- 不要把本地 `.env`、API Key、私钥、客户敏感原文提交到 Git。

## 目录架构

- `/inbox/`: 原始客户背景、会议纪要、邮件摘要、聊天记录整理稿。
- `/insights/`: 市场分析员 `market-analyst` 的输出目录。
- `/contracts/`: 合同、报价、方案草案，以及合同专家 `contract-expert` 的风险报告。
- `/manager/`: 经理审批、折扣策略、最终方案。
- `/sales_alice/`, `/sales_bob/`: 销售个人工作目录示例。
- `/templates/`: 可复用模板。

## Agent 角色

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

## 流转规则

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

