import requests
import json
import re
import socket
import ssl
from urllib.parse import urljoin, urlparse

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TARGET_HTTPS = "https://119.29.238.216:8088"
TIMEOUT = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

session = requests.Session()
session.verify = False
session.headers.update(HEADERS)


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_port(host, port, timeout=3):
    """检查单个端口是否开放"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except:
        return False


def port_scan():
    """端口扫描"""
    print_section("1. 端口扫描")
    
    host = "119.29.238.216"
    
    common_ports = [
        21, 22, 23, 25, 53, 80, 443, 8080, 8088, 8443,
        3306, 5432, 6379, 27017, 11211,
        3389, 5900, 5901,
        873, 2121, 990,
        1433, 1521, 5000, 5001,
        8888, 9090, 9091,
        27018, 27019,
        1025, 1026, 1027,
        8000, 8008, 8090,
        8880, 8899,
        3000, 3001, 5000,
        6000, 6001,
        7000, 7001,
        9200, 9300,
        11211,
        2181, 2888, 3888,
        8069, 8071,
        8883,
        9999, 10000,
    ]
    
    open_ports = []
    print(f"\n  正在扫描 {len(common_ports)} 个常用端口...")
    print(f"  目标: {host}\n")
    
    for port in sorted(common_ports):
        if check_port(host, port):
            open_ports.append(port)
            service = get_service_info(host, port)
            print(f"  ✅ [{port}] {service}")
    
    if open_ports:
        print(f"\n  共发现 {len(open_ports)} 个开放端口: {sorted(open_ports)}")
    else:
        print("  ❌ 未发现开放端口")
    
    return open_ports


def get_service_info(host, port):
    """获取端口服务信息"""
    common_services = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        443: "HTTPS",
        8080: "HTTP Proxy",
        8088: "HTTP (宝塔/应用)",
        8443: "HTTPS",
        3306: "MySQL",
        5432: "PostgreSQL",
        6379: "Redis",
        27017: "MongoDB",
        3389: "RDP",
        5900: "VNC",
        1433: "SQL Server",
        1521: "Oracle",
        873: "Rsync",
        9200: "Elasticsearch",
        11211: "Memcached",
        2181: "ZooKeeper",
        3000: "Node.js",
        5000: "FastAPI",
        6000: "X11",
    }
    return common_services.get(port, "未知服务")


def check_target_accessibility():
    """检查目标可达性"""
    print_section("2. 目标可达性检测")
    
    print(f"\n  目标: {TARGET}")
    
    try:
        r = session.get(TARGET, timeout=TIMEOUT, allow_redirects=True)
        print(f"\n  ✅ HTTP 请求成功")
        print(f"     状态码: {r.status_code}")
        print(f"     最终URL: {r.url}")
        print(f"     服务器: {r.headers.get('Server', '未披露')}")
        print(f"     X-Powered-By: {r.headers.get('X-Powered-By', '未披露')}")
        print(f"     页面标题: {re.search(r'<title>(.*?)</title>', r.text, re.I).group(1)[:50] if re.search(r'<title>(.*?)</title>', r.text, re.I) else '未找到'}")
        print(f"     页面大小: {len(r.text)} bytes")
        return r
    except requests.exceptions.RequestException as e:
        print(f"  ❌ HTTP 请求失败: {e}")
    
    print("\n  尝试 HTTPS...")
    try:
        r = session.get(TARGET_HTTPS, timeout=TIMEOUT, allow_redirects=True)
        print(f"  ✅ HTTPS 请求成功")
        print(f"     状态码: {r.status_code}")
        return r
    except requests.exceptions.RequestException as e:
        print(f"  ❌ HTTPS 请求失败: {e}")
    
    return None


def check_security_headers(response):
    """检查安全响应头"""
    print_section("3. 安全响应头检查")
    
    if not response:
        print("  无法获取响应，跳过")
        return
    
    security_headers = {
        "Strict-Transport-Security": "HSTS",
        "X-Frame-Options": "点击劫持防护",
        "X-Content-Type-Options": "MIME嗅探防护",
        "Content-Security-Policy": "内容安全策略",
        "X-XSS-Protection": "XSS防护",
        "Referrer-Policy": "Referrer策略",
        "Permissions-Policy": "权限策略",
        "Cross-Origin-Opener-Policy": "跨域隔离",
        "Cross-Origin-Resource-Policy": "跨域资源策略",
    }
    
    missing = []
    for header, desc in security_headers.items():
        value = response.headers.get(header)
        status = "✅" if value else "❌"
        print(f"  {status} {header} - {desc}")
        if value:
            print(f"       值: {value[:80]}")
        else:
            missing.append(header)
    
    print(f"\n  缺失的安全头数量: {len(missing)}")


def check_information_disclosure(response):
    """检查信息泄露点"""
    print_section("4. 信息泄露点探测")
    
    paths = [
        "robots.txt",
        "sitemap.xml",
        ".env",
        ".git/HEAD",
        "phpinfo.php",
        "info.php",
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
        "config.php",
        "db.php",
        "database.php",
        ".htaccess",
        "backup/",
        "backups/",
        "sql/",
        "data/",
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
                found.append({"path": path, "status": status})
                
                if status == 200 and length < 3000:
                    if path.endswith('.txt') or path.endswith('.md'):
                        print(f"         内容: {r.text[:150]}")
                    elif path.endswith('.php'):
                        if '<?php' in r.text or 'phpinfo' in r.text:
                            print(f"         ⚠️  疑似PHP源码泄露")
        except:
            pass
    
    if not found:
        print("  未发现明显的信息泄露文件")
    
    return found


def check_cors():
    """检查CORS配置"""
    print_section("5. CORS配置检查")
    
    test_origins = [
        "https://evil.com",
        "http://localhost:8080",
        "null",
    ]
    
    for origin in test_origins:
        try:
            headers = HEADERS.copy()
            headers["Origin"] = origin
            r = session.options(TARGET, headers=headers, timeout=TIMEOUT)
            
            acao = r.headers.get("Access-Control-Allow-Origin", "")
            acac = r.headers.get("Access-Control-Allow-Credentials", "")
            
            if acao:
                risk = "⚠️  危险" if acao == "*" else "✅"
                print(f"  {risk} Origin: {origin}")
                print(f"     AC-AO: {acao}")
                print(f"     AC-AC: {acac}")
        except:
            pass


def analyze_js(response):
    """分析前端JS文件"""
    print_section("6. 前端JS文件分析")
    
    if not response:
        print("  无法获取页面内容")
        return
    
    html = response.text
    js_files = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', html)
    
    if not js_files:
        print("  未发现JS文件")
        return
    
    print(f"\n  发现 {len(js_files)} 个JS文件")
    
    api_endpoints = set()
    
    for js_path in js_files[:3]:
        js_url = urljoin(TARGET, js_path)
        print(f"\n  分析: {js_path[:60]}")
        
        try:
            r = session.get(js_url, timeout=TIMEOUT)
            if r.status_code != 200:
                print(f"    状态码: {r.status_code}")
                continue
            
            content = r.text
            
            apis = re.findall(r'["\'](/[a-zA-Z0-9_/\-]+(?:api|auth|login|register|admin)[a-zA-Z0-9_/\-]*)["\']', content)
            for api in apis[:10]:
                if api not in api_endpoints:
                    api_endpoints.add(api)
                    print(f"    API: {api}")
            
            secrets = re.findall(r'(?:api[_-]?key|secret[_-]?key|token)\s*[:=]\s*["\']([^"\']{10,})["\']', content)
            if secrets:
                print(f"    ⚠️  发现疑似密钥: {secrets[0][:30]}...")
        
        except Exception as e:
            print(f"    请求失败: {e}")
    
    print(f"\n  共发现 {len(api_endpoints)} 个API端点")


def check_error_handling():
    """检查错误处理"""
    print_section("7. 错误页面信息泄露检查")
    
    test_paths = [
        "nonexistent_page_12345.html",
        "api/nonexistent_endpoint",
        "<script>alert(1)</script>",
        "' OR 1=1--",
    ]
    
    error_signatures = [
        "Warning:",
        "Error:",
        "Fatal error",
        "Stack trace",
        "Traceback",
        "MySQL",
        "SQL syntax",
        "ORA-",
        "phpMyAdmin",
    ]
    
    for path in test_paths:
        url = urljoin(TARGET, path)
        try:
            r = session.get(url, timeout=TIMEOUT)
            content = r.text.lower()
            
            for sig in error_signatures:
                if sig.lower() in content:
                    print(f"  ⚠️  [{r.status_code}] {path} - 检测到错误信息: {sig}")
                    break
        except:
            pass


def check_admin_paths():
    """检查管理后台路径"""
    print_section("8. 管理后台路径探测")
    
    admin_paths = [
        "/admin",
        "/admin/login",
        "/admin/index",
        "/admin/dashboard",
        "/swagger",
        "/swagger-ui",
        "/api-docs",
        "/v2/api-docs",
        "/docs",
        "/graphql",
        "/playground",
        "/console",
        "/panel",
        "/control",
        "/manage",
        "/wp-admin",
        "/phpmyadmin",
        "/pma",
        "/adminer",
        "/webmin",
        "/宝塔",
        "/bt",
    ]
    
    for path in admin_paths:
        url = urljoin(TARGET, path)
        try:
            r = session.get(url, timeout=TIMEOUT, allow_redirects=False)
            status = r.status_code
            
            if status in [200, 301, 302]:
                if status in [301, 302]:
                    print(f"  [{status}] {path} -> {r.headers.get('Location', '?')}")
                else:
                    content_type = r.headers.get("Content-Type", "")
                    print(f"  [{status}] {path} ({len(r.content)} bytes)")
                    if "text/html" in content_type and len(r.content) > 500:
                        title = re.search(r'<title>(.*?)</title>', r.text, re.I)
                        if title:
                            print(f"       标题: {title.group(1)[:50]}")
        except:
            pass


def check_default_credentials():
    """检查默认凭据"""
    print_section("9. 默认凭据测试")
    
    login_endpoints = [
        "/api/user/login",
        "/api/login",
        "/admin/login",
        "/login",
    ]
    
    default_creds = [
        ("admin", "admin"),
        ("admin", "admin123"),
        ("admin", "password"),
        ("root", "root"),
        ("test", "test"),
        ("admin", ""),
        ("", ""),
    ]
    
    for endpoint in login_endpoints:
        url = urljoin(TARGET, endpoint)
        try:
            r = session.get(url, timeout=TIMEOUT)
            if r.status_code in [200, 401]:
                print(f"\n  测试: {endpoint}")
                for username, password in default_creds[:3]:
                    try:
                        r = session.post(url, json={
                            "username": username,
                            "password": password,
                        }, timeout=TIMEOUT)
                        if r.status_code == 200:
                            try:
                                data = r.json()
                                if data.get("success") or data.get("token"):
                                    print(f"    ⚠️  {username}/{password} 可能成功！")
                                else:
                                    print(f"    [{r.status_code}] {username}/{password}: {data.get('message', '')[:30]}")
                            except:
                                print(f"    [{r.status_code}] {username}/{password}")
                    except:
                        pass
        except:
            pass


def check_db_exposure():
    """检查数据库暴露"""
    print_section("10. 数据库服务检查")
    
    host = "119.29.238.216"
    db_ports = [3306, 5432, 6379, 27017, 1433, 1521, 2181]
    
    for port in db_ports:
        if check_port(host, port):
            service = get_service_info(host, port)
            print(f"  ⚠️  [{port}] {service} 端口开放")


def main():
    print("*" * 70)
    print("  119.29.238.216:8088 安全检测")
    print("*" * 70)
    
    port_scan()
    response = check_target_accessibility()
    check_security_headers(response)
    check_information_disclosure(response)
    check_cors()
    analyze_js(response)
    check_error_handling()
    check_admin_paths()
    check_db_exposure()
    check_default_credentials()
    
    print_section("检测完成")
    print("\n  ⚠️  免责声明:")
    print("  本检测仅用于安全配置自查，不涉及漏洞利用")
    print("  检测结果仅供参考，请结合实际业务进行评估")
    print()


if __name__ == "__main__":
    main()
