# -*- coding: utf-8 -*-
"""
依次执行教学六阶段流水线 +（若允许）真实 HTTP 探测，
并将 config / web_targets 快照与本轮相关 JSON、报告复制到同一目录：

  data/run_outputs/Bundle_<时间戳>/

索引：同目录 RUN_INDEX.md
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"

GLOB_PATTERNS = (
    "teach_phase*.json",
    "ehole_fingerprint_sim.json",
    "weakpass_sim.json",
    "risk_judge_sim.json",
)


def main() -> None:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle = ROOT / "data" / "run_outputs" / f"Bundle_{stamp}"
    bundle.mkdir(parents=True, exist_ok=True)
    scan_dir = ROOT / Path(cfg["scan_result_dir"])
    report_dir = ROOT / Path(cfg["report_dir"])
    target_path = ROOT / Path(cfg["target_file"])
    root_report = ROOT / Path(cfg.get("report_file", "data/reports/simulation_report.md"))

    shutil.copy2(CONFIG_PATH, bundle / "config_snapshot.json")
    if target_path.is_file():
        shutil.copy2(target_path, bundle / "targets_snapshot.txt")

    print(f"[RUN] 汇总目录：{bundle}", flush=True)

    r1 = subprocess.run(
        [sys.executable, str(SCRIPTS / "teach_six_phase_simulation_run.py")],
        cwd=str(ROOT),
    )
    if r1.returncode != 0:
        print(f"[FAIL] teach_six_phase_simulation_run 退出码 {r1.returncode}", flush=True)
        sys.exit(r1.returncode)

    print("[SKIP] 真实 HTTP 探测已禁用（仅本地模拟）", flush=True)

    dest_scan = bundle / "scan_results"
    dest_scan.mkdir(parents=True, exist_ok=True)
    for pat in GLOB_PATTERNS:
        for p in sorted(scan_dir.glob(pat)):
            if p.is_file():
                shutil.copy2(p, dest_scan / p.name)

    dest_rep = bundle / "reports"
    dest_rep.mkdir(parents=True, exist_ok=True)
    for p in sorted(report_dir.glob("teach_six_phase_simulation_*.md")):
        shutil.copy2(p, dest_rep / p.name)

    if root_report.is_file():
        shutil.copy2(root_report, bundle / root_report.name)

    index_lines = [
        "# 本轮运行输出索引",
        "",
        f"- **生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **汇总根目录**：`{bundle}`",
        "",
        "## 已执行步骤",
        "",
        f"1. `scripts/teach_six_phase_simulation_run.py`",
        f"2. 真实 HTTP 探测（本工程已禁用）",
        "",
        "## 本 Bundle 内文件（相对路径）",
        "",
    ]
    files_sorted = sorted(
        [p for p in bundle.rglob("*") if p.is_file() and p.name != "RUN_INDEX.md"],
        key=lambda x: str(x.relative_to(bundle)),
    )
    for fp in files_sorted:
        sub = fp.relative_to(bundle).as_posix()
        index_lines.append(f"- `{sub}` — {fp.stat().st_size} bytes")
    index_lines.extend(
        [
            "",
            "## 源目录",
            "",
            f"- `{scan_dir.relative_to(ROOT)}`",
            f"- `{report_dir.relative_to(ROOT)}`",
            "",
        ]
    )
    (bundle / "RUN_INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")

    # 镜像到仅 ASCII 路径，避免 Cursor 对「中文目录 + 文件夹名」解析失败
    exports_root = ROOT / "exports"
    mirror = exports_root / f"Bundle_{stamp}"
    if mirror.exists():
        shutil.rmtree(mirror)
    shutil.copytree(bundle, mirror)
    (exports_root / "README_open_here.txt").write_text(
        "在 Cursor 里请用「打开文件」打开本目录下的 RUN_INDEX.md，\n"
        "不要尝试把 Bundle_ 文件夹当成单个文件标签打开。\n"
        f"镜像源（中文路径）：{bundle}\n",
        encoding="utf-8",
    )
    index_mirror_note = (
        f"\n## ASCII 镜像路径（推荐在 Cursor 中从此处打开）\n\n"
        f"- `{mirror}`\n"
        f"- 同内容副本，避免 URI 编码中文路径导致 Unable to resolve resource。\n"
    )
    (mirror / "RUN_INDEX.md").write_text(
        (bundle / "RUN_INDEX.md").read_text(encoding="utf-8") + index_mirror_note,
        encoding="utf-8",
    )

    print(f"\n[OK] 全部输出已汇总到：{bundle}", flush=True)
    print(f"     打开索引：{bundle / 'RUN_INDEX.md'}", flush=True)
    print(f"     ASCII 镜像：{mirror / 'RUN_INDEX.md'}", flush=True)


if __name__ == "__main__":
    main()
