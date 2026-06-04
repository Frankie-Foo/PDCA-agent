# -*- coding: utf-8 -*-
"""
【可选、一次性】从桌面 xlsx 重新汇总越南指标，写入 vietnam_store_metrics.json。
日常构建请用 build_walkin_bundle.py，驾驶舱不读 Excel。
"""
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("需要 openpyxl: pip install openpyxl")

XLSX = Path(r"c:\Users\frank\Desktop\越南门店数据.xlsx")
OUT = Path(__file__).resolve().parents[1] / "modules" / "walkin_cockpit" / "data" / "vietnam_store_metrics.json"

def _num(v):
    try:
        return float(v) if v not in (None, "") else 0.0
    except (TypeError, ValueError):
        return 0.0

def _month_key(dt):
    return dt.strftime("%Y-%m") if isinstance(dt, datetime) else str(dt)[:7]

def aggregate(rows, ym):
    month_rows = [r for r in rows if _month_key(r[0]) == ym]
    if not month_rows:
        return None
    days = len(month_rows)
    instore = sum(_num(r[2]) for r in month_rows)
    touch = sum(_num(r[10]) for r in month_rows)
    contact = sum(_num(r[15]) for r in month_rows)
    order = sum(_num(r[16]) for r in month_rows)
    introduce = sum(_num(r[4]) for r in month_rows)
    scale = 30.0 / max(days, 1)
    visit_groups = max(1, int(round(instore * scale)))
    add_rate = min(0.95, contact / instore) if instore > 0 else 0.35
    touch_rate = min(0.95, touch / instore) if instore > 0 else 0.5
    use_rate = min(0.95, sum(_num(r[3]) for r in month_rows) / instore * scale) if instore > 0 else 0.4
    deal_groups = max(0, int(round(order * scale)))
    walkin_people = max(visit_groups, int(round(visit_groups * 1.66)))
    sales_amount = int(deal_groups * 38000) if deal_groups else int(visit_groups * add_rate * 28000)
    return {
        "name": "胡志明 Walk-in 旗舰店",
        "city": "胡志明",
        "region": "越南区",
        "class": "Class 1",
        "totalVisitGroups": visit_groups,
        "avgAddRate": round(add_rate, 3),
        "totalSalesAmount": sales_amount,
        "anomalies": [] if add_rate >= 0.35 else ["添加率低"],
        "avgTouchRate": round(touch_rate, 3),
        "avgUseRate": round(use_rate, 3),
        "walkinPeople": walkin_people,
        "wechatAddCount": max(0, int(round(contact * scale))),
        "dealGroups": deal_groups,
        "touchCount": max(0, int(round(touch * scale))),
        "useCount": max(0, int(round(introduce * scale))),
        "effectiveCustomers": max(0, int(round(walkin_people * 0.41))),
        "effectiveAdded": max(0, int(round(walkin_people * 0.41 * 0.79))),
    }

def main():
    if not XLSX.exists():
        sys.exit(f"找不到: {XLSX}")
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    rows = [r for r in wb.active.iter_rows(values_only=True)][3:]
    wb.close()
    rows = [r for r in rows if r and r[0]]
    months = sorted({_month_key(r[0]) for r in rows})
    payload = {
        "note": "参考用户提供的越南门店 Excel 汇总结果，已固化为 JSON。驾驶舱与构建脚本只读此文件，不读取、不操作 xlsx。",
        "storeId": "vn1",
        "months": {ym: aggregate(rows, ym) for ym in months},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("written", OUT, "months", months)

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", type=Path, default=XLSX)
    ns = ap.parse_args()
    if ns.xlsx.is_file():
        XLSX = ns.xlsx
    main()
