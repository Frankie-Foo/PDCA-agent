# -*- coding: utf-8 -*-
import argparse
import csv
import re
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from difflib import SequenceMatcher


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


def parse_customer_actions(log_path):
    """从日报的客户动作表中解析每行记录，返回列表。

    @returns {list[dict]} 每条记录包含 customer/action/result/next_step/next_followup_date
    """
    if not log_path.exists():
        return []
    lines = read_lines(log_path)
    actions = []
    in_table = False
    header_passed = False
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not in_table:
            # 识别表头行（含"客户"列）
            if any("客户" in c for c in cells):
                in_table = True
                header_passed = False
            continue
        if not header_passed:
            # 跳过分隔行 |---|---|...|
            header_passed = True
            continue
        if len(cells) < 5:
            continue
        customer, action, result, next_step, next_date = cells[0], cells[1], cells[2], cells[3], cells[4]
        if not customer:
            continue
        actions.append({
            "customer": customer,
            "action": action,
            "result": result,
            "next_step": next_step,
            "next_followup_date": next_date,
        })
    return actions


def fuzzy_match(name, candidates, threshold=0.6):
    """模糊匹配客户名称，返回最佳匹配的候选项或 None。

    @param {str} name - 日报中填写的客户名
    @param {list[str]} candidates - customers.csv 中的正式名称列表
    @param {float} threshold - 相似度阈值
    @returns {str|None} 最佳匹配的正式客户名，若无匹配则返回 None
    """
    best_ratio = 0.0
    best_match = None
    name_lower = name.lower()
    for candidate in candidates:
        # 先尝试包含关系（优先级高于相似度）
        if name_lower in candidate.lower() or candidate.lower() in name_lower:
            return candidate
        ratio = SequenceMatcher(None, name_lower, candidate.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = candidate
    return best_match if best_ratio >= threshold else None


def generate_writeback_list(team_path, date_text, customers, summaries):
    """解析各成员日报客户动作表，生成待回写 customers.csv 的建议清单。

    @param {Path} team_path - 小组根目录
    @param {str} date_text - 检查日期 YYYY-MM-DD
    @param {list[dict]} customers - customers.csv 行列表
    @param {dict} summaries - 各成员日报摘要（用于判断是否有日报）
    @returns {str} 待回写清单 Markdown 文本
    """
    customer_names = [c["dealer_name"] for c in customers]
    rows_matched = []
    rows_unmatched = []

    for member in MEMBERS:
        if not summaries[member]["submitted"]:
            continue
        slug = SLUGS[member]
        log_path = team_path / "daily_logs" / slug / f"{date_text}.md"
        actions = parse_customer_actions(log_path)
        for act in actions:
            matched = fuzzy_match(act["customer"], customer_names)
            row = {
                "member": member,
                "log_customer": act["customer"],
                "matched_customer": matched,
                "action": act["action"],
                "result": act["result"],
                "next_step": act["next_step"],
                "next_followup_date": act["next_followup_date"],
            }
            if matched:
                rows_matched.append(row)
            else:
                rows_unmatched.append(row)

    lines = [f"# 客户跟进回写清单 {date_text}", ""]
    lines.append("根据各成员 " + date_text + " 日报自动生成，建议核实后手动更新 `customers.csv`。")
    lines.append("")

    if rows_matched:
        lines.append("## 可回写记录（已匹配 customers.csv）")
        lines.append("")
        lines.append("| 负责人 | 日报客户名 | 匹配正式名 | 跟进动作 | 下一步 | 建议回写日期 |")
        lines.append("|---|---|---|---|---|---|")
        for r in rows_matched:
            lines.append(
                f"| {r['member']} | {r['log_customer']} | {r['matched_customer']} "
                f"| {r['action']} | {r['next_step']} | {r['next_followup_date']} |"
            )
        lines.append("")
        lines.append(
            "> **操作**：将上表【匹配正式名】行的 `last_followup_date` 更新为 "
            f"`{date_text}`，`next_action` 更新为【下一步】列内容。"
        )
    else:
        lines.append("## 可回写记录")
        lines.append("")
        lines.append("_今日日报中无可匹配的客户动作记录。_")

    lines.append("")

    if rows_unmatched:
        lines.append("## 未匹配记录（需人工确认）")
        lines.append("")
        lines.append("| 负责人 | 日报客户名 | 跟进动作 | 下一步 | 备注 |")
        lines.append("|---|---|---|---|---|")
        for r in rows_unmatched:
            lines.append(
                f"| {r['member']} | {r['log_customer']} | {r['action']} "
                f"| {r['next_step']} | 请确认是否为新客户，若是则补录至 customers.csv |"
            )

    return "\n".join(lines)


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

    writeback_text = generate_writeback_list(team_path, date_text, customers, summaries)
    writeback_path = action_dir / f"{date_text}_customer_writeback.md"
    write(writeback_path, writeback_text)

    print(f"Generated reports for {TEAM_NAME} on {date_text}")
    print(f"Team check: {check_dir / f'{date_text}_team_check.md'}")
    print(f"Actions: {action_dir}")
    print(f"Writeback list: {writeback_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate daily PDCA check reports for a dealer team.")
    parser.add_argument("--team-path", default=r"D:\经销商PDCA\teams\yang-jingjing")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    args = parser.parse_args()
    generate(args.team_path, args.date)


if __name__ == "__main__":
    main()
