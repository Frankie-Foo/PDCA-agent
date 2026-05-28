---
name: dealer-data-daily-report
description: Build and push dealer daily performance reports.
version: 0.1.0
author: Vertu Data Platform
metadata:
  hermes:
    category: domain
    tags:
      - dealer
      - daily-report
      - odoo
      - im
---

# Dealer Data Daily Report

Use this skill when the user asks Hermes to generate, verify, or push the daily dealer performance report to the IM group `经销商数据核对`.

## Trigger Phrases

- 每日经销商数据汇报
- 当月业绩目标达成
- 推送到经销商数据核对
- 今日录单收款
- 当日在途业绩
- 经销商日报

## Workflow

1. Pull full dealer sales data from Odoo / VPS first. Prefer the system query fragment:
   `D:\经销商PDCA\data_platform\daily_dealer_report\system_queries\dealer_daily_report_sql_read.py`.
2. Save the pulled result as JSON under `D:\经销商PDCA\data_raw\`.
3. Run `D:\经销商PDCA\data_platform\daily_dealer_report\scripts\daily_dealer_report.py` with `--input-json`.
4. Confirm the output has team subtotals for:
   - 于冰组
   - 杨晶晶组
   - Lina组
5. Confirm sales alias mapping is applied:
   - `DEHDAHOUMAIMA` must display as `Lina`.
6. If IM webhook is configured, push to group `经销商数据核对` with `--push`.
7. If webhook is missing, write the payload to `outputs\outbox` and report that it is pending push.

## Required Files

- `D:\经销商PDCA\data_platform\daily_dealer_report\config\daily_targets_template.csv`
- `D:\经销商PDCA\data_platform\daily_dealer_report\config\sales_aliases.csv`
- `D:\经销商PDCA\data_platform\daily_dealer_report\config\pipeline_template.csv`
- `D:\经销商PDCA\data_platform\daily_dealer_report\config\im_channels.json`

## Command Template

```powershell
python D:\经销商PDCA\data_platform\daily_dealer_report\scripts\daily_dealer_report.py `
  --input-json "D:\经销商PDCA\data_raw\dealer_daily_report_YYYY-MM-DD.json" `
  --date YYYY-MM-DD `
  --targets "D:\经销商PDCA\data_platform\daily_dealer_report\config\daily_targets_template.csv" `
  --aliases "D:\经销商PDCA\data_platform\daily_dealer_report\config\sales_aliases.csv" `
  --pipeline "D:\经销商PDCA\data_platform\daily_dealer_report\config\pipeline_template.csv" `
  --out-dir "D:\经销商PDCA\data_platform\daily_dealer_report\outputs" `
  --push
```

## Quality Rules

- Do not use temporary partial Excel files as the formal data source unless the user explicitly says it is the source of truth.
- Do not treat unknown sales names as zero; list them in data quality reminders.
- Do not claim the IM message was sent unless the webhook POST succeeds.
- If `DEHDAHOUMAIMA` appears in the output, the alias mapping failed.
- If total target is not `582.0 万` for the current template, check the target config before pushing.

## IM Group

```text
经销商数据核对
```

The webhook should be read from:

```text
DEALER_IM_WEBHOOK_URL
```

