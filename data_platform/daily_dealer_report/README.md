# 每日经销商数据汇报 Hermes Agent 配置

本包先解决“每天汇报数据”这一件事。设计前提：

```text
Hermes = 调度中枢
Cursor = 工作台
Agent = 专业工种
IM 群 = 经销商数据核对
```

## 每日链路需要几个 Agent

第一版建议 5 个 Agent，够用且不复杂：

1. `daily-file-ingestion-agent`：接收每日 Excel / CSV 数据文件。
2. `daily-metric-agent`：计算当月业绩、目标、达成率、当日录单收款、在途业绩。
3. `daily-data-quality-agent`：检查缺字段、缺目标、日期异常、金额异常。
4. `daily-insight-agent`：生成“谁落后、谁异常、今天要核对什么”。
5. `im-publisher-agent`：把汇报消息推到 IM 群 `经销商数据核对`。

## 推荐安装位置

复制到：

```text
D:\经销商PDCA\data_platform\daily_dealer_report
```

## 快速运行

```powershell
python D:\经销商PDCA\data_platform\daily_dealer_report\scripts\daily_dealer_report.py `
  --input-xlsx "D:\Vertu\data\excel\26年数据\5月\临时需求\26-杨晶晶.xlsx" `
  --sheet 26 `
  --date 2026-05-20 `
  --targets "D:\经销商PDCA\data_platform\daily_dealer_report\config\daily_targets_template.csv" `
  --out-dir "D:\经销商PDCA\data_platform\daily_dealer_report\outputs"
```

## IM 推送

脚本支持 webhook 推送。需要配置环境变量：

```powershell
$env:DEALER_IM_WEBHOOK_URL="https://your-im-webhook"
$env:DEALER_IM_GROUP="经销商数据核对"
```

然后加参数：

```powershell
--push
```

如果没有 webhook，脚本不会假装发送成功，会把消息写入：

```text
outputs\outbox\YYYY-MM-DD_im_payload.json
```

Hermes 可以监听这个 outbox，或者你把 webhook 给 Cursor 后接入真实发送。
