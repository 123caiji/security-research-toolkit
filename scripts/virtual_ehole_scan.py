# -*- coding: utf-8 -*-
"""纯本地模拟指纹输出，不发起任何网络请求。"""
import json
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

SRC = cfg.get("virtual_source", "local_virtual_no_network")
target_path = ROOT / Path(cfg["target_file"])
out_path = ROOT / Path(cfg["scan_result_dir"]) / "ehole_fingerprint_sim.json"

# 虚构主机 -> (服务类型代号, 默认优先级)
HOST_PROFILE: dict[str, tuple[str, str]] = {
    "127.0.0.1": ("T01", "P2"),
    "10.0.0.1": ("T02", "P0"),
    "10.0.0.2": ("T03", "P1"),
    "10.0.0.3": ("T04", "P2"),
    "10.0.0.4": ("T05", "P3"),
}

PORT_DEFAULT: dict[int, tuple[str, str]] = {
    80: ("T04", "P2"),
    443: ("T04", "P2"),
    8080: ("T03", "P1"),
    8765: ("T01", "P2"),
    22: ("T02", "P0"),
    8000: ("T03", "P1"),
}

META_BY_TYPE: dict[str, Tuple[str, int, int, str]] = {
    "T01": ("http-demo/1.0", 200, 512, "demo-page"),
    "T02": ("mgmt-demo/1.0", 200, 1024, ""),
    "T03": ("app-demo/1.0", 200, 2048, ""),
    "T04": ("static-demo/1.0", 200, 1536, ""),
    "T05": ("svc-demo/1.0", 200, 768, ""),
    "T00": ("unknown-demo/1.0", 200, 555, ""),
}


def _resolve_profile(host: str, port: int) -> tuple[str, str]:
    if host in HOST_PROFILE:
        return HOST_PROFILE[host]
    return PORT_DEFAULT.get(port, ("T00", "P3"))


results = []
with open(target_path, "r", encoding="utf-8") as f:
    urls = [u.strip() for u in f.readlines() if u.strip() and not u.strip().startswith("#")]

for url in urls:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    service_type, priority = _resolve_profile(host, port)
    server, statuscode, length, title = META_BY_TYPE.get(service_type, META_BY_TYPE["T00"])
    results.append(
        {
            "url": url,
            "host": host,
            "port": port,
            "service_type": service_type,
            "priority_hint": priority,
            "server": server,
            "statuscode": statuscode,
            "length": length,
            "title": title,
            "_simulation": True,
            "_source": SRC,
        }
    )

out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"[OK] 虚拟指纹扫描完成，输出：{out_path}")
