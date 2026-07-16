import requests
import json
import time
import hashlib
import hmac
import base64
import random
import string

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
user_id = account["kula_ai"]["user_id"]

api_base = "https://api.877ai.cn/api"

base_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://kulaai.cn",
    "Referer": "https://kulaai.cn/",
    "Content-Type": "application/json",
}

payload = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "hi"}],
    "stream": False
}

print("=" * 60)
print("测试各种认证方式和签名")
print("=" * 60)

# 测试1: 不同的token位置
print("\n[1] 测试Token位置...")
token_tests = [
    ("Authorization: Bearer", {"Authorization": f"Bearer {token}"}),
    ("Authorization: Token", {"Authorization": f"Token {token}"}),
    ("X-Token", {"X-Token": token}),
    ("x-token", {"x-token": token}),
    ("token (header)", {"token": token}),
    ("access_token (header)", {"access_token": token}),
    ("X-Access-Token", {"X-Access-Token": token}),
    ("X-Auth-Token", {"X-Auth-Token": token}),
    ("X-User-Token", {"X-User-Token": token}),
    ("X-API-Key", {"X-API-Key": token}),
]

for name, extra in token_tests:
    try:
        h = base_headers.copy()
        h.update(extra)
        r = requests.post(api_base + "/chat/stream", json=payload, headers=h, timeout=10, proxies=proxies, verify=False)
        if r.status_code != 403:
            print(f"  ✅ [{r.status_code}] {name}: {r.text[:100]}")
        elif '签名' not in r.text:
            print(f"  ⚠️  [{r.status_code}] {name}: {r.text[:100]}")
    except:
        pass

# 测试2: 带时间戳的签名
print("\n[2] 测试带时间戳的签名...")
ts = str(int(time.time() * 1000))
nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

sign_params = [
    ("ts + token md5", {"X-Timestamp": ts, "X-Sign": hashlib.md5((token + ts).encode()).hexdigest()}),
    ("token + ts md5", {"X-Timestamp": ts, "X-Sign": hashlib.md5((ts + token).encode()).hexdigest()}),
    ("ts+nonce+token md5", {"X-Timestamp": ts, "X-Nonce": nonce, "X-Sign": hashlib.md5((ts + nonce + token).encode()).hexdigest()}),
    ("sha256 token+ts", {"X-Timestamp": ts, "X-Sign": hashlib.sha256((token + ts).encode()).hexdigest()}),
    ("md5 of body+token", {"X-Sign": hashlib.md5((json.dumps(payload) + token).encode()).hexdigest()}),
]

for name, extra in sign_params:
    try:
        h = base_headers.copy()
        h["Authorization"] = f"Bearer {token}"
        h.update(extra)
        r = requests.post(api_base + "/chat/stream", json=payload, headers=h, timeout=10, proxies=proxies, verify=False)
        if r.status_code != 403:
            print(f"  ✅ [{r.status_code}] {name}: {r.text[:150]}")
    except:
        pass

# 测试3: Cookie认证
print("\n[3] 测试Cookie认证...")
session = requests.Session()
session.verify = False
session.headers.update(base_headers)
session.cookies.set("token", token, domain="api.877ai.cn")

try:
    r = session.post(api_base + "/chat/stream", json=payload, timeout=10, proxies=proxies, verify=False)
    print(f"  Cookie token: [{r.status_code}] {r.text[:100]}")
except:
    pass

# 用登录后的session
print("\n[4] 使用登录后的Session...")
login_session = requests.Session()
login_session.verify = False
login_session.headers.update(base_headers)

login_resp = login_session.post(api_base + "/auth/login", json={
    "email": account["kula_ai"]["email"],
    "password": account["kula_ai"]["password"]
}, timeout=15, proxies=proxies, verify=False)

print(f"  登录状态: {login_resp.status_code}")
print(f"  Cookies: {dict(login_session.cookies)}")

# 用登录后的session请求聊天
r = login_session.post(api_base + "/chat/stream", json=payload, timeout=10, proxies=proxies, verify=False)
print(f"  聊天请求: [{r.status_code}] {r.text[:150]}")

# 测试5: user_id相关的签名
print("\n[5] 测试user_id相关签名...")
user_tests = [
    ("X-User-Id", {"X-User-Id": user_id}),
    ("userId", {"userId": user_id}),
    ("uid", {"uid": user_id}),
    ("X-UID", {"X-UID": user_id}),
]

for name, extra in user_tests:
    try:
        h = base_headers.copy()
        h["Authorization"] = f"Bearer {token}"
        h.update(extra)
        r = requests.post(api_base + "/chat/stream", json=payload, headers=h, timeout=10, proxies=proxies, verify=False)
        if r.status_code != 403:
            print(f"  ✅ [{r.status_code}] {name}: {r.text[:100]}")
    except:
        pass

# 测试6: 从网页获取必要参数
print("\n[6] 检查kulaai.cn页面中的注入参数...")
page_resp = requests.get("https://kulaai.cn/", headers=base_headers, timeout=15, proxies=proxies, verify=False)

import re
# 搜索可能的配置注入
config_patterns = [
    r'window\.__.*?__\s*=\s*({[^}]+})',
    r'const\s+[A-Z_]+KEY\s*=\s*["\']([^"\']+)["\']',
    r'APP_KEY["\s:=]+["\']([^"\']+)["\']',
    r'apiKey["\s:=]+["\']([^"\']+)["\']',
    r'secret["\s:=]+["\']([^"\']+)["\']',
    r'appId["\s:=]+["\']([^"\']+)["\']',
    r'appKey["\s:=]+["\']([^"\']+)["\']',
]

for pat in config_patterns:
    matches = re.findall(pat, page_resp.text, re.IGNORECASE)
    if matches:
        print(f"  模式 {pat[:30]}: {matches[:5]}")

# 搜索script中的数据
script_data = re.findall(r'<script[^>]*>([\s\S]*?)</script>', page_resp.text)
for i, script in enumerate(script_data):
    if len(script) > 50 and ('key' in script.lower() or 'token' in script.lower() or 'sign' in script.lower() or 'config' in script.lower()):
        print(f"\n  Script {i+1} ({len(script)} chars):")
        print(f"  {script[:300]}")

# 测试7: 检查响应头中的提示
print("\n[7] 检查403响应头中的提示...")
h = base_headers.copy()
h["Authorization"] = f"Bearer {token}"
r = requests.post(api_base + "/chat/stream", json=payload, headers=h, timeout=10, proxies=proxies, verify=False)
print(f"  状态码: {r.status_code}")
print(f"  响应体: {r.text}")
print(f"  响应头:")
for k, v in r.headers.items():
    print(f"    {k}: {v}")

# 测试8: 不同的API路径
print("\n[8] 测试不同的聊天API路径...")
chat_paths = [
    "/chat/stream",
    "/chat/completions",
    "/v1/chat/completions",
    "/api/v1/chat/completions",
    "/openai/chat/completions",
    "/completions",
    "/generate",
    "/conversation",
    "/send",
    "/message",
    "/ai/chat",
]

for path in chat_paths:
    try:
        h = base_headers.copy()
        h["Authorization"] = f"Bearer {token}"
        r = requests.post(api_base + path, json=payload, headers=h, timeout=8, proxies=proxies, verify=False)
        if r.status_code not in [404, 405]:
            print(f"  [{r.status_code}] POST {path}: {r.text[:100]}")
    except:
        pass
