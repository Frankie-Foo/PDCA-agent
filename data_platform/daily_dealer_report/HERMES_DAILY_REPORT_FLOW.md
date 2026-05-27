# Hermes 每日汇报调度流

## 群信息

```yaml
im_group_name: 经销商数据核对
default_channel_type: im_group
```

## 调度入口

当 Hermes 收到以下触发时启动：

```text
每日数据汇报
今日经销商数据
当月业绩目标达成
推送到经销商数据核对
```

## Agent 链路

```text
daily-file-ingestion-agent
-> daily-metric-agent
-> daily-data-quality-agent
-> daily-insight-agent
-> im-publisher-agent
```

## 标准任务卡

```yaml
task_name: dealer_daily_report
run_date: YYYY-MM-DD
input_files:
  sales_detail:
  targets:
  pipeline:
output:
  markdown_report:
  im_payload:
  quality_report:
im:
  group_name: 经销商数据核对
  webhook_env: DEALER_IM_WEBHOOK_URL
```

## Hermes 调度命令模板

```powershell
python D:\经销商PDCA\data_platform\daily_dealer_report\scripts\daily_dealer_report.py `
  --input-json "{system_json_file}" `
  --date "{run_date}" `
  --targets "D:\经销商PDCA\data_platform\daily_dealer_report\config\daily_targets_template.csv" `
  --aliases "D:\经销商PDCA\data_platform\daily_dealer_report\config\sales_aliases.csv" `
  --pipeline "{pipeline_file_optional}" `
  --out-dir "D:\经销商PDCA\data_platform\daily_dealer_report\outputs" `
  --push
```

## 输出给群的消息结构

```text
【海外经销商每日数据汇报】YYYY-MM-DD

一句话结论

团队/销售达成表

数据核对提醒

需要业务确认
```

## 失败处理

- 缺少输入文件：Hermes 通知数据中台补文件。
- 缺少目标表：继续生成业绩，但标记“目标缺失，达成率不可用”。
- 缺少 webhook：写入 outbox，由 Hermes 后续补推。
- 数据质量阻塞：只推送“数据核对异常提醒”，不推正式日报。

## 系统取数片段

每日正式取数优先使用：

```text
D:\经销商PDCA\data_platform\daily_dealer_report\system_queries\dealer_daily_report_sql_read.py
```

查询来源：

```text
dealer_sale_analysis
```

输出字段：

```text
销售日期、销售员、客户名称、实际业绩、付款时间、是否退款、渠道、二级部门、部门
```
