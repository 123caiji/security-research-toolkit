import requests
import re
import os
import base64
import html
from urllib.parse import unquote

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
session = requests.Session()
session.verify = False
session.proxies = {}
session.headers.update({"User-Agent": "Mozilla/5.0"})

print("="*70)
print("深度检查所有页面中的隐藏信息")
print("="*70)

# 获取所有页面
pages = [
    "/",
    "/login",
    "/upload",
    "/upload-source",
    "/search",
    "/ping",
    "/backup",
    "/include",
    "/message",
    "/dashboard",
    "/style.css",
]

for page in pages:
    r = session.get(f"{TARGET}{page}", timeout=15)
    
    print(f"\n{'='*50}")
    print(f"页面: {page}")
    print(f"状态码: {r.status_code}")
    print(f"{'='*50}")
    
    # 检查响应头
    print(f"响应头:")
    for key, value in r.headers.items():
        print(f"  {key}: {value}")
        
        # 搜索flag在响应头中
        flag_match = re.search(r'flag\{[^}]+\}', value, re.IGNORECASE)
        if flag_match:
            print(f"\n🚩🚩🚩 FLAG FOUND IN HEADER: {flag_match.group(0)} 🚩🚩🚩")
            exit(0)
        
        # 检查Base64编码
        try:
            decoded = base64.b64decode(value).decode('utf-8', errors='replace')
            flag_match = re.search(r'flag\{[^}]+\}', decoded, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND IN BASE64 HEADER: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
        except:
            pass
    
    # 检查HTML注释
    comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
    if comments:
        print(f"\nHTML注释: {comments}")
        for comment in comments:
            flag_match = re.search(r'flag\{[^}]+\}', comment, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND IN COMMENT: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    
    # 检查隐藏的input字段
    hidden_inputs = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*value=["\']([^"\']+)["\']', r.text)
    if hidden_inputs:
        print(f"\n隐藏input值: {hidden_inputs}")
        for value in hidden_inputs:
            flag_match = re.search(r'flag\{[^}]+\}', value, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND IN HIDDEN INPUT: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
            
            # 检查Base64编码
            try:
                decoded = base64.b64decode(value).decode('utf-8', errors='replace')
                flag_match = re.search(r'flag\{[^}]+\}', decoded, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND IN BASE64 INPUT: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
            except:
                pass
    
    # 检查data属性
    data_attrs = re.findall(r'data-[a-z]+=["\']([^"\']+)["\']', r.text)
    if data_attrs:
        print(f"\ndata属性: {data_attrs}")
        for data in data_attrs:
            flag_match = re.search(r'flag\{[^}]+\}', data, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND IN DATA ATTR: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    
    # 检查内联JS
    inline_js = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL)
    if inline_js:
        print(f"\n内联JS:")
        for js in inline_js:
            flag_match = re.search(r'flag\{[^}]+\}', js, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND IN JS: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
            
            # 检查变量定义
            var_matches = re.findall(r'(var|let|const)\s+[a-zA-Z_]+\s*=\s*["\']([^"\']+)["\']', js)
            for var_name, var_value in var_matches:
                flag_match = re.search(r'flag\{[^}]+\}', var_value, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND IN JS VAR: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
    
    # 检查内联CSS
    inline_css = re.findall(r'<style[^>]*>(.*?)</style>', r.text, re.DOTALL)
    if inline_css:
        print(f"\n内联CSS:")
        for css in inline_css:
            flag_match = re.search(r'flag\{[^}]+\}', css, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND IN CSS: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    
    # 检查Base64编码内容
    b64_matches = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', r.text)
    if b64_matches:
        for b64 in b64_matches:
            try:
                decoded = base64.b64decode(b64).decode('utf-8', errors='replace')
                if 'flag' in decoded.lower():
                    print(f"\nBase64解码: {decoded}")
                    flag_match = re.search(r'flag\{[^}]+\}', decoded, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND IN BASE64: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
            except:
                pass
    
    # 检查URL编码内容
    url_encoded = re.findall(r'%[0-9A-F]{2}+', r.text)
    if url_encoded:
        decoded_url = unquote(r.text)
        flag_match = re.search(r'flag\{[^}]+\}', decoded_url, re.IGNORECASE)
        if flag_match:
            print(f"\n🚩🚩🚩 FLAG FOUND IN URL ENCODED: {flag_match.group(0)} 🚩🚩🚩")
            exit(0)
    
    # 检查HTML实体编码
    decoded_html = html.unescape(r.text)
    flag_match = re.search(r'flag\{[^}]+\}', decoded_html, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND IN HTML ENTITY: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)
    
    # 检查源码中可能的硬编码flag
    if "source-code" in r.text:
        source_match = re.search(r'<pre class="source-code">(.*?)</pre>', r.text, re.DOTALL)
        if source_match:
            source = html.unescape(source_match.group(1))
            
            # 搜索flag
            flag_match = re.search(r'flag\{[^}]+\}', source, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND IN SOURCE: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
            
            # 搜索敏感变量
            secrets = re.findall(r'(SECRET|FLAG|PASSWORD|KEY|TOKEN|ADMIN)\s*=\s*["\']([^"\']+)["\']', source, re.IGNORECASE)
            if secrets:
                print(f"\n源码中的敏感变量: {secrets}")

print("\n" + "="*70)
print("检查CSS文件完整内容")
print("="*70)

r = session.get(f"{TARGET}/style.css", timeout=15)
print(f"\nCSS完整内容:\n{r.text}")

# 搜索flag
flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
if flag_match:
    print(f"\n🚩🚩🚩 FLAG FOUND IN CSS: {flag_match.group(0)} 🚩🚩🚩")
    exit(0)

# 搜索CSS注释
css_comments = re.findall(r'/\*(.*?)\*/', r.text)
print(f"\nCSS注释: {css_comments}")

for comment in css_comments:
    flag_match = re.search(r'flag\{[^}]+\}', comment, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND IN CSS COMMENT: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

print("\n测试完成")