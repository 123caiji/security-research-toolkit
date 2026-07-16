import requests
import re
import json

requests.packages.urllib3.disable_warnings()

import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

proxies = {"http": None, "https": None}

base_url = "https://kulaai.cn"

print("=" * 60)
print("[1] 获取首页HTML")
print("=" * 60)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

try:
    resp = requests.get(base_url, headers=headers, timeout=15, proxies=proxies, verify=False)
    print(f"状态码: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
    print(f"页面大小: {len(resp.text)} 字符")
    
    title = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE | re.DOTALL)
    if title:
        print(f"页面标题: {title.group(1).strip()}")
    
    js_files = re.findall(r'<script[^>]+src="([^"]+\.js[^"]*)"', resp.text, re.IGNORECASE)
    css_files = re.findall(r'<link[^>]+href="([^"]+\.css[^"]*)"', resp.text, re.IGNORECASE)
    
    print(f"\n发现 {len(js_files)} 个JS文件:")
    for js in js_files[:10]:
        print(f"  - {js}")
    
    print(f"\n发现 {len(css_files)} 个CSS文件:")
    for css in css_files[:5]:
        print(f"  - {css}")
        
except Exception as e:
    print(f"访问失败: {e}")

print()
print("=" * 60)
print("[2] 分析JS文件中的API接口")
print("=" * 60)

api_patterns = [
    r'(?:api|API)\s*[:=]\s*[\'"]([^\'"]+)[\'"]',
    r'baseURL\s*[:=]\s*[\'"]([^\'"]+)[\'"]',
    r'fetch\(\s*[\'"]([^\'"]*api[^\'"]*)[\'"]',
    r'axios\.(?:get|post|put|delete)\(\s*[\'"]([^\'"]+)[\'"]',
    r'url\s*:\s*[\'"]([^\'"]*chat[^\'"]*)[\'"]',
    r'url\s*:\s*[\'"]([^\'"]*api[^\'"]*)[\'"]',
    r'["\'](/api/[^"\']+)["\']',
    r'["\']([^"\']*chat[^"\']*)["\']',
    r'["\']([^"\']*completion[^"\']*)["\']',
    r'["\']([^"\']*generate[^"\']*)["\']',
    r'["\']([^"\']*stream[^"\']*)["\']',
    r'["\']([^"\']*model[^"\']*)["\']',
]

model_patterns = [
    r'model["\s:]+["\']([^"\']*gpt[^"\']*)["\']',
    r'model["\s:]+["\']([^"\']*claude[^"\']*)["\']',
    r'model["\s:]+["\']([^"\']*llm[^"\']*)["\']',
    r'model["\s:]+["\']([^"\']*qwen[^"\']*)["\']',
    r'model["\s:]+["\']([^"\']*deepseek[^"\']*)["\']',
    r'model["\s:]+["\']([^"\']*glm[^"\']*)["\']',
    r'model["\s:]+["\']([^"\']*spark[^"\']*)["\']',
    r'model["\s:]+["\']([a-zA-Z0-9_-]{5,50})["\']',
    r'["\']model["\']\s*:\s*["\']([^"\']+)["\']',
]

all_apis = set()
all_models = set()

for js in js_files[:20]:
    try:
        js_url = js
        if not js.startswith('http'):
            if js.startswith('/'):
                js_url = base_url + js
            else:
                js_url = base_url + '/' + js
        
        print(f"\n分析: {js_url[:80]}...")
        r = requests.get(js_url, headers=headers, timeout=10, proxies=proxies, verify=False)
        
        if r.status_code == 200:
            content = r.text
            print(f"  大小: {len(content)} 字符")
            
            for pat in api_patterns:
                matches = re.findall(pat, content, re.IGNORECASE)
                for m in matches:
                    if len(m) > 5 and len(m) < 200:
                        all_apis.add(m)
            
            for pat in model_patterns:
                matches = re.findall(pat, content, re.IGNORECASE)
                for m in matches:
                    if len(m) > 2 and len(m) < 100:
                        all_models.add(m)
        else:
            print(f"  状态码: {r.status_code}")
            
    except Exception as e:
        print(f"  失败: {e}")

print()
print("=" * 60)
print("[3] 发现的API接口")
print("=" * 60)

for api in sorted(all_apis):
    print(f"  - {api}")

print()
print("=" * 60)
print("[4] 发现的模型名称")
print("=" * 60)

for model in sorted(all_models):
    print(f"  - {model}")

print()
print("=" * 60)
print("[5] 尝试常见AI接口路径")
print("=" * 60)

common_paths = [
    "/api/chat",
    "/api/chat/completions",
    "/api/completions",
    "/api/generate",
    "/api/stream",
    "/api/models",
    "/api/v1/chat/completions",
    "/api/v1/models",
    "/v1/chat/completions",
    "/v1/models",
    "/chat",
    "/api/conversation",
    "/api/message",
    "/api/ask",
    "/api/answer",
    "/api/ai/chat",
    "/api/ai/completion",
]

for path in common_paths:
    try:
        url = base_url + path
        r = requests.get(url, headers=headers, timeout=5, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"  [{r.status_code}] {path} - {len(r.text)} 字节")
            if r.status_code == 200:
                try:
                    data = r.json()
                    print(f"       JSON: {json.dumps(data, ensure_ascii=False)[:200]}")
                except:
                    pass
    except:
        pass
