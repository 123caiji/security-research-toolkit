import requests
import json
import string
import random
import re

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
print("[1] 测试免登录的功能")
print("=" * 60)

session = requests.Session()
session.verify = False
session.headers.update(headers)

# 测试模型列表
print("\n1.1 模型列表:")
r = session.get(api_base + "/chat/models", timeout=15, proxies=proxies, verify=False)
models_data = r.json()
print(f"  模型分组数: {len(models_data)}")
for g in models_data:
    print(f"  - {g['name']} ({len(g['subModels'])}个模型)")

# 测试其他免登录端点
print("\n1.2 免登录端点测试:")
endpoints = [
    ("/chat/models", "GET", "模型列表"),
    ("/auth/resolve-host?host=kulaai.cn", "GET", "主机解析"),
    ("/tracking/pageview", "POST", "页面统计"),
]

for ep, method, desc in endpoints:
    try:
        if method == "GET":
            r = session.get(api_base + ep, timeout=8, proxies=proxies, verify=False)
        else:
            r = session.post(api_base + ep, json={}, timeout=8, proxies=proxies, verify=False)
        status = "✅" if r.status_code == 200 else "❌"
        print(f"  {status} [{r.status_code}] {desc} - {ep}")
    except Exception as e:
        print(f"  ❌ {desc} - 失败: {e}")

print()
print("=" * 60)
print("[2] 探测游客/免登录聊天")
print("=" * 60)

guest_tests = [
    ("/chat/stream", "POST", {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}], "stream": False}),
    ("/chat/completions", "POST", {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}]}),
    ("/free-chat", "POST", {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}]}),
    ("/trial/chat", "POST", {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}]}),
    ("/chat/free", "POST", {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}]}),
    ("/v1/chat/completions", "POST", {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}]}),
]

print("\n2.1 测试免登录聊天端点:")
for ep, method, payload in guest_tests:
    try:
        r = session.post(api_base + ep, json=payload, timeout=15, proxies=proxies, verify=False)
        if r.status_code == 200:
            print(f"  ✅ [{r.status_code}] {ep} - 可能可用!")
            print(f"     响应: {r.text[:200]}")
        elif r.status_code == 401:
            print(f"  ⚠️  [{r.status_code}] {ep} - 需要登录")
        else:
            print(f"  ❌ [{r.status_code}] {ep}")
    except Exception as e:
        print(f"  ❌ {ep} - 失败: {e}")

print()
print("=" * 60)
print("[3] 测试发送验证码")
print("=" * 60)

# 生成随机邮箱
random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
test_email = f"{random_name}@example.com"
print(f"随机邮箱: {test_email}")

# 发送注册验证码
print("\n3.1 发送注册验证码:")
r = session.post(api_base + "/auth/send-code", json={
    "email": test_email,
    "type": "register"
}, timeout=15, proxies=proxies, verify=False)
print(f"  状态码: {r.status_code}")
print(f"  响应: {r.text}")

# 尝试其他类型
print("\n3.2 测试其他验证码类型:")
for ctype in ["login", "reset", "email", "bind"]:
    try:
        tmp_email = f"test{random.randint(1000,9999)}@example.com"
        r = session.post(api_base + "/auth/send-code", json={"email": tmp_email, "type": ctype}, timeout=8, proxies=proxies, verify=False)
        if r.status_code == 201 or r.status_code == 200:
            print(f"  ✅ [{r.status_code}] type={ctype}")
        else:
            print(f"  ❌ [{r.status_code}] type={ctype}: {r.text[:100]}")
    except:
        pass

print()
print("=" * 60)
print("[4] 探测注册所需字段")
print("=" * 60)

# 用错误的验证码测试，看需要哪些字段
register_payloads = [
    {"email": test_email, "password": "Test123456", "code": "000000"},
    {"email": test_email, "password": "Test123456", "username": "testuser", "code": "000000"},
    {"email": test_email, "password": "Test123456", "code": "000000", "invite_code": ""},
    {"email": test_email, "password": "Test123456", "code": "000000", "referral_code": ""},
]

print("\n4.1 测试注册字段组合:")
for payload in register_payloads:
    try:
        r = session.post(api_base + "/auth/register", json=payload, timeout=10, proxies=proxies, verify=False)
        keys = list(payload.keys())
        if "验证码无效" in r.text or "code" in r.text.lower():
            print(f"  ⚠️  [{r.status_code}] 字段: {', '.join(keys)} - 验证码错误(字段正确)")
        elif "缺少" in r.text or "请提供" in r.text:
            print(f"  ❌ [{r.status_code}] 字段: {', '.join(keys)} - {r.text[:100]}")
        else:
            print(f"  ❓ [{r.status_code}] 字段: {', '.join(keys)} - {r.text[:100]}")
    except Exception as e:
        print(f"  ❌ 失败: {e}")

print()
print("=" * 60)
print("[5] 测试速率限制极限")
print("=" * 60)

print("\n5.1 模型接口速率:")
for i in range(5):
    try:
        r = session.get(api_base + "/chat/models", timeout=5, proxies=proxies, verify=False)
        limit = r.headers.get('X-RateLimit-Limit', 'N/A')
        remaining = r.headers.get('X-RateLimit-Remaining', 'N/A')
        print(f"  请求 {i+1}: 剩余 {remaining}/{limit}")
    except:
        pass

print("\n5.2 聊天接口速率（未登录）:")
for i in range(5):
    try:
        r = session.post(api_base + "/chat/stream", json={"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"hi"}]}, timeout=5, proxies=proxies, verify=False)
        limit = r.headers.get('X-RateLimit-Limit', 'N/A')
        remaining = r.headers.get('X-RateLimit-Remaining', 'N/A')
        print(f"  请求 {i+1}: 剩余 {remaining}/{limit} (状态: {r.status_code})")
    except:
        pass

print()
print("=" * 60)
print("[6] 探测更多功能端点")
print("=" * 60)

more_endpoints = [
    "/image/generations",
    "/images/generations",
    "/image/generate",
    "/text-to-image",
    "/audio/speech",
    "/audio/transcriptions",
    "/embeddings",
    "/files",
    "/fine-tuning",
    "/assistants",
    "/threads",
    "/runs",
    "/payments",
    "/orders",
    "/pricing",
    "/plans",
    "/vip/info",
    "/user/credits",
    "/user/balance",
    "/usage",
]

print("\n6.1 探测其他功能端点:")
for ep in more_endpoints:
    try:
        r = session.get(api_base + ep, timeout=5, proxies=proxies, verify=False)
        if r.status_code not in [404]:
            print(f"  [{r.status_code}] GET {ep}: {r.text[:100]}")
        r = session.post(api_base + ep, json={}, timeout=5, proxies=proxies, verify=False)
        if r.status_code not in [404]:
            print(f"  [{r.status_code}] POST {ep}: {r.text[:100]}")
    except:
        pass

print()
print("=" * 60)
print("[7] 检查响应头中的重要信息")
print("=" * 60)

r = session.get(api_base + "/chat/models", timeout=10, proxies=proxies, verify=False)
print("\n7.1 响应头信息:")
for k, v in r.headers.items():
    if any(x in k.lower() for x in ['x-', 'server', 'powered', 'rate', 'limit', 'cookie', 'token', 'set-cookie']):
        print(f"  {k}: {v}")
