# 业绩数据 Agent 小组

目标：把 VPS/Odoo 或本地导出的销售明细，稳定加工成经销商 PDCA 需要的业绩表、质量检查和后续行动输入。

## 第一版 subagent 分工

1. `performance-data-puller`
   - 从 Vertu/VPS/Odoo 拉销售明细、库存、客户、产品等原始数据。
   - 输出到 `data_raw/`，保留查询条件和来源。

2. `performance-cleaner`
   - 清洗字段：销售日期、客户名称、实际业绩、渠道、部门、退款、数量、产品、仓库。
   - 输出到 `data_clean/`，质量问题输出到 `data_quality/`。

3. `performance-aggregator`
   - 按客户、月份、销售员、产品、渠道、部门等维度聚合。
   - 输出指标表到 `data_metrics/`。

4. `performance-report-builder`
   - 生成销售团队可直接查看的 Excel 报表。
   - 第一版报表是“客户名称 x 1-12月 x 总计”的实际业绩表。

## 当前已跑通的本地闭环

源文件格式：`销售明细报表 (sale.order.line.report).xlsx`

必要字段：

- `销售日期`
- `客户名称`，为空时回退到 `收货人名称`
- `实际业绩`

推荐命令：

```powershell
Set-Location -LiteralPath 'D:\经销商PDCA'
powershell -ExecutionPolicy Bypass -File .\scripts\build-performance-report.ps1 `
  -InputPath 'C:\Users\frank\Desktop\销售明细报表 (sale.order.line.report) (5).xlsx' `
  -Year 2025 `
  -Channel '代理' `
  -Department '经销商' `
  -Topic 'dealer-2025'
```

输出：

- `data_reports/*_customer_monthly_performance.xlsx`：客户月度业绩表
- `data_metrics/*_customer_monthly.csv`：机器可读指标表
- `data_clean/*_clean.csv`：清洗后的明细
- `data_quality/*_quality.md`：质量检查

这些运行输出默认被 `.gitignore` 忽略，不会提交到 GitHub。

## VPS 拉取如何接入

当前项目已有 `scripts/call-vps-data.ps1`，可以先用它确认 VPS 模型、字段和权限。拉到 `data_raw/` 后，只要字段与销售明细导出一致，或者能映射到以下标准字段，就可以进入同一条处理流水线：

- `销售日期`
- `客户名称`
- `实际业绩`
- `渠道`
- `二级部门` 或 `部门`
- `是否退款`
- `产品编码`
- `存货名称`
- `出货仓库`

库存数据建议作为第二阶段单独接入：从库存模型拉 `产品编码/仓库/可用库存/在途/保留量`，再与销售业绩按产品或仓库维度做联合分析。
