import requests
import json
import string
import random

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
print("[1] 探测验证码发送接口")
print("=" * 60)

captcha_endpoints = [
    "/auth/captcha",
    "/auth/verification-code",
    "/auth/verify-code",
    "/auth/send-code",
    "/auth/send-email",
    "/auth/email-code",
    "/captcha",
    "/verification",
    "/verify",
    "/code/send",
    "/email/send",
    "/sms/send",
]

random_email = "testuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + "@example.com"
print(f"随机邮箱: {random_email}")

for ep in captcha_endpoints:
    try:
        url = api_base + ep
        r = requests.post(url, json={"email": random_email}, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"[{r.status_code}] POST {ep}: {r.text[:300]}")
    except:
        pass

print()
print("=" * 60)
print("[2] 探测图片验证码接口")
print("=" * 60)

image_captcha_endpoints = [
    "/captcha/image",
    "/captcha/gen",
    "/captcha/generate",
    "/auth/captcha/image",
    "/captcha.png",
    "/captcha.jpg",
]

for ep in image_captcha_endpoints:
    try:
        url = api_base + ep
        r = requests.get(url, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404 and len(r.content) > 100:
            ct = r.headers.get('Content-Type', '')
            print(f"[{r.status_code}] GET {ep} - Content-Type: {ct}, 大小: {len(r.content)}")
    except:
        pass

print()
print("=" * 60)
print("[3] 探测邀请码/推广码相关接口")
print("=" * 60)

invite_endpoints = [
    "/auth/invite-code",
    "/invite/verify",
    "/invite/check",
    "/promo/check",
    "/referral/check",
]

for ep in invite_endpoints:
    try:
        url = api_base + ep
        r = requests.post(url, json={"code": "TEST123"}, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"[{r.status_code}] POST {ep}: {r.text[:300]}")
    except:
        pass

print()
print("=" * 60)
print("[4] 测试完整注册流程（先获取验证码）")
print("=" * 60)

session = requests.Session()
session.verify = False
session.headers.update(headers)

# 尝试各种验证码发送方式
test_email = "test" + ''.join(random.choices(string.digits, k=10)) + "@example.com"
print(f"测试邮箱: {test_email}")

send_methods = [
    ("email", test_email),
    ("account", test_email),
    ("username", test_email),
    ("to", test_email),
]

captcha_types = ["register", "login", "reset", "email"]

for param, val in send_methods:
    for ctype in captcha_types:
        for ep in ["/auth/send-code", "/auth/verification-code", "/auth/captcha/send"]:
            try:
                payload = {param: val, "type": ctype}
                r = session.post(api_base + ep, json=payload, timeout=8, proxies=proxies, verify=False)
                if r.status_code not in [404, 400, 401]:
                    print(f"[{r.status_code}] {ep} {param}={val} type={ctype}: {r.text[:200]}")
            except:
                pass

print()
print("=" * 60)
print("[5] 探测用户相关端点")
print("=" * 60)

user_endpoints = [
    "/user/profile",
    "/user/info",
    "/user/balance",
    "/user/credits",
    "/user/subscription",
    "/user/vip",
    "/user/plan",
    "/user/usage",
    "/user/settings",
]

for ep in user_endpoints:
    try:
        url = api_base + ep
        r = session.get(url, timeout=8, proxies=proxies, verify=False)
        if r.status_code not in [404]:
            print(f"[{r.status_code}] GET {ep}: {r.text[:200]}")
    except:
        pass

print()
print("=" * 60)
print("[6] 检查是否有免登录的免费额度/游客模式")
print("=" * 60)

guest_endpoints = [
    "/auth/guest",
    "/auth/anonymous",
    "/auth/trial",
    "/trial",
    "/free-trial",
    "/guest",
    "/chat/free",
    "/chat/trial",
]

for ep in guest_endpoints:
    try:
        url = api_base + ep
        r = session.post(url, json={}, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"[{r.status_code}] POST {ep}: {r.text[:300]}")
    except:
        pass

for ep in guest_endpoints:
    try:
        url = api_base + ep
        r = session.get(url, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"[{r.status_code}] GET {ep}: {r.text[:300]}")
    except:
        pass

print()
print("=" * 60)
print("[7] 检查速率限制相关信息")
print("=" * 60)

# 连续发送多次请求，观察速率限制响应
print("连续请求测试速率限制:")
for i in range(5):
    try:
        r = session.post(api_base + "/chat/stream", json={"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"hi"}]}, timeout=5, proxies=proxies, verify=False)
        limit = r.headers.get('X-RateLimit-Limit', 'N/A')
        remaining = r.headers.get('X-RateLimit-Remaining', 'N/A')
        reset = r.headers.get('X-RateLimit-Reset', 'N/A')
        print(f"  请求 {i+1}: 剩余 {remaining}/{limit}, 重置: {reset}s")
    except:
        pass
