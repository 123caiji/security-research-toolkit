---
name: mobile-app-sec
description: >-
  Entry P1 category router for mobile application security. Use when testing Android/iOS applications, including reverse engineering, certificate pinning bypass, API security, and mobile-specific vulnerabilities.
---

# Mobile Application Security Router

这是移动应用（Android/iOS）安全测试的分类入口。

先用这个skill判断当前移动应用更偏向于逆向分析、证书劫持、API安全、本地存储，还是移动特有的漏洞类型，再进入更细的专题skill。

## When to Use

- 目标是Android APK或iOS IPA应用
- 需要测试移动应用的API通信、加密机制、本地存储
- 怀疑存在证书固定绕过、代码混淆、反调试绕过
- 需要分析移动应用的认证机制和权限滥用

## Skill Map

- [Android Reverse Engineering](../android-reverse-engineering/SKILL.md): APK反编译、代码分析、Frida动态Hook
- [iOS Reverse Engineering](../ios-reverse-engineering/SKILL.md): IPA解密、Mach-O分析、LLDB调试
- [Mobile API Security](../mobile-api-security/SKILL.md): 移动端API测试、请求伪造、签名绕过
- [Certificate Pinning Bypass](../certificate-pinning-bypass/SKILL.md): SSL/TLS证书劫持、Frida脚本绕过
- [Mobile Data Storage](../mobile-data-storage/SKILL.md): SharedPreferences、Keychain、SQLite数据泄露
- [Mobile Permission Abuse](../mobile-permission-abuse/SKILL.md): 权限过度申请、敏感权限滥用
- [Mobile Authentication](../mobile-authentication/SKILL.md): 本地认证绕过、生物识别漏洞、Token安全

## Quick Triage

| Observation | Route |
|---|---|
| Android APK文件 | [android-reverse-engineering](../android-reverse-engineering/SKILL.md) |
| iOS IPA文件 | [ios-reverse-engineering](../ios-reverse-engineering/SKILL.md) |
| SSL/TLS通信无法抓包 | [certificate-pinning-bypass](../certificate-pinning-bypass/SKILL.md) |
| 移动端API请求加密 | [mobile-api-security](../mobile-api-security/SKILL.md) |
| 本地存储敏感数据 | [mobile-data-storage](../mobile-data-storage/SKILL.md) |
| 权限弹窗异常 | [mobile-permission-abuse](../mobile-permission-abuse/SKILL.md) |
| 登录/认证流程异常 | [mobile-authentication](../mobile-authentication/SKILL.md) |

## Recommended Flow

1. 先确认目标平台（Android/iOS）
2. 再确认测试重点：逆向分析、API安全、数据存储、认证机制
3. 若需要抓包，先处理证书固定问题
4. 若需要动态分析，使用Frida/LLDB进行Hook

## Related Categories

- [api-sec](../api-sec/SKILL.md)
- [auth-sec](../auth-sec/SKILL.md)
- [reverse-engineering](../reverse-engineering/SKILL.md)

## [补充推演] 移动应用安全测试决策树

```
移动应用测试
├── 平台识别
│   ├── Android（APK）→ android-reverse-engineering
│   └── iOS（IPA）→ ios-reverse-engineering
│
├── 测试阶段
│   ├── 静态分析
│   │   ├── 代码混淆检测
│   │   ├── 加密算法识别
│   │   ├── 权限清单分析
│   │   └── 敏感API调用检测
│   │
│   ├── 动态分析
│   │   ├── Frida/LLDB Hook
│   │   ├── 运行时数据捕获
│   │   ├── 内存dump分析
│   │   └── 反调试绕过
│   │
│   └── 通信分析
│       ├── 证书固定检测
│       ├── 请求加密分析
│       ├── 签名算法破解
│       └── API接口测试
│
└── 漏洞类型
    ├── 认证绕过 → mobile-authentication
    ├── 数据泄露 → mobile-data-storage
    ├── 权限滥用 → mobile-permission-abuse
    ├── API安全 → mobile-api-security
    └── 代码注入 → android-reverse-engineering/ios-reverse-engineering
```

## [补充推演] 移动应用安全测试工具链

| 类别 | Android工具 | iOS工具 |
|---|---|---|
| 反编译 | apktool, jadx, dex2jar | class-dump, Hopper, IDA Pro |
| 动态分析 | Frida, Xposed, Substrate | Frida, Cycript, LLDB |
| 证书劫持 | JustTrustMe, SSLUnpinning | SSL Kill Switch |
| 抓包 | Burp Suite, Charles, Wireshark | Burp Suite, Charles, Proxyman |
| 代码审计 | QARK, MobSF, OWASP MSTG | MobSF, OWASP MSTG |
| 签名分析 | apksigner, jarsigner | codesign, ldid |
| 内存分析 | Volatility, frida-memory | Volatility, LLDB memory |

## [补充推演] 跨Skill协作关系

| 场景 | 本Skill提供 | 衔接Skill |
|---|---|---|
| 移动端API测试 | API请求分析、加密算法识别 | api-sec |
| 认证机制分析 | 本地Token安全、生物识别漏洞 | auth-sec |
| 代码逆向分析 | APK/IPA反编译、动态Hook | reverse-engineering |
| 数据加密分析 | 加密算法识别、密钥提取 | reverse-engineering |
| 内网渗透 | 移动设备作为内网入口 | internal-penetration |