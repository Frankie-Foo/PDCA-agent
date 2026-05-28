# 数据岗位 PDCA MVP 使用手册

面向没有编程基础的使用者。

## 每天怎么用

### 方法一：双击运行

打开：

```text
D:\经销商PDCA\data_platform\data_role_pdca_mvp\scripts\run_data_role_pdca.bat
```

双击即可运行当天流程。

### 方法二：对 Hermes 说

```text
运行今天的数据岗位 PDCA MVP
```

Hermes 会使用 `data-role-pdca-mvp` skill。

## 你会看到什么

运行后看这个目录：

```text
D:\经销商PDCA\data_platform\data_role_pdca_mvp\outputs\当天日期
```

里面有：

- 今日代办提醒
- 数据汇总报告
- 销售员/产品/客户汇总 Excel
- 物流核查报告
- PDCA 日结
- 数据看板 HTML

## 晚上要填什么

填写：

```text
D:\经销商PDCA\data_platform\data_role_pdca_mvp\inputs\questionnaires\当天日期_questionnaire.md
```

只需要回答：

- 今天完成了什么
- 明天要完成什么
- 昨天遗留完成了哪些
- 上级交办交付了哪些
- 今天卡在哪里

第二天系统会自动把未完成和明日计划滚入待办。

## 业绩数据从哪里来

正式口径必须从 VPS/Odoo 拉取，使用：

```text
vps-cli skill: odoo-data-query-assistant
vps-cli skill: odoo-sandbox-script-guide
命令: vertu odoo data sandbox
数据表: dealer_sale_analysis
```

Excel 只允许作为离线调试或演示，不作为正式业绩来源。

当前正式业绩口径：

```text
数据表：sale_order_line_report
销售类型：agent_sale / agent_sale_replacement / agent_sale_return
```

系统会自动生成：

- 销售员业绩/数量汇总
- 产品业绩/数量汇总
- 客户业绩/数量汇总
- Excel 原生图表
- HTML 数据看板

## 物流怎么用

把物流单号放进：

```text
inputs\logistics\当天日期_tracking.csv
```

如果有 UPS/FedEx/DHL API，会自动查。  
如果没有 API，物流 Agent 会调用浏览器打开官网查询链接，由 Agent 判断正常/异常。
