import requests
import json
import re

requests.packages.urllib3.disable_warnings()

import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

proxies = {"http": None, "https": None}

with open(r"e:\BaiduNetdiskDownload\1\kulaai_account.json", "r", encoding="utf-8") as f:
    account = json.load(f)

token = account["kula_ai"]["token"]
print(f"Token长度: {len(token)}")

api_base = "https://api.877ai.cn/api"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://kulaai.cn",
    "Referer": "https://kulaai.cn/",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

print("=" * 60)
print("分析签名机制")
print("=" * 60)

# 从JS中找签名相关代码
print("\n[1] 从JS中搜索签名相关代码...")
js_url = "https://kulaai.cn/assets/index-CMjn12iu.js"
r = requests.get(js_url, timeout=15, proxies=proxies, verify=False)
content = r.text

# 搜索签名相关关键词
sign_keywords = [
    'sign', 'signature', 'Sign', 'Signature',
    'hmac', 'HMAC', 'sha256', 'SHA256', 'md5', 'MD5',
    'timestamp', 'nonce', 'appKey', 'appkey', 'app_id', 'appId',
    'encrypt', 'decrypt', 'crypto', 'CryptoJS',
    'X-Sign', 'x-sign', 'X-Signature', 'x-signature',
]

for kw in sign_keywords:
    count = content.lower().count(kw.lower())
    if count > 0:
        print(f"  {kw}: {count} 次")

# 搜索请求头设置
print("\n[2] 搜索请求拦截器/axios配置...")
axios_patterns = [
    r'interceptors\.request\.use',
    r'headers\[[^\]]+\]\s*=',
    r'config\.headers',
    r'X-[A-Za-z-]+',
    r'x-[a-z-]+',
]

for pat in axios_patterns:
    matches = re.findall(pat, content, re.IGNORECASE)
    if matches:
        unique = set(matches)
        print(f"\n  模式 {pat[:30]}: {len(unique)} 个")
        for m in list(unique)[:10]:
            print(f"    - {m[:80]}")

# 搜索具体的X-头
print("\n[3] 搜索自定义请求头...")
x_headers = re.findall(r'"(X-[A-Za-z0-9-]+)"', content)
x_headers_lower = re.findall(r'"(x-[a-z0-9-]+)"', content)
all_x_headers = set(x_headers + x_headers_lower)

print(f"  找到 {len(all_x_headers)} 个X-头:")
for h in sorted(all_x_headers):
    print(f"    - {h}")

# 搜索sign函数
print("\n[4] 搜索签名函数定义...")
sign_funcs = re.findall(r'function\s+([a-zA-Z]*[Ss]ign[a-zA-Z]*)\s*\(', content)
sign_methods = re.findall(r'\.([a-zA-Z]*[Ss]ign[a-zA-Z]*)\s*=', content)
all_sign_funcs = set(sign_funcs + sign_methods)

print(f"  找到 {len(all_sign_funcs)} 个签名相关函数:")
for f in sorted(all_sign_funcs):
    print(f"    - {f}")

# 搜索timestamp和nonce
print("\n[5] 搜索时间戳/随机数相关代码...")
ts_keywords = ['Date.now', 'Date.parse', 'timestamp', 'nonce', 'randomString', 'uuid', 'Math.random']
for kw in ts_keywords:
    count = content.count(kw)
    if count > 0:
        print(f"  {kw}: {count} 次")

# 提取包含sign的上下文
print("\n[6] 提取签名相关代码上下文...")
sign_contexts = re.findall(r'.{0,100}[Ss]ign.{0,100}', content)
unique_ctx = set()
for ctx in sign_contexts[:30]:
    if len(ctx) > 30:
        unique_ctx.add(ctx[:150])

print(f"  找到 {len(unique_ctx)} 个上下文:")
for i, ctx in enumerate(list(unique_ctx)[:15]):
    print(f"\n  [{i+1}] {ctx}")

# 搜索完整的请求拦截器
print("\n[7] 搜索完整的请求拦截器...")
interceptor_matches = re.findall(r'interceptors\.request\.use[^}]{200,500}', content)
if interceptor_matches:
    print(f"  找到 {len(interceptor_matches)} 个拦截器:")
    for i, m in enumerate(interceptor_matches[:5]):
        print(f"\n  [{i+1}] {m[:300]}")

# 尝试不同的请求头组合
print("\n[8] 测试常见的自定义请求头...")
test_headers = [
    {},
    {"X-Sign": "test"},
    {"x-sign": "test"},
    {"X-Signature": "test"},
    {"X-Timestamp": str(int(__import__('time').time() * 1000))},
    {"x-timestamp": str(int(__import__('time').time() * 1000))},
    {"X-Nonce": "test123"},
    {"X-App-Key": "test"},
    {"appkey": "test"},
    {"X-Request-Id": "test"},
]

payload = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "hi"}],
    "stream": False
}

for extra_headers in test_headers:
    try:
        h = headers.copy()
        h.update(extra_headers)
        r = requests.post(api_base + "/chat/stream", json=payload, headers=h, timeout=10, proxies=proxies, verify=False)
        if r.status_code == 403 and '缺少签名' in r.text:
            pass
        else:
            header_name = list(extra_headers.keys())[0] if extra_headers else "(无额外头)"
            print(f"  [{r.status_code}] {header_name}: {r.text[:100]}")
    except Exception as e:
        pass
