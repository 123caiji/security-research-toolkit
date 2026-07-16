---
name: reverse-engineering
description: >-
  Entry P1 category router for reverse engineering. Use when analyzing binary code, firmware, web applications, and mobile applications, including decompilation, debugging, patching, and vulnerability discovery.
---

# Reverse Engineering Router

这是逆向工程与代码分析的分类入口。

先用这个skill判断当前目标更偏向于二进制分析、固件逆向、Web应用审计，还是移动应用逆向，再进入更细的专题skill。

## When to Use

- 需要分析二进制程序（PE/ELF/Mach-O）
- 需要逆向固件或嵌入式系统
- 需要审计Web应用源代码
- 需要分析加密算法或密钥提取
- 需要进行漏洞挖掘和POC开发

## Skill Map

- [Binary Analysis](../binary-analysis/SKILL.md): PE/ELF/Mach-O分析、调试器使用、漏洞挖掘
- [Firmware Reverse Engineering](../firmware-reverse-engineering/SKILL.md): 固件提取、QEMU仿真、嵌入式漏洞
- [Web Application Audit](../web-application-audit/SKILL.md): 源代码审计、框架漏洞、逻辑分析
- [Cryptography Analysis](../cryptography-analysis/SKILL.md): 加密算法识别、密钥提取、签名破解
- [Mobile Reverse Engineering](../mobile-reverse-engineering/SKILL.md): APK/IPA反编译、Frida Hook、证书绕过
- [Vulnerability Research](../vulnerability-research/SKILL.md): CVE分析、漏洞复现、POC开发

## Quick Triage

| Observation | Route |
|---|---|
| Windows PE文件 | [binary-analysis](../binary-analysis/SKILL.md) |
| Linux ELF文件 | [binary-analysis](../binary-analysis/SKILL.md) |
| 固件镜像 | [firmware-reverse-engineering](../firmware-reverse-engineering/SKILL.md) |
| Web应用源代码 | [web-application-audit](../web-application-audit/SKILL.md) |
| 加密通信分析 | [cryptography-analysis](../cryptography-analysis/SKILL.md) |
| APK/IPA文件 | [mobile-reverse-engineering](../mobile-reverse-engineering/SKILL.md) |

## Recommended Flow

1. 先确认目标类型（二进制/固件/Web/移动）
2. 再确认分析目标：漏洞挖掘、密钥提取、功能分析、POC开发
3. 选择合适的逆向工具链
4. 逐步深入分析：静态分析→动态分析→漏洞验证

## Related Categories

- [api-sec](../api-sec/SKILL.md)
- [mobile-app-sec](../mobile-app-sec/SKILL.md)
- [container-sec](../container-sec/SKILL.md)

## [补充推演] 逆向工程决策树

```
逆向工程分析
├── 目标类型识别
│   ├── 二进制程序（PE/ELF/Mach-O）→ binary-analysis
│   ├── 固件镜像 → firmware-reverse-engineering
│   ├── Web应用源代码 → web-application-audit
│   ├── 移动应用（APK/IPA）→ mobile-reverse-engineering
│   └── 加密通信/协议 → cryptography-analysis
│
├── 分析阶段
│   ├── 静态分析
│   │   ├── 反编译（IDA/Ghidra/Hopper）
│   │   ├── 字符串分析
│   │   ├── 函数调用图分析
│   │   └── 控制流分析
│   │
│   ├── 动态分析
│   │   ├── 调试器调试（GDB/WinDbg/LLDB）
│   │   ├── 内存dump分析
│   │   ├── 运行时数据捕获
│   │   └── Hook技术（Frida/Xposed）
│   │
│   └── 漏洞挖掘
│       ├── 代码审计
│       ├── Fuzz测试
│       ├── 漏洞验证
│       └── POC开发
│
└── 分析目标
    ├── 漏洞挖掘 → vulnerability-research
    ├── 密钥提取 → cryptography-analysis
    ├── 功能分析 → binary-analysis
    ├── 协议逆向 → cryptography-analysis
    └── 代码审计 → web-application-audit
```

## [补充推演] 逆向工程工具链

| 类别 | 工具 | 用途 |
|---|---|---|
| 反编译 | IDA Pro, Ghidra, Hopper, Binary Ninja | 二进制反编译 |
| 调试 | GDB, WinDbg, LLDB, x64dbg | 程序调试 |
| 固件 | binwalk, radare2, QEMU, Firmadyne | 固件分析 |
| Web审计 | SonarQube, Burp Suite, Semgrep | 源代码审计 |
| 加密分析 | openssl, cryptography libraries | 加密算法分析 |
| 移动逆向 | apktool, jadx, frida, class-dump | APK/IPA分析 |
| Fuzz测试 | AFL++, libFuzzer, Zzuf | 漏洞发现 |

## [补充推演] 跨Skill协作关系

| 场景 | 本Skill提供 | 衔接Skill |
|---|---|---|
| Web应用漏洞挖掘 | 源代码审计、框架分析 | api-sec |
| 移动应用逆向 | APK/IPA反编译、动态Hook | mobile-app-sec |
| 容器镜像分析 | 镜像漏洞扫描、二进制分析 | container-sec |
| 加密通信破解 | 密钥提取、协议分析 | api-sec |
| 漏洞利用开发 | CVE分析、POC开发 | injection-checking |