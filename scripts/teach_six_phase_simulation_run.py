# -*- coding: utf-8 -*-
"""
教学用：六阶段全流程本地模拟（无真实网络、无外部探测）。

阶段映射
  1 信息收集 — 仅读取 config 与 target_file 文本，生成 JSON 占位
  2 虚拟扫描 — 调用 virtual_ehole_scan + virtual_weakpass_scan + auto_risk_judge（均无 socket）
  3 场景占位 — 仅根据上步 JSON 生成叙事占位 JSON
  4 后续占位 — 本地叙事 JSON
  5 收尾占位 — 本地叙事 JSON
  6 生成报告 — 写入 data/reports/teach_six_phase_simulation_<时间>.md，并追加 auto_report_generate 总报告

约束：不执行 auto_cleanup（避免静默删缓存）；不发起 DNS/HTTP。
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"


def run_child(name: str) -> None:
    path = SCRIPTS / name
    print(f"\n>> [子进程] {name}", flush=True)
    r = subprocess.run([sys.executable, str(path)], cwd=str(ROOT))
    if r.returncode != 0:
        print(f"[FAIL] {name} 退出码 {r.returncode}", flush=True)
        sys.exit(r.returncode)


def main() -> None:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    src = cfg.get("virtual_source", "local_virtual_no_network")
    scan_dir = ROOT / Path(cfg["scan_result_dir"])
    report_dir = ROOT / Path(cfg.get("report_dir", "data/reports"))
    scan_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    target_path = ROOT / Path(cfg["target_file"])
    lines = [
        ln.strip()
        for ln in target_path.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    phase1 = {
        "phase": 1,
        "title": "信息收集（本地模拟）",
        "collected_at": now,
        "target_file": str(cfg["target_file"]),
        "virtual_rows": len(lines),
        "targets_preview": lines[:20],
        "_simulation": True,
        "_source": src,
        "note": "仅从工程内文本读取目标列表，未对任何主机发起连接或扫描。",
    }
    p1_path = scan_dir / "teach_phase1_info_gather_sim.json"
    p1_path.write_text(json.dumps(phase1, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 阶段1 输出：{p1_path.relative_to(ROOT)}")

    print("\n>> 阶段2：虚拟指纹 + 凭证占位 + 研判", flush=True)
    run_child("virtual_ehole_scan.py")
    run_child("virtual_weakpass_scan.py")
    run_child("auto_risk_judge.py")

    finger_path = scan_dir / "ehole_fingerprint_sim.json"
    weak_path = scan_dir / "weakpass_sim.json"
    judge_path = scan_dir / "risk_judge_sim.json"
    finger = json.loads(finger_path.read_text(encoding="utf-8"))
    weak = json.loads(weak_path.read_text(encoding="utf-8"))
    judge = json.loads(judge_path.read_text(encoding="utf-8"))

    phase3 = {
        "phase": 3,
        "title": "场景占位（未执行任何外部操作）",
        "scenarios": [
            {
                "id": "SCN_01",
                "description": "高优先级条目的理论核查步骤（仅占位，不演示真实命令）。",
                "tied_to_priority": "P0",
            },
            {
                "id": "SCN_02",
                "description": "中优先级条目的方法论说明（仅占位，不对外发包）。",
                "tied_to_priority": "P1",
            },
        ],
        "based_on_entries": len(judge),
        "_simulation": True,
        "_source": src,
    }
    p3_path = scan_dir / "teach_phase3_scenario_sim.json"
    p3_path.write_text(json.dumps(phase3, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 阶段3 输出：{p3_path.relative_to(ROOT)}")

    phase4 = {
        "phase": 4,
        "title": "后续流程占位",
        "items": [
            "拓扑推断：仅课堂讨论，无真实探测。",
            "凭据相关话题：本阶段不调用任何外部工具。",
            "横向话题：不在本脚本中实现或指导。",
        ],
        "_simulation": True,
        "_source": src,
    }
    p4_path = scan_dir / "teach_phase4_followup_sim.json"
    p4_path.write_text(json.dumps(phase4, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 阶段4 输出：{p4_path.relative_to(ROOT)}")

    phase5 = {
        "phase": 5,
        "title": "收尾占位",
        "items": [
            "讲解常见风险类别（仅占位说明，不生成任何样本文件）。",
            "检测与清理思路：日志、完整性校验、最小权限。",
        ],
        "_simulation": True,
        "_source": src,
    }
    p5_path = scan_dir / "teach_phase5_wrapup_sim.json"
    p5_path.write_text(json.dumps(phase5, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 阶段5 输出：{p5_path.relative_to(ROOT)}")

    report_md = report_dir / f"teach_six_phase_simulation_{stamp}.md"
    lines_md = [
        "# 六阶段本地模拟报告",
        "",
        f"> 生成时间：`{now}`  |  `_simulation: true`  |  `_source: {src}`",
        "> **声明**：未对外网或内网发起扫描；所有条目均为本地虚构数据。",
        "",
        "## 阶段 1 — 信息收集",
        "",
        f"- 输出：`{p1_path.relative_to(ROOT)}`",
        f"- 自 `{cfg['target_file']}` 读取 **{len(lines)}** 条占位目标（无连接）。",
        "",
        "## 阶段 2 — 虚拟扫描",
        "",
        f"- `ehole_fingerprint_sim.json`：{len(finger)} 条",
        f"- `weakpass_sim.json`：{len(weak)} 条",
        f"- `risk_judge_sim.json`：{len(judge)} 条",
        "",
        "## 阶段 3 — 场景占位",
        "",
        f"- 输出：`{p3_path.relative_to(ROOT)}`",
        "",
        "## 阶段 4 — 后续占位",
        "",
        f"- 输出：`{p4_path.relative_to(ROOT)}`",
        "",
        "## 阶段 5 — 收尾占位",
        "",
        f"- 输出：`{p5_path.relative_to(ROOT)}`",
        "",
        "## 阶段 6 — 与工程总报告对接",
        "",
        f"- 下一步子进程将执行 `auto_report_generate.py`，向 `{cfg.get('report_file', 'data/reports/simulation_report.md')}` **追加**本轮摘要。",
        "",
        "### 研判摘要（本地数据）",
        "",
        "| 主机 | 端口 | 服务类型 | 优先级 |",
        "|------|------|----------|--------|",
    ]
    for j in judge[:15]:
        lines_md.append(
            f"| {j.get('host', '')} | {j.get('port', '')} | {j.get('service_type', '')} | {j.get('priority', '')} |"
        )
    if len(judge) > 15:
        lines_md.append(f"\n（共 {len(judge)} 条，表内仅列前 15 条。）")

    report_md.write_text("\n".join(lines_md) + "\n", encoding="utf-8")
    print(f"[OK] 阶段6 主报告：{report_md.relative_to(ROOT)}")

    run_child("auto_report_generate.py")

    root_report = ROOT / cfg.get("report_file", "data/reports/simulation_report.md")
    print("\n" + "=" * 60, flush=True)
    print("[完成] 六阶段本地模拟已结束。", flush=True)
    print(f"  主报告（本流程）：{report_md}", flush=True)
    print(f"  追加总报告：      {root_report}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
