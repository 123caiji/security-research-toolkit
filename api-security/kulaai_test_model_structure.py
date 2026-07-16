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

# 获取模型列表
models_url = f"{API_BASE}/chat/display-models?capability=chat"
headers = signed_headers("GET", models_url, "", token)
r = requests.get(models_url, headers=headers, timeout=15, proxies=proxies, verify=False)
models = r.json()

print("模型数据类型:", type(models))
print("模型数据长度:", len(models))

# 看第一个模型
if isinstance(models, list) and len(models) > 0:
    first = models[0]
    print("\n第一个模型的keys:", list(first.keys()))
    print("第一个模型:", json.dumps(first, ensure_ascii=False, indent=2)[:500])

# 用之前浏览器抓到的displayModelId来测试
print("\n" + "=" * 60)
print("用已知displayModelId测试")
print("=" * 60)

test_display_id = "c4bfbb2b-62c4-417f-9fe3-ea0b52f441ab"  # gpt-5.4-nano的displayId
url = f"{API_BASE}/chat/stream"

payload = {
    "model": "chatgpt",
    "displayModelId": test_display_id,
    "messages": [{"role": "user", "content": "你好，请用一句话介绍Python"}],
    "stream": True
}
body = json.dumps(payload)
headers = signed_headers("POST", url, body, token)

r = requests.post(url, data=body, headers=headers, timeout=60, stream=True, proxies=proxies, verify=False)
print(f"状态码: {r.status_code}")

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
                    print(f"错误: {j['error']}")
                    break
                if 'content' in j and j['content']:
                    full_text += j['content']
                    print(j['content'], end='', flush=True)
            except:
                pass

print(f"\n\n完整回复: {full_text[:200]}")
print(f"回复长度: {len(full_text)}")
