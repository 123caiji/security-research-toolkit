# -*- coding: utf-8 -*-
"""将本轮模拟结果追加写入总报告（无网络）。"""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

SRC = cfg.get("virtual_source", "local_virtual_no_network")
scan_dir = ROOT / Path(cfg["scan_result_dir"])
judge_file = scan_dir / "risk_judge_sim.json"
finger_file = scan_dir / "ehole_fingerprint_sim.json"
weak_file = scan_dir / "weakpass_sim.json"
report_rel = cfg.get("report_file", "data/reports/simulation_report.md")
report_file = ROOT / report_rel

with open(judge_file, "r", encoding="utf-8") as f:
    judge_data = json.load(f)
with open(finger_file, "r", encoding="utf-8") as f:
    finger_data = json.load(f)
with open(weak_file, "r", encoding="utf-8") as f:
    weak_data = json.load(f)

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

if report_file.exists():
    body = report_file.read_text(encoding="utf-8")
    round_no = body.count("## 自动全流程") + body.count("## 第") + 1
else:
    round_no = 1
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(
        """# 全自动本地模拟演练 — 总报告

> **说明**：本文件由 `scripts/auto_report_generate.py` 按轮次 **追加** 写入。  
> **强制规则**：`config.json` 中 `simulation_mode` / `forbid_real_network`；所有 JSON 含 `_simulation: true`、`_source: """
        + SRC
        + """`。

---

""",
        encoding="utf-8",
    )

report_content = f"""
## 自动全流程本地模拟演练（第 {round_no} 轮 · {now}）

> **附加声明**：`data/targets.txt` 仅作模拟目标文本读取；指纹 / 凭证占位 / 研判均为本地虚构，**未发送任何网络流量**，不构成真实结论。字段统一 `_simulation: true`、`_source: {SRC}`。

### 步骤 1：虚拟指纹扫描

- 输出：`{cfg["scan_result_dir"]}/ehole_fingerprint_sim.json`
- 条目数：{len(finger_data)}

### 步骤 2：虚拟凭证占位研判

- 输出：`{cfg["scan_result_dir"]}/weakpass_sim.json`
- 条目数：{len(weak_data)}
- `flagged=true` 表示教学标记，**不得视为真实结论**。

### 步骤 3：优先级研判

| 主机 | 端口 | 服务类型 | 优先级 | 说明 | 教学标记 |
|------|------|----------|--------|------|----------|
"""

for j, w in zip(judge_data, weak_data):
    flagged = "是" if w.get("flagged", w.get("sim_suspected")) else "否"
    host = j.get("host", j.get("ip", ""))
    service_type = j.get("service_type", j.get("cms", ""))
    report_content += (
        f"| {host} | {j['port']} | {service_type} | {j['priority']} | {j['risk_note']} | {flagged} |\n"
    )

report_content += f"""
### 步骤 4：验证逻辑（方法论占位）

会话、页面可达性、未认证访问、错误凭据行为等维度**仅为课堂讨论**，本流程不访问真实页面。

### 步骤 5：后续流程（原理占位）

仅概念层说明，**禁止**在未授权环境执行任何真实操作。

### 步骤 6：本地环境清理

由 `scripts/auto_cleanup.py` 执行（受 `config.json` 中 `auto_cleanup` 控制）：缓存目录清理、`__pycache__` 等。**不删除** `data/scan_results` 下本轮 JSON。

---
"""

with open(report_file, "a", encoding="utf-8") as f:
    f.write(report_content)

print(f"[OK] 本轮模拟报告已追加写入：{report_file}（时间戳 {stamp}）")
