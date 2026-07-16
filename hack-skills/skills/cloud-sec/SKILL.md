---
name: cloud-sec
description: >-
  Entry P1 category router for cloud security. Use when testing cloud infrastructure (AWS, Azure, GCP), including misconfiguration detection, cloud metadata exposure, S3 bucket security, and serverless vulnerabilities.
---

# Cloud Security Router

这是云基础设施（AWS、Azure、GCP等）安全测试的分类入口。

先用这个skill判断当前云环境更偏向于配置错误、云元数据暴露、S3存储安全、无服务器漏洞，还是身份与访问管理问题，再进入更细的专题skill。

## When to Use

- 目标使用AWS、Azure、GCP等云服务
- 需要测试云存储桶（S3、Blob Storage）的访问控制
- 怀疑存在云元数据端点暴露
- 需要分析IAM策略配置和权限滥用
- 目标包含Serverless函数（Lambda、Function App）

## Skill Map

- [Cloud Misconfiguration](../cloud-misconfiguration/SKILL.md): AWS/Azure/GCP配置错误检测
- [Cloud Metadata Exposure](../cloud-metadata-exposure/SKILL.md): IMDS/Instance Metadata服务漏洞
- [Cloud Storage Security](../cloud-storage-security/SKILL.md): S3/Blob/GCS存储桶安全
- [Serverless Security](../serverless-security/SKILL.md): Lambda/Function App安全测试
- [Cloud IAM Security](../cloud-iam-security/SKILL.md): IAM策略、角色配置、权限滥用
- [Cloud API Security](../cloud-api-security/SKILL.md): 云服务API安全、密钥泄露、签名滥用

## Quick Triage

| Observation | Route |
|---|---|
| AWS EC2实例 | [cloud-metadata-exposure](../cloud-metadata-exposure/SKILL.md) |
| S3存储桶可公开访问 | [cloud-storage-security](../cloud-storage-security/SKILL.md) |
| Lambda函数 | [serverless-security](../serverless-security/SKILL.md) |
| IAM角色配置异常 | [cloud-iam-security](../cloud-iam-security/SKILL.md) |
| Azure/AD配置 | [cloud-misconfiguration](../cloud-misconfiguration/SKILL.md) |
| 云API密钥泄露 | [cloud-api-security](../cloud-api-security/SKILL.md) |

## Recommended Flow

1. 先确认云平台（AWS/Azure/GCP/其他）
2. 再确认测试重点：存储安全、元数据、IAM、Serverless
3. 先检查公开暴露的云资源（S3、API端点）
4. 再检查配置错误和权限滥用

## Related Categories

- [api-sec](../api-sec/SKILL.md)
- [auth-sec](../auth-sec/SKILL.md)
- [recon-for-sec](../recon-for-sec/SKILL.md)

## [补充推演] 云安全测试决策树

```
云安全测试
├── 云平台识别
│   ├── AWS → cloud-metadata-exposure, cloud-storage-security
│   ├── Azure → cloud-misconfiguration, cloud-iam-security
│   ├── GCP → cloud-metadata-exposure, cloud-storage-security
│   └── 混合云 → 多平台综合测试
│
├── 测试阶段
│   ├── 资源发现
│   │   ├── 存储桶枚举（S3/Blob/GCS）
│   │   ├── 云函数发现（Lambda/Function App）
│   │   ├── API网关发现
│   │   └── 云服务子域名枚举
│   │
│   ├── 配置审计
│   │   ├── IAM策略分析
│   │   ├── 存储桶访问控制
│   │   ├── 网络安全组配置
│   │   └── 密钥管理配置
│   │
│   └── 漏洞利用
│       ├── 元数据端点利用
│       ├── 存储桶越权访问
│       ├── Serverless函数注入
│       └── IAM权限提升
│
└── 漏洞类型
    ├── 配置错误 → cloud-misconfiguration
    ├── 元数据暴露 → cloud-metadata-exposure
    ├── 存储安全 → cloud-storage-security
    ├── Serverless漏洞 → serverless-security
    └── IAM滥用 → cloud-iam-security
```

## [补充推演] 云安全测试工具链

| 类别 | 工具 | 用途 |
|---|---|---|
| 资源发现 | AWS CLI, Azure CLI, GCP CLI | 枚举云资源 |
| 存储桶扫描 | s3scanner, cloud_enum, bucket_finder | S3/Blob/GCS枚举 |
| 配置审计 | Prowler, Scout Suite, Checkov | IAM/配置审计 |
| 元数据测试 | curl, nmap, SSRF工具 | IMDS访问测试 |
| 权限分析 | AWS IAM Access Analyzer | IAM策略分析 |
| 基础设施扫描 | CloudMapper, Scout Suite | 云架构可视化 |
| Serverless测试 | Serverless Security Framework | Lambda/函数安全 |

## [补充推演] 跨Skill协作关系

| 场景 | 本Skill提供 | 衔接Skill |
|---|---|---|
| 云API安全测试 | 云服务API端点、密钥管理 | api-sec |
| IAM权限分析 | 身份与访问管理策略 | auth-sec |
| 云资源发现 | 资产枚举、子域名发现 | recon-for-sec |
| SSRF云元数据利用 | IMDS端点利用、内网穿透 | injection-checking |
| Serverless代码审计 | 函数代码分析、依赖漏洞 | reverse-engineering |