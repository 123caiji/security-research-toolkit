# HackSkills 集群矩阵总览

## 文档说明

**原始内容**：基于现有skill文件的实际结构和内容

**[补充推演]**：基于逻辑推导和安全测试方法论补充的内容

---

## 一、Skill集群矩阵总览

### 1.1 分层架构（原始内容）

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

### 1.2 各层功能定位（原始内容）

| 层级 | 功能定位 | 核心职责 |
|---|---|---|
| P0 | 总入口 | 接收任务，识别目标类型，路由到P1分类 |
| P1 | 分类路由 | 按领域细分，识别具体测试方向，路由到P2/P3/P4 |
| P2 | 深度专题 | 具体漏洞类型的测试方法论、payload、验证流程 |
| P3 | 内网域渗透 | 高级攻击技术，包含完整攻击链和持久化 |
| P4 | 防御反制 | 安全事件响应、攻击者溯源、蜜罐部署 |

### 1.3 P1分类路由详细映射（原始内容）

| P1分类 | 子Skill | 测试方向 |
|---|---|---|
| recon-for-sec | recon-and-methodology | 资产发现、指纹识别、方法论 |
| api-sec | api-recon-and-docs, api-authorization-and-bola, api-auth-and-jwt-abuse, graphql-and-hidden-parameters | API文档、BOLA、JWT、GraphQL |
| auth-sec | authbypass-authentication-flaws, idor-broken-object-authorization, jwt-oauth-token-attacks, oauth-oidc-misconfiguration, cors-cross-origin-misconfiguration, csrf-cross-site-request-forgery, saml-sso-assertion-attacks | 认证绕过、IDOR、JWT、OAuth、CORS、CSRF、SAML |
| injection-checking | xss, sqli, ssrf, xxe, ssti, cmdi, nosql, deserialization, jndi, expression-language, crlf, xslt, csv-injection, request-smuggling, prototype-pollution, type-juggling, http-parameter-pollution | 各类注入漏洞 |
| file-access-vuln | upload-insecure-files, path-traversal-lfi | 文件上传、路径遍历 |
| business-logic-vuln | business-logic-vulnerabilities, race-condition | 业务逻辑、竞态条件 |
| mobile-app-sec | android-reverse-engineering, ios-reverse-engineering, mobile-api-security, certificate-pinning-bypass, mobile-data-storage, mobile-permission-abuse, mobile-authentication | 移动应用全维度安全 |
| cloud-sec | cloud-misconfiguration, cloud-metadata-exposure, cloud-storage-security, serverless-security, cloud-iam-security, cloud-api-security | 云基础设施安全 |
| container-sec | docker-security, kubernetes-security, container-escape, container-image-security, kubernetes-rbac, container-supply-chain | 容器化环境安全 |
| reverse-engineering | binary-analysis, firmware-reverse-engineering, web-application-audit, cryptography-analysis, mobile-reverse-engineering, vulnerability-research | 逆向工程与漏洞挖掘 |
| osint | domain-osint, ip-osint, social-media-osint, code-repository-osint, infrastructure-osint, threat-intelligence-osint | 开源情报收集 |

---

## 二、攻击链路协作矩阵（原始内容）

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

---

## 三、完整逻辑链（[补充推演]）

### 3.1 漏洞赏金完整测试流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      漏洞赏金测试流程                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: 情报收集                                               │
│  ├── OSINT（域名/IP/代码仓库/资产测绘）                          │
│  │   └── recon-for-sec（攻击面梳理）                            │
│  │                                                             │
│  Phase 2: 目标识别                                               │
│  ├── Web应用 → injection-checking / api-sec / auth-sec         │
│  ├── 移动应用 → mobile-app-sec → api-sec                        │
│  ├── 云环境 → cloud-sec → injection-checking                    │
│  ├── 容器环境 → container-sec → reverse-engineering             │
│  └── 二进制/固件 → reverse-engineering → injection-checking     │
│                                                                 │
│  Phase 3: 漏洞挖掘                                               │
│  ├── Web漏洞（XSS/SQLi/SSRF/SSTI/XXE/IDOR/JWT/CSRF/CORS）      │
│  ├── 业务逻辑漏洞（竞态条件/价格操纵/认证绕过）                   │
│  ├── 云安全漏洞（元数据暴露/S3越权/IAM滥用）                     │
│  ├── 容器漏洞（镜像漏洞/RBAC滥用/容器逃逸）                      │
│  └── 移动漏洞（证书固定绕过/API加密破解/本地数据泄露）            │
│                                                                 │
│  Phase 4: 漏洞验证                                               │
│  ├── POC开发 → reverse-engineering                             │
│  ├── 权限提升 → injection-checking / domain-penetration        │
│  └── 证据收集 → traceback-counterattack（取证流程参考）          │
│                                                                 │
│  Phase 5: 报告提交                                               │
│  └── 漏洞描述 + 复现步骤 + POC + 修复建议                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 红队评估完整攻击链

```
┌─────────────────────────────────────────────────────────────────┐
│                      红队评估攻击链                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ① OSINT情报收集                                                │
│     └── osint → recon-for-sec                                   │
│                                                                 │
│  ② 外网突破                                                     │
│     └── recon-and-methodology → injection-checking              │
│         → api-sec / auth-sec                                    │
│                                                                 │
│  ③ C2建立                                                       │
│     └── c2-remote-control（上线/通信/规避）                      │
│                                                                 │
│  ④ 内网渗透                                                     │
│     └── internal-penetration（代理隧道/内网发现）                │
│                                                                 │
│  ⑤ 横向移动                                                     │
│     └── pivoting-lateral-movement（PsExec/Impacket/DCOM）      │
│                                                                 │
│  ⑥ 域控突破                                                     │
│     └── domain-penetration（Kerberoasting/委派/漏洞利用）       │
│                                                                 │
│  ⑦ 持久化维持                                                   │
│     └── c2-remote-control（黄金票据/Skeleton Key/持久化）       │
│                                                                 │
│  ⑧ 数据导出                                                     │
│     └── internal-penetration（凭据导出/数据收集）                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 蓝队溯源反制流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      蓝队溯源反制流程                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ① 事件发现                                                     │
│     └── traceback-counterattack（监控告警）                     │
│                                                                 │
│  ② 证据固定                                                     │
│     └── traceback-counterattack（磁盘镜像/内存转储）            │
│                                                                 │
│  ③ 日志分析                                                     │
│     └── traceback-counterattack（Sysmon/ELK/事件ID分析）       │
│                                                                 │
│  ④ 时间线重建                                                   │
│     └── traceback-counterattack（时间线/日志关联/MITRE映射）     │
│                                                                 │
│  ⑤ 攻击者画像                                                   │
│     └── osint（IP情报/域名分析/个人信息挖掘）                   │
│                                                                 │
│  ⑥ 蜜罐部署                                                     │
│     └── honeypot-counterattack（蜜罐部署/诱饵投放）             │
│                                                                 │
│  ⑦ 溯源反制                                                     │
│     └── traceback-counterattack（攻击者身份定位/溯源报告）       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 四、跨Skill协作关系（[补充推演]）

### 4.1 协作关系矩阵

| 主Skill | 上游Skill | 下游Skill | 协作场景 |
|---|---|---|---|
| osint | - | recon-for-sec, cloud-sec, traceback-counterattack | 情报收集为各阶段提供基础 |
| recon-for-sec | osint | injection-checking, api-sec, auth-sec | 攻击面梳理后进入具体测试 |
| api-sec | recon-for-sec, mobile-app-sec, cloud-sec | injection-checking, auth-sec | API测试需结合多领域知识 |
| auth-sec | api-sec, mobile-app-sec | injection-checking | 认证漏洞常作为突破入口 |
| injection-checking | api-sec, auth-sec, cloud-sec, container-sec, reverse-engineering | internal-penetration, domain-penetration | 漏洞利用后进入内网渗透 |
| mobile-app-sec | osint | api-sec, auth-sec, reverse-engineering | 移动分析结果用于API/认证测试 |
| cloud-sec | osint | injection-checking, auth-sec | 云漏洞需结合注入和认证测试 |
| container-sec | cloud-sec | reverse-engineering, c2-remote-control | 容器分析需逆向工程支持 |
| reverse-engineering | mobile-app-sec, container-sec | injection-checking, c2-remote-control | 逆向分析支持漏洞利用开发 |
| internal-penetration | injection-checking | pivoting-lateral-movement, domain-penetration | 内网突破后进入横向移动 |
| pivoting-lateral-movement | internal-penetration | domain-penetration | 横向移动后攻击域控 |
| domain-penetration | pivoting-lateral-movement | c2-remote-control | 域控突破后建立持久化 |
| c2-remote-control | internal-penetration, domain-penetration | - | C2建立和持久化是最终阶段 |
| traceback-counterattack | osint, c2-remote-control | honeypot-counterattack | 溯源需情报支持，联动蜜罐 |
| honeypot-counterattack | traceback-counterattack | traceback-counterattack | 蜜罐与溯源相互协作 |

### 4.2 典型场景Skill组合

**场景1：移动应用安全测试**
```
mobile-app-sec → api-sec → auth-sec → reverse-engineering
```

**场景2：云安全评估**
```
osint → cloud-sec → injection-checking → auth-sec
```

**场景3：容器安全评估**
```
container-sec → reverse-engineering → c2-remote-control
```

**场景4：逆向工程分析**
```
reverse-engineering → injection-checking → internal-penetration
```

**场景5：OSINT情报侦察**
```
osint → recon-for-sec → api-sec / injection-checking
```

**场景6：域渗透专项**
```
internal-penetration → pivoting-lateral-movement → domain-penetration → c2-remote-control
```

**场景7：HW红蓝对抗**
```
honeypot-counterattack → traceback-counterattack → osint → traceback-counterattack
```

---

## 五、Skill选择决策树（[补充推演]）

```
目标类型识别
├── Web应用
│   ├── API端点暴露 → api-sec
│   ├── 认证机制存在 → auth-sec
│   ├── 输入可控 → injection-checking
│   └── 文件操作 → file-access-vuln
│
├── 移动应用（APK/IPA）
│   └── mobile-app-sec
│       ├── 证书固定 → certificate-pinning-bypass
│       ├── API加密 → mobile-api-security
│       ├── 代码分析 → android-reverse-engineering/ios-reverse-engineering
│       └── 数据存储 → mobile-data-storage
│
├── 云环境（AWS/Azure/GCP）
│   └── cloud-sec
│       ├── 元数据端点 → cloud-metadata-exposure
│       ├── 存储桶 → cloud-storage-security
│       ├── IAM配置 → cloud-iam-security
│       └── Serverless → serverless-security
│
├── 容器环境（Docker/K8s）
│   └── container-sec
│       ├── 镜像安全 → container-image-security
│       ├── 容器逃逸 → container-escape
│       ├── RBAC配置 → kubernetes-rbac
│       └── 供应链 → container-supply-chain
│
├── 二进制/固件
│   └── reverse-engineering
│       ├── 二进制分析 → binary-analysis
│       ├── 固件逆向 → firmware-reverse-engineering
│       ├── 加密分析 → cryptography-analysis
│       └── 漏洞研究 → vulnerability-research
│
├── 域环境（Active Directory）
│   └── domain-penetration → pivoting-lateral-movement
│
├── 内网环境
│   └── internal-penetration → pivoting-lateral-movement
│
└── 情报收集
    └── osint
        ├── 域名分析 → domain-osint
        ├── IP情报 → ip-osint
        ├── 资产测绘 → infrastructure-osint
        └── 威胁情报 → threat-intelligence-osint
```

---

## 六、工具链矩阵（[补充推演]）

### 6.1 各领域工具链

| 领域 | 核心工具 | 辅助工具 |
|---|---|---|
| OSINT | subfinder, amass, dnsx, shodan, fofa, zoomeye | maltego, sherlock, trufflehog, gau, waybackurls |
| Web安全 | Burp Suite, sqlmap, nmap, nuclei | nikto, dirb, feroxbuster, zap |
| API安全 | Burp Suite, Postman, GraphQL Voyager | arjun, graphql-scanner, jwt_tool |
| 移动安全 | Frida, apktool, jadx, Charles, MobSF | Xposed, Substrate, QARK, SSL Kill Switch |
| 云安全 | AWS CLI, Azure CLI, Prowler, Scout Suite, Checkov | s3scanner, cloud_enum, CloudMapper |
| 容器安全 | Trivy, Snyk, Docker Bench Security, kube-bench, kube-hunter | Clair, Falco, grype, syft |
| 逆向工程 | IDA Pro, Ghidra, GDB, WinDbg, LLDB | binwalk, radare2, QEMU, AFL++, libFuzzer |
| 内网渗透 | CrackMapExec, Impacket, BloodHound, SharpHound | evil-winrm, rdp_check, smbmap |
| C2通信 | Metasploit, Cobalt Strike, Empire, Covenant | frp, nps, reGeorg, Neo-reGeorg |
| 溯源反制 | Volatility, Sysmon, ELK, MITRE ATT&CK | Autopsy, FTK Imager, Sigma Rules |

### 6.2 工具与Skill对应关系

| Skill | 推荐工具 |
|---|---|
| osint | subfinder, amass, dnsx, shodan, fofa, zoomeye, maltego |
| recon-for-sec | nmap, nuclei, feroxbuster, gau, waybackurls |
| api-sec | Burp Suite, Postman, arjun, graphql-scanner |
| auth-sec | Burp Suite, jwt_tool, oauth_tool |
| injection-checking | Burp Suite, sqlmap, nuclei, xsstrike |
| mobile-app-sec | Frida, apktool, jadx, Charles, MobSF |
| cloud-sec | Prowler, Scout Suite, Checkov, s3scanner |
| container-sec | Trivy, Snyk, kube-bench, kube-hunter, Falco |
| reverse-engineering | IDA Pro, Ghidra, GDB, binwalk, AFL++ |
| internal-penetration | CrackMapExec, Impacket, BloodHound |
| pivoting-lateral-movement | CrackMapExec, evil-winrm, smbmap |
| domain-penetration | Impacket, BloodHound, CrackMapExec |
| c2-remote-control | Metasploit, Cobalt Strike, frp, reGeorg |
| traceback-counterattack | Volatility, Sysmon, ELK |
| honeypot-counterattack | HFish, T-Pot, HoneyPy |

---

## 七、专家直觉汇总（[补充推演]）

1. **移动应用先过证书固定**：Frida脚本是最有效的SSL/TLS抓包绕过方法
2. **云安全先查元数据端点**：AWS IMDSv1无需认证即可获取临时凭证
3. **容器安全先扫镜像漏洞**：Trivy/Snyk能快速发现基础镜像中的已知漏洞
4. **逆向工程先用静态分析**：字符串分析和函数调用图能快速定位敏感逻辑
5. **OSINT先做资产测绘**：FoFa/Zoomeye能快速发现目标的全部在线资产
6. **域渗透先做BloodHound拓扑分析**：找到最优攻击路径再动手
7. **内网渗透优先凭据复用**：利用现有凭据横向移动更隐蔽、成功率更高
8. **C2通信协议按出网条件选择**：能出网用HTTPS，仅DNS出网用DNS隧道
9. **Kerberoasting优先于漏洞利用**：仅凭普通域用户即可获取服务账户密码
10. **委派攻击是最隐蔽的域管路径**：RBCD只需修改机器属性，不触发日志告警
11. **溯源反制先固定证据再操作**：获取磁盘镜像和内存转储后再进行反制
12. **蜜罐要高仿真**：使用真实漏洞环境而非云蜜罐

---

## 八、矩阵版本信息

- **版本**：v1.0
- **更新日期**：2026-07-16
- **包含Skill数量**：6层 × 40+ Skill
- **协作链路**：13条核心攻击链路 + 7条典型场景组合

---

## 九、迭代方向（[补充推演]）

未来迭代重点：

1. **补充P2深度专题Skill**：为mobile-app-sec、cloud-sec、container-sec、reverse-engineering、osint创建完整的P2子Skill
2. **完善工具链集成**：添加更多工具与Skill的对应关系，优化工具选择建议
3. **增强协作矩阵**：添加更多攻击场景的Skill组合路径
4. **补充漏洞POC模板**：为各深度专题Skill添加标准化的POC模板
5. **集成自动化测试框架**：添加基于nuclei/Python的自动化测试脚本
6. **完善防御视角**：从蓝队视角补充防御建议和安全加固指南
