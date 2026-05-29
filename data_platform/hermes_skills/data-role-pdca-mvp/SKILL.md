---
name: data-role-pdca-mvp
description: Run the data role PDCA MVP workflow.
version: 0.1.0
author: Vertu Data Platform
metadata:
  hermes:
    category: productivity
    tags:
      - pdca
      - data-platform
      - todo
      - logistics
      - questionnaire
---

# Data Role PDCA MVP

Use this skill when the user wants to run or demonstrate the data role PDCA MVP.

## Trigger Phrases

- 数据岗位 PDCA MVP
- 今天代办
- 数据岗位每日问卷
- 物流核查
- 今日完成和明日计划
- 早上提醒我今天要做什么

## Workflow

1. Run the daily MVP runner:

```powershell
powershell -ExecutionPolicy Bypass -File D:\经销商PDCA\data_platform\data_role_pdca_mvp\scripts\run_data_role_pdca_daily.ps1 `
  -Date YYYY-MM-DD
```

Or run the Python script directly:

```powershell
python D:\经销商PDCA\data_platform\data_role_pdca_mvp\scripts\data_role_pdca_daily.py `
  --date YYYY-MM-DD `
  --workspace D:\经销商PDCA\data_platform\data_role_pdca_mvp
```

2. Read generated files:

```text
outputs\YYYY-MM-DD\todo_reminder.md
outputs\YYYY-MM-DD\data_summary_report.md
outputs\YYYY-MM-DD\dashboard.html
outputs\YYYY-MM-DD\YYYY-MM-DD_data_summary.xlsx
outputs\YYYY-MM-DD\logistics_check_report.md
outputs\YYYY-MM-DD\pdca_daily_check.md
outbox\YYYY-MM-DD_im_message.md
```

3. Ask the user to fill:

```text
inputs\questionnaires\YYYY-MM-DD_questionnaire.md
```

4. If IM webhook is configured, push `outbox\YYYY-MM-DD_im_message.md`.

## Official Performance Data Rule

All performance numbers must come from VPS/Odoo.

Use:

```text
vps-cli skill: odoo-data-query-assistant
vps-cli skill: odoo-sandbox-script-guide
command: vertu odoo data sandbox
table: sale_order_line_report
dealer sale_type: agent_sale / agent_sale_replacement / agent_sale_return
scope: level1_department_id=1569 and level2_department_id=1577
```

Excel input is allowed only when the command explicitly uses `--allow-excel-demo`.
Do not present Excel-derived numbers as official performance.

## Agent Roles

- `vps-sales-data-agent`
- `data-summary-router-agent`
- `todo-planner-agent`
- `sales-summary-agent`
- `product-summary-agent`
- `customer-summary-agent`
- `chart-packaging-agent`
- `logistics-tracking-agent`
- `logistics-browser-agent`
- `pdca-questionnaire-agent`
- `pdca-check-act-agent`
- `im-notifier-agent`

## Rules

- Do not fabricate logistics status. If API is unavailable, produce tracking links and a manual check list.
- For logistics tracking, prefer a browser agent visiting UPS/FedEx/DHL official tracking pages when no carrier API key is configured.
- Do not treat the questionnaire as complete until the user fills it.
- Keep unfinished tasks rolling into the next day.
- For data summaries, use Odoo/VPS data as source of truth when available.
