# 六阶段本地模拟报告

> 生成时间：`2026-06-25 23:04:33`  |  `_simulation: true`  |  `_source: local_virtual_no_network`
> **声明**：未对外网或内网发起扫描；所有条目均为本地虚构数据。

## 阶段 1 — 信息收集

- 输出：`data\scan_results\teach_phase1_info_gather_sim.json`
- 自 `data/targets.txt` 读取 **3** 条占位目标（无连接）。

## 阶段 2 — 虚拟扫描

- `ehole_fingerprint_sim.json`：3 条
- `weakpass_sim.json`：3 条
- `risk_judge_sim.json`：3 条

## 阶段 3 — 场景占位

- 输出：`data\scan_results\teach_phase3_scenario_sim.json`

## 阶段 4 — 后续占位

- 输出：`data\scan_results\teach_phase4_followup_sim.json`

## 阶段 5 — 收尾占位

- 输出：`data\scan_results\teach_phase5_wrapup_sim.json`

## 阶段 6 — 与工程总报告对接

- 下一步子进程将执行 `auto_report_generate.py`，向 `data/reports/simulation_report.md` **追加**本轮摘要。

### 研判摘要（本地数据）

| 主机 | 端口 | 服务类型 | 优先级 |
|------|------|----------|--------|
| 127.0.0.1 | 8765 | T01 | P2 |
| 10.0.0.1 | 80 | T02 | P0 |
| 10.0.0.2 | 8080 | T03 | P1 |
