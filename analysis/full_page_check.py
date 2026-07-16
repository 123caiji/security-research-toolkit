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
print("完整检查所有页面内容")
print("="*70)

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
]

for page in pages:
    try:
        r = session.get(f"{TARGET}{page}", timeout=15)
        print(f"\n{'='*70}")
        print(f"页面: {page}")
        print(f"状态码: {r.status_code}")
        print(f"{'='*70}")
        print(f"完整HTML:\n{r.text}")
        
        # 搜索flag
        flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
        if flag_match:
            print(f"\n🚩🚩🚩 FLAG FOUND IN {page}: {flag_match.group(0)} 🚩🚩🚩")
            exit(0)
        
        # 搜索base64编码的内容
        import base64
        base64_matches = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', r.text)
        for b64 in base64_matches:
            try:
                decoded = base64.b64decode(b64).decode('utf-8', errors='replace')
                if 'flag' in decoded.lower():
                    print(f"\nBase64解码内容: {decoded}")
                    flag_match = re.search(r'flag\{[^}]+\}', decoded, re.IGNORECASE)
                    if flag_match:
                        print(f"\n🚩🚩🚩 FLAG FOUND IN BASE64: {flag_match.group(0)} 🚩🚩🚩")
                        exit(0)
            except:
                pass
        
        # 搜索HTML实体编码的内容
        decoded_html = html.unescape(r.text)
        flag_match2 = re.search(r'flag\{[^}]+\}', decoded_html, re.IGNORECASE)
        if flag_match2:
            print(f"\n🚩🚩🚩 FLAG FOUND IN HTML ENTITY: {flag_match2.group(0)} 🚩🚩🚩")
            exit(0)
        
        # 搜索URL编码的内容
        from urllib.parse import unquote
        decoded_url = unquote(r.text)
        flag_match3 = re.search(r'flag\{[^}]+\}', decoded_url, re.IGNORECASE)
        if flag_match3:
            print(f"\n🚩🚩🚩 FLAG FOUND IN URL ENCODED: {flag_match3.group(0)} 🚩🚩🚩")
            exit(0)
    except Exception as e:
        print(f"错误: {e}")

print("\n" + "="*70)
print("检查搜索页面完整响应")
print("="*70)

# 搜索关键词
r = session.get(f"{TARGET}/search", params={"q": "%"}, timeout=15)
print(f"\n搜索 '%' 的完整响应:")
print(f"状态码: {r.status_code}")
print(f"内容:\n{r.text}")

# 搜索flag
flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
if flag_match:
    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
    exit(0)

print("\n测试完成")