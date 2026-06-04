# -*- coding: utf-8 -*-
"""从 online_cockpit/index.html 导出渠道/OKR 参考 JSON（一次性，日常只读 JSON）。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "modules" / "online_cockpit" / "index.html"
OUT = ROOT / "modules" / "walkin_cockpit" / "data" / "online_channel_reference.json"


def js_object_to_json(text: str) -> str:
    """将 BASE / OKR 等 JS 对象字面量转为 JSON。"""
    out = []
    i = 0
    n = len(text)
    in_str = False
    quote = ""
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                i += 1
                out.append(text[i])
            elif ch == quote:
                in_str = False
            i += 1
            continue
        if ch in "\"'":
            in_str = True
            quote = ch
            out.append(ch)
            i += 1
            continue
        if ch.isalpha() or ch == "_":
            j = i
            while j < n and (text[j].isalnum() or text[j] == "_"):
                j += 1
            key = text[i:j]
            k = j
            while k < n and text[k].isspace():
                k += 1
            if k < n and text[k] == ":":
                out.append('"')
                out.append(key)
                out.append('":')
                i = k + 1
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    base_m = re.search(r"var BASE = (\[[\s\S]*?\]);", text)
    okr_m = re.search(r"var OKR_BY_MONTH = (\{[\s\S]*?\});", text)
    if not base_m or not okr_m:
        if OUT.is_file():
            print("skip: online index 已改为跳转页，保留现有", OUT)
            return
        raise SystemExit("无法在 online_cockpit/index.html 中定位 BASE 或 OKR_BY_MONTH")

    stores = json.loads(js_object_to_json(base_m.group(1)))
    okr = json.loads(js_object_to_json(okr_m.group(1)))
    keep = ("rg", "nm", "mgr", "hk", "Ls", "Ll", "Lo", "sal", "yk", "sv", "lv")
    payload = {
        "note": "参考线下事业部渠道线索表结构与 online 驾驶舱 BASE；Walk-in 只读此 JSON，不读 xlsx。",
        "estRatio": 4,
        "channelLabels": ["短视频", "直播", "其他"],
        "regionOrder": ["北区", "西区", "东区", "南区"],
        "okrByMonth": okr,
        "stores": [{k: row[k] for k in keep if k in row} for row in stores],
        "scaleByMonth": {
            "2026-05": 1,
            "2026-06": 0.35,
            "2026-04": 0.93,
            "2026-03": 0.88,
            "2026-02": 0.84,
            "2026-01": 0.81,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT, "stores", len(payload["stores"]))


if __name__ == "__main__":
    main()
