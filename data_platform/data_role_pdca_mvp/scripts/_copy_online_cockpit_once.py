# -*- coding: utf-8 -*-
"""一次性：从桌面对标目录复制「线上模块驾驶舱」到 modules/online_cockpit。"""
import shutil
from pathlib import Path

SRC = Path(r"c:\Users\frank\Desktop\海外PDCA\对标\线下事业部线上模块驾驶舱.html")
DST = Path(__file__).resolve().parents[1] / "modules" / "online_cockpit"


def main():
    if not SRC.exists():
        raise SystemExit(f"源文件不存在: {SRC}")
    DST.mkdir(parents=True, exist_ok=True)
    (DST / "data").mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC, DST / "index.html")
    print("copied", DST / "index.html", (DST / "index.html").stat().st_size, "bytes")


if __name__ == "__main__":
    main()
