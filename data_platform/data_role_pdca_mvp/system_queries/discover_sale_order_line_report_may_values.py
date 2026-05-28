run_date = params.get("run_date") or "2026-05-20"
month_start = run_date[:8] + "01"
sale_types = sql_read("""
    SELECT sale_type, COUNT(*) AS line_count, SUM(performance) AS performance
    FROM sale_order_line_report
    WHERE sale_date >= %(month_start)s
      AND sale_date <= %(run_date)s
    GROUP BY sale_type
    ORDER BY COUNT(*) DESC
    LIMIT 20
""", {"month_start": month_start, "run_date": run_date})
salespeople = sql_read("""
    SELECT salesperson, COUNT(*) AS line_count, SUM(performance) AS performance
    FROM sale_order_line_report
    WHERE sale_date >= %(month_start)s
      AND sale_date <= %(run_date)s
    GROUP BY salesperson
    ORDER BY SUM(performance) DESC
    LIMIT 20
""", {"month_start": month_start, "run_date": run_date})
ai["result"] = {
    "run_date": run_date,
    "month_start": month_start,
    "sale_types": sale_types,
    "salespeople": salespeople,
}
