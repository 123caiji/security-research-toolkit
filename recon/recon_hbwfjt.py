#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目标信息收集与漏洞扫描脚本
目标: www.hbwfjt.com
说明: 仅做只读探测，不影响网站运行
"""

import requests
import socket
import ssl
import json
import time
import urllib3
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET = "www.hbwfjt.com"
TARGET_URL = "https://www.hbwfjt.com"

print("=" * 80)
print(f"  目标信息收集与漏洞扫描")
print(f"  目标: {TARGET}")
print(f"  时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ============================================================
# 第1步: DNS解析
# ============================================================
print(f"\n{'='*80}")
print("  [1] DNS解析")
print(f"{'='*80}")

try:
    ips = socket.getaddrinfo(TARGET, None)
    ip_list = list(set([ip[4][0] for ip in ips]))
    for ip in ip_list:
        print(f"  {TARGET} -> {ip}")
except Exception as e:
    print(f"  DNS解析失败: {e}")
    ip_list = []

# ============================================================
# 第2步: 端口扫描
# ============================================================
print(f"\n{'='*80}")
print("  [2] 常用端口扫描")
print(f"{'='*80}")

if ip_list:
    target_ip = ip_list[0]
    common_ports = [80, 443, 8080, 8443, 8888, 8081, 8088, 8090, 8099, 
                    9090, 3306, 6379, 27017, 22, 21, 3389, 1521, 5432]
    open_ports = []
    
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                print(f"  ✅ {target_ip}:{port} 开放")
                open_ports.append(port)
            sock.close()
        except:
            pass
    
    if not open_ports:
        print(f"  所有测试端口均已关闭或被过滤")
    print(f"\n  开放端口: {open_ports}")

# ============================================================
# 第3步: HTTP响应分析
# ============================================================
print(f"\n{'='*80}")
print("  [3] HTTP响应分析")
print(f"{'='*80}")

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})

try:
    resp = session.get(TARGET_URL, timeout=15, allow_redirects=True)
    print(f"  最终URL: {resp.url}")
    print(f"  状态码: {resp.status_code}")
    print(f"  Server: {resp.headers.get('Server', 'N/A')}")
    print(f"  X-Powered-By: {resp.headers.get('X-Powered-By', 'N/A')}")
    print(f"  Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
    print(f"  X-Frame-Options: {resp.headers.get('X-Frame-Options', 'N/A')}")
    print(f"  X-Content-Type-Options: {resp.headers.get('X-Content-Type-Options', 'N/A')}")
    print(f"  X-XSS-Protection: {resp.headers.get('X-XSS-Protection', 'N/A')}")
    print(f"  Strict-Transport-Security: {resp.headers.get('Strict-Transport-Security', 'N/A')}")
    print(f"  Content-Security-Policy: {resp.headers.get('Content-Security-Policy', 'N/A')[:80]}")
    print(f"  Set-Cookie: {resp.headers.get('Set-Cookie', 'N/A')[:100]}")
    
    # 识别技术栈
    body = resp.text
    techs = []
    if "nginx" in resp.headers.get("Server", "").lower():
        techs.append("Nginx")
    if "apache" in resp.headers.get("Server", "").lower():
        techs.append("Apache")
    if "iis" in resp.headers.get("Server", "").lower():
        techs.append("IIS")
    if "asp.net" in resp.headers.get("X-Powered-By", "").lower() or "asp.net" in body.lower():
        techs.append("ASP.NET")
    if "php" in resp.headers.get("X-Powered-By", "").lower() or ".php" in body.lower():
        techs.append("PHP")
    if "jsp" in body.lower() or ".do" in body.lower() or "java" in body.lower():
        techs.append("Java")
    if "spring" in body.lower():
        techs.append("Spring")
    if "vue" in body.lower() or "vue.js" in body.lower() or "vite" in body.lower():
        techs.append("Vue.js")
    if "react" in body.lower():
        techs.append("React")
    if "angular" in body.lower():
        techs.append("Angular")
    if "jquery" in body.lower():
        techs.append("jQuery")
    if "bootstrap" in body.lower():
        techs.append("Bootstrap")
    if "layui" in body.lower():
        techs.append("Layui")
    if "element" in body.lower():
        techs.append("Element UI")
    
    print(f"\n  识别技术栈: {', '.join(techs) if techs else '未识别'}")
    print(f"  页面大小: {len(body)} bytes")

except Exception as e:
    print(f"  连接失败: {e}")
    body = ""

# ============================================================
# 第4步: SSL证书信息
# ============================================================
print(f"\n{'='*80}")
print("  [4] SSL证书信息")
print(f"{'='*80}")

try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with ctx.wrap_socket(socket.socket(), server_hostname=TARGET) as s:
        s.settimeout(5)
        s.connect((TARGET, 443))
        cert = s.getpeercert(binary_form=False)
        if cert is None:
            # 尝试获取DER格式证书
            der_cert = s.getpeercert(True)
            print(f"  证书获取成功 (DER格式)")
        else:
            print(f"  证书主体: {cert.get('subject', 'N/A')}")
            print(f"  签发者: {cert.get('issuer', 'N/A')}")
            print(f"  有效期: {cert.get('notBefore', 'N/A')} ~ {cert.get('notAfter', 'N/A')}")
except Exception as e:
    print(f"  SSL信息获取: {e}")

# ============================================================
# 第5步: 常见路径探测
# ============================================================
print(f"\n{'='*80}")
print("  [5] 常见敏感路径探测 (只读GET请求)")
print(f"{'='*80}")

common_paths = [
    "/robots.txt",
    "/sitemap.xml",
    "/.git/config",
    "/.env",
    "/web.config",
    "/WEB-INF/web.xml",
    "/admin/",
    "/login",
    "/api/",
    "/swagger-ui.html",
    "/v2/api-docs",
    "/v3/api-docs",
    "/doc.html",
    "/actuator",
    "/actuator/env",
    "/actuator/health",
    "/druid/",
    "/druid/index.html",
    "/phpinfo.php",
    "/info.php",
    "/test.php",
    "/console/",
    "/manager/",
    "/index.php",
    "/wp-admin/",
    "/wp-login.php",
    "/backup/",
    "/db/",
    "/database/",
    "/.svn/entries",
    "/crossdomain.xml",
    "/favicon.ico",
    "/server-status",
    "/server-info",
    "/trace",
    "/metrics",
    "/env",
    "/health",
    "/info",
    "/dump",
    "/heapdump",
    "/jolokia",
]

found_paths = []
for path in common_paths:
    try:
        url = f"{TARGET_URL}{path}"
        r = session.get(url, timeout=5, allow_redirects=False)
        if r.status_code == 200 and len(r.content) > 10:
            found_paths.append((path, r.status_code, len(r.content), r.headers.get("Content-Type", "")))
            print(f"  ✅ {path} -> {r.status_code} | {len(r.content)} bytes | {r.headers.get('Content-Type', '')[:40]}")
        elif r.status_code in [301, 302, 303, 307, 308]:
            location = r.headers.get("Location", "")
            print(f"  ↪️  {path} -> {r.status_code} -> {location[:60]}")
        elif r.status_code == 403:
            print(f"  🔒 {path} -> 403 Forbidden")
    except:
        pass
    time.sleep(0.1)

print(f"\n  发现可访问路径: {len(found_paths)} 个")

# ============================================================
# 第6步: 常见子域名/同站探测
# ============================================================
print(f"\n{'='*80}")
print("  [6] 常见子域名探测")
print(f"{'='*80}")

subdomains = [
    "www", "mail", "ftp", "admin", "test", "dev", "staging", 
    "api", "app", "m", "wap", "oa", "crm", "erp", "hr",
    "vpn", "git", "jenkins", "ci", "jira", "wiki", "doc",
    "cdn", "img", "static", "assets", "blog", "forum",
    "shop", "pay", "sso", "auth", "login", "portal",
    "db", "mysql", "redis", "mongo", "es", "mq",
]

domain = TARGET.replace("www.", "")
found_subs = []

for sub in subdomains:
    try:
        hostname = f"{sub}.{domain}"
        ip = socket.gethostbyname(hostname)
        found_subs.append((hostname, ip))
        print(f"  ✅ {hostname} -> {ip}")
    except:
        pass
    time.sleep(0.05)

if not found_subs:
    print(f"  未发现额外子域名（常见前缀）")

# ============================================================
# 第7步: 敏感信息泄露检测
# ============================================================
print(f"\n{'='*80}")
print("  [7] 敏感信息泄露检测")
print(f"{'='*80}")

# robots.txt
try:
    r = session.get(f"{TARGET_URL}/robots.txt", timeout=5)
    if r.status_code == 200 and "disallow" in r.text.lower():
        print(f"\n  [robots.txt] 泄露内容:")
        lines = [l.strip() for l in r.text.split("\n") if l.strip() and not l.startswith("#")]
        for line in lines[:20]:
            print(f"    {line}")
except:
    pass

# 页面中的注释/敏感信息
try:
    r = session.get(TARGET_URL, timeout=10)
    if r.status_code == 200:
        # 注释
        comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
        if comments:
            print(f"\n  [HTML注释] 发现 {len(comments)} 条:")
            for c in comments[:5]:
                c = c.strip()[:100]
                if c:
                    print(f"    <!-- {c} -->")
        
        # 内部IP
        internal_ips = re.findall(r'(?:10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)', r.text)
        if internal_ips:
            print(f"\n  [内部IP泄露] 发现: {list(set(internal_ips))}")
        
        # 邮箱
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        if emails:
            print(f"\n  [邮箱泄露] 发现: {list(set(emails))[:5]}")
        
        # 电话
        phones = re.findall(r'(?:1[3-9]\d{9}|0\d{2,3}-?\d{7,8})', r.text)
        if phones:
            print(f"\n  [电话泄露] 发现: {list(set(phones))[:5]}")

except:
    pass

# ============================================================
# 汇总
# ============================================================
print(f"\n\n{'='*80}")
print("  信息收集完成")
print(f"{'='*80}")
print(f"  目标: {TARGET_URL}")
print(f"  IP: {', '.join(ip_list)}")
print(f"  开放端口: {open_ports}")
print(f"  发现路径: {len(found_paths)} 个")
print(f"  子域名: {len(found_subs)} 个")
print(f"{'='*80}")
