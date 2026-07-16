# -*- coding: utf-8 -*-
"""Register the card workflow AI page in the local toolbox config."""
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    tools_file = root / "config" / "tools.json"
    tools = json.loads(tools_file.read_text(encoding="utf-8")) if tools_file.exists() else []
    entry = {
        "name": "卡片式工作流审核自动任务规划系统",
        "category": "网页工具",
        "type": "网页",
        "description": "本地运行的 AI 卡片识别、自动分类、派单、优先级排序、审核流转和预警看板。",
        "weight": 0,
        "path": "",
        "params": "",
        "url": "http://127.0.0.1:8788/",
        "tags": ["workflow", "card", "ai", "local"],
        "group": "AI自动化"
    }
    tools = [t for t in tools if t.get("name") != entry["name"]]
    tools.insert(0, entry)
    tools_file.write_text(json.dumps(tools, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[OK] registered card workflow AI tool")


if __name__ == "__main__":
    main()
