rows = sql_read("""
    SELECT *
    FROM sale_order_line_report
    WHERE sale_date >= %(month_start)s
      AND sale_date <= %(run_date)s
    LIMIT 1
""", {"month_start": params.get("run_date", "2026-05-20")[:8] + "01", "run_date": params.get("run_date", "2026-05-20")})
ai["result"] = {"rows": rows}
