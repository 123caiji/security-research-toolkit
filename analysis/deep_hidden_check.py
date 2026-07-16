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
print("检查CSS文件完整内容")
print("="*70)

r = session.get(f"{TARGET}/style.css", timeout=15)
print(f"CSS完整内容:\n{r.text}")

# 在CSS中搜索flag
flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
if flag_match:
    print(f"\n🚩🚩🚩 FLAG FOUND IN CSS: {flag_match.group(0)} 🚩🚩🚩")
    exit(0)

print("\n" + "="*70)
print("检查所有静态文件")
print("="*70)

static_files = [
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml",
    "/manifest.json",
    "/sw.js",
    "/service-worker.js",
    "/config.json",
    "/settings.json",
    "/data.json",
    "/api.json",
    "/.well-known/security.txt",
    "/.well-known/flag.txt",
    "/humans.txt",
    "/ads.txt",
    "/app-ads.txt",
]

for path in static_files:
    try:
        r = session.get(f"{TARGET}{path}", timeout=10)
        if r.status_code == 200 and len(r.text) > 10:
            print(f"\n>>> {path}")
            print(f"状态码: {r.status_code}")
            print(f"内容类型: {r.headers.get('Content-Type', '')}")
            print(f"内容: {r.text[:500]}")
            
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    except:
        pass

print("\n" + "="*70)
print("检查隐藏HTML元素")
print("="*70)

# 检查主页面的隐藏元素
r = session.get(f"{TARGET}/", timeout=15)
html_content = r.text

# 检查隐藏属性
hidden_elements = re.findall(r'<[^>]*hidden[^>]*>(.*?)</[^>]*>', html_content)
print(f"\n隐藏元素: {hidden_elements}")

# 检查display:none的元素
display_none = re.findall(r'style=["\'][^"\']*display:\s*none[^"\']*["\'][^>]*>(.*?)<', html_content)
print(f"display:none元素: {display_none}")

# 检查注释中的内容
comments = re.findall(r'<!--(.*?)-->', html_content, re.DOTALL)
print(f"\nHTML注释: {comments}")

for comment in comments:
    flag_match = re.search(r'flag\{[^}]+\}', comment, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND IN COMMENT: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

# 检查base64编码的内容
base64_matches = re.findall(r'data:[^;]+;base64,[^"\'>\s]+', html_content)
print(f"\nBase64数据: {base64_matches[:3]}")

print("\n" + "="*70)
print("检查HTTP响应头中的信息")
print("="*70)

r = session.get(f"{TARGET}/", timeout=15)
print(f"\n所有响应头:")
for key, value in r.headers.items():
    print(f"  {key}: {value}")
    
    flag_match = re.search(r'flag\{[^}]+\}', value, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND IN HEADER: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

print("\n" + "="*70)
print("检查POST请求隐藏字段")
print("="*70)

# 获取登录页面并检查隐藏字段
r = session.get(f"{TARGET}/login", timeout=15)

# 检查所有input字段
inputs = re.findall(r'<input[^>]*>', r.text)
print(f"\n所有input字段:")
for input_field in inputs:
    print(f"  {input_field}")
    
    flag_match = re.search(r'flag\{[^}]+\}', input_field, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND IN INPUT: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

# 检查data属性
data_attrs = re.findall(r'data-[^=]+=["\']([^"\']+)["\']', r.text)
print(f"\nData属性: {data_attrs}")

for data_attr in data_attrs:
    flag_match = re.search(r'flag\{[^}]+\}', data_attr, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND IN DATA ATTR: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

print("\n" + "="*70)
print("检查JS脚本中的变量")
print("="*70)

# 检查内联JS
inline_js = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
print(f"\n内联JS: {inline_js}")

for js in inline_js:
    # 检查变量定义
    var_matches = re.findall(r'(var|let|const)\s+[^=]+\s*=\s*["\']([^"\']+)["\']', js)
    print(f"JS变量: {var_matches}")
    
    flag_match = re.search(r'flag\{[^}]+\}', js, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND IN JS: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

print("\n" + "="*70)
print("检查所有页面的完整源码")
print("="*70)

pages = [
    "/",
    "/login",
    "/upload",
    "/search",
    "/ping",
    "/backup",
    "/include",
    "/message",
    "/upload-source",
]

for page in pages:
    try:
        r = session.get(f"{TARGET}{page}", timeout=15)
        print(f"\n>>> {page}")
        print(f"内容长度: {len(r.text)}")
        
        # 检查flag
        flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
        if flag_match:
            print(f"\n🚩🚩🚩 FLAG FOUND IN {page}: {flag_match.group(0)} 🚩🚩🚩")
            exit(0)
        
        # 检查隐藏元素
        hidden = re.findall(r'<[^>]*hidden[^>]*>', r.text)
        if hidden:
            print(f"隐藏元素: {hidden}")
        
        # 检查注释
        comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
        if comments:
            print(f"注释: {comments}")
    except:
        pass

print("\n测试完成")