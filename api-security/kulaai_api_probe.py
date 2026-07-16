import requests
import json

requests.packages.urllib3.disable_warnings()

import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

proxies = {"http": None, "https": None}

api_base = "https://api.877ai.cn/api"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://kulaai.cn",
    "Referer": "https://kulaai.cn/",
}

print("=" * 60)
print("[1] 测试常见API端点")
print("=" * 60)

endpoints = [
    "/models",
    "/model/list",
    "/v1/models",
    "/chat/models",
    "/chat/list",
    "/chat/completions",
    "/v1/chat/completions",
    "/conversation",
    "/session",
    "/user/info",
    "/auth/session",
    "/chat",
    "/generate",
    "/completions",
    "/image/generations",
    "/files",
    "/balance",
    "/usage",
    "/health",
    "/status",
]

for ep in endpoints:
    try:
        url = api_base + ep
        r = requests.get(url, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            ct = r.headers.get('Content-Type', '')
            print(f"\n[{r.status_code}] {ep} ({len(r.text)} bytes)")
            if 'json' in ct.lower():
                try:
                    data = r.json()
                    print(f"  JSON: {json.dumps(data, ensure_ascii=False)[:300]}")
                except:
                    print(f"  内容: {r.text[:200]}")
            elif r.status_code == 200:
                print(f"  内容: {r.text[:200]}")
    except Exception as e:
        pass

print()
print("=" * 60)
print("[2] 测试POST端点")
print("=" * 60)

post_endpoints = [
    "/chat/completions",
    "/v1/chat/completions",
    "/chat",
    "/generate",
    "/completions",
    "/conversation",
]

for ep in post_endpoints:
    try:
        url = api_base + ep
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "hi"}],
            "stream": False
        }
        r = requests.post(url, json=payload, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404 and r.status_code != 405:
            ct = r.headers.get('Content-Type', '')
            print(f"\n[{r.status_code}] POST {ep} ({len(r.text)} bytes)")
            if 'json' in ct.lower():
                try:
                    data = r.json()
                    print(f"  JSON: {json.dumps(data, ensure_ascii=False)[:300]}")
                except:
                    print(f"  内容: {r.text[:200]}")
            else:
                print(f"  内容: {r.text[:200]}")
    except Exception as e:
        pass

print()
print("=" * 60)
print("[3] 测试auth相关端点")
print("=" * 60)

auth_endpoints = [
    "/auth/resolve-host?host=kulaai.cn",
    "/auth/resolve-subdomain?subdomain=kulaai",
    "/auth/session",
    "/auth/login",
    "/auth/register",
]

for ep in auth_endpoints:
    try:
        url = api_base + ep
        r = requests.get(url, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            ct = r.headers.get('Content-Type', '')
            print(f"\n[{r.status_code}] {ep} ({len(r.text)} bytes)")
            if 'json' in ct.lower():
                try:
                    data = r.json()
                    print(f"  JSON: {json.dumps(data, ensure_ascii=False)[:500]}")
                except:
                    print(f"  内容: {r.text[:300]}")
            else:
                print(f"  内容: {r.text[:200]}")
    except Exception as e:
        print(f"  {ep}: {e}")

print()
print("=" * 60)
print("[4] 从kulaai.cn首页提取更多信息")
print("=" * 60)

try:
    resp = requests.get("https://kulaai.cn/", headers=headers, timeout=10, proxies=proxies, verify=False)
    
    import re
    script_tags = re.findall(r'<script[^>]*>(.*?)</script>', resp.text, re.DOTALL)
    for i, script in enumerate(script_tags):
        if len(script) > 50:
            print(f"\n--- Script {i+1} ({len(script)} chars) ---")
            print(script[:500])
            
except Exception as e:
    print(f"失败: {e}")

print()
print("=" * 60)
print("[5] 探测常见模型名称API")
print("=" * 60)

model_endpoints = [
    "/models",
    "/api/models",
    "/v1/models",
    "/option/models",
    "/config/models",
    "/setting/models",
]

for ep in model_endpoints:
    try:
        url = "https://api.877ai.cn" + ep
        r = requests.get(url, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code == 200 and len(r.text) > 50:
            ct = r.headers.get('Content-Type', '')
            print(f"\n[{r.status_code}] {ep} ({len(r.text)} bytes)")
            if 'json' in ct.lower():
                try:
                    data = r.json()
                    print(f"  JSON: {json.dumps(data, ensure_ascii=False)[:500]}")
                except:
                    pass
    except:
        pass

print()
print("=" * 60)
print("[6] 从JS中提取更多API信息")
print("=" * 60)

js_url = "https://kulaai.cn/assets/index-CMjn12iu.js"
try:
    r = requests.get(js_url, headers=headers, timeout=15, proxies=proxies, verify=False)
    content = r.text
    
    api_paths = re.findall(r'api[^"\']*["\']\s*:\s*["\']([^"\']+)', content)
    unique_paths = set(api_paths)
    print(f"找到 {len(unique_paths)} 个API路径:")
    for p in sorted(unique_paths)[:30]:
        print(f"  - {p}")
    
    print()
    model_names = re.findall(r'["\']([a-zA-Z0-9_.-]{5,40})["\']', content)
    model_filtered = [m for m in model_names if any(kw in m.lower() for kw in ['gpt', 'claude', 'gemini', 'gork', 'deepseek', 'qwen', 'glm', 'spark', 'kimi', 'doubao', 'llama', 'mistral'])]
    if model_filtered:
        print(f"模型名称: {sorted(set(model_filtered))}")
        
except Exception as e:
    print(f"失败: {e}")
