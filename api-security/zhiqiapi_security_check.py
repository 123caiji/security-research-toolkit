import requests
import json
import re
import sys
from urllib.parse import urljoin, urlparse

requests.packages.urllib3.disable_warnings()

TARGET = "https://zhiqiapi.com/"
TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

session = requests.Session()
session.verify = False
session.headers.update(HEADERS)


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_headers():
    """检查安全响应头"""
    print_section("1. 安全响应头检查")
    
    try:
        r = session.get(TARGET, timeout=TIMEOUT, allow_redirects=True)
        print(f"\n  状态码: {r.status_code}")
        print(f"  最终URL: {r.url}")
        print(f"  服务器: {r.headers.get('Server', '未披露')}")
        print(f"  技术栈标识: {r.headers.get('X-Powered-By', '未披露')}")
        
        print("\n  --- 安全头检查 ---")
        
        security_headers = {
            "Strict-Transport-Security": "HSTS (HTTP严格传输安全)",
            "X-Frame-Options": "点击劫持防护",
            "X-Content-Type-Options": "MIME类型嗅探防护",
            "Content-Security-Policy": "内容安全策略",
            "X-XSS-Protection": "XSS防护(旧版)",
            "Referrer-Policy": "Referrer策略",
            "Permissions-Policy": "权限策略",
            "Cross-Origin-Opener-Policy": "跨域打开器策略",
            "Cross-Origin-Resource-Policy": "跨域资源策略",
        }
        
        missing = []
        for header, desc in security_headers.items():
            value = r.headers.get(header)
            status = "✅" if value else "❌ 缺失"
            print(f"  {status} {header} - {desc}")
            if value:
                print(f"         值: {value[:80]}")
            else:
                missing.append(header)
        
        print(f"\n  缺失的安全头数量: {len(missing)}")
        return r
        
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return None


def check_information_disclosure():
    """检查常见信息泄露点"""
    print_section("2. 信息泄露点探测")
    
    paths = [
        "robots.txt",
        "sitemap.xml",
        ".env",
        ".git/HEAD",
        "phpinfo.php",
        "info.php",
        ".DS_Store",
        "README.md",
        "package.json",
        "composer.json",
        ".gitignore",
        "crossdomain.xml",
        "clientaccesspolicy.xml",
        "swagger/",
        "swagger-ui.html",
        "api-docs",
        "docs/",
        "admin/",
        "login",
        "auth/login",
        "favicon.ico",
        "favicon.png",
    ]
    
    found = []
    
    for path in paths:
        url = urljoin(TARGET, path)
        try:
            r = session.get(url, timeout=TIMEOUT, allow_redirects=False)
            status = r.status_code
            length = len(r.content)
            
            if status in [200, 401, 403]:
                result = f"  ✅ [{status}] {path} ({length} bytes)"
                print(result)
                found.append({"path": path, "status": status, "length": length})
                
                if status == 200 and path.endswith('.txt') and length < 5000:
                    print(f"         内容预览: {r.text[:200]}")
            elif status == 301 or status == 302:
                print(f"  ➡️  [{status}] {path} -> {r.headers.get('Location', '?')}")
        except Exception as e:
            pass
    
    if not found:
        print("  未发现明显的信息泄露文件")
    
    return found


def check_cors():
    """检查CORS配置"""
    print_section("3. CORS (跨域资源共享) 配置检查")
    
    test_origins = [
        "https://evil.com",
        "http://localhost:8080",
        "null",
        "https://zhiqiapi.com.evil.com",
    ]
    
    results = []
    
    for origin in test_origins:
        try:
            headers = HEADERS.copy()
            headers["Origin"] = origin
            r = session.get(TARGET, headers=headers, timeout=TIMEOUT)
            
            acao = r.headers.get("Access-Control-Allow-Origin", "")
            acac = r.headers.get("Access-Control-Allow-Credentials", "")
            
            if acao:
                risk = ""
                if acao == "*":
                    risk = "⚠️  允许任意源 (通配符)"
                elif acao == origin:
                    risk = "⚠️  反射任意Origin"
                else:
                    risk = "✅ 特定源"
                
                print(f"  {risk}")
                print(f"     Origin: {origin}")
                print(f"     AC-AO: {acao}")
                print(f"     AC-AC: {acac}")
                results.append({"origin": origin, "acao": acao, "acac": acac})
        except Exception as e:
            pass
    
    if not results:
        print("  未检测到CORS响应头（可能未启用CORS）")
    
    return results


def analyze_js(response):
    """分析前端JS文件，提取API端点和敏感信息"""
    print_section("4. 前端JS文件分析")
    
    if not response:
        print("  无法获取页面内容，跳过JS分析")
        return []
    
    html = response.text
    
    js_files = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', html)
    js_files += re.findall(r'href=["\']([^"\']+\.js[^"\']*)["\']', html)
    
    js_files = list(set(js_files))
    print(f"\n  发现 {len(js_files)} 个JS文件")
    
    api_endpoints = set()
    secrets = []
    
    for js_path in js_files[:5]:
        js_url = urljoin(TARGET, js_path)
        print(f"\n  分析: {js_path[:80]}")
        
        try:
            r = session.get(js_url, timeout=TIMEOUT)
            if r.status_code != 200:
                print(f"    状态码: {r.status_code}, 跳过")
                continue
            
            content = r.text
            
            apis = re.findall(r'["\'](/[a-zA-Z0-9_/\-]+(?:api|auth|login|register|user|admin)[a-zA-Z0-9_/\-]*)["\']', content)
            apis += re.findall(r'["\'](https?://[a-zA-Z0-9._\-/]+(?:api|auth)[a-zA-Z0-9_/\-]*)["\']', content)
            
            for api in apis:
                if api not in api_endpoints:
                    api_endpoints.add(api)
                    print(f"    API: {api[:80]}")
            
            secret_patterns = [
                (r'(?:api[_-]?key|secret[_-]?key|token|password)\s*[:=]\s*["\']([^"\']{10,})["\']', "API Key/Secret"),
                (r'(?:AKIA|ASIA)[A-Z0-9]{16}', "AWS Access Key"),
                (r'sk_[a-zA-Z0-9]{20,}', "Stripe Key"),
                (r'ghp_[a-zA-Z0-9]{36}', "GitHub Token"),
                (r'AIza[a-zA-Z0-9_\-]{35}', "Google API Key"),
            ]
            
            for pattern, name in secret_patterns:
                matches = re.findall(pattern, content)
                for m in matches:
                    secret_val = m if isinstance(m, str) else m[0]
                    secrets.append({"type": name, "value": secret_val[:50] + "..."})
                    print(f"    ⚠️  疑似 {name}: {secret_val[:30]}...")
            
        except Exception as e:
            print(f"    请求失败: {e}")
    
    print(f"\n  共发现 {len(api_endpoints)} 个API端点")
    return list(api_endpoints), secrets


def check_tech_stack(response):
    """识别技术栈"""
    print_section("5. 技术栈识别")
    
    if not response:
        print("  无法获取页面")
        return
    
    html = response.text
    headers = response.headers
    
    techs = []
    
    server = headers.get("Server", "")
    powered = headers.get("X-Powered-By", "")
    
    if server:
        techs.append(f"服务器: {server}")
    if powered:
        techs.append(f"框架: {powered}")
    
    if 'vue' in html.lower():
        techs.append("前端框架: Vue.js")
    if 'react' in html.lower():
        techs.append("前端框架: React")
    if 'angular' in html.lower():
        techs.append("前端框架: Angular")
    if 'jquery' in html.lower():
        techs.append("前端库: jQuery")
    
    if 'wp-content' in html:
        techs.append("CMS: WordPress")
    if 'drupal' in html.lower():
        techs.append("CMS: Drupal")
    
    if '.php' in html:
        techs.append("后端语言: PHP (可能)")
    if 'jsp' in html.lower():
        techs.append("后端语言: Java/JSP (可能)")
    if 'aspx' in html.lower():
        techs.append("后端语言: ASP.NET (可能)")
    
    cookies = response.cookies
    for cookie in cookies:
        if 'PHPSESSID' in cookie.name:
            techs.append("会话: PHP Session")
        if 'JSESSIONID' in cookie.name:
            techs.append("会话: Java Session")
        if 'session' in cookie.name.lower():
            techs.append(f"会话Cookie: {cookie.name}")
    
    if techs:
        for t in techs:
            print(f"  📌 {t}")
    else:
        print("  未能识别明确的技术栈特征")
    
    print(f"\n  页面标题: {re.search(r'<title>(.*?)</title>', html, re.I).group(1) if re.search(r'<title>(.*?)</title>', html, re.I) else '未找到'}")
    print(f"  页面大小: {len(html)} bytes")


def check_error_handling():
    """检查错误处理和信息泄露"""
    print_section("6. 错误页面信息泄露检查")
    
    test_paths = [
        "nonexistent_page_12345.html",
        "api/nonexistent_endpoint_test",
        "<script>alert(1)</script>",
        "' OR 1=1--",
    ]
    
    error_signatures = [
        "Warning:",
        "Error:",
        "Fatal error",
        "Stack trace",
        "Traceback",
        "at line",
        "in /",
        "MySQL",
        "SQL syntax",
        "ORA-",
        "PostgreSQL",
        "Notice:",
        "Deprecated:",
        "phpMyAdmin",
    ]
    
    findings = []
    
    for path in test_paths:
        url = urljoin(TARGET, path)
        try:
            r = session.get(url, timeout=TIMEOUT)
            content = r.text.lower()
            
            for sig in error_signatures:
                if sig.lower() in content:
                    print(f"  ⚠️  [{r.status_code}] {path} - 检测到错误信息: {sig}")
                    findings.append({"path": path, "status": r.status_code, "signature": sig})
                    break
        except Exception as e:
            pass
    
    if not findings:
        print("  未检测到明显的错误信息泄露")
    
    return findings


def check_ssl_tls():
    """检查SSL/TLS基本配置"""
    print_section("7. SSL/TLS 配置检查")
    
    try:
        import ssl
        import socket
        from urllib.parse import urlparse
        
        parsed = urlparse(TARGET)
        host = parsed.hostname
        port = parsed.port or 443
        
        print(f"\n  目标: {host}:{port}")
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((host, port), timeout=TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                print(f"  协议版本: {ssock.version()}")
                print(f"  密码套件: {ssock.cipher()[0]}")
                
                cert = ssock.getpeercert(binary_form=False)
                if cert:
                    subject = dict(x[0] for x in cert.get('subject', []))
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    print(f"  证书主题: {subject.get('commonName', 'N/A')}")
                    print(f"  证书颁发者: {issuer.get('organizationName', issuer.get('commonName', 'N/A'))}")
                    print(f"  有效期至: {cert.get('notAfter', 'N/A')}")
                    
                    sans = cert.get('subjectAltName', [])
                    print(f"  SAN数量: {len(sans)}")
        
        print("\n  ✅ TLS连接正常")
        
    except Exception as e:
        print(f"  ❌ 检测失败: {e}")


def main():
    print("*" * 60)
    print("  ZHIQIAPI.COM 安全配置检测")
    print("  目标: " + TARGET)
    print("*" * 60)
    
    response = check_headers()
    check_tech_stack(response)
    check_ssl_tls()
    check_information_disclosure()
    check_cors()
    analyze_js(response)
    check_error_handling()
    
    print_section("检测完成")
    print("\n  ⚠️  免责声明:")
    print("  本检测仅用于安全配置自查，不涉及漏洞利用")
    print("  检测结果仅供参考，请结合实际业务进行评估")
    print("  如需进一步测试，请确保已获得授权")
    print()


if __name__ == "__main__":
    main()
