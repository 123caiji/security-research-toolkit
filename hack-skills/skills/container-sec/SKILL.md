---
name: container-sec
description: >-
  Entry P1 category router for container security. Use when testing Docker, Kubernetes, and containerized environments, including container escape, image vulnerabilities, RBAC misconfiguration, and supply chain attacks.
---

# Container Security Router

这是容器化环境（Docker、Kubernetes）安全测试的分类入口。

先用这个skill判断当前容器环境更偏向于容器逃逸、镜像漏洞、RBAC配置错误、供应链攻击，还是Kubernetes集群安全问题，再进入更细的专题skill。

## When to Use

- 目标使用Docker容器
- 目标使用Kubernetes集群
- 需要测试容器镜像安全性
- 怀疑存在容器逃逸漏洞
- 需要分析Kubernetes RBAC配置和权限滥用

## Skill Map

- [Docker Security](../docker-security/SKILL.md): Docker配置安全、容器逃逸、镜像安全
- [Kubernetes Security](../kubernetes-security/SKILL.md): K8s集群安全、RBAC配置、Pod安全
- [Container Escape](../container-escape/SKILL.md): 容器逃逸技术、CVE利用、提权路径
- [Container Image Security](../container-image-security/SKILL.md): 镜像漏洞扫描、恶意镜像检测
- [Kubernetes RBAC](../kubernetes-rbac/SKILL.md): RBAC权限配置、ServiceAccount滥用
- [Container Supply Chain](../container-supply-chain/SKILL.md): 供应链攻击、镜像篡改、依赖漏洞

## Quick Triage

| Observation | Route |
|---|---|
| Docker容器运行 | [docker-security](../docker-security/SKILL.md) |
| Kubernetes集群 | [kubernetes-security](../kubernetes-security/SKILL.md) |
| 容器镜像可疑 | [container-image-security](../container-image-security/SKILL.md) |
| 特权容器运行 | [container-escape](../container-escape/SKILL.md) |
| ServiceAccount配置 | [kubernetes-rbac](../kubernetes-rbac/SKILL.md) |
| 镜像仓库可疑 | [container-supply-chain](../container-supply-chain/SKILL.md) |

## Recommended Flow

1. 先确认容器平台（Docker/Kubernetes）
2. 再确认测试重点：镜像安全、容器逃逸、K8s配置、RBAC
3. 先检查镜像漏洞和配置错误
4. 再检查容器逃逸和权限提升路径

## Related Categories

- [api-sec](../api-sec/SKILL.md)
- [auth-sec](../auth-sec/SKILL.md)
- [cloud-sec](../cloud-sec/SKILL.md)

## [补充推演] 容器安全测试决策树

```
容器安全测试
├── 容器平台识别
│   ├── Docker（单机）→ docker-security
│   ├── Kubernetes（集群）→ kubernetes-security
│   └── 混合环境 → 多平台综合测试
│
├── 测试阶段
│   ├── 镜像安全
│   │   ├── 基础镜像漏洞扫描
│   │   ├── 恶意镜像检测
│   │   ├── 镜像签名验证
│   │   └── 镜像仓库安全
│   │
│   ├── 容器运行时
│   │   ├── 容器逃逸测试
│   │   ├── 特权模式检测
│   │   ├── 挂载卷安全
│   │   └── 网络隔离测试
│   │
│   └── 集群安全（K8s）
│       ├── RBAC权限分析
│       ├── ServiceAccount安全
│       ├── NetworkPolicy配置
│       └── 控制平面安全
│
└── 漏洞类型
    ├── 容器逃逸 → container-escape
    ├── 镜像漏洞 → container-image-security
    ├── RBAC滥用 → kubernetes-rbac
    ├── 供应链攻击 → container-supply-chain
    └── 配置错误 → docker-security/kubernetes-security
```

## [补充推演] 容器安全测试工具链

| 类别 | 工具 | 用途 |
|---|---|---|
| 镜像扫描 | Trivy, Snyk, Clair | 漏洞扫描 |
| 容器安全 | Docker Bench Security | Docker配置审计 |
| K8s安全 | kube-bench, kube-hunter | K8s配置审计 |
| 容器逃逸 | cve-exploits, custom POC | CVE利用验证 |
| 镜像仓库 | Harbor, Quay安全扫描 | 仓库安全 |
| 供应链 | grype, syft | SBOM生成与验证 |
| 运行时 | Falco, Tracee | 运行时监控 |

## [补充推演] 跨Skill协作关系

| 场景 | 本Skill提供 | 衔接Skill |
|---|---|---|
| K8s API安全 | Kubernetes API端点测试 | api-sec |
| RBAC权限分析 | 角色与访问控制策略 | auth-sec |
| 云容器安全 | 云平台容器服务测试 | cloud-sec |
| 镜像漏洞分析 | 二进制漏洞检测 | reverse-engineering |
| 容器逃逸利用 | 本地提权、权限维持 | c2-remote-control |