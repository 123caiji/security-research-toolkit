import requests
import json
import re
import socket
import ssl

requests.packages.urllib3.disable_warnings()

HOST = "119.29.238.216"
TIMEOUT = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

session = requests.Session()
session.verify = False
session.headers.update(HEADERS)


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_port_service(host, port, protocol="http"):
    """检查端口上的服务"""
    url = f"{protocol}://{host}:{port}"
    print(f"\n  检测: {url}")
    
    try:
        r = session.get(url, timeout=TIMEOUT, allow_redirects=True)
        print(f"  状态码: {r.status_code}")
        print(f"  最终URL: {r.url}")
        print(f"  服务器: {r.headers.get('Server', '未披露')}")
        print(f"  X-Powered-By: {r.headers.get('X-Powered-By', '未披露')}")
        
        if len(r.text) > 0:
            title = re.search(r'<title>(.*?)</title>', r.text, re.I)
            if title:
                print(f"  页面标题: {title.group(1)[:80]}")
            print(f"  页面大小: {len(r.text)} bytes")
            
            if len(r.text) < 3000:
                print(f"  页面内容预览:\n{r.text[:500]}")
        
        return r
    except requests.exceptions.RequestException as e:
        print(f"  请求失败: {e}")
        
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            r_ssl = session.get(f"https://{host}:{port}", timeout=TIMEOUT)
            print(f"  HTTPS成功: {r_ssl.status_code}")
            return r_ssl
        except:
            print(f"  HTTPS也失败")
            return None


def check_ssh_banner(host, port=22):
    """检查SSH服务"""
    print_section("SSH服务检测")
    print(f"\n  目标: {host}:{port}")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((host, port))
            
            banner = sock.recv(1024).decode().strip()
            print(f"  SSH Banner: {banner}")
            
            if "OpenSSH" in banner:
                version = re.search(r'OpenSSH_([\d.]+)', banner)
                if version:
                    print(f"  OpenSSH版本: {version.group(1)}")
                    if float(version.group(1)) < 8.0:
                        print(f"  ⚠️  OpenSSH版本较旧，可能存在已知漏洞")
            
            sock.close()
    except Exception as e:
        print(f"  获取Banner失败: {e}")


def check_port_8888():
    """详细检测8888端口"""
    print_section("8888端口详细检测")
    
    check_port_service(HOST, 8888, "http")
    
    paths = [
        "/",
        "/admin",
        "/login",
        "/api",
        "/swagger",
        "/docs",
        "/phpmyadmin",
        "/pma",
        "/adminer",
        "/webmin",
        "/宝塔",
        "/bt",
        "/console",
        "/panel",
        "/manage",
    ]
    
    print("\n  路径探测:")
    for path in paths:
        url = f"http://{HOST}:8888{path}"
        try:
            r = session.get(url, timeout=TIMEOUT, allow_redirects=False)
            if r.status_code in [200, 301, 302, 401, 403]:
                if r.status_code in [301, 302]:
                    print(f"  [{r.status_code}] {path} -> {r.headers.get('Location', '?')}")
                else:
                    print(f"  [{r.status_code}] {path} ({len(r.content)} bytes)")
        except:
            pass


def check_port_8088_deep():
    """详细检测8088端口（503错误）"""
    print_section("8088端口深度检测")
    
    print("\n  测试不同的请求方法和路径:")
    
    test_paths = [
        "/",
        "/index.html",
        "/index.php",
        "/default.aspx",
        "/api",
        "/health",
        "/status",
        "/ping",
    ]
    
    for path in test_paths:
        url = f"http://{HOST}:8088{path}"
        try:
            r = session.get(url, timeout=TIMEOUT)
            print(f"  GET {path}: [{r.status_code}]")
            if r.status_code != 503:
                print(f"     Content-Type: {r.headers.get('Content-Type', '')}")
                if len(r.text) > 0:
                    print(f"     内容: {r.text[:100]}")
        except:
            print(f"  GET {path}: [ERR]")


def check_cms_signatures():
    """检查CMS特征"""
    print_section("CMS识别")
    
    for port in [8088, 8888]:
        url = f"http://{HOST}:{port}"
        try:
            r = session.get(url, timeout=TIMEOUT)
            content = r.text.lower()
            
            cms_signatures = {
                "wordpress": ["wp-content", "wp-includes", "wp-admin"],
                "drupal": ["drupal", "sites/default"],
                "joomla": ["joomla", "jdocument"],
                "magento": ["magento", "mage"],
                "thinkphp": ["thinkphp", "tp5"],
                "laravel": ["laravel", "laravel_session"],
                "django": ["django", "csrfmiddlewaretoken"],
                "spring": ["spring", "whitelabel"],
                "nodejs": ["node", "express"],
                "baota": ["宝塔", "bt.cn"],
            }
            
            detected = []
            for cms, sigs in cms_signatures.items():
                for sig in sigs:
                    if sig in content:
                        detected.append(cms)
                        break
            
            if detected:
                print(f"  端口 {port}: 检测到 {', '.join(set(detected))}")
            else:
                print(f"  端口 {port}: 未识别到CMS特征")
                
        except:
            print(f"  端口 {port}: 无法访问")


def check_ssl_tls():
    """检查SSL/TLS"""
    print_section("SSL/TLS配置检查")
    
    for port in [8088, 8888]:
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((HOST, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=HOST) as ssock:
                    print(f"\n  端口 {port}:")
                    print(f"    协议: {ssock.version()}")
                    print(f"    密码套件: {ssock.cipher()[0]}")
        except Exception as e:
            print(f"  端口 {port}: TLS连接失败 ({e})")


def main():
    print("*" * 70)
    print("  119.29.238.216 深度安全检测")
    print("*" * 70)
    
    check_ssh_banner(HOST, 22)
    check_port_8088_deep()
    check_port_8888()
    check_ssl_tls()
    check_cms_signatures()
    
    print_section("检测完成")
    print()


if __name__ == "__main__":
    main()
