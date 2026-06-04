# -*- coding: utf-8 -*-
"""一次性：从桌面对标目录复制 Walk-in 驾驶舱到 modules/walkin_cockpit。"""
import json
import shutil
from pathlib import Path

SRC = Path(r"c:\Users\frank\Desktop\海外PDCA\对标\线下事业部walk in模块驾驶舱.html")
DST = Path(__file__).resolve().parents[1] / "modules" / "walkin_cockpit"

def main():
    if not SRC.exists():
        raise SystemExit(f"源文件不存在: {SRC}")
    (DST / "scripts").mkdir(parents=True, exist_ok=True)
    (DST / "data").mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC, DST / "index.html")
    (DST / "scripts" / "walkin-shanghai-guojin-teams.json").write_text(
        json.dumps({"hanTeamUserIds": [], "liuTeamUserIds": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    (DST / "scripts" / "walkin-guojin-browser.js").write_text(
        "// placeholder：国金拆店同步脚本（对标页同路径）\n",
        encoding="utf-8",
    )
    print("copied", DST / "index.html", (DST / "index.html").stat().st_size, "bytes")


if __name__ == "__main__":
    main()
