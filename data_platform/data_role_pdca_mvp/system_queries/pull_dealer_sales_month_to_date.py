# VPS/Odoo sandbox script.
# Run with:
# vertu odoo data sandbox --code-file pull_dealer_sales_month_to_date.py --params '{"run_date":"2026-05-28"}'
#
# Must not contain imports. The Odoo safe_eval sandbox injects sql_read, params, ai, etc.

run_date = params.get("run_date")
if not run_date:
    run_date = fields.Date.today().strftime("%Y-%m-%d")
month_start = run_date[:8] + "01"

base_where = """
    sale_date >= %(month_start)s
    AND sale_date <= %(run_date)s
    AND sale_type IN ('agent_sale', 'agent_sale_replacement', 'agent_sale_return')
"""

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

ai["result"] = {
    "source": "vps-cli / odoo-data-query-assistant / odoo-sandbox-script-guide",
    "table": "sale_order_line_report",
    "run_date": run_date,
    "month_start": month_start,
    "summary_mode": True,
    "salesperson_summary": salesperson_summary,
    "customer_summary": customer_summary,
    "product_summary": product_summary,
}
