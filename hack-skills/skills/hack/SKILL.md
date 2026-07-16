---
name: hack
description: >-
  Entry P0 primary router for HackSkills. Use when the task involves web
  application testing, API security assessment, recon, vulnerability triage,
  exploit path planning, or choosing the right next category skill before any
  deep topic skill.
---

# HACKING SKILLS / HackSkills

## Overview

这是一个面向 **漏洞赏金、Web 安全、API 安全、授权渗透测试** 的总入口技能。

它的核心作用不是替代所有专题技巧，而是帮助 Agent：

1. 先确定测试阶段（Recon / 验证 / 提权 / 组合链）
2. 再选择正确的漏洞类别
3. 避免只依赖基础训练数据，优先使用结构化方法论
4. 优先关注 AI 容易忽略但在实战里很重要的边界条件

## Trust Model

- 本知识库强调内容安全与可审查性。
- 使用时应限定在 **授权目标**、**合法研究**、**防御验证**、**漏洞赏金规则允许** 的范围内。
- 不要把这里的技巧用于未授权攻击。

## When to Use This Skill

在以下场景优先使用本技能：

- 你刚接手一个新的漏洞赏金目标，不知道先测什么
- 你需要决定应该加载 XSS / SQLi / SSRF / IDOR / JWT / API 等哪类思路
- 你想让 Agent 按更稳定的方法论进行 Web/API 安全测试
- 你需要把零散的现象路由到合适的攻击面
- 你希望 AI 在安全领域少漏掉关键测试点

## Operating Model

### Step 1: 先做 Recon 和上下文确认

优先收集：

- 目标类型：传统 Web、REST API、移动端后端、管理后台、支付流程、文件上传、GraphQL
- 身份与权限模型：匿名、普通用户、管理员、多租户
- 输入位置：URL、查询参数、JSON、Header、Cookie、文件名、导入文件、模板、回显点
- 输出位置：HTML、属性、JS、PDF、邮件、日志、后台任务、移动端接口

### Step 2: 按观察到的现象路由

| 现象 | 优先方向 |
|---|---|
| 输入反射到 HTML / JS | XSS / SSTI |
| 服务端会主动访问 URL / 主机名 | SSRF |
| 接收 XML / Office / SVG | XXE |
| 路径、文件名、下载接口可控 | Path Traversal / LFI |
| API 中大量对象 ID | IDOR / BOLA / BFLA |
| 登录、找回密码、2FA、Session | Auth Bypass / JWT / OAuth |
| 多步骤交易、优惠券、价格、库存 | Business Logic |
| MongoDB / JSON 查询语法暴露 | NoSQL Injection |
| 命令行工具、图像处理、导入器 | Command Injection |
| HTTP 请求解析异常 / 前后端分帧不一致 | Request Smuggling |
| Node.js JSON 处理 / `__proto__` 可控 | Prototype Pollution |
| PHP 弱比较 / 0e hash / 松散条件 | Type Juggling |
| 同名参数重复 / WAF 与应用解析不一致 | HTTP Parameter Pollution |
| 一次性操作（优惠券/库存/重置） | Race Condition |
| XML/XSLT 模板处理 | XSLT Injection |
| .git/.svn/.env 路径可访问 | Insecure SCM |
| 导出 CSV/Excel 功能 | CSV Formula Injection |
| WebSocket 协议升级 | WebSocket Security |
| 内部包名 / 供应链清单 | Dependency Confusion |
| 域环境 / Active Directory / 域控 | Domain Penetration |
| 内网渗透 / 横向移动 / 跳板攻击 | Internal Penetration / Pivoting |
| C2通信 / Beacon / Session / 远控框架 | C2 Remote Control |
| 安全事件响应 / 攻击者溯源 / 反制 | Traceback Counterattack |
| 蜜罐部署 / 红蓝对抗 / 溯源攻击 | Honeypot Counterattack |
| 移动应用 / APK / IPA / 证书劫持 | Mobile App Security |
| 云平台 / AWS / Azure / GCP / S3存储 | Cloud Security |
| Docker / Kubernetes / 容器逃逸 | Container Security |
| 二进制 / 固件 / 加密分析 / 反编译 | Reverse Engineering |
| 开源情报 / 域名分析 / 资产测绘 / 威胁情报 | OSINT |
| NetLogon / Zerologon / MS14-068 / NoPac | Domain Penetration |
| ADCS / ESC系列 / 证书漏洞 | Domain Penetration |
| ACL权限滥用 / 域管理员添加 | Domain Penetration |
| BloodHound / SharpHound / AD拓扑分析 | Pivoting Lateral Movement |
| Impacket / DCSync / secretsdump | Domain Penetration |
| Kerberoasting / AS-REP Roasting | Domain Penetration |
| 委派攻击 / 非约束委派 / 约束委派 / RBCD | Domain Penetration |
| PrintNightmare / Print Spooler漏洞 | Domain Penetration |
| NTDS.dit / 域控数据库提取 | Domain Penetration |
| WinRM / evil-winrm / 5985端口 | Pivoting Lateral Movement |
| DCOM / MMC20 / ShellWindows横向 | Pivoting Lateral Movement |
| RDP劫持 / tscon会话接管 | Pivoting Lateral Movement |
| CrackMapExec / NetExec / 密码喷洒 | Pivoting Lateral Movement |
| frp / nps / earthworm / 隧道代理 | Internal Penetration |
| reGeorg / Neo-reGeorg / Web隧道 | Internal Penetration |
| AMSI Bypass / ETW Bypass / 免杀 | C2 Remote Control |
| Domain Fronting / CDN中转 / C2隐蔽 | C2 Remote Control |
| WMI事件订阅 / COM劫持 / 持久化 | C2 Remote Control |
| Skeleton Key / DSRM后门 / 域控维持 | C2 Remote Control |
| 内存取证 / Volatility / LSASS转储 | Traceback Counterattack |
| 时间线重建 / 日志关联 / 事件ID分析 | Traceback Counterattack |
| MITRE ATT&CK / Sigma规则 / TTP映射 | Traceback Counterattack |
| Sysmon / ELK / 日志收集分析 | Traceback Counterattack |
| HoneyUser / HoneyToken / 蜜罐标记 | Honeypot Counterattack |
| 蜜网 / HFish / T-Pot / 蜜罐部署 | Honeypot Counterattack |

### Step 3: 使用最可能命中的测试顺序

1. Recon / Methodology
2. API Security / Auth / IDOR
3. XSS / SQLi / SSRF / SSTI / XXE
4. Business Logic / Race Condition
5. 组合链与提权路径

## Core Skill Map

如果你拥有完整仓库，优先结合这些专题文档一起使用：

- [Recon and Methodology](../recon-and-methodology/SKILL.md)
- [XSS Cross Site Scripting](../xss-cross-site-scripting/SKILL.md)
- [SQLi SQL Injection](../sqli-sql-injection/SKILL.md)
- [SSRF Server Side Request Forgery](../ssrf-server-side-request-forgery/SKILL.md)
- [XXE XML External Entity](../xxe-xml-external-entity/SKILL.md)
- [SSTI Server Side Template Injection](../ssti-server-side-template-injection/SKILL.md)
- [IDOR Broken Object Authorization](../idor-broken-object-authorization/SKILL.md)
- [CMDi Command Injection](../cmdi-command-injection/SKILL.md)
- [Path Traversal LFI](../path-traversal-lfi/SKILL.md)
- [CSRF Cross Site Request Forgery](../csrf-cross-site-request-forgery/SKILL.md)
- [API Security Router](../api-sec/SKILL.md)
- [JWT OAuth Token Attacks](../jwt-oauth-token-attacks/SKILL.md)
- [OAuth OIDC Misconfiguration](../oauth-oidc-misconfiguration/SKILL.md)
- [CORS Cross Origin Misconfiguration](../cors-cross-origin-misconfiguration/SKILL.md)
- [SAML SSO Assertion Attacks](../saml-sso-assertion-attacks/SKILL.md)
- [Authentication Bypass](../authbypass-authentication-flaws/SKILL.md)
- [Business Logic Vulnerabilities](../business-logic-vulnerabilities/SKILL.md)
- [Upload Insecure Files](../upload-insecure-files/SKILL.md)
- [NoSQL Injection](../nosql-injection/SKILL.md)
- [Request Smuggling](../request-smuggling/SKILL.md)
- [Prototype Pollution](../prototype-pollution/SKILL.md)
- [Type Juggling (PHP)](../type-juggling/SKILL.md)
- [HTTP Parameter Pollution](../http-parameter-pollution/SKILL.md)
- [Race Condition](../race-condition/SKILL.md)
- [XSLT Injection](../xslt-injection/SKILL.md)
- [Insecure Source Code Management](../insecure-source-code-management/SKILL.md)
- [CSV Formula Injection](../csv-formula-injection/SKILL.md)
- [WebSocket Security](../websocket-security/SKILL.md)
- [Dependency Confusion](../dependency-confusion/SKILL.md)
- [C2 Remote Control](../c2-remote-control/SKILL.md)
- [Pivoting Lateral Movement](../pivoting-lateral-movement/SKILL.md)
- [Domain Penetration](../domain-penetration/SKILL.md)
- [Internal Penetration](../internal-penetration/SKILL.md)
- [Traceback Counterattack](../traceback-counterattack/SKILL.md)
- [Honeypot Counterattack](../honeypot-counterattack/SKILL.md)
- [Mobile App Security Router](../mobile-app-sec/SKILL.md)
- [Cloud Security Router](../cloud-sec/SKILL.md)
- [Container Security Router](../container-sec/SKILL.md)
- [Reverse Engineering Router](../reverse-engineering/SKILL.md)
- [OSINT Router](../osint/SKILL.md)

原先单独拆出的 payload-selection、brute-selection 一类小 skill 已并回对应主 skill，避免入口过多导致 loader 负担和选择噪音。

## Cross-Skill Collaboration Map

[补充推演] 以下矩阵展示各skill间的协作关系，用于在复杂攻击链中选择正确的skill组合：

### 攻击链路协作矩阵

| 攻击阶段 | 主Skill | 提供能力 | 衔接Skill | 衔接用途 |
|---|---|---|---|---|
| 初始突破 | recon-and-methodology | 资产发现/指纹识别 | internal-penetration | 外网突破入口 |
| OSINT情报收集 | osint | 域名分析/IP情报/资产测绘 | recon-for-sec | 侦察情报补充 |
| 移动应用分析 | mobile-app-sec | APK反编译/API加密分析 | api-sec | 移动端API测试 |
| 云环境分析 | cloud-sec | 云元数据/S3存储/IAM配置 | injection-checking | SSRF云元数据利用 |
| 容器环境分析 | container-sec | Docker/K8s安全/镜像漏洞 | reverse-engineering | 容器逃逸漏洞挖掘 |
| 逆向工程分析 | reverse-engineering | 二进制/固件/加密算法分析 | injection-checking | 漏洞利用开发 |
| C2建立 | c2-remote-control | 上线/通信协议/规避 | internal-penetration | 内网隧道选择 |
| 内网渗透 | internal-penetration | 完整渗透流程/代理隧道 | pivoting-lateral-movement | 横向移动技术 |
| 横向移动 | pivoting-lateral-movement | PsExec/Impacket/DCOM | domain-penetration | 域内横向 |
| 域控突破 | domain-penetration | Kerberoasting/委派/漏洞利用 | internal-penetration | 凭据导出 |
| 持久化维持 | c2-remote-control | 黄金票据/Skeleton Key/持久化 | domain-penetration | 域控持久化 |
| 溯源反制 | traceback-counterattack | 日志分析/内存取证/溯源 | honeypot-counterattack | 蜜罐联动溯源 |
| 蜜罐反制 | honeypot-counterattack | 蜜罐部署/诱饵投放/反制 | traceback-counterattack | 攻击者画像 |

### 典型攻击场景skill组合

**场景1：红队评估全流程**
```
recon-and-methodology → internal-penetration → c2-remote-control
→ pivoting-lateral-movement → domain-penetration → c2-remote-control（持久化）
```

**场景2：域渗透专项**
```
domain-penetration → pivoting-lateral-movement（BloodHound分析）
→ domain-penetration（Kerberoasting/委派/漏洞利用）
→ internal-penetration（凭据导出）→ c2-remote-control（权限维持）
```

**场景3：蓝队溯源反制**
```
traceback-counterattack（日志分析/内存取证）
→ traceback-counterattack（MITRE ATT&CK映射/时间线重建）
→ honeypot-counterattack（蜜罐部署/诱饵投放）
→ traceback-counterattack（攻击者身份溯源）
```

**场景4：内网不出网场景**
```
internal-penetration（外网突破）→ c2-remote-control（SMB Beacon/隧道选择）
→ pivoting-lateral-movement（横向移动）→ internal-penetration（代理隧道）
→ domain-penetration（域控突破）
```

**场景5：HW红蓝对抗**
```
honeypot-counterattack（蜜罐部署/诱饵投放）
→ traceback-counterattack（监控告警/攻击者上线分析）
→ honeypot-counterattack（溯源反制/身份定位）
→ traceback-counterattack（完整溯源报告）
```

**场景6：移动应用安全测试**
```
mobile-app-sec（平台识别/测试规划）
→ mobile-app-sec（证书固定绕过/抓包）
→ mobile-app-sec（API加密分析/密钥提取）
→ api-sec（移动端API测试/BOLA）
→ auth-sec（认证机制分析/Token安全）
```

**场景7：云安全评估**
```
osint（云资源发现/存储桶枚举）
→ cloud-sec（云平台识别/测试规划）
→ cloud-sec（元数据端点测试/存储桶访问控制）
→ cloud-sec（IAM策略分析/权限滥用）
→ injection-checking（SSRF云元数据利用）
```

**场景8：容器安全评估**
```
container-sec（容器平台识别/Docker/K8s）
→ container-sec（镜像漏洞扫描/配置审计）
→ container-sec（容器逃逸测试/RBAC分析）
→ reverse-engineering（镜像二进制分析）
→ c2-remote-control（容器逃逸后权限维持）
```

**场景9：逆向工程分析**
```
reverse-engineering（目标类型识别/工具链选择）
→ reverse-engineering（静态分析/反编译）
→ reverse-engineering（动态分析/调试/Hook）
→ reverse-engineering（漏洞挖掘/POC开发）
→ injection-checking（漏洞利用验证）
```

**场景10：OSINT情报侦察**
```
osint（目标类型识别/情报收集方向）
→ osint（域名分析/子域名枚举）
→ osint（IP情报/威胁评分查询）
→ osint（代码仓库分析/密钥泄露检测）
→ recon-for-sec（资产测绘/攻击面梳理）
```

### Skill分层架构

```
P0 入口层
  └── hack（总路由器）

P1 分类路由层
  ├── recon-for-sec（侦察与方法论）
  ├── recon-and-methodology（深度侦察）
  ├── api-sec（API安全）
  ├── auth-sec（认证授权）
  ├── injection-checking（注入测试）
  ├── file-access-vuln（文件访问漏洞）
  ├── business-logic-vuln（业务逻辑漏洞）
  ├── mobile-app-sec（移动应用安全）
  ├── cloud-sec（云安全）
  ├── container-sec（容器安全）
  ├── reverse-engineering（逆向工程）
  └── osint（开源情报）

P2 深度专题层（Web/API攻击）
  ├── xss / sqli / ssrf / ssti / xxe
  ├── idor / authbypass / jwt / oauth / saml / cors / csrf
  ├── business-logic / race-condition / prototype-pollution
  ├── cmdi / path-traversal / nosql / type-juggling
  ├── upload / request-smuggling / websocket / csv-injection
  ├── xslt-injection / crlf-injection / expression-language
  ├── jndi-injection / deserialization / open-redirect
  ├── clickjacking / web-cache-deception / dependency-confusion
  ├── insecure-source-code-management / http-parameter-pollution
  └── api-recon / api-auth / api-authorization / graphql

P3 内网与域渗透层
  ├── internal-penetration（内网渗透全流程）
  ├── pivoting-lateral-movement（跳板/横向移动）
  ├── domain-penetration（域渗透全流程）
  └── c2-remote-control（C2远控/持久化）

P4 防御与反制层
  ├── traceback-counterattack（溯源反制）
  └── honeypot-counterattack（蜜罐反制）
```

## High-Value Expert Intuitions

这些点是很多基础模型容易忽略，但在真实漏洞赏金里经常有效：

1. **同一套过滤逻辑往往复用在多个页面**：一个点可绕过，类似页面通常也能绕过。
2. **参数名本身也是攻击面**：WAF 经常只盯参数值，不盯参数名。
3. **二阶漏洞非常常见**：存储时安全，不代表读取后进入危险上下文时也安全。
4. **BOLA 的本质是“有认证、无授权”**：A/B 账号切换重放非常关键。
5. **老版本接口最容易漏补丁**：v2 修了不代表 v1 下线了。
6. **业务逻辑漏洞往往回报最高**：它们难以被扫描器发现，也更容易长期存在。
7. **Race Condition 应优先测试“一次性”操作**：优惠券、领取、重置、邀请、试用、库存扣减。
8. **JWT 攻击先看密钥与算法上下文**：不要盲目试 payload，要先确认 `alg`、`kid`、JWKS、密钥来源。
9. **[补充推演] 域渗透先做BloodHound拓扑分析**：不要盲目尝试漏洞，先用BloodHound找到最优攻击路径再动手。
10. **[补充推演] 内网渗透优先凭据复用**：利用现有凭据横向移动比漏洞利用更隐蔽、成功率更高。
11. **[补充推演] C2通信协议按出网条件选择**：能出网用HTTPS，仅DNS出网用DNS隧道，不出网用SMB Beacon。
12. **[补充推演] Kerberoasting优先于漏洞利用**：不需要域控权限，仅凭普通域用户即可获取服务账户密码。
13. **[补充推演] 委派攻击是最隐蔽的域管路径**：RBCD只需修改机器属性，不触发域控日志告警。
14. **[补充推演] 溯源反制先固定证据再操作**：获取磁盘镜像和内存转储后再进行反制，避免证据丢失。
15. **[补充推演] 蜜罐要高仿真**：使用真实漏洞环境而非云蜜罐，避免被攻击者快速识别。
16. **[补充推演] 移动应用先过证书固定**：Frida脚本是最有效的SSL/TLS抓包绕过方法，优先尝试JustTrustMe/SSLUnpinning。
17. **[补充推演] 云安全先查元数据端点**：AWS IMDSv1无需认证即可获取临时凭证，这是最常见的云安全突破口。
18. **[补充推演] 容器安全先扫镜像漏洞**：Trivy/Snyk能快速发现基础镜像中的已知漏洞，比手动分析效率高10倍以上。
19. **[补充推演] 逆向工程先用静态分析**：字符串分析和函数调用图能快速定位敏感逻辑，避免不必要的动态调试。
20. **[补充推演] OSINT先做资产测绘**：FoFa/Zoomeye能快速发现目标的全部在线资产，为后续攻击面梳理提供基础。

## Suggested Prompts

可把本技能当作路由器来用，先让 Agent 明确阶段和目标：

- “先按漏洞赏金方法论帮我做这个目标的测试路线规划。”
- “这是一个 REST API，请优先从 BOLA、BFLA、Mass Assignment、JWT 角度审视。”
- “这个参数会触发服务端请求，请按 SSRF 思路列出关键验证点。”
- “这个功能是支付/优惠券/库存流程，请优先考虑业务逻辑和竞态。”
- “我只看到登录和找回密码流程，请按 Auth Bypass + OAuth/JWT + CSRF 路线分析。”
- "[补充推演] 这是域环境，请按BloodHound拓扑分析→Kerberoasting→委派攻击→域控漏洞利用路线规划。"
- "[补充推演] 目标内网不出网，请按SMB Beacon→隧道选择→横向移动→域控突破路线分析。"
- "[补充推演] 这是HW红蓝对抗，请按蜜罐部署→诱饵投放→溯源反制→身份定位路线规划。"
- "[补充推演] 发生安全事件，请按日志分析→内存取证→时间线重建→MITRE映射→溯源反制路线处理。"
- "[补充推演] 目标是Android APK，请按证书固定绕过→API加密分析→密钥提取→API安全测试路线规划。"
- "[补充推演] 目标使用AWS云服务，请按云资源发现→元数据端点测试→S3存储桶安全→IAM策略分析路线规划。"
- "[补充推演] 目标使用Kubernetes集群，请按镜像漏洞扫描→RBAC配置审计→容器逃逸测试→控制平面安全路线规划。"
- "[补充推演] 需要分析加密算法，请按静态分析→加密算法识别→密钥提取→协议逆向路线规划。"

## Installation Notes

推荐 skill 名称：

- `hack`

推荐检索关键词：

- `HackSkills`
- `HACKING SKILLS`
- `bug bounty`
- `赏金猎人`

## Guidelines

- 优先按目标类型与现象路由，而不是随机枚举 payload。
- 需要 payload 时，优先使用对应主 skill 里的 quick start / first-pass 样本，而不是再跳一个中间入口。
- 优先寻找可复用的过滤器、共享组件和跨页面复现路径。
- 先确认认证边界、授权边界、版本边界，再深入利用。
- 优先保留可解释、可审查、可复现的测试过程。
- 当完整仓库可用时，优先回到专题文档获取更细的攻击细节。
