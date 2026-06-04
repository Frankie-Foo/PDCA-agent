# -*- coding: utf-8 -*-
"""
工作台数据解析：VPS(vertu CLI) > Excel 固化 JSON > mock。

供 pdca_workbench /api/walkin 与 sync_workbench_data 使用。
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSPACE.parents[1]
DATA_SOURCES = WORKSPACE / "config" / "data_sources.json"
DATA_RAW = REPO_ROOT / "data_raw"
WALKIN_DATA = WORKSPACE / "modules" / "walkin_cockpit" / "data"
BUILD_WALKIN = WORKSPACE / "scripts" / "build_walkin_bundle.py"
VN_METRICS = WALKIN_DATA / "vietnam_store_metrics.json"
VN_COLLECT = WALKIN_DATA / "vn_data_collect_reference.json"
DEFAULT_VN_XLSX = Path(r"c:\Users\frank\Desktop\越南门店数据.xlsx")
DEFAULT_COLLECT_XLSX = Path(r"c:\Users\frank\Desktop\Data collecet(5).xlsx")


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def load_data_sources() -> dict:
    payload = _read_json(DATA_SOURCES)
    return payload if isinstance(payload, dict) else {}


def resolve_vps_sales_json(date_text: str) -> tuple[Path | None, str]:
    """按检查日匹配 data_raw 下 VPS 经销商业绩 JSON。"""
    cfg = load_data_sources()
    configured = (cfg.get("sales_json") or "").strip()
    if configured:
        p = Path(configured)
        if p.is_file():
            return p, "config/data_sources.json"

    if not DATA_RAW.is_dir():
        return None, ""

    ym = date_text[:7] if date_text else ""
    candidates = sorted(
        DATA_RAW.glob(f"dealer_sales_month_to_date_*{date_text}*.json"),
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )
    if not candidates and ym:
        candidates = sorted(
            DATA_RAW.glob(f"dealer_sales_month_to_date_{ym}*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )
    if not candidates:
        candidates = sorted(
            DATA_RAW.glob("dealer_sales_month_to_date_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )
    if candidates:
        return candidates[0], candidates[0].name
    return None, ""


def vps_performance_wan(date_text: str) -> tuple[float | None, str]:
    path, label = resolve_vps_sales_json(date_text)
    if not path:
        return None, ""
    payload = _read_json(path)
    if not payload:
        return None, label
    result = (payload.get("execution") or {}).get("result") or payload
    teams = result.get("team_summary") or []
    total = sum(float(t.get("performance") or 0) for t in teams)
    if total <= 0:
        return None, label
    return round(total / 10000, 2), label


def walkin_bundle_path(month: str) -> Path:
    return WALKIN_DATA / f"walkin-{month}.json"


def ensure_walkin_bundle(month: str) -> Path | None:
    out = walkin_bundle_path(month)
    if out.is_file():
        return out
    if not BUILD_WALKIN.is_file():
        return None
    try:
        subprocess.run(
            [sys.executable, str(BUILD_WALKIN), "--month", month],
            cwd=str(WORKSPACE),
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None
    return out if out.is_file() else None


def excel_reference_flags() -> list[str]:
    flags = []
    if VN_METRICS.is_file():
        flags.append("excel_vietnam_store")
    if VN_COLLECT.is_file():
        flags.append("excel_data_collect")
    return flags


def format_source_detail(sources: list[str], month: str, date_text: str, vps_file: str) -> str:
    parts = []
    if "vps" in sources:
        parts.append(f"VPS 业绩（{vps_file or 'data_raw'}）")
    if "excel_vietnam_store" in sources or "excel_data_collect" in sources:
        parts.append("Excel 固化（越南门店数据 + Data collecet(5)）")
    if "walkin_json" in sources:
        parts.append(f"客流包 walkin-{month}.json")
    if "mock" in sources:
        parts.append("部分指标 mock")
    if not parts:
        parts.append("演示 mock")
    return "数据优先级：vertu CLI → Excel 参考 JSON → mock · " + " · ".join(parts) + f" · 检查日 {date_text}"


def build_walkin_api_payload(month: str, date_text: str) -> dict:
    """
    @param month YYYY-MM
    @param date_text YYYY-MM-DD
    """
    sources: list[str] = []
    excel_flags = excel_reference_flags()
    sources.extend(excel_flags)

    path = ensure_walkin_bundle(month) or walkin_bundle_path(month)
    bundle = _read_json(path) if path and path.is_file() else None

    vps_wan, vps_file = vps_performance_wan(date_text)
    if vps_wan is not None:
        sources.insert(0, "vps")

    if bundle:
        if "walkin_json" not in sources:
            sources.append("walkin_json")
    else:
        sources.append("mock")
        bundle = {
            "meta": {"month": month, "periodLabel": month, "storeCount": 0},
            "stores": [],
            "staff": [],
        }

    meta = bundle.setdefault("meta", {})
    meta["dataSources"] = sources
    meta["dataSourcePriority"] = ["vps", "excel_vietnam_store", "excel_data_collect", "walkin_json", "mock"]
    meta["dataSourceDetail"] = format_source_detail(sources, month, date_text, vps_file)
    if vps_wan is not None:
        meta["vpsMonthPerformanceWan"] = vps_wan
    meta["generatedAt"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    meta["checkDate"] = date_text
    return bundle
