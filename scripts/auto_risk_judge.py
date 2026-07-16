# -*- coding: utf-8 -*-
"""合并指纹与凭证占位结果，本地生成优先级研判 JSON（无网络）。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

SRC = cfg.get("virtual_source", "local_virtual_no_network")
finger_file = ROOT / Path(cfg["scan_result_dir"]) / "ehole_fingerprint_sim.json"
weak_file = ROOT / Path(cfg["scan_result_dir"]) / "weakpass_sim.json"
out_path = ROOT / Path(cfg["scan_result_dir"]) / "risk_judge_sim.json"

with open(finger_file, "r", encoding="utf-8") as f:
    finger = json.load(f)
with open(weak_file, "r", encoding="utf-8") as f:
    weak = json.load(f)

if len(finger) != len(weak):
    raise ValueError("指纹与凭证占位条数不一致，请重新运行前两步脚本")

rules = cfg.get("priority_rules", {})
judge_results = []

for f_item, w_item in zip(finger, weak):
    host = f_item.get("host") or f_item.get("ip", "")
    port = f_item["port"]
    service_type = f_item.get("service_type") or f_item.get("cms", "T00")
    priority = f_item.get("priority_hint", "P3")
    flagged = w_item.get("flagged", w_item.get("sim_suspected", False))
    note = rules.get(priority, "占位说明")
    if flagged:
        note = f"{note} / 教学标记"

    judge_results.append(
        {
            "host": host,
            "port": port,
            "service_type": service_type,
            "priority": priority,
            "risk_note": f"本地模拟：{note}",
            "flagged": flagged,
            "_simulation": True,
            "_source": SRC,
        }
    )

out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(judge_results, f, ensure_ascii=False, indent=2)

print(f"[OK] 自动优先级研判完成，输出：{out_path}")
