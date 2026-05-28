# 数据岗位 PDCA MVP Agents

实际落地版共 9 个 Agent。所有入口都应由 Hermes 调度；Cursor 只作为工作台。

## 1. todo-planner-agent

职责：

- 从 VPS/Hermes 拉今日代办。
- 合并昨天未完成、今天新规划、上级临时交办。
- 生成早上提醒。

输入：

- `inputs/todos/*.csv`
- 昨日问卷
- 上级交办记录

输出：

- `todo_reminder.md`

## 2. data-summary-router-agent

职责：

- 判断今天要做哪类数据汇总。
- 分派给销售、产品、客户维度汇总 Agent。
- 正式业绩数据必须先由 `vps-sales-data-agent` 从 VPS/Odoo 拉取。

输出：

- 汇总任务清单

## 2a. vps-sales-data-agent

职责：

- 使用 vps-cli 从 VPS/Odoo 拉正式业绩数据。
- 使用 skill：
  - `odoo-data-query-assistant`
  - `odoo-sandbox-script-guide`
- 使用命令：
  - `vertu odoo data sandbox`
- 使用数据源：
  - `sale_order_line_report`

禁止：

- 不允许把临时 Excel 当作正式业绩数据。
- 不允许编造销售员、产品、客户业绩。

## 3. sales-summary-agent

职责：

- 按销售员汇总业绩、数量、回款、在途。

## 4. product-summary-agent

职责：

- 按产品/品类/系列汇总业绩和数量。

## 5. customer-summary-agent

职责：

- 按客户/经销商汇总业绩、数量、回款、在途。

## 6. chart-packaging-agent

职责：

- 把汇总表生成图表数据和可视化建议。
- MVP 先输出 JSON 和 Markdown，后续可接 Excel 图表。

## 7. logistics-tracking-agent

职责：

- 读取物流单号。
- 查询 UPS/FedEx/DHL/SF 等物流状态。
- 判断正常/异常。

MVP 规则：

- 如果没有官方 API key 或网页权限，先生成待查 URL 和人工核对清单。
- 不伪造物流状态。

## 8. pdca-questionnaire-agent

职责：

- 生成每日问卷。
- 读取问卷答案。
- 把答案转为完成事项、遗留事项和明日计划。

## 9. pdca-check-act-agent

职责：

- 汇总今日代办、问卷、数据汇总、物流检查。
- 生成每日 Check 和次日 Act。

## 10. im-notifier-agent

职责：

- 把今日提醒、异常物流、PDCA 日结推送给用户。
- 如果 webhook 不存在，写入 outbox。
