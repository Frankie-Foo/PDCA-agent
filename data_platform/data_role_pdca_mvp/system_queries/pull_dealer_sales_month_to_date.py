# VPS/Odoo sandbox script.
# Run with:
# vertu odoo data sandbox --code-file pull_dealer_sales_month_to_date.py --params '{"run_date":"2026-05-28"}'
#
# Must not contain imports. The Odoo safe_eval sandbox injects sql_read, params, ai, etc.

run_date = params.get("run_date")
if not run_date:
    run_date = fields.Date.today().strftime("%Y-%m-%d")
month_start = params.get("start_date") or (run_date[:8] + "01")
period_start = month_start

base_where = """
    sale_date >= %(month_start)s
    AND sale_date <= %(run_date)s
    AND sale_type IN ('agent_sale', 'agent_sale_replacement', 'agent_sale_return')
    AND level1_department_id = 1569
    AND level2_department_id = 1577
"""

team_summary = sql_read("""
    SELECT
        COALESCE(hd.name->>'zh_CN', hd.name->>'en_US', solr.level3_department_id::text, '(空)') AS team,
        SUM(solr.performance) AS performance,
        SUM(COALESCE(solr.real_quantity, solr.quantity, 0)) AS quantity,
        COUNT(*) AS line_count
    FROM sale_order_line_report solr
    LEFT JOIN hr_department hd ON hd.id = solr.level3_department_id
    WHERE """ + base_where + """
    GROUP BY COALESCE(hd.name->>'zh_CN', hd.name->>'en_US', solr.level3_department_id::text, '(空)')
    ORDER BY SUM(solr.performance) DESC
""", {"month_start": month_start, "run_date": run_date})

salesperson_summary = sql_read("""
    SELECT
        COALESCE(rp.name, salesperson::text, '(空)') AS salesperson,
        SUM(solr.performance) AS performance,
        SUM(COALESCE(solr.real_quantity, solr.quantity, 0)) AS quantity,
        COUNT(*) AS line_count
    FROM sale_order_line_report solr
    LEFT JOIN res_users ru ON ru.id = solr.salesperson
    LEFT JOIN res_partner rp ON rp.id = ru.partner_id
    WHERE """ + base_where + """
    GROUP BY COALESCE(rp.name, salesperson::text, '(空)')
    ORDER BY SUM(performance) DESC
""", {"month_start": month_start, "run_date": run_date})

customer_summary = sql_read("""
    SELECT
        COALESCE(solr.partner_name, '(空)') AS partner_name,
        SUM(solr.performance) AS performance,
        SUM(COALESCE(solr.real_quantity, solr.quantity, 0)) AS quantity,
        COUNT(*) AS line_count
    FROM sale_order_line_report solr
    WHERE """ + base_where + """
    GROUP BY COALESCE(solr.partner_name, '(空)')
    ORDER BY SUM(performance) DESC
""", {"month_start": month_start, "run_date": run_date})

product_summary = sql_read("""
    SELECT
        COALESCE(pt.name->>'zh_CN', pt.name->>'en_US', solr.product_id::text, '(空)') AS product_name,
        SUM(solr.performance) AS performance,
        SUM(COALESCE(solr.real_quantity, solr.quantity, 0)) AS quantity,
        COUNT(*) AS line_count
    FROM sale_order_line_report solr
    LEFT JOIN product_product pp ON pp.id = solr.product_id
    LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
    WHERE """ + base_where + """
    GROUP BY COALESCE(pt.name->>'zh_CN', pt.name->>'en_US', solr.product_id::text, '(空)')
    ORDER BY SUM(performance) DESC
""", {"month_start": month_start, "run_date": run_date})

daily_team_summary = sql_read("""
    SELECT
        COALESCE(hd.name->>'zh_CN', hd.name->>'en_US', solr.level3_department_id::text, '(空)') AS team,
        SUM(solr.performance) AS performance,
        SUM(COALESCE(solr.real_quantity, solr.quantity, 0)) AS quantity,
        COUNT(*) AS line_count
    FROM sale_order_line_report solr
    LEFT JOIN hr_department hd ON hd.id = solr.level3_department_id
    WHERE """ + base_where + """
        AND sale_date = %(run_date)s
    GROUP BY COALESCE(hd.name->>'zh_CN', hd.name->>'en_US', solr.level3_department_id::text, '(空)')
    ORDER BY SUM(solr.performance) DESC
""", {"month_start": month_start, "run_date": run_date})

daily_salesperson_summary = sql_read("""
    SELECT
        COALESCE(rp.name, salesperson::text, '(空)') AS salesperson,
        SUM(solr.performance) AS performance,
        SUM(COALESCE(solr.real_quantity, solr.quantity, 0)) AS quantity,
        COUNT(*) AS line_count
    FROM sale_order_line_report solr
    LEFT JOIN res_users ru ON ru.id = solr.salesperson
    LEFT JOIN res_partner rp ON rp.id = ru.partner_id
    WHERE """ + base_where + """
        AND sale_date = %(run_date)s
    GROUP BY COALESCE(rp.name, salesperson::text, '(空)')
    ORDER BY SUM(solr.performance) DESC
""", {"month_start": month_start, "run_date": run_date})

yesterday_team_summary = sql_read("""
    SELECT
        COALESCE(hd.name->>'zh_CN', hd.name->>'en_US', solr.level3_department_id::text, '(空)') AS team,
        SUM(solr.performance) AS performance,
        SUM(COALESCE(solr.real_quantity, solr.quantity, 0)) AS quantity,
        COUNT(*) AS line_count
    FROM sale_order_line_report solr
    LEFT JOIN hr_department hd ON hd.id = solr.level3_department_id
    WHERE sale_date = (%(run_date)s::date - interval '1 day')::date
        AND sale_type IN ('agent_sale', 'agent_sale_replacement', 'agent_sale_return')
        AND level1_department_id = 1569
        AND level2_department_id = 1577
    GROUP BY COALESCE(hd.name->>'zh_CN', hd.name->>'en_US', solr.level3_department_id::text, '(空)')
    ORDER BY SUM(solr.performance) DESC
""", {"run_date": run_date})

yesterday_salesperson_summary = sql_read("""
    SELECT
        COALESCE(rp.name, salesperson::text, '(空)') AS salesperson,
        SUM(solr.performance) AS performance,
        SUM(COALESCE(solr.real_quantity, solr.quantity, 0)) AS quantity,
        COUNT(*) AS line_count
    FROM sale_order_line_report solr
    LEFT JOIN res_users ru ON ru.id = solr.salesperson
    LEFT JOIN res_partner rp ON rp.id = ru.partner_id
    WHERE sale_date = (%(run_date)s::date - interval '1 day')::date
        AND sale_type IN ('agent_sale', 'agent_sale_replacement', 'agent_sale_return')
        AND level1_department_id = 1569
        AND level2_department_id = 1577
    GROUP BY COALESCE(rp.name, salesperson::text, '(空)')
    ORDER BY SUM(solr.performance) DESC
""", {"run_date": run_date})

week_team_summary = sql_read("""
    SELECT
        COALESCE(hd.name->>'zh_CN', hd.name->>'en_US', solr.level3_department_id::text, '(空)') AS team,
        SUM(solr.performance) AS performance,
        SUM(COALESCE(solr.real_quantity, solr.quantity, 0)) AS quantity,
        COUNT(*) AS line_count
    FROM sale_order_line_report solr
    LEFT JOIN hr_department hd ON hd.id = solr.level3_department_id
    WHERE sale_date >= date_trunc('week', %(run_date)s::date)::date
        AND sale_date <= %(run_date)s
        AND sale_type IN ('agent_sale', 'agent_sale_replacement', 'agent_sale_return')
        AND level1_department_id = 1569
        AND level2_department_id = 1577
    GROUP BY COALESCE(hd.name->>'zh_CN', hd.name->>'en_US', solr.level3_department_id::text, '(空)')
    ORDER BY SUM(solr.performance) DESC
""", {"run_date": run_date})

week_salesperson_summary = sql_read("""
    SELECT
        COALESCE(rp.name, salesperson::text, '(空)') AS salesperson,
        SUM(solr.performance) AS performance,
        SUM(COALESCE(solr.real_quantity, solr.quantity, 0)) AS quantity,
        COUNT(*) AS line_count
    FROM sale_order_line_report solr
    LEFT JOIN res_users ru ON ru.id = solr.salesperson
    LEFT JOIN res_partner rp ON rp.id = ru.partner_id
    WHERE sale_date >= date_trunc('week', %(run_date)s::date)::date
        AND sale_date <= %(run_date)s
        AND sale_type IN ('agent_sale', 'agent_sale_replacement', 'agent_sale_return')
        AND level1_department_id = 1569
        AND level2_department_id = 1577
    GROUP BY COALESCE(rp.name, salesperson::text, '(空)')
    ORDER BY SUM(solr.performance) DESC
""", {"run_date": run_date})

daily_trend_by_salesperson = sql_read("""
    SELECT
        to_char(sale_date, 'MM-DD') AS day_label,
        COALESCE(rp.name, salesperson::text, '(空)') AS salesperson,
        SUM(solr.performance) AS performance,
        SUM(COALESCE(solr.real_quantity, solr.quantity, 0)) AS quantity
    FROM sale_order_line_report solr
    LEFT JOIN res_users ru ON ru.id = solr.salesperson
    LEFT JOIN res_partner rp ON rp.id = ru.partner_id
    WHERE """ + base_where + """
    GROUP BY to_char(sale_date, 'MM-DD'), COALESCE(rp.name, salesperson::text, '(空)')
    ORDER BY to_char(sale_date, 'MM-DD'), SUM(solr.performance) DESC
""", {"month_start": month_start, "run_date": run_date})

daily_trend_by_team = sql_read("""
    SELECT
        to_char(sale_date, 'MM-DD') AS day_label,
        COALESCE(hd.name->>'zh_CN', hd.name->>'en_US', solr.level3_department_id::text, '(空)') AS team,
        SUM(solr.performance) AS performance,
        SUM(COALESCE(solr.real_quantity, solr.quantity, 0)) AS quantity
    FROM sale_order_line_report solr
    LEFT JOIN hr_department hd ON hd.id = solr.level3_department_id
    WHERE """ + base_where + """
    GROUP BY to_char(sale_date, 'MM-DD'), COALESCE(hd.name->>'zh_CN', hd.name->>'en_US', solr.level3_department_id::text, '(空)')
    ORDER BY to_char(sale_date, 'MM-DD'), SUM(solr.performance) DESC
""", {"month_start": month_start, "run_date": run_date})

ai["result"] = {
    "source": "vps-cli / odoo-data-query-assistant / odoo-sandbox-script-guide",
    "table": "sale_order_line_report",
    "run_date": run_date,
    "month_start": month_start,
    "period_start": period_start,
    "scope": "海外事业部 / 经销商",
    "filters": {
        "level1_department_id": 1569,
        "level2_department_id": 1577,
        "sale_type": ["agent_sale", "agent_sale_replacement", "agent_sale_return"],
    },
    "summary_mode": True,
    "team_summary": team_summary,
    "salesperson_summary": salesperson_summary,
    "customer_summary": customer_summary,
    "product_summary": product_summary,
    "daily_team_summary": daily_team_summary,
    "daily_salesperson_summary": daily_salesperson_summary,
    "yesterday_team_summary": yesterday_team_summary,
    "yesterday_salesperson_summary": yesterday_salesperson_summary,
    "week_team_summary": week_team_summary,
    "week_salesperson_summary": week_salesperson_summary,
    "daily_trend_by_salesperson": daily_trend_by_salesperson,
    "daily_trend_by_team": daily_trend_by_team,
}
