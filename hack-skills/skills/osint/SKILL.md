---
name: osint
description: "Authorized penetration-testing skill for OSINT. Use for reconnaissance and OSINT, red-team validation, exploitability triage, evidence collection, remediation guidance, and retesting within a written scope."
---

# OSINT Router

这是开源情报（Open Source Intelligence）收集的分类入口。

先用这个skill判断当前OSINT任务更偏向于域名/IP分析、社交媒体挖掘、代码仓库分析，还是基础设施测绘，再进入更细的专题skill。

## When to Use

- 需要收集目标的公开信息
- 需要分析域名、IP、DNS记录
- 需要挖掘社交媒体和个人信息
- 需要分析GitHub/GitLab代码仓库
- 需要进行资产测绘和威胁情报收集

## Skill Map

- [Domain OSINT](../domain-osint/SKILL.md): 域名分析、DNS记录、WHOIS查询
- [IP OSINT](../ip-osint/SKILL.md): IP归属、威胁情报、端口扫描、指纹识别
- [Social Media OSINT](../social-media-osint/SKILL.md): 社交媒体挖掘、个人信息收集、关联分析
- [Code Repository OSINT](../code-repository-osint/SKILL.md): GitHub/GitLab分析、密钥泄露检测、源代码分析
- [Infrastructure OSINT](../infrastructure-osint/SKILL.md): 资产测绘、搜索引擎挖掘、Shodan/FoFa/Zoomeye
- [Threat Intelligence OSINT](../threat-intelligence-osint/SKILL.md): 威胁情报查询、IOC分析、APT关联

## Quick Triage

| Observation | Route |
|---|---|
| 目标域名 | [domain-osint](../domain-osint/SKILL.md) |
| 目标IP地址 | [ip-osint](../ip-osint/SKILL.md) |
| 个人信息挖掘 | [social-media-osint](../social-media-osint/SKILL.md) |
| GitHub/GitLab仓库 | [code-repository-osint](../code-repository-osint/SKILL.md) |
| 资产测绘 | [infrastructure-osint](../infrastructure-osint/SKILL.md) |
| 威胁情报查询 | [threat-intelligence-osint](../threat-intelligence-osint/SKILL.md) |

## Recommended Flow

1. 先确认OSINT目标：域名/IP/个人/代码/基础设施
2. 再选择对应的专题skill
3. 从多个数据源交叉验证信息
4. 记录证据链和来源

## Related Categories

- [recon-for-sec](../recon-for-sec/SKILL.md)
- [traceback-counterattack](../traceback-counterattack/SKILL.md)

## [补充推演] OSINT测试决策树

```
OSINT情报收集
├── 目标类型识别
│   ├── 域名/子域名 → domain-osint
│   ├── IP地址 → ip-osint
│   ├── 个人信息 → social-media-osint
│   ├── 代码仓库 → code-repository-osint
│   ├── 基础设施 → infrastructure-osint
│   └── 威胁情报 → threat-intelligence-osint
│
├── 收集阶段
│   ├── 被动收集
│   │   ├── WHOIS查询
│   │   ├── DNS记录分析
│   │   ├── 搜索引擎挖掘
│   │   └── 缓存快照
│   │
│   ├── 主动收集
│   │   ├── 端口扫描
│   │   ├── 服务指纹识别
│   │   ├── 资产测绘
│   │   └── 社交媒体验证
│   │
│   └── 交叉验证
│       ├── 多数据源对比
│       ├── 信息可信度评估
│       ├── 时间线重建
│       └── 证据链保全
│
└── 应用场景
    ├── 漏洞赏金侦察 → recon-for-sec
    ├── 攻击者溯源 → traceback-counterattack
    ├── 威胁情报分析 → threat-intelligence-osint
    └── 资产发现 → infrastructure-osint
```

## [补充推演] OSINT工具链

| 类别 | 工具 | 用途 |
|---|---|---|
| 域名分析 | subfinder, amass, dnsx | 子域名枚举 |
| IP分析 | shodan, censys, threatbook | IP情报查询 |
| 社交媒体 | maltego, sherlock, spiderfoot | 个人信息挖掘 |
| 代码仓库 | trufflehog, gitleaks | 密钥泄露检测 |
| 资产测绘 | fofa, zoomeye, hunter | 大规模资产发现 |
| 搜索引擎 | gau, waybackurls | 历史快照分析 |
| 威胁情报 | virustotal, abuseipdb | 威胁评分查询 |

## [补充推演] 跨Skill协作关系

| 场景 | 本Skill提供 | 衔接Skill |
|---|---|---|
| 漏洞赏金侦察 | 资产发现、子域名枚举 | recon-for-sec |
| 攻击者溯源 | IP情报、域名分析、个人信息挖掘 | traceback-counterattack |
| 蜜罐反制 | 攻击者身份定位、工具溯源 | honeypot-counterattack |
| 云安全 | 云资源发现、配置泄露检测 | cloud-sec |
| 供应链攻击 | 代码仓库分析、依赖漏洞 | container-sec |