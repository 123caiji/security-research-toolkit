#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第三阶段: 针对性深度扫描
- 主站详细页面分析
- erp子域名多端口探测
- sitemap解析
- 针对性漏洞测试
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
# 1. 主站页面深度分析
# ============================================================
print("=" * 80)
print("  [1] 主站页面深度分析")
print("=" * 80)

try:
    r = session.get("https://www.hbwfjt.com/", timeout=15)
    body = r.text
    
    # 提取标题
    title = re.search(r'<title>(.*?)</title>', body, re.DOTALL)
    if title:
        print(f"  页面标题: {title.group(1).strip()[:80]}")
    
    # 提取所有链接
    links = re.findall(r'href=["\']([^"\']*)["\']', body)
    internal_links = [l for l in links if l.startswith("/") or "hbwfjt.com" in l]
    external_links = [l for l in links if l.startswith("http") and "hbwfjt.com" not in l]
    
    print(f"  内部链接: {len(internal_links)} 个")
    print(f"  外部链接: {len(external_links)} 个")
    
    # 提取JS/CSS文件
    js_files = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', body)
    css_files = re.findall(r'href=["\']([^"\']*\.css[^"\']*)["\']', body)
    print(f"  JS文件: {len(js_files)} 个")
    print(f"  CSS文件: {len(css_files)} 个")
    
    # 提取API端点
    api_endpoints = re.findall(r'["\'](?:/api/[^"\']*|/admin/[^"\']*|/manage/[^"\']*)["\']', body)
    if api_endpoints:
        print(f"  API端点: {list(set(api_endpoints))[:10]}")
    
    # 提取注释
    comments = re.findall(r'<!--(.*?)-->', body, re.DOTALL)
    if comments:
        print(f"  HTML注释: {len(comments)} 条")
        for c in comments[:5]:
            c = c.strip()[:100]
            if c:
                print(f"    <!-- {c} -->")
    
    # 提取内部IP
    internal_ips = re.findall(r'(?:10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)', body)
    if internal_ips:
        print(f"  内部IP: {list(set(internal_ips))}")
    
    # 提取邮箱
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', body)
    if emails:
        print(f"  邮箱: {list(set(emails))[:10]}")
    
    # 提取电话
    phones = re.findall(r'(?:1[3-9]\d{9}|0\d{2,3}-?\d{7,8})', body)
    if phones:
        print(f"  电话: {list(set(phones))[:10]}")
    
    # 提取form表单
    forms = re.findall(r'<form[^>]*action=["\']?([^"\'>\s]*)', body)
    if forms:
        print(f"  表单: {forms[:10]}")
    
    # 提取内部链接路径
    unique_paths = sorted(set([l.split("?")[0] for l in internal_links if l.startswith("/") and len(l) > 3]))
    print(f"\n  内部路径 ({len(unique_paths)}个):")
    for p in unique_paths[:30]:
        print(f"    {p}")

except Exception as e:
    print(f"  分析失败: {e}")

# ============================================================
# 2. sitemap.xml 深度分析
# ============================================================
print(f"\n{'='*80}")
print("  [2] sitemap.xml 深度分析")
print(f"{'='*80}")

try:
    r = session.get("https://www.hbwfjt.com/sitemap.xml", timeout=15)
    if r.status_code == 200:
        urls = re.findall(r'<loc>(.*?)</loc>', r.text)
        print(f"  总URL数: {len(urls)}")
        
        # 按路径分类
        categories = {}
        for url in urls:
            path = url.replace("https://www.hbwfjt.com", "").split("?")[0]
            parts = path.strip("/").split("/")
            cat = parts[0] if parts else "root"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(path)
        
        print(f"\n  路径分类:")
        for cat, paths in sorted(categories.items(), key=lambda x: -len(x[1])):
            print(f"    /{cat}/ -> {len(paths)} 个")
        
        # 找敏感路径
        sensitive_patterns = ["admin", "login", "manage", "system", "config", "api", 
                            "upload", "backup", "test", "debug", "console", "swagger"]
        print(f"\n  敏感路径检测:")
        for url in urls:
            for pattern in sensitive_patterns:
                if pattern in url.lower():
                    print(f"    ⚠️ {url}")
                    break
except Exception as e:
    print(f"  分析失败: {e}")

# ============================================================
# 3. robots.txt 分析
# ============================================================
print(f"\n{'='*80}")
print("  [3] robots.txt 分析")
print(f"{'='*80}")

try:
    r = session.get("https://www.hbwfjt.com/robots.txt", timeout=10)
    if r.status_code == 200:
        print(f"  内容:")
        for line in r.text.split("\n"):
            line = line.strip()
            if line:
                print(f"    {line}")
except Exception as e:
    print(f"  获取失败: {e}")

# ============================================================
# 4. erp.hbwfjt.com 多端口探测
# ============================================================
print(f"\n{'='*80}")
print("  [4] erp.hbwfjt.com 多端口探测")
print(f"{'='*80}")

erp_ip = "60.2.211.133"
erp_ports = {
    443: "HTTPS",
    8088: "可能的Web服务",
    8090: "可能的Web服务/ZLMediaKit",
    9090: "可能的管理后台",
    7001: "WebLogic",
}

for port, desc in erp_ports.items():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((erp_ip, port))
        sock.close()
        
        if result == 0:
            print(f"\n  ✅ 端口 {port} 开放 ({desc})")
            
            # 尝试HTTP请求
            for scheme in ["http", "https"]:
                try:
                    url = f"{scheme}://{erp_ip}:{port}/"
                    r = session.get(url, timeout=8, allow_redirects=False)
                    print(f"     {scheme}://{erp_ip}:{port}/ -> {r.status_code}")
                    if r.headers.get("Server"):
                        print(f"     Server: {r.headers.get('Server')}")
                    if r.headers.get("Location"):
                        print(f"     Location: {r.headers.get('Location')[:80]}")
                    if r.status_code == 200 and len(r.content) > 0:
                        title = re.search(r'<title>(.*?)</title>', r.text[:5000], re.DOTALL)
                        if title:
                            print(f"     标题: {title.group(1).strip()[:60]}")
                    break
                except:
                    pass
    except:
        pass

# ============================================================
# 5. 主站详细路径探测 (限速)
# ============================================================
print(f"\n{'='*80}")
print("  [5] 主站详细路径探测")
print(f"{'='*80}")

detail_paths = [
    # 管理后台
    "/admin", "/admin/", "/admin/login", "/manage/", "/manage/login",
    "/system/", "/system/login", "/backend/", "/console/",
    # API
    "/api/", "/api/v1/", "/api/v2/", "/api/swagger", "/api/docs",
    # 信息泄露
    "/phpinfo.php", "/info.php", "/test.php", "/debug/", "/trace",
    "/actuator", "/actuator/env", "/actuator/health", "/actuator/info",
    "/druid/", "/druid/index.html",
    "/swagger-ui.html", "/doc.html", "/v2/api-docs", "/v3/api-docs",
    # 常见CMS
    "/wp-admin/", "/wp-login.php", "/administrator/",
    # 备份/配置
    "/.git/config", "/.git/HEAD", "/.env", "/web.config",
    "/WEB-INF/web.xml", "/config/", "/backup/",
    # 其他
    "/user/", "/login", "/register", "/upload/", "/download/",
    "/editor/", "/kindeditor/", "/ueditor/",
]

for path in detail_paths:
    try:
        time.sleep(0.5)  # 限速
        url = f"https://www.hbwfjt.com{path}"
        r = session.get(url, timeout=8, allow_redirects=False)
        
        if r.status_code == 200:
            if len(r.content) > 50:
                print(f"  ✅ {path} -> 200 | {len(r.content)} bytes")
        elif r.status_code in [301, 302, 303, 307, 308]:
            loc = r.headers.get("Location", "")
            print(f"  ↪️  {path} -> {r.status_code} -> {loc[:60]}")
        elif r.status_code == 403:
            print(f"  🔒 {path} -> 403")
        elif r.status_code == 429:
            print(f"  ⏱️  {path} -> 429 限频，暂停5秒")
            time.sleep(5)
    except:
        pass

# ============================================================
# 6. Cookie安全检测
# ============================================================
print(f"\n{'='*80}")
print("  [6] Cookie安全检测")
print(f"{'='*80}")

try:
    r = session.get("https://www.hbwfjt.com/", timeout=10)
    set_cookies = r.headers.get("Set-Cookie", "")
    if set_cookies:
        print(f"  Set-Cookie: {set_cookies[:200]}")
        issues = []
        if "httponly" not in set_cookies.lower():
            issues.append("缺少HttpOnly标志")
        if "secure" not in set_cookies.lower():
            issues.append("缺少Secure标志")
        if "samesite" not in set_cookies.lower():
            issues.append("缺少SameSite标志")
        if issues:
            print(f"  ⚠️ Cookie安全问题: {', '.join(issues)}")
        else:
            print(f"  ✅ Cookie安全配置正常")
except:
    pass

# ============================================================
# 7. 安全头检测
# ============================================================
print(f"\n{'='*80}")
print("  [7] 安全响应头检测")
print(f"{'='*80}")

try:
    r = session.get("https://www.hbwfjt.com/", timeout=10)
    
    security_headers = {
        "Strict-Transport-Security": "HSTS",
        "Content-Security-Policy": "CSP",
        "X-Content-Type-Options": "X-Content-Type-Options",
        "X-Frame-Options": "X-Frame-Options",
        "X-XSS-Protection": "X-XSS-Protection",
        "Referrer-Policy": "Referrer-Policy",
        "Permissions-Policy": "Permissions-Policy",
    }
    
    for header, name in security_headers.items():
        value = r.headers.get(header)
        if value:
            print(f"  ✅ {name}: {value[:60]}")
        else:
            print(f"  ❌ {name}: 未设置")
except:
    pass

print(f"\n{'='*80}")
print("  扫描完成")
print(f"{'='*80}")
