# Hermes data-access-agent query fragment
# Purpose: pull full dealer daily report data from the system instead of relying on temporary Excel files.
# Usage: run through Hermes data-access-agent / sql_read environment, then export ai['result'] to the daily report input.

RUN_DATE = "2026-05-20"
MONTH_START = RUN_DATE[:8] + "01"

rows = sql_read(f"""
    SELECT
        "销售日期",
        "销售员",
        "客户名称",
        "实际业绩",
        "付款时间",
        "是否退款",
        "渠道",
        "二级部门",
        "部门"
    FROM dealer_sale_analysis
    WHERE "销售日期" >= '{MONTH_START}'
      AND "销售日期" <= '{RUN_DATE}'
      AND (
            "渠道" = '代理'
         OR "二级部门" = '经销商'
         OR "部门" = '经销商'
      )
""")

ai["result"] = {
    "run_date": RUN_DATE,
    "month_start": MONTH_START,
    "rows": rows,
}
