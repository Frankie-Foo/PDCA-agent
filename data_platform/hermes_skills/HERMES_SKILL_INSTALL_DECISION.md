# Hermes Skill 安装决策记录

日期：2026-05-28

## 已安装

已安装到：

- `C:\Users\frank\.hermes\skills`
- `C:\Users\frank\.hermes\profiles\data-access-agent\skills`
- `C:\Users\frank\.hermes\profiles\performance-data-puller\skills`
- `C:\Users\frank\.hermes\profiles\performance-aggregator\skills`
- `C:\Users\frank\.hermes\profiles\performance-report-builder\skills`

### dealer-data-daily-report

用途：每日经销商数据汇报，支持从系统 JSON 生成日报并推送到 `经销商数据核对`。

### dealer-data-skill-selection

用途：后续判断哪些外部 skill 值得装，避免乱装。

### dealer-data-web-research

用途：承接 Tavily / Jina Reader 类能力，用于周报/月报外部市场证据、公开网页读取、竞品资料整理。

状态：先安装规程，API key 到位后再接真实 Tavily/Jina 调用。

### dealer-data-hindsight

用途：沉淀复盘记忆，记录反复出现的数据口径、别名、目标、数据质量问题。

### agency-agents-zh-lite

用途：中文多 Agent 编排，用于 Hermes 把日报、周报、月报、临时取数拆给专业角色。

## 暂不安装

### Fal.ai

原因：偏图片/视频生成，对当前经销商日报、周报、临时数据需求帮助不大。

### RTK

原因：如果指 Redux Toolkit，是前端状态管理；目前还没有进入 Web 看板开发阶段。

### Tailscale / Tokscale

原因：如果指 Tailscale，它是跨设备网络访问能力，不是数据报表 skill。只有当 Hermes 需要外网/跨设备访问时再配置。

### Hermes Agent Self-Evolution

原因：高风险，可能改变 Agent 行为。等每日汇报到 IM 群稳定运行一周后，再加审查门槛启用。

## 推荐下一步

1. 配置 `DEALER_IM_WEBHOOK_URL`，让 `dealer-data-daily-report` 真正推送到 IM 群。
2. 若周报需要外部资料，提供 Tavily API key 或 Jina Reader 可用接口。
3. 跑一周后启用 `dealer-data-hindsight` 做自动复盘沉淀。
