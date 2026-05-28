# Agent 数量与职责

实际落地版一共有 9 个 Agent，由 Hermes 调度。

1. `todo-planner-agent`：早上拉取和合并今日代办。
2. `vps-sales-data-agent`：通过 vps-cli 从 Odoo/VPS 拉正式业绩汇总。
3. `sales-summary-agent`：按销售员汇总业绩和数量。
4. `product-summary-agent`：按产品汇总业绩和数量。
5. `customer-summary-agent`：按客户/经销商汇总业绩和数量。
6. `logistics-browser-agent`：调用浏览器去 UPS/FedEx/DHL 官网查询物流单号。
7. `pdca-questionnaire-agent`：生成并解析每日问卷。
8. `pdca-check-act-agent`：生成日结、未完成事项和明日行动。
9. `im-notifier-agent`：推送到 IM 或写入 outbox。

其中业绩相关的 3 个汇总 Agent 必须依赖 `vps-sales-data-agent` 的正式数据，不允许使用虚假数据或临时 Excel 作为正式口径。

## 当前使用的 VPS Skill / 命令

- `vps-cli`
- `odoo-data-query-assistant`
- `odoo-sandbox-script-guide`
- 命令：`vertu odoo data sandbox`
- 正式业绩表：`sale_order_line_report`
- 经销商口径：`sale_type IN ('agent_sale', 'agent_sale_replacement', 'agent_sale_return')`
