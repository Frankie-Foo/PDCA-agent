# Hermes 调度流：数据岗位 PDCA MVP

## 每日早上触发

建议北京时间每天 09:00 触发。

本地实际运行入口：

```powershell
powershell -ExecutionPolicy Bypass -File D:\经销商PDCA\data_platform\data_role_pdca_mvp\scripts\run_data_role_pdca_daily.ps1
```

```text
Hermes
-> todo-planner-agent
-> data-summary-router-agent
-> vps-sales-data-agent
-> sales-summary-agent / product-summary-agent / customer-summary-agent
-> chart-packaging-agent
-> logistics-tracking-agent
-> logistics-browser-agent
-> pdca-questionnaire-agent
-> pdca-check-act-agent
-> im-notifier-agent
```

## 任务 1：今日代办

来源：

- 昨天未完成
- 今天新规划
- 上级临时交办
- Hermes/VPS 任务记录
- 昨晚问卷中“明日计划”

输出：

```text
今日必须完成
今日应完成
今日可延后
需要上级/业务方确认
```

## 任务 2：数据汇总

正式数据只取海外经销商：

```text
VPS/Odoo table: sale_order_line_report
level1_department_id: 1569 / 海外事业部
level2_department_id: 1577 / 经销商
sale_type: agent_sale / agent_sale_replacement / agent_sale_return
```

维度：

- 团队
- 销售员
- 产品
- 客户

指标：

- 业绩
- 数量
- 回款
- 在途
- 订单数

输出：

- Excel
- Markdown 表
- 图表数据 JSON

## 任务 3：物流核查

输入：

- 金山文档在线表，或导出的 CSV/XLSX
- 字段至少包含：单号、承运商、客户、销售、发货日期

输出：

- 正常清单
- 异常清单
- 需要人工确认清单
- IM 消息

## 任务 4：每日问卷

问题：

1. 今天完成了什么？
2. 明天要完成什么？
3. 昨天没完成的，今天完成了哪些？
4. 上级临时交办完成了哪些？
5. 今天卡点是什么？
6. 哪些事项需要明天继续？

## 任务 5：Check / Act

生成：

- 今日完成率
- 遗留事项
- 异常数据/物流
- 明日行动清单
- 需要上级确认事项

## IM 群

默认消息输出到：

```text
outbox/YYYY-MM-DD_im_message.md
```

目标群：

```text
经销商数据核对
```

真实推送需要配置：

```text
DATA_PDCA_IM_WEBHOOK_URL
```
