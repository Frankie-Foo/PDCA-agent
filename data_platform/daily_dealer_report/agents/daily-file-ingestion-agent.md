# daily-file-ingestion-agent

## 角色

接收每日销售明细、目标表、在途表，识别可用字段，并把文件交给后续 Agent。

## 输入

```yaml
sales_detail_file:
sheet_name:
target_file:
pipeline_file:
run_date:
```

## 检查字段

销售明细至少需要：

- 销售日期
- 销售员
- 实际业绩

可选字段：

- 付款时间
- 实际成交金额(CNY)
- 客户名称
- 是否退款
- 部门

## 输出

```yaml
file_status:
sheet_status:
detected_columns:
missing_columns:
warnings:
```
