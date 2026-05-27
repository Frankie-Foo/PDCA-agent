# -*- coding: utf-8 -*-
import argparse
import csv
import re
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path


MEMBERS = ["杨晶晶", "何海文", "王宇彤"]
LEADER = "杨晶晶"
TEAM_NAME = "杨晶晶小组"
SLUGS = {
    "杨晶晶": "yang-jingjing",
    "何海文": "he-haiwen",
    "王宇彤": "wang-yutong",
}


def read_lines(path):
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8-sig").splitlines()


def number_from_line(lines, label):
    pattern = re.compile(rf"^\s*-\s*{re.escape(label)}\s*[:：]\s*(\d+(?:\.\d+)?)")
    for line in lines:
        match = pattern.match(line)
        if match:
            return float(match.group(1))
    return None


def text_from_line(lines, label):
    pattern = re.compile(rf"^\s*-\s*{re.escape(label)}\s*[:：]\s*(.*)$")
    for line in lines:
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return ""


def daily_defaults(monthly_target_path):
    defaults = OrderedDict(
        [
            ("新增客户", 3),
            ("有效触达", 15),
            ("客户跟进", 8),
            ("报价", 2),
            ("重点客户维护", 2),
            ("日报提交", 1),
        ]
    )
    lines = read_lines(monthly_target_path)
    for key in list(defaults.keys()):
        value = number_from_line(lines, key)
        if value is not None:
            defaults[key] = int(value)
    return defaults


def daily_log_summary(log_path, defaults):
    if not log_path.exists():
        return {
            "submitted": False,
            "completeness": 0,
            "metrics": {key: 0 for key in defaults if key != "日报提交"},
            "missing_fields": ["日报"],
            "process_rate": 0,
            "quote_count": 0,
            "has_next_action": False,
        }

    lines = read_lines(log_path)
    fields = ["实际业绩", "回款", "报价金额", "新增成交", "新增客户", "有效触达", "客户跟进", "报价", "重点客户维护"]
    missing = [field for field in fields if not text_from_line(lines, field)]
    metrics = {}
    for key in ["新增客户", "有效触达", "客户跟进", "报价", "重点客户维护"]:
        metrics[key] = number_from_line(lines, key) or 0

    parts = []
    for key in ["新增客户", "有效触达", "客户跟进", "报价", "重点客户维护"]:
        target = defaults[key]
        parts.append(1 if target <= 0 else min(1, metrics[key] / target))

    has_next_action = any(
        line.startswith("|") and len([cell.strip() for cell in line.split("|")]) >= 6 and "下一步" not in line
        for line in lines
    )
    return {
        "submitted": True,
        "completeness": round(((len(fields) - len(missing)) / len(fields)) * 100, 1),
        "metrics": metrics,
        "missing_fields": missing,
        "process_rate": round((sum(parts) / len(parts)) * 100, 1),
        "quote_count": int(metrics["报价"]),
        "has_next_action": has_next_action,
    }


def risk_text(summary, owned_count):
    risks = []
    if not summary["submitted"]:
        risks.append("未提交日报")
    if summary["submitted"] and summary["process_rate"] < 80:
        risks.append("过程指标不足")
    if summary["submitted"] and summary["completeness"] < 80:
        risks.append("日报字段不完整")
    if summary["submitted"] and summary["quote_count"] < 2:
        risks.append("报价动作不足")
    if owned_count == 0:
        risks.append("无明确负责客户")
    return "；".join(risks) if risks else "正常"


def bullet(items):
    return "\n".join(f"- {item}" for item in items)


def load_customers(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def generate(team_path, date_text):
    team_path = Path(team_path)
    check_date = datetime.strptime(date_text, "%Y-%m-%d")
    month = check_date.strftime("%Y-%m")
    next_day = (check_date + timedelta(days=1)).strftime("%Y-%m-%d")

    customers = load_customers(team_path / "customers.csv")
    defaults = daily_defaults(team_path / "monthly_targets" / f"{month}.md")
    check_dir = team_path / "check_reports"
    action_dir = team_path / "pdca_actions"

    summaries = {}
    for member in MEMBERS:
        slug = SLUGS[member]
        summaries[member] = daily_log_summary(team_path / "daily_logs" / slug / f"{date_text}.md", defaults)

    owner_counts = {member: sum(1 for customer in customers if customer["owner"] == member) for member in MEMBERS}
    total_customers = len(customers)
    leader_share = round((owner_counts[LEADER] / total_customers) * 100, 1) if total_customers else 0
    coverage_risk = leader_share > 60 and any(owner_counts[member] == 0 for member in ["何海文", "王宇彤"])

    overdue = []
    for customer in customers:
        last = customer.get("last_followup_date", "").strip()
        if not last:
            overdue.append(f"{customer['dealer_name']}：无最近跟进日期")
            continue
        days = (check_date - datetime.strptime(last, "%Y-%m-%d")).days
        limit = 7 if customer["priority"] == "A" else 14
        if days > limit:
            overdue.append(f"{customer['dealer_name']}：{days} 天未跟进")

    member_rows = []
    team_risks = []
    if coverage_risk:
        team_risks.append("客户资源高度集中在组长，组员成长和覆盖不足")

    for member in MEMBERS:
        summary = summaries[member]
        risk = risk_text(summary, owner_counts[member])
        submitted = "已提交" if summary["submitted"] else "未提交"
        member_rows.append(f"| {member} | {submitted} | {summary['process_rate']}% | 待补充 | {risk} |")
        if risk != "正常":
            team_risks.append(f"{member}：{risk}")

    team_risks.extend(f"客户跟进风险：{item}" for item in overdue)
    if not team_risks:
        team_risks.append("暂无明显风险")

    team_actions = []
    if coverage_risk:
        team_actions.append("从杨晶晶客户池中选择 1-2 个 B/C 类客户转交给王宇彤做维护练习")
        team_actions.append("何海文继续负责 Sidd Senthil，同时新增印度拓客任务")
    team_actions.append("检查所有 A 类客户下一步动作，并补齐最近跟进日期")
    team_actions.append("督促未提交或字段不完整的成员补齐日报")

    team_report = f"""# {TEAM_NAME} {date_text} Check

## 团队概览
- 团队业绩目标：待补充
- 当前完成：待补充
- 完成率：待补充
- 时间进度：待补充
- 状态：{"需关注" if any(item != "暂无明显风险" for item in team_risks) else "正常"}

## 成员完成情况
| 成员 | 日报 | 过程完成率 | 业绩完成率 | 风险 |
|---|---|---:|---:|---|
{chr(10).join(member_rows)}

## 客户资源健康度
- 杨晶晶负责 {owner_counts["杨晶晶"]} 个客户
- 何海文负责 {owner_counts["何海文"]} 个客户
- 王宇彤负责 {owner_counts["王宇彤"]} 个客户
- 组长客户占比：{leader_share}%
- 风险：{"客户资源高度集中在组长，组员成长和覆盖不足" if coverage_risk else "暂无明显资源失衡"}

## 今日风险
{bullet(team_risks)}

## 明日管理动作
{bullet(team_actions)}
"""
    write(check_dir / f"{date_text}_team_check.md", team_report)

    for member in MEMBERS:
        slug = SLUGS[member]
        summary = summaries[member]
        owned = [customer for customer in customers if customer["owner"] == member]
        risk = risk_text(summary, len(owned))
        owned_text = bullet([customer["dealer_name"] for customer in owned]) if owned else "- 暂无"
        missing_text = bullet(summary["missing_fields"]) if summary["missing_fields"] else "- 无"

        metric_rows = "\n".join(
            f"| {key} | {summary['metrics'][key]} | {defaults[key]} |"
            for key in ["新增客户", "有效触达", "客户跟进", "报价", "重点客户维护"]
        )
        personal_report = f"""# {member} {date_text} Check

## 日报状态
- 是否提交：{"已提交" if summary["submitted"] else "未提交"}
- 完整度：{summary["completeness"]}%
- 缺失字段：
{missing_text}

## 过程指标
| 指标 | 实际 | 默认目标 |
|---|---:|---:|
{metric_rows}

## 当前负责客户
{owned_text}

## 风险判断
- {risk}

## 建议
- 补齐日报中的空字段和客户下一步动作。
- 对负责客户确认本月采购计划、报价机会和下次跟进日期。
"""
        write(check_dir / f"{date_text}_{slug}_check.md", personal_report)

        must_do = []
        if not summary["submitted"]:
            must_do.append(f"补交 {date_text} 日报，补齐过程指标、客户动作和明日计划")
        if not owned:
            must_do.append("新增 3 个目标客户线索，并请组长分配 1 个低风险客户做维护练习")
        else:
            for customer in owned[:2]:
                must_do.append(f"跟进 {customer['dealer_name']}，确认本月采购计划和下一步动作")
        must_do.append(f"完成 {defaults['新增客户']} 个新增客户")
        must_do.append(f"完成 {defaults['有效触达']} 次有效触达")
        must_do.append(f"输出 {defaults['报价']} 个报价机会")

        if member == "杨晶晶":
            support = ["安排一次组员日报复盘", "选择 1-2 个 B/C 类客户作为组员维护练习样例"]
        elif member == "何海文":
            support = ["请杨晶晶提供 2 个印度老客户跟进样例", "安排一次报价转化辅导"]
        else:
            support = ["请杨晶晶分配 1 个低风险客户做维护练习", "安排一次新客户开发话术辅导"]

        action_report = f"""# {member} {next_day} 行动建议

## 必做
{bullet(must_do)}

## 组长支持
{bullet(support)}

## 风险提醒
- {risk}
"""
        write(action_dir / f"{next_day}_{slug}_actions.md", action_report)

    leader_action = f"""# 杨晶晶 {next_day} 管理动作

## 客户资源调整建议
- 从杨晶晶客户池中选择 1-2 个 B/C 类客户转交给王宇彤做维护练习。
- 何海文继续负责 Sidd Senthil，同时新增印度拓客任务。
- 保留 LLC “TC Azimut” 和 Altyn Zaman H.J. 为 A 类重点客户，每周至少 2 次有效维护。

## 辅导动作
- 何海文：辅导报价跟进和印度客户开发。
- 王宇彤：建立客户池，先从新客户开发和低风险老客户维护开始。
- 团队：统一日报填写口径，要求每个客户动作都有下一步和下次跟进日期。

## 风险提醒
{bullet(team_risks)}
"""
    write(action_dir / f"{next_day}_team_leader_actions.md", leader_action)

    print(f"Generated reports for {TEAM_NAME} on {date_text}")
    print(f"Team check: {check_dir / f'{date_text}_team_check.md'}")
    print(f"Actions: {action_dir}")


def main():
    parser = argparse.ArgumentParser(description="Generate daily PDCA check reports for a dealer team.")
    parser.add_argument("--team-path", default=r"D:\经销商PDCA\teams\yang-jingjing")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    args = parser.parse_args()
    generate(args.team_path, args.date)


if __name__ == "__main__":
    main()
