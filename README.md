# 前端静态分析与本地安全研究工具链

本工程保留离线/本机教学用 Python 工具、Cursor 规则、HackSkills 方法论库和少量 GUI 工具资源。默认 `config.json` 开启本地模拟模式，禁止真实网络探测；数据和报告使用 `T01`、`P0` 等通用代号，不写真实资产名称、IP 或凭证。

## 推荐链路

1. 本地前端演示：`python scripts/serve_local_web_demo.py`
2. 本地静态镜像：`python scripts/download_spa_static_mirror.py --base-url http://127.0.0.1:8765/ --include-css`
3. JS 静态分析：`python scripts/analyze_frontend_crypto_in_file.py exports/local_web_demo/main.js`
4. 六阶段模拟：`python scripts/teach_six_phase_simulation_run.py`
5. 汇总打包：`python scripts/run_all_and_bundle_outputs.py`

## 目录说明

| 路径 | 用途 |
|------|------|
| `scripts/` | 本地 Python 工具 |
| `data/` | 目标占位、虚拟扫描结果、报告 |
| `exports/` | 本地演示页、镜像和打包输出 |
| `tools/` | 当前工程实际存在的 GUI 工具资源 |
| `config/tools.json` | 天狐工具箱完整工具清单 |
| `Java_path/` | Java 8/11 便携运行环境 |
| `core/`、`config/` | 天狐框架组件与配置 |
| `hack-skills/` | HackSkills 方法论库，只读参考 |
| `.cursor/rules/` | Cursor 全局规则 |
| `.cursor/skills/` | Cursor 工作流 skill |

## 当前工具资源

当前 `tools/` 已合入天狐工具箱目录：

| 路径 | 定位 |
|------|------|
| `tools/gui_other/` | 抓包代理、辅助工具、部分后渗透/其他工具 |
| `tools/gui_scan/` | 漏洞扫描、框架验证、数据库/中间件相关工具 |
| `tools/gui_shouji/` | 信息收集工具 |
| `tools/gui_webshell/` | WebShell 管理工具，仅授权实验/防御验证 |

完整清单见 `config/tools.json`。执行具体工具前仍需校验路径存在，并遵守 `config.json` 网络边界。

## Cursor 规则

| 文件 | 作用 |
|------|------|
| `bilingual-master-governance.mdc` | 中英双语总控规则：优先级、审计、范围扩大、工具路由 |
| `user-governance-priority.mdc` | 用户治理优先级、审计门禁与模型默认判断覆盖 |
| `project-tool-autonomy.mdc` | 工程内自主执行、本地工具优先 |
| `overall-security-toolchain.mdc` | 总体工具链路、规则路由与执行边界 |
| `imported-security-research-workflow.mdc` | 安全研究场景路由与输出模板 |
| `scope-expansion-authorization.mdc` | 授权范围扩大、目标记录与配置变更 |
| `security-research-context.mdc` | 授权范围与安全研究协作行为 |
| `hack-skills-routing.mdc` | `hack-skills/` 三层方法论路由 |
| `local-simulation-boundaries.mdc` | 网络边界、脱敏字段与本地模拟约束 |
| `local-toolbox-inventory.mdc` | 本地工具箱清单与天狐参考包映射 |

## Cursor Skills

| Skill | 作用 |
|-------|------|
| `project-security-router` | 总入口：方法论、本地脚本、工具箱路由 |
| `hack-skills-library` | HackSkills 专题索引与读取顺序 |
| `local-frontend-toolchain` | 前端静态分析与本地镜像 |
| `local-simulation-workflow` | 六阶段本地模拟与虚拟扫描报告 |
| `local-toolbox-index` | 本地 `tools/` 与天狐参考清单的工具选择 |

## 边界

- 默认只执行本机和工程内路径操作。
- 真实目标扫描、爆破、利用必须有明确授权，并同步调整 `config.json`。
- WebShell、后渗透、免杀、远控类工具默认只用于防御认知、风险说明和授权实验规划。
