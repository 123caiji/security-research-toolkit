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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://kulaai.cn",
    "Referer": "https://kulaai.cn/",
    "Content-Type": "application/json",
}

print("=" * 60)
print("[1] 探测所有可能的聊天端点")
print("=" * 60)

chat_endpoints = [
    "/chat/stream",
    "/chat/send",
    "/chat/message",
    "/chat/completion",
    "/chat/create",
    "/chat/start",
    "/conversation/create",
    "/conversation/start",
    "/message/send",
    "/ai/chat",
    "/ai/stream",
]

for ep in chat_endpoints:
    try:
        url = api_base + ep
        payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}]}
        r = requests.post(url, json=payload, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"[{r.status_code}] POST {ep}: {r.text[:300]}")
    except:
        pass

print()
print("=" * 60)
print("[2] 探测用户/认证端点")
print("=" * 60)

auth_endpoints = [
    "/auth/login",
    "/auth/register",
    "/auth/logout",
    "/auth/refresh",
    "/auth/me",
    "/auth/session",
    "/auth/token",
    "/auth/api-key",
    "/user/info",
    "/user/profile",
    "/user/api-key",
    "/user/keys",
    "/user/tokens",
    "/keys",
    "/tokens",
    "/api-key",
]

for ep in auth_endpoints:
    try:
        url = api_base + ep
        r = requests.get(url, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"[{r.status_code}] GET {ep}: {r.text[:300]}")
    except:
        pass

for ep in auth_endpoints:
    try:
        url = api_base + ep
        r = requests.post(url, json={}, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"[{r.status_code}] POST {ep}: {r.text[:300]}")
    except:
        pass

print()
print("=" * 60)
print("[3] 测试登录接口格式")
print("=" * 60)

login_payloads = [
    {"email": "test@test.com", "password": "test123"},
    {"username": "test", "password": "test123"},
    {"account": "test@test.com", "password": "test123"},
    {"phone": "13800138000", "password": "test123"},
]

for payload in login_payloads:
    try:
        r = requests.post(api_base + "/auth/login", json=payload, headers=headers, timeout=8, proxies=proxies, verify=False)
        print(f"Payload {list(payload.keys())}: [{r.status_code}] {r.text[:200]}")
    except Exception as e:
        print(f"失败: {e}")

print()
print("=" * 60)
print("[4] 测试注册接口")
print("=" * 60)

register_payload = {
    "email": "test_test123@example.com",
    "password": "Test123456!",
    "username": "testuser12345"
}

try:
    r = requests.post(api_base + "/auth/register", json=register_payload, headers=headers, timeout=8, proxies=proxies, verify=False)
    print(f"注册响应 [{r.status_code}]: {r.text[:500]}")
    print(f"响应头: {dict(r.headers)}")
except Exception as e:
    print(f"失败: {e}")

print()
print("=" * 60)
print("[5] 探测OpenAI兼容路径")
print("=" * 60)

openai_paths = [
    "/v1/chat/completions",
    "/v1/models",
    "/v1/completions",
    "/openai/v1/chat/completions",
    "/openai/chat/completions",
    "/proxy/v1/chat/completions",
    "/relay/v1/chat/completions",
]

for ep in openai_paths:
    try:
        url = "https://api.877ai.cn" + ep
        r = requests.get(url, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"[{r.status_code}] GET {ep}: {r.text[:200]}")
        r = requests.post(url, json={"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"hi"}]}, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"[{r.status_code}] POST {ep}: {r.text[:200]}")
    except:
        pass

print()
print("=" * 60)
print("[6] 检查kulaai.cn是否有单独的API")
print("=" * 60)

kulaai_apis = [
    "https://kulaai.cn/api/chat/models",
    "https://kulaai.cn/api/chat/stream",
    "https://kulaai.cn/api/auth/login",
    "https://kulaai.cn/api/auth/register",
    "https://kulaai.cn/api/v1/chat/completions",
]

for url in kulaai_apis:
    try:
        r = requests.get(url, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404 and len(r.text) != 7393:
            print(f"[{r.status_code}] GET {url}: {r.text[:200]}")
        r = requests.post(url, json={"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"hi"}]}, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404 and len(r.text) != 7393:
            print(f"[{r.status_code}] POST {url}: {r.text[:200]}")
    except:
        pass

print()
print("=" * 60)
print("[7] 检查 OPTIONS / CORS 信息")
print("=" * 60)

try:
    r = requests.options(api_base + "/chat/stream", headers=headers, timeout=8, proxies=proxies, verify=False)
    print(f"OPTIONS /chat/stream [{r.status_code}]")
    for k, v in r.headers.items():
        if any(x in k.lower() for x in ['allow', 'access', 'method', 'cors']):
            print(f"  {k}: {v}")
except Exception as e:
    print(f"失败: {e}")

print()
print("=" * 60)
print("[8] 查看chat/stream的响应头")
print("=" * 60)

try:
    r = requests.post(api_base + "/chat/stream", json={"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"hi"}]}, headers=headers, timeout=8, proxies=proxies, verify=False)
    print(f"状态码: {r.status_code}")
    print(f"响应头:")
    for k, v in r.headers.items():
        print(f"  {k}: {v}")
    print(f"响应内容: {r.text[:500]}")
except Exception as e:
    print(f"失败: {e}")
