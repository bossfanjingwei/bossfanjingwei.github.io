#!/usr/bin/env python3
"""Append today's brief into the archive site and push.

Usage: python3 add_entry.py /tmp/brief.json /tmp/brief.png
Reads date from system clock (Asia/Shanghai).
"""
import datetime
import json
import shutil
import subprocess
import sys

SITE = "/root/.openclaw/workspace/site-archive"
WD = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def main():
    brief_path, png_path = sys.argv[1], sys.argv[2]
    brief = json.load(open(brief_path, encoding="utf-8"))

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    date = now.strftime("%Y-%m-%d")
    weekday = WD[now.weekday()]

    img_rel = f"images/{date}.png"
    shutil.copy(png_path, f"{SITE}/{img_rel}")

    entry = {
        "date": date,
        "weekday": weekday,
        "weekday_label": brief.get("weekday", ""),
        "overview": brief.get("overview", ""),
        "sections": brief.get("sections", []),
        "thought": brief.get("thought", ""),
        "note": brief.get("note", ""),
        "sign": brief.get("sign", ""),
        "image": img_rel,
        "quotes": [],
    }

    entries_file = f"{SITE}/entries.js"
    raw = open(entries_file, encoding="utf-8").read().strip()
    data = json.loads(raw.removeprefix("const ENTRIES = ").removesuffix(";"))
    data = [e for e in data if e.get("date") != date]  # 去重：同一天覆盖
    data.append(entry)
    with open(entries_file, "w", encoding="utf-8") as f:
        f.write("const ENTRIES = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")

    subprocess.run(["git", "-C", SITE, "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", SITE, "-c", "user.name=bossfanjingwei",
         "-c", "user.email=bossfanjingwei@users.noreply.github.com",
         "commit", "-q", "-m", f"早报归档 {date}"],
        check=True,
    )
    subprocess.run(["git", "-C", SITE, "push", "-q", "origin", "main"], check=True)
    print(f"archived {date} -> https://bossfanjingwei.github.io/")


if __name__ == "__main__":
    main()
