import argparse
import csv
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def load_json(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build_todo_reminder(workspace, date_text):
    today_path = workspace / "inputs" / "todos" / f"{date_text}_todos.csv"
    yesterday = (datetime.strptime(date_text, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_path = workspace / "inputs" / "todos" / f"{yesterday}_todos.csv"

    rows = []
    rows.extend(read_csv(yesterday_path))
    rows.extend(read_csv(today_path))

    pending = [r for r in rows if (r.get("status") or "").lower() not in {"done", "completed", "已完成"}]
    high = [r for r in pending if (r.get("priority") or "").upper() == "HIGH"]
    medium = [r for r in pending if (r.get("priority") or "").upper() == "MEDIUM"]
    other = [r for r in pending if r not in high and r not in medium]

    lines = [f"# 今日代办提醒 {date_text}", ""]
    lines.append("## 今日必须完成")
    lines.extend(f"- [{r.get('source')}] {r.get('title')}（截止：{r.get('due_date') or date_text}）" for r in high)
    if not high:
        lines.append("- 暂无")

    lines.extend(["", "## 今日应完成"])
    lines.extend(f"- [{r.get('source')}] {r.get('title')}" for r in medium)
    if not medium:
        lines.append("- 暂无")

    lines.extend(["", "## 可延后/待确认"])
    lines.extend(f"- [{r.get('source')}] {r.get('title')}" for r in other)
    if not other:
        lines.append("- 暂无")

    return "\n".join(lines), pending


def build_data_summary(workspace, date_text):
    sample_sources = [
        workspace.parent / "daily_dealer_report" / "outputs" / "reports" / f"{date_text}_dealer_daily_report.md"
    ]
    source_note = next((str(p) for p in sample_sources if p.exists()), "未发现当天经销商日报输出，MVP 先生成汇总任务框架")

    lines = [
        f"# 数据汇总任务 {date_text}",
        "",
        f"- 数据来源：{source_note}",
        "",
        "## 销售员汇总 Agent",
        "- 指标：业绩、数量、回款、在途",
        "- 输出：销售员维度 Excel / Markdown / 图表数据",
        "",
        "## 产品汇总 Agent",
        "- 指标：业绩、数量",
        "- 输出：产品/系列/品类维度汇总",
        "",
        "## 客户汇总 Agent",
        "- 指标：业绩、数量、订单、回款",
        "- 输出：客户/经销商维度汇总",
        "",
        "## MVP 状态",
        "- 当前已生成任务框架；接入 Odoo/VPS 明细后可自动产出 Excel 和图表。",
    ]
    chart_data = {
        "date": date_text,
        "charts": [
            {"name": "销售员业绩排行", "dimension": "salesperson", "metric": "performance"},
            {"name": "产品数量排行", "dimension": "product", "metric": "quantity"},
            {"name": "客户业绩排行", "dimension": "customer", "metric": "performance"},
        ],
    }
    return "\n".join(lines), chart_data


def logistics_url(carriers, carrier, tracking_number):
    info = carriers.get(carrier) or carriers.get(carrier.upper()) or {}
    template = info.get("tracking_url", "")
    return template.replace("{tracking_number}", tracking_number) if template else ""


def build_logistics_report(workspace, date_text):
    carriers = load_json(workspace / "config" / "carriers.json")
    path = workspace / "inputs" / "logistics" / f"{date_text}_tracking.csv"
    rows = read_csv(path)

    lines = [
        f"# 物流核查报告 {date_text}",
        "",
        "## 结论",
    ]
    if not rows:
        lines.append("- 今日没有物流单号输入。")
    else:
        lines.append(f"- 读取到 {len(rows)} 个物流单号。MVP 当前生成查询链接和待核对清单；接入 UPS/FedEx API 后可自动判断状态。")

    lines.extend([
        "",
        "## 待核查单号",
        "| 单号 | 承运商 | 客户 | 销售 | 发货日期 | 期望状态 | 查询链接 | 判断 |",
        "|---|---|---|---|---|---|---|---|",
    ])
    for row in rows:
        tracking_number = row.get("tracking_number", "").strip()
        carrier = row.get("carrier", "").strip()
        url = logistics_url(carriers, carrier, tracking_number)
        judgement = "待接 API/人工核对"
        lines.append(
            f"| {tracking_number} | {carrier} | {row.get('customer','')} | {row.get('salesperson','')} | {row.get('ship_date','')} | {row.get('expected_status','')} | {url} | {judgement} |"
        )
    return "\n".join(lines), rows


def ensure_questionnaire(workspace, date_text):
    template = (workspace / "templates" / "daily_questionnaire.md").read_text(encoding="utf-8")
    text = template.replace("YYYY-MM-DD", date_text)
    path = workspace / "inputs" / "questionnaires" / f"{date_text}_questionnaire.md"
    if not path.exists():
        write(path, text)
    return path


def build_pdca_check(date_text, pending_todos, logistics_rows, questionnaire_path):
    unfinished = [r for r in pending_todos if (r.get("status") or "").lower() not in {"done", "completed", "已完成"}]
    lines = [
        f"# 数据岗位 PDCA 日结 {date_text}",
        "",
        "## Plan",
        f"- 今日代办 {len(pending_todos)} 项，其中未完成 {len(unfinished)} 项。",
        "",
        "## Do",
        "- 已生成数据汇总任务框架。",
        f"- 已读取物流单号 {len(logistics_rows)} 个。",
        f"- 已生成每日问卷：`{questionnaire_path}`",
        "",
        "## Check",
    ]
    if unfinished:
        lines.extend(f"- 未完成：{r.get('title')}" for r in unfinished)
    else:
        lines.append("- 今日代办均已完成。")
    if logistics_rows:
        lines.append("- 物流状态仍需接 API 或人工核对后闭环。")

    lines.extend([
        "",
        "## Act",
        "- 明早继续滚动未完成代办。",
        "- 补充问卷答案后，自动生成明日计划。",
        "- 接入 Odoo/VPS 明细后，自动生成销售员/产品/客户 Excel 和图表。",
        "- 接入物流 API 或金山文档导出后，自动判断物流异常并推送。",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--workspace", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace)
    date_text = args.date
    day_out = workspace / "outputs" / date_text

    todo_text, pending = build_todo_reminder(workspace, date_text)
    data_text, chart_data = build_data_summary(workspace, date_text)
    logistics_text, logistics_rows = build_logistics_report(workspace, date_text)
    questionnaire_path = ensure_questionnaire(workspace, date_text)
    pdca_text = build_pdca_check(date_text, pending, logistics_rows, questionnaire_path)

    write(day_out / "todo_reminder.md", todo_text)
    write(day_out / "data_summary_report.md", data_text)
    write(day_out / "logistics_check_report.md", logistics_text)
    write(day_out / "pdca_daily_check.md", pdca_text)
    write(day_out / "chart_data.json", json.dumps(chart_data, ensure_ascii=False, indent=2))

    im_message = "\n\n".join([todo_text, logistics_text, pdca_text])
    write(workspace / "outbox" / f"{date_text}_im_message.md", im_message)

    print(f"Generated MVP outputs: {day_out}")
    print(f"Questionnaire: {questionnaire_path}")
    print(f"IM outbox: {workspace / 'outbox' / f'{date_text}_im_message.md'}")


if __name__ == "__main__":
    main()
