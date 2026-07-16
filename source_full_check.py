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
print("获取上传源码完整内容")
print("="*70)

r = session.get(f"{TARGET}/upload-source", timeout=15)

# 提取源码
source_match = re.search(r'<pre class="source-code">(.*?)</pre>', r.text, re.DOTALL)
if source_match:
    source = html.unescape(source_match.group(1))
    
    print(f"\n完整上传源码:\n")
    print(source)
    
    # 搜索flag
    flag_match = re.search(r'flag\{[^}]+\}', source, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND IN SOURCE: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)
    
    # 搜索FLAG变量
    flag_vars = re.findall(r'(FLAG|flag|SECRET|secret)\s*=\s*["\']([^"\']+)["\']', source, re.IGNORECASE)
    print(f"\n可能的FLAG变量: {flag_vars}")
    
    # 搜索关键词
    keywords = re.findall(r'(flag|secret|password|admin|root)', source, re.IGNORECASE)
    print(f"\n关键词出现次数: {len(keywords)}")
    
    # 保存源码到文件
    with open("upload_source_full.txt", "w", encoding="utf-8") as f:
        f.write(source)
    print("\n源码已保存到 upload_source_full.txt")

# 检查其他源码页面
print("\n" + "="*70)
print("检查其他源码页面")
print("="*70)

source_pages = [
    "/upload-source",
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
            
            # 提取源码
            source_match = re.search(r'<pre class="source-code">(.*?)</pre>', r.text, re.DOTALL)
            if source_match:
                source = html.unescape(source_match.group(1))
                print(f"源码长度: {len(source)}")
                
                # 搜索flag
                flag_match = re.search(r'flag\{[^}]+\}', source, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
                
                # 搜索FLAG变量
                flag_vars = re.findall(r'(FLAG|flag|SECRET|secret)\s*=\s*["\']([^"\']+)["\']', source, re.IGNORECASE)
                if flag_vars:
                    print(f"FLAG变量: {flag_vars}")
                
                # 显示前500字符
                print(f"源码前500字符:\n{source[:500]}")
            else:
                print(f"页面内容: {r.text[:300]}")
    except:
        pass

print("\n" + "="*70)
print("检查所有源码中的关键信息")
print("="*70)

# 下载所有源码页面并搜索
for page in source_pages:
    try:
        r = session.get(f"{TARGET}{page}", timeout=15)
        if r.status_code == 200:
            # 搜索所有内容
            flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND IN {page}: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
            
            # 搜索硬编码的密钥
            secret_matches = re.findall(r'(secret|key|password|token)\s*[=:]\s*["\']([^"\']+)["\']', r.text, re.IGNORECASE)
            if secret_matches:
                print(f"\n{page}中的密钥: {secret_matches}")
    except:
        pass

print("\n测试完成")