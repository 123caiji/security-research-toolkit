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
print("[1] 测试无认证调用 /chat/completions")
print("=" * 60)

payload = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": False
}

try:
    r = requests.post(api_base + "/chat/completions", json=payload, headers=headers, timeout=15, proxies=proxies, verify=False)
    print(f"状态码: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type', 'N/A')}")
    print(f"响应长度: {len(r.text)}")
    print(f"响应内容: {r.text[:500]}")
except Exception as e:
    print(f"失败: {e}")

print()
print("=" * 60)
print("[2] 测试OpenAI兼容格式 /v1/chat/completions")
print("=" * 60)

try:
    r = requests.post("https://api.877ai.cn/v1/chat/completions", json=payload, headers=headers, timeout=15, proxies=proxies, verify=False)
    print(f"状态码: {r.status_code}")
    print(f"响应内容: {r.text[:500]}")
except Exception as e:
    print(f"失败: {e}")

print()
print("=" * 60)
print("[3] 测试带假API Key调用")
print("=" * 60)

headers_auth = headers.copy()
headers_auth["Authorization"] = "Bearer sk-test123456"

try:
    r = requests.post(api_base + "/chat/completions", json=payload, headers=headers_auth, timeout=15, proxies=proxies, verify=False)
    print(f"状态码: {r.status_code}")
    print(f"响应内容: {r.text[:500]}")
except Exception as e:
    print(f"失败: {e}")

print()
print("=" * 60)
print("[4] 测试 /chat 端点")
print("=" * 60)

try:
    r = requests.post(api_base + "/chat", json=payload, headers=headers, timeout=15, proxies=proxies, verify=False)
    print(f"状态码: {r.status_code}")
    print(f"响应内容: {r.text[:500]}")
except Exception as e:
    print(f"失败: {e}")

print()
print("=" * 60)
print("[5] 测试 /api/conversation 端点")
print("=" * 60)

try:
    r = requests.post(api_base + "/conversation", json=payload, headers=headers, timeout=15, proxies=proxies, verify=False)
    print(f"状态码: {r.status_code}")
    print(f"响应内容: {r.text[:500]}")
except Exception as e:
    print(f"失败: {e}")

print()
print("=" * 60)
print("[6] 测试 /api/auth/login 端点（查看登录方式）")
print("=" * 60)

login_payload = {
    "username": "test",
    "password": "test"
}

try:
    r = requests.post(api_base + "/auth/login", json=login_payload, headers=headers, timeout=15, proxies=proxies, verify=False)
    print(f"状态码: {r.status_code}")
    print(f"响应内容: {r.text[:500]}")
except Exception as e:
    print(f"失败: {e}")

print()
print("=" * 60)
print("[7] 测试 /api/user/info 端点")
print("=" * 60)

try:
    r = requests.get(api_base + "/user/info", headers=headers, timeout=15, proxies=proxies, verify=False)
    print(f"状态码: {r.status_code}")
    print(f"响应内容: {r.text[:500]}")
except Exception as e:
    print(f"失败: {e}")

print()
print("=" * 60)
print("[8] 测试 /api/keys 端点（获取API Key）")
print("=" * 60)

key_endpoints = [
    "/keys",
    "/api-keys",
    "/tokens",
    "/api-tokens",
    "/user/keys",
    "/user/tokens",
    "/settings/keys",
]

for ep in key_endpoints:
    try:
        r = requests.get(api_base + ep, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"[{r.status_code}] {ep}: {r.text[:200]}")
    except:
        pass

print()
print("=" * 60)
print("[9] 检查响应头中的认证信息")
print("=" * 60)

try:
    r = requests.get(api_base + "/chat/models", headers=headers, timeout=15, proxies=proxies, verify=False)
    print("响应头:")
    for k, v in r.headers.items():
        if any(x in k.lower() for x in ['auth', 'token', 'key', 'cookie', 'session', 'csrf']):
            print(f"  {k}: {v}")
except Exception as e:
    print(f"失败: {e}")

print()
print("=" * 60)
print("[10] 测试流式请求")
print("=" * 60)

stream_payload = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": True
}

try:
    r = requests.post(api_base + "/chat/completions", json=stream_payload, headers=headers, timeout=15, proxies=proxies, verify=False, stream=True)
    print(f"状态码: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type', 'N/A')}")
    chunk_count = 0
    for line in r.iter_lines():
        if line:
            chunk_count += 1
            if chunk_count <= 5:
                print(f"  Chunk {chunk_count}: {line.decode('utf-8', errors='ignore')[:200]}")
    print(f"总chunk数: {chunk_count}")
except Exception as e:
    print(f"失败: {e}")
