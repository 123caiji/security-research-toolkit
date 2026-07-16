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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

print("=" * 60)
print("[1] 下载JS并提取所有/api/路径")
print("=" * 60)

js_url = "https://kulaai.cn/assets/index-CMjn12iu.js"
r = requests.get(js_url, headers=headers, timeout=15, proxies=proxies, verify=False)
content = r.text

api_paths = re.findall(r'["`\'](/api/[a-zA-Z0-9_/\-]+)["`\']', content)
unique_paths = sorted(set(api_paths))
print(f"找到 {len(unique_paths)} 个/api/路径:")
for p in unique_paths:
    print(f"  - {p}")

print()
print("=" * 60)
print("[2] 提取所有/auth/路径")
print("=" * 60)

auth_paths = re.findall(r'["`\'](/auth/[a-zA-Z0-9_/\-]+)["`\']', content)
unique_auth = sorted(set(auth_paths))
print(f"找到 {len(unique_auth)} 个/auth/路径:")
for p in unique_auth:
    print(f"  - {p}")

print()
print("=" * 60)
print("[3] 提取所有/chat/路径")
print("=" * 60)

chat_paths = re.findall(r'["`\'](/chat/[a-zA-Z0-9_/\-]+)["`\']', content)
unique_chat = sorted(set(chat_paths))
print(f"找到 {len(unique_chat)} 个/chat/路径:")
for p in unique_chat:
    print(f"  - {p}")

print()
print("=" * 60)
print("[4] 搜索所有可能的POST端点")
print("=" * 60)

post_patterns = [
    r'fetch\(`[^`]*?(/[^`]+)`[^)]*\)',
    r'\.post\(`([^`]+)`',
    r'method:\s*["`]POST["`][^}]*?url:\s*["`]([^"`]+)',
]

for pat in post_patterns:
    matches = re.findall(pat, content)
    if matches:
        unique = sorted(set(matches))
        print(f"\n模式 {pat[:40]}:")
        for m in unique[:20]:
            if len(m) < 100:
                print(f"  - {m}")

print()
print("=" * 60)
print("[5] 搜索包含'send'或'message'的路径")
print("=" * 60)

msg_patterns = [
    r'["`\'](/[a-zA-Z0-9_/\-]*send[a-zA-Z0-9_/\-]*)["`\']',
    r'["`\'](/[a-zA-Z0-9_/\-]*message[a-zA-Z0-9_/\-]*)["`\']',
    r'["`\'](/[a-zA-Z0-9_/\-]*stream[a-zA-Z0-9_/\-]*)["`\']',
    r'["`\'](/[a-zA-Z0-9_/\-]*chat[a-zA-Z0-9_/\-]*)["`\']',
    r'["`\'](/[a-zA-Z0-9_/\-]*completion[a-zA-Z0-9_/\-]*)["`\']',
    r'["`\'](/[a-zA-Z0-9_/\-]*generate[a-zA-Z0-9_/\-]*)["`\']',
]

for pat in msg_patterns:
    matches = re.findall(pat, content, re.IGNORECASE)
    if matches:
        unique = sorted(set(matches))
        print(f"\n路径 ({len(unique)}个):")
        for m in unique[:20]:
            print(f"  - {m}")

print()
print("=" * 60)
print("[6] 搜索fetch调用完整上下文")
print("=" * 60)

fetch_calls = re.findall(r'fetch\(`?\$\{[^}]+\}([^`]+)`?[^)]*\)', content)
if fetch_calls:
    print(f"fetch调用 ({len(set(fetch_calls))}个):")
    for f in sorted(set(fetch_calls))[:30]:
        if len(f) < 100:
            print(f"  - {f}")

print()
print("=" * 60)
print("[7] 搜索baseURL和API配置")
print("=" * 60)

config_patterns = [
    r'baseURL["\s:]+["`]([^"`]+)["`]',
    r'API_BASE["\s:]+["`]([^"`]+)["`]',
    r'VITE_API["\s:]+["`]([^"`]+)["`]',
    r'apiBase["\s:]+["`]([^"`]+)["`]',
]

for pat in config_patterns:
    matches = re.findall(pat, content, re.IGNORECASE)
    if matches:
        for m in set(matches):
            print(f"  - {m}")

print()
print("=" * 60)
print("[8] 搜索完整URL路径（带变量）")
print("=" * 60)

template_urls = re.findall(r'`\$\{[^}]+\}([^`]+)`', content)
unique_templates = sorted(set(template_urls))
print(f"模板URL ({len(unique_templates)}个):")
for t in unique_templates[:30]:
    if len(t) < 80 and len(t) > 2:
        print(f"  - {t}")

print()
print("=" * 60)
print("[9] 尝试探测可能的聊天端点")
print("=" * 60)

api_base = "https://api.877ai.cn/api"
possible_endpoints = [
    "/chat/send",
    "/chat/message",
    "/chat/stream",
    "/chat/create",
    "/message/send",
    "/conversation/create",
    "/conversation/send",
    "/v1/chat/completions",
    "/openai/v1/chat/completions",
    "/proxy/chat/completions",
    "/relay/v1/chat/completions",
    "/api/v1/chat/completions",
]

for ep in possible_endpoints:
    try:
        url = api_base + ep
        payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}]}
        r = requests.post(url, json=payload, headers={**headers, "Content-Type": "application/json", "Origin": "https://kulaai.cn", "Referer": "https://kulaai.cn/"}, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"[{r.status_code}] POST {ep}: {r.text[:200]}")
    except:
        pass
