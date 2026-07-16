# Snyk 初始扫描报告（工具箱依赖）

`_source: snyk_cli_initial_probe` · `_simulation: false`

## 为什么对本工程有价值

本仓库是天狐渗透工具箱合入版，含 **500+ 嵌套 `package.json`** 与 **14 个 Python `requirements.txt`**。  
手工审计不现实；Snyk 可：

1. 对 `tools/` 下各工具 manifest 做 CVE 关联
2. 通过 `/snyk-fix` 批量升级有修复版本的依赖
3. 编辑 `scripts/` 或新增依赖时，由 **Secure at Inception** hook 在保存后自动提示

## 本次已执行动作

| 步骤 | 结果 |
|------|------|
| `npx snyk --version` | CLI **1.1305.1** 可用 |
| 扫描 `tools/gui_scan/dirsearch/requirements.txt` | 需 `--package-manager=pip`；未安装虚拟环境时提示 *Missing required packages* |
| 扫描 `tools/gui_webshell/AntSword/...` (npm) | 检测到 `node_modules`，但需 **`snyk auth`** |
| 创建 `.snyk` | 排除 `node_modules`、AntSword 等 vendor 树，聚焦 Python 工具 |
| 创建 `scripts/run_snyk_toolbox_scan.ps1` | 一键扫描 5 个高优先级 manifest |

## 高优先级扫描目标（P0）

| 工具 | Manifest | 风险关注点 |
|------|----------|------------|
| dirsearch | `tools/gui_scan/dirsearch/requirements.txt` | `urllib3`、`requests`、`cryptography`、`pyOpenSSL` 历史 CVE 多 |
| impacket | `tools/gui_other/hengxiang/impacket-0.11.0/requirements.txt` | `pyOpenSSL`、`ldap3`、`flask` |
| OneForAll | `tools/gui_shouji/oneforall/requirements.txt` | 子域枚举依赖链 |
| webpackscan | `tools/gui_scan/webpackscan/requirements.txt` | 前端扫描栈 |
| vcenterKit | `tools/gui_other/vcenterKit/requirements.txt` | PyQt / 网络库 |

## 下一步（需你完成一次 OAuth）

```powershell
npx snyk auth
# 浏览器登录后：
powershell -ExecutionPolicy Bypass -File scripts/run_snyk_toolbox_scan.ps1
```

或在 Cursor 聊天框运行 **`/snyk-fix`**，对检出项自动修复并验证。

## MCP 状态

当前工作区 MCP 目录中 **尚未出现 `snyk` 服务**（仅有 hexstrike-ai 等）。  
完成 `snyk auth` 后重启 Cursor，Snyk 插件 MCP 通常会注册；届时 Agent 可直接调用 MCP 扫描而无需手动 CLI。
