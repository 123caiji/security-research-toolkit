import requests
import json
import hashlib
import hmac
import uuid
import time

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
    from urllib.parse import urlparse
    path = urlparse(url).path if url.startswith("http") else url
    body_sha256 = hashlib.sha256(body.encode() if body else b"").hexdigest()
    sign_string = f"{method.upper()}\n{path}\n{timestamp}\n{nonce}\n{body_sha256}"
    return hmac.new(SIGN_SECRET.encode(), sign_string.encode(), hashlib.sha256).hexdigest()


def signed_headers(method, url, body="", token=None):
    timestamp = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4())
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://kulaai.cn",
        "Referer": "https://kulaai.cn/",
        "Content-Type": "application/json",
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": generate_signature(method, url, body, timestamp, nonce),
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


with open(r"e:\BaiduNetdiskDownload\1\kulaai_account.json", "r", encoding="utf-8") as f:
    account = json.load(f)

token = account["kula_ai"]["token"]
url = f"{API_BASE}/chat/stream"

print("=" * 60)
print("测试 displayModelId 聊天")
print("=" * 60)

# 先获取模型列表找到displayModelId
print("\n[1] 获取模型列表...")
models_url = f"{API_BASE}/chat/display-models?capability=chat"
headers = signed_headers("GET", models_url, "", token)
r = requests.get(models_url, headers=headers, timeout=15, proxies=proxies, verify=False)
models = r.json()

print(f"模型分组数: {len(models)}")

# 找几个模型的displayModelId
test_models = []
for group in models:
    subs = group.get('subModels', [])
    if subs:
        for m in subs[:2]:
            if len(test_models) < 6:
                test_models.append({
                    'name': group.get('name'),
                    'displayModelId': m.get('displayModelId'),
                    'actualModelId': m.get('actualModelId'),
                    'providerName': m.get('providerName'),
                })

print(f"\n找到 {len(test_models)} 个测试模型:")
for i, m in enumerate(test_models):
    print(f"  [{i+1}] {m['name']} - {m['actualModelId']} (displayId: {m['displayModelId']})")

# 测试聊天
print("\n[2] 测试聊天...")
for i, m in enumerate(test_models[:3]):
    print(f"\n测试 {i+1}: {m['name']} ({m['actualModelId']})")
    
    payload = {
        "model": "chatgpt",
        "displayModelId": m['displayModelId'],
        "messages": [{"role": "user", "content": "你好，请用一句话介绍你自己"}],
        "stream": True
    }
    body = json.dumps(payload)
    headers = signed_headers("POST", url, body, token)
    
    r = requests.post(url, data=body, headers=headers, timeout=60, stream=True, proxies=proxies, verify=False)
    
    full_text = ""
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
                        print(f"  ❌ 错误: {j['error']}")
                        break
                    if 'content' in j and j['content']:
                        full_text += j['content']
                except:
                    pass
    
    if full_text:
        print(f"  ✅ 回复: {full_text[:100]}...")
    else:
        print(f"  ⚠️  无回复内容 (状态: {r.status_code})")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
