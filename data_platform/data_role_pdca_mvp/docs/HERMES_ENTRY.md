# Hermes 入口说明

## 已安装 Skill

```text
data-role-pdca-mvp
```

## 推荐口令

```text
运行今天的数据岗位 PDCA MVP
```

```text
拉取今天 VPS 业绩数据并生成数据岗位 PDCA 看板
```

```text
检查今天物流异常并生成消息
```

## Hermes 应做的事

1. 使用 `data-role-pdca-mvp` skill。
2. 先运行 `scripts\pull_vps_sales_data.ps1` 从 VPS/Odoo 拉正式业绩数据。
3. 再运行 `scripts\run_data_role_pdca_daily.ps1`。
4. 读取输出并给用户摘要。
5. 如果配置了 IM webhook，推送消息。

## 正式业绩数据口径

- 必须通过 vps-cli 查询。
- 使用 skill：
  - `odoo-data-query-assistant`
  - `odoo-sandbox-script-guide`
- 使用命令：
  - `vertu odoo data sandbox`
- 使用数据表：
  - `sale_order_line_report`
- 经销商口径：
  - `agent_sale`
  - `agent_sale_replacement`
  - `agent_sale_return`

## 不能做的事

- 不能把临时 Excel 当正式业绩口径。
- 不能伪造 UPS/FedEx 查询结果。
- 不能说消息已推送，除非 webhook 返回成功。
