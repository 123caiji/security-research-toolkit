# 网络安全研究工具链 & HackSkills 知识库

> **声明**：本项目仅用于授权安全测试、教学研究和防御验证。所有真实目标测试需获得书面授权。默认 `config.json` 开启本地模拟模式，禁止真实网络探测。

## 项目概述

本项目整合了网络安全研究相关的技能文档（SKILL）、渗透测试脚本、漏洞利用工具和自动化审计工具链，涵盖 Web 安全、API 安全、内网渗透、CTF 竞技、密钥提取等多个方向。

## 目录结构

```
.
├── README.md                          # 本文件
├── TOOLCHAIN_NOTES.md                 # 工具链补充说明
├── cybersecurity-skills-integrated.md # 安全技能集成文档（全量索引）
├── .gitignore
│
├── hack-skills/                       # HackSkills 方法论库（66 文件）
│   ├── SKILL_MATRIX.md                #   技能矩阵总览
│   ├── README.md / README_CN.md       #   项目说明
│   └── skills/                        #   各漏洞类型 SKILL 文档
│       ├── api-sec/                   #   API 安全
│       ├── auth-sec/                  #   认证安全
│       ├── hack/                      #   黑客方法论
│       ├── osint/                     #   开源情报
│       ├── sqli-sql-injection/        #   SQL 注入
│       ├── xss-cross-site-scripting/  #   XSS
│       ├── ssrf-server-side-request-forgery/  # SSRF
│       ├── xxe-xml-external-entity/   #   XXE
│       ├── injection-checking/        #   注入类总览
│       ├── ...                        #   更多漏洞类型
│
├── skills/                            # 核心 SKILL 文档（4 文件）
│   ├── api-sec/SKILL.md
│   ├── auth-sec/SKILL.md
│   ├── hack/SKILL.md
│   └── osint/SKILL.md
│
├── scripts/                           # 核心工具脚本（23 文件）
│   ├── nacos_exploit.py               #   Nacos 未授权访问利用
│   ├── zen_rce.py                     #   禅道 RCE 利用
│   ├── jumpserver_pwn.py              #   JumpServer 堡垒机利用
│   ├── docker_enum.py                 #   Docker 容器枚举
│   ├── auto_risk_judge.py             #   自动化风险研判
│   ├── virtual_ehole_scan.py          #   模拟指纹扫描
│   ├── virtual_weakpass_scan.py       #   模拟弱口令扫描
│   ├── frontend_crypto_analyzer.py    #   前端加密算法分析
│   ├── credential_collector.py        #   凭证收集
│   ├── serve_local_web_demo.py        #   本地演示服务
│   ├── download_spa_static_mirror.py  #   SPA 静态镜像下载
│   ├── teach_six_phase_simulation_run.py  # 六阶段模拟
│   ├── run_all_and_bundle_outputs.py  #   批量执行打包
│   ├── auto_report_generate.py        #   自动报告生成
│   ├── auto_cleanup.py                #   自动清理
│   └── ...
│
├── apo/                               # 自动化渗透测试（34 文件）
│   ├── auto_pentest.py                #   自动渗透编排
│   ├── c2_exploit.py                  #   C2 利用
│   ├── smb_brute.py                   #   SMB 暴力破解
│   ├── kali_pentest.py                #   Kali SSH 渗透
│   ├── fast_scan.py                   #   异步端口扫描
│   ├── impacket_smb.py                #   Impacket SMB 利用
│   ├── vmrun_pentest.py               #   VMWare 渗透
│   ├── step1_scan.py ~ step15_vnc.py  #   分步渗透脚本
│   └── SECURITY_AUDIT_REPORT.md       #   安全审计报告
│
├── ctf/                               # CTF 竞赛脚本（32 文件）
│   ├── ctf_deep_test.py               #   深度漏洞测试
│   ├── ctf_source_analysis.py         #   源码分析
│   ├── ctf_image_payload.py           #   图片马利用
│   ├── find_flag.py / get_flag.py     #   Flag 搜索
│   ├── flag_finder.py                 #   Flag 定位
│   └── ...
│
├── xss/                               # XSS 检测与验证（14 文件）
│   ├── xss_verify.py                  #   XSS 验证
│   ├── xss_check.py                   #   XSS 检测
│   ├── xss_hjlib_analyze.py           #   XSS 库分析
│   ├── xss_tag_full_verify.py         #   标签验证
│   └── ...
│
├── sqli/                              # SQL 注入测试（3 文件）
│   ├── sql_bypass_deep.py             #   SQL 注入绕过
│   ├── sql_full_response.py           #   完整响应分析
│   └── sqlmap_req.txt
│
├── ssrf/                              # SSRF 验证（2 文件）
│   ├── ssrf_xss_verify.py
│   └── ssrf_xss_verify_curl.py
│
├── api-security/                      # API 安全测试（45 文件）
│   ├── kulaai_*.py                    #   Kulaai API 测试系列
│   ├── swagger_check.py               #   Swagger 检测
│   ├── extract_apis.py                #   API 提取
│   ├── pinnacle_*.js                  #   Pinnacle API 分析
│   └── ...
│
├── key-extraction/                    # 密钥提取与分析（15 文件）
│   ├── extract_spgkeys.py             #   SPG 密钥提取
│   ├── find_spgkeys.py                #   密钥搜索
│   ├── decode_keys.py                 #   密钥解码
│   ├── sm4_real_test.py               #   SM4 加密测试
│   └── ...
│
├── bypass/                            # 绕过技术（7 文件）
│   ├── advanced_bypass.py             #   高级绕过
│   ├── cmd_bypass.py                  #   命令执行绕过
│   ├── include_bypass.py             #   文件包含绕过
│   ├── bypass_ip.py                   #   IP 绕过
│   └── ...
│
├── recon/                             # 侦察扫描（12 文件）
│   ├── recon_hbwfjt.py                #   侦察脚本
│   ├── quick_dirscan.py               #   目录扫描
│   ├── robots_sitemap_exploit.py      #   robots/sitemap 利用
│   ├── server_deep_scan.py            #   深度服务器扫描
│   └── ...
│
├── upload/                            # 文件上传测试（6 文件）
│   ├── upload_and_exec.py             #   上传并执行
│   ├── upload_deep_test.py            #   深度上传测试
│   ├── csrf_upload_login.py           #   CSRF 上传登录
│   └── ...
│
├── ssh-enum/                          # SSH 枚举（6 文件）
│   ├── ssh_enum_kali.py               #   SSH 枚举（Kali）
│   ├── ssh_server_check.py            #   SSH 服务检测
│   ├── socks_test.py                  #   SOCKS 测试
│   └── ...
│
├── port-scan/                         # 端口扫描（3 文件）
│   ├── port_scan_deep.py              #   深度端口扫描
│   ├── port_scan_119_29_238_216.py    #   指定目标扫描
│   └── mysql_version_check.ps1        #   MySQL 版本检测
│
├── verification/                      # 漏洞验证（21 文件）
│   ├── verify_vuln.py                 #   漏洞验证
│   ├── verify_critical_endpoints.py   #   关键端点验证
│   ├── cve_2017_7529_check.py         #   CVE-2017-7529 检测
│   ├── iweboffice_verify.py           #   iWebOffice 验证
│   ├── seeyon_license_check.py        #   致远 OA License 检测
│   └── ...
│
├── analysis/                          # 代码分析（35 文件）
│   ├── analyze_authentication.py      #   认证分析
│   ├── deep_analysis.py               #   深度分析
│   ├── source_leak_verify.py          #   源码泄露验证
│   ├── deep_vuln_mining.py            #   深度漏洞挖掘
│   └── ...
│
├── target-specific/                   # 目标特定测试（26 文件）
│   ├── baota_security_test.py         #   宝塔面板测试
│   ├── erp_hbwfjt_scan.py             #   ERP 扫描
│   ├── malaqin_verify.py              #   Malacin 验证
│   ├── zhiqiapi_security_check.py     #   ZhiqiAPI 安全检查
│   └── ...
│
├── misc-scripts/                      # 杂项脚本（25 文件）
│   ├── main.py / config.py            #   框架入口和配置
│   ├── loader.py / utils.py           #   工具加载器
│   ├── batch_test*.ps1                #   批量测试
│   └── ...
│
├── config/                            # 配置文件
│   ├── tools.json                     #   工具清单
│   ├── categories.json                #   分类配置
│   ├── settings.json                  #   全局设置
│   └── shortcuts.ini                  #   快捷方式
│
├── core/                              # 核心模块
│   ├── env_manager.py                 #   环境管理（单例）
│   ├── modern_grid.py                 #   UI 网格组件
│   └── window_effect.py               #   窗口特效
│
├── data/                              # 数据与报告
│   ├── targets.txt                    #   目标列表
│   ├── scan_results/                  #   扫描结果（JSON）
│   └── reports/                       #   模拟报告
│
├── exports/                           # 导出演示
│   ├── local_web_demo/                #   本地 Web 演示
│   └── card_workflow_ai/              #   卡片工作流 AI
│
└── reports/                           # 安全报告
    ├── SECURITY_AUDIT_REPORT.md
    ├── sdqb_availability_report.txt
    └── ...
```

## 快速开始

### 环境要求

- Python 3.8+（工程内含便携 Python3，也可使用系统 Python）
- Git
- 部分 APO 脚本需要 Kali Linux 环境

### 核心工具使用

#### 1. Nacos 漏洞利用

```bash
python scripts/nacos_exploit.py
# 检测 Nacos 未授权访问、默认凭证(nacos/nacos)、User-Agent 绕过
```

#### 2. 禅道 RCE

```bash
python scripts/zen_rce.py
# 使用弱口令 admin/123456 登录禅道，通过 repo 接口触发 RCE
```

#### 3. JumpServer 利用

```bash
python scripts/jumpserver_pwn.py
# 登录 JumpServer 堡垒机，获取 Bearer Token，枚举资产
```

#### 4. Docker 枚举

```bash
python scripts/docker_enum.py
# 本地：执行 docker ps/images 检查，检测 docker.sock 和逃逸风险
# 远程：python scripts/docker_enum.py --target 192.168.1.100
```

#### 5. 前端加密分析

```bash
python scripts/frontend_crypto_analyzer.py exports/local_web_demo/main.js
# 正则匹配 JS 中的 md5/sha/aes/rsa/des/base64 加密关键词
```

#### 6. 凭证收集

```bash
python scripts/credential_collector.py
# 遍历 SSH 私钥、/etc/passwd、MySQL 配置、.env 等敏感文件
```

#### 7. 六阶段模拟演练

```bash
python scripts/teach_six_phase_simulation_run.py
# 纯本地模拟：信息收集 → 指纹识别 → 弱口令 → 场景利用 → 后渗透 → 报告
```

#### 8. 批量执行打包

```bash
python scripts/run_all_and_bundle_outputs.py
# 依次执行所有模拟脚本，打包输出到 data/ 目录
```

### APO 自动化渗透

```bash
# 快速端口扫描
python apo/fast_scan.py

# SMB 暴力破解
python apo/smb_brute.py

# 自动渗透编排（需 Kali SSH）
python apo/auto_pentest.py

# 分步渗透（step1 ~ step15）
python apo/step1_scan.py    # 端口扫描
python apo/step4_cve.py     # CVE 检测
python apo/step5_exploit.py # 漏洞利用
python apo/step6_msf.py     # MSF 利用
```

### CTF 竞赛工具

```bash
# 源码分析
python ctf/ctf_source_analysis.py

# Flag 搜索
python ctf/find_flag.py
python ctf/flag_finder.py

# 图片马利用
python ctf/ctf_image_payload.py

# 深度漏洞测试
python ctf/ctf_deep_test.py
```

### XSS 检测

```bash
python xss/xss_check.py        # XSS 检测
python xss/xss_verify.py       # XSS 验证
python xss/xss_tag_full_verify.py  # 标签完整性验证
```

### API 安全测试

```bash
# Swagger 接口检测
python api-security/swagger_check.py

# API 定义提取
python api-security/extract_apis.py

# Kulaai API 安全分析
python api-security/kulaai_deep_analysis.py
```

### 漏洞验证

```bash
# CVE-2017-7529 检测
python verification/cve_2017_7529_check.py

# 关键端点验证
python verification/verify_critical_endpoints.py

# iWebOffice 验证
python verification/iweboffice_verify.py
```

## HackSkills 方法论库

`hack-skills/` 目录包含完整的漏洞类型 SKILL 文档，每个 SKILL 包含：
- 漏洞原理与检测方法
- 利用场景与 PoC
- 绕过技巧
- 修复建议

| 分类 | 目录 | 说明 |
|------|------|------|
| API 安全 | `skills/api-sec/` | API 认证、授权、BOLA |
| 认证安全 | `skills/auth-sec/` | 认证绕过、JWT 攻击 |
| SQL 注入 | `skills/sqli-sql-injection/` | 注入检测与绕过 |
| XSS | `skills/xss-cross-site-scripting/` | 跨站脚本 |
| SSRF | `skills/ssrf-server-side-request-forgery/` | 服务端请求伪造 |
| XXE | `skills/xxe-xml-external-entity/` | XML 外部实体 |
| SSTI | `skills/ssti-server-side-template-injection/` | 模板注入 |
| 文件上传 | `skills/upload-insecure-files/` | 不安全文件上传 |
| 命令注入 | `skills/injection-checking/` | 各类注入 |
| 反序列化 | `skills/deserialization-insecure/` | 不安全反序列化 |
| 内网渗透 | `skills/internal-penetration/` | 内网横向移动 |
| 域渗透 | `skills/domain-penetration/` | 域控攻击 |
| 云安全 | `skills/cloud-sec/` | 云环境安全 |
| 容器安全 | `skills/container-sec/` | 容器逃逸 |
| 移动安全 | `skills/mobile-app-sec/` | 移动应用安全 |
| 逆向工程 | `skills/reverse-engineering/` | 二进制逆向 |
| OSINT | `skills/osint/` | 开源情报收集 |
| C2 远控 | `skills/c2-remote-control/` | 命令与控制 |
| 蜜罐反制 | `skills/honeypot-counterattack/` | 蜜罐与反制 |
| 追踪反制 | `skills/traceback-counterattack/` | 追踪与反追踪 |

## 工具链推荐流程

```
1. 信息收集    → recon/ + port-scan/ + api-security/swagger_check.py
2. 指纹识别    → scripts/virtual_ehole_scan.py
3. 漏洞扫描    → ctf/ + xss/ + sqli/ + ssrf/ + verification/
4. 漏洞利用    → scripts/nacos_exploit.py + scripts/zen_rce.py + apo/
5. 后渗透      → scripts/credential_collector.py + scripts/docker_enum.py
6. 报告生成    → scripts/auto_report_generate.py
```

## 配置说明

| 文件 | 作用 |
|------|------|
| `config.json` | 全局配置，控制本地模拟模式和网络边界 |
| `config/settings.json` | 工具箱设置 |
| `config/tools.json` | 工具清单（天狐工具箱映射） |
| `config/categories.json` | 工具分类配置 |

`config.json` 关键字段：
```json
{
  "simulation_mode": true,     // true=本地模拟，false=真实网络
  "allowed_targets": [],       // 授权目标列表
  "blocked_ranges": ["10.0.0.0/8", "172.16.0.0/12"]
}
```

## 核心模块

| 模块 | 文件 | 作用 |
|------|------|------|
| 环境管理 | `core/env_manager.py` | 单例模式管理工程路径、Python/Java 环境 |
| UI 网格 | `core/modern_grid.py` | 工具箱界面网格组件 |
| 窗口特效 | `core/window_effect.py` | 窗口动画与特效 |
| 配置加载 | `misc-scripts/config.py` | 全局配置读取 |

## 安全边界

- 默认只执行本机和工程内路径操作
- 真实目标扫描、爆破、利用必须有明确书面授权
- 修改 `config.json` 的 `simulation_mode` 为 `false` 前需确认授权范围
- WebShell、后渗透、免杀、远控类工具仅用于防御认知和授权实验

## License

见 `hack-skills/` 目录下的 LICENSE 文件。
