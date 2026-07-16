# -*- coding: utf-8 -*-
"""纯本地模拟凭证占位研判，不发起任何网络请求。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

SRC = cfg.get("virtual_source", "local_virtual_no_network")

finger_file = ROOT / Path(cfg["scan_result_dir"]) / "ehole_fingerprint_sim.json"
out_path = ROOT / Path(cfg["scan_result_dir"]) / "weakpass_sim.json"

PLACEHOLDER_CREDENTIALS: dict[str, list[str]] = {
    "T01": ["占位条目-无", "占位条目-自定义"],
    "T02": ["占位组合-A", "占位组合-B"],
    "T03": ["占位组合-C", "占位组合-D"],
    "T04": ["占位条目-无", "占位组合-E"],
    "T05": ["占位条目-无", "占位组合-F"],
    "T00": ["未配置"],
}

with open(finger_file, "r", encoding="utf-8") as f:
    finger_data = json.load(f)

weak_results = []
for item in finger_data:
    host = item.get("host") or item.get("ip", "")
    port = item["port"]
    service_type = item.get("service_type") or item.get("cms", "T00")
    creds = PLACEHOLDER_CREDENTIALS.get(service_type, ["未配置"])
    flagged = host == "10.0.0.1"
    weak_results.append(
        {
            "host": host,
            "port": port,
            "service_type": service_type,
            "placeholder_credentials": creds,
            "flagged": flagged,
            "_simulation": True,
            "_source": SRC,
        }
    )

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(weak_results, f, ensure_ascii=False, indent=2)

print(f"[OK] 虚拟凭证占位研判完成，输出：{out_path}")
