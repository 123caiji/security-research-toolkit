import requests
import re
import socket
import time

requests.packages.urllib3.disable_warnings()

HOST = "119.29.238.216"
TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

session = requests.Session()
session.verify = False
session.headers.update(HEADERS)

security_issues = []


def add_issue(severity, title, description, suggestion):
    """记录安全问题"""
    security_issues.append({
        "severity": severity,
        "title": title,
        "description": description,
        "suggestion": suggestion
    })
    print(f"\n  {severity} {title}")
    print(f"     描述: {description}")
    print(f"     建议: {suggestion}")


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_port(host, port, timeout=3):
    """检查端口是否开放"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            return sock.connect_ex((host, port)) == 0
    except:
        return False


def scan_ports():
    """端口扫描（轻量级）"""
    print_section("1. 端口扫描")
    
    common_ports = [21, 22, 23, 25, 53, 80, 443, 8080, 8088, 8888, 8443, 
                    3306, 5432, 6379, 27017, 3389, 5900]
    
    open_ports = []
    for port in common_ports:
        if check_port(HOST, port):
            open_ports.append(port)
            service = get_service_name(port)
            print(f"  ✅ [{port}] {service}")
            
            if port in [3306, 5432, 6379, 27017]:
                add_issue("🔴 高危", f"数据库端口 {port} 暴露", 
                    f"数据库服务({service})端口直接暴露在外网，可能被暴力破解",
                    "关闭外网访问，仅允许内网或特定IP访问")
            elif port in [21, 23]:
                add_issue("🟡 中危", f"明文协议端口 {port} 暴露",
                    f"{service}协议明文传输，密码可能被截获",
                    "禁用或改用加密协议")
    
    print(f"\n  共发现 {len(open_ports)} 个开放端口")
    return open_ports


def get_service_name(port):
    services = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 443: "HTTPS", 8080: "HTTP", 8088: "HTTP", 8888: "宝塔面板", 8443: "HTTPS",
        3306: "MySQL", 5432: "PostgreSQL", 6379: "Redis", 27017: "MongoDB",
        3389: "RDP", 5900: "VNC"
    }
    return services.get(port, "未知服务")


def check_ssh():
    """检查SSH服务"""
    print_section("2. SSH服务安全检查")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((HOST, 22))
            banner = sock.recv(1024).decode().strip()
            print(f"  SSH Banner: {banner}")
            
            if "OpenSSH" in banner:
                version = re.search(r'OpenSSH_([\d.]+)', banner)
                if version:
                    v = version.group(1)
                    print(f"  OpenSSH版本: {v}")
                    if float(v) < 8.0:
                        add_issue("🟡 中危", "OpenSSH版本较旧",
                            f"版本{v}可能存在已知漏洞",
                            "升级OpenSSH到最新版本")
            
            sock.close()
    except Exception as e:
        print(f"  获取Banner失败: {e}")
    
    add_issue("🟡 中危", "SSH默认端口暴露",
        "SSH服务运行在标准22端口，容易成为攻击目标",
        "修改SSH端口为非标准端口，禁用密码登录")


def check_baota_panel():
    """检查宝塔面板"""
    print_section("3. 宝塔面板安全检查")
    
    url = f"http://{HOST}:8888"
    
    try:
        r = session.get(url, timeout=TIMEOUT)
        print(f"  状态码: {r.status_code}")
        
        if r.status_code == 200:
            title = re.search(r'<title>(.*?)</title>', r.text, re.I)
            if title:
                print(f"  页面标题: {title.group(1)}")
            
            # 检查是否有安全相关信息
            if "宝塔" in r.text or "BT-Panel" in r.text:
                print("  ✅ 确认是宝塔面板")
                
                # 检查登录页面特征
                if "登录" in r.text or "login" in r.text.lower():
                    print("  ✅ 宝塔面板登录页面正常")
                else:
                    add_issue("🔴 高危", "宝塔面板可能未登录保护",
                        "未看到登录页面，可能存在访问控制问题",
                        "确认宝塔面板登录状态和访问控制")
            
            # 检查页面大小
            print(f"  页面大小: {len(r.text)} bytes")
            
            # 检查响应头
            server = r.headers.get('Server', '')
            if server:
                print(f"  Server: {server}")
            
        elif r.status_code == 503:
            print("  ⚠️  宝塔面板返回503（服务不可用）")
            add_issue("🟡 中危", "宝塔面板服务不可用",
                "宝塔面板返回503，可能正在维护或后端故障",
                "检查宝塔面板状态，确认服务是否正常运行")
            
    except Exception as e:
        print(f"  访问失败: {e}")
        add_issue("🔴 高危", "宝塔面板无法访问",
            f"无法访问宝塔面板: {e}",
            "检查宝塔面板是否运行，确认端口和防火墙配置")


def check_app_8088():
    """检查8088端口应用"""
    print_section("4. 8088端口应用检查")
    
    url = f"http://{HOST}:8088"
    
    try:
        r = session.get(url, timeout=TIMEOUT)
        print(f"  状态码: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('Content-Type', 'N/A')}")
        print(f"  Server: {r.headers.get('Server', '未披露')}")
        
        if r.status_code == 200:
            title = re.search(r'<title>(.*?)</title>', r.text, re.I)
            if title:
                print(f"  页面标题: {title.group(1)}")
            
            print(f"  页面大小: {len(r.text)} bytes")
            
            # 检查是否有安全头
            security_headers = ["X-Frame-Options", "X-Content-Type-Options", 
                               "Content-Security-Policy", "Strict-Transport-Security"]
            missing_headers = []
            for h in security_headers:
                if h not in r.headers:
                    missing_headers.append(h)
            
            if missing_headers:
                add_issue("🟡 中危", "缺少安全响应头",
                    f"缺少以下安全头: {', '.join(missing_headers)}",
                    "在Nginx配置中添加安全响应头")
            
            # 检查是否有敏感信息泄露
            sensitive_patterns = ["phpinfo", "mysql_connect", "database", 
                                 "password", "secret", "api_key"]
            for pattern in sensitive_patterns:
                if pattern in r.text.lower():
                    add_issue("🔴 高危", f"页面包含敏感信息({pattern})",
                        "页面内容可能泄露敏感信息",
                        "检查页面内容，移除敏感信息")
            
            # 检查CORS配置
            acao = r.headers.get('Access-Control-Allow-Origin', '')
            if acao == '*':
                add_issue("🔴 高危", "CORS配置允许任意源",
                    "Access-Control-Allow-Origin设置为*，可能导致跨域攻击",
                    "修改CORS配置，仅允许特定域名")
            
            return r.text
        
        elif r.status_code == 503:
            print("  ⚠️  应用返回503（服务不可用）")
            add_issue("🟡 中危", "8088端口应用服务不可用",
                "应用返回503，可能是后端服务故障",
                "检查后端应用状态，查看Nginx和应用日志")
            
    except Exception as e:
        print(f"  访问失败: {e}")
        add_issue("🟡 中危", "8088端口无法访问",
            f"无法访问8088端口: {e}",
            "检查Nginx配置和后端应用状态")


def check_security_headers():
    """检查安全响应头"""
    print_section("5. 安全响应头检查")
    
    for port in [8088, 8888]:
        url = f"http://{HOST}:{port}"
        try:
            r = session.get(url, timeout=TIMEOUT)
            
            if r.status_code == 200:
                print(f"\n  端口 {port}:")
                
                headers_to_check = {
                    "X-Frame-Options": "点击劫持防护",
                    "X-Content-Type-Options": "MIME嗅探防护",
                    "Content-Security-Policy": "内容安全策略",
                    "Strict-Transport-Security": "HSTS",
                    "Referrer-Policy": "Referrer策略",
                    "Permissions-Policy": "权限策略",
                }
                
                for header, desc in headers_to_check.items():
                    if header in r.headers:
                        print(f"    ✅ {header}: {r.headers[header][:50]}")
                    else:
                        print(f"    ❌ {header} - {desc}")
            
        except:
            pass


def check_robots():
    """检查robots.txt"""
    print_section("6. 信息泄露检查")
    
    urls = [
        f"http://{HOST}:8088/robots.txt",
        f"http://{HOST}:8888/robots.txt",
        f"http://{HOST}:8088/sitemap.xml",
        f"http://{HOST}:8088/.git/HEAD",
        f"http://{HOST}:8088/.env",
    ]
    
    for url in urls:
        try:
            r = session.get(url, timeout=TIMEOUT)
            if r.status_code == 200:
                print(f"\n  ✅ {url}")
                print(f"     内容: {r.text[:150]}")
                
                if ".git" in url:
                    add_issue("🔴 高危", "Git仓库信息泄露",
                        "可以访问.git目录，可能泄露源代码",
                        "删除.git目录或配置Web服务器禁止访问")
                elif ".env" in url:
                    add_issue("🔴 高危", "环境配置文件泄露",
                        ".env文件包含敏感配置信息",
                        "配置Web服务器禁止访问.env文件")
                        
        except:
            pass


def main():
    print("*" * 70)
    print("  宝塔服务器安全测试")
    print(f"  目标: {HOST}")
    print("*" * 70)
    print("\n  ⚠️  警告: 本测试仅进行安全配置检查")
    print("          不会执行任何可能影响服务器运行的操作")
    
    scan_ports()
    check_ssh()
    check_baota_panel()
    html = check_app_8088()
    check_security_headers()
    check_robots()
    
    print_section("安全隐患汇总")
    
    if security_issues:
        print(f"\n  共发现 {len(security_issues)} 个安全隐患")
        
        # 按严重程度排序
        severity_order = {"🔴 高危": 0, "🟡 中危": 1, "🟢 低危": 2}
        security_issues.sort(key=lambda x: severity_order.get(x['severity'], 2))
        
        for i, issue in enumerate(security_issues):
            print(f"\n  [{i+1}] {issue['severity']} {issue['title']}")
            print(f"      描述: {issue['description']}")
            print(f"      建议: {issue['suggestion']}")
    else:
        print("\n  ✅ 未发现明显安全隐患")
    
    print("\n" + "=" * 70)
    print("  测试完成")
    print("=" * 70)


if __name__ == "__main__":
    main()