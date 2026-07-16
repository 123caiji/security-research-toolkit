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

# 先用stream=False试试
print("=" * 60)
print("测试非流式请求")
print("=" * 60)

payload = {
    "model": "chatgpt",
    "subModel": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "用一句话介绍Python"}],
    "stream": False
}
body = json.dumps(payload)
headers = signed_headers("POST", url, body, token)

r = requests.post(url, data=body, headers=headers, timeout=30, proxies=proxies, verify=False)
print(f"状态码: {r.status_code}")
print(f"Content-Type: {r.headers.get('Content-Type')}")
print(f"响应长度: {len(r.text)}")
print(f"响应前500字:")
print(r.text[:500])

print("\n" + "=" * 60)
print("测试流式请求 - 详细输出")
print("=" * 60)

payload["stream"] = True
body = json.dumps(payload)
headers = signed_headers("POST", url, body, token)

r = requests.post(url, data=body, headers=headers, timeout=30, stream=True, proxies=proxies, verify=False)
print(f"状态码: {r.status_code}")

full_text = ""
chunk_count = 0
print("\n流式内容:")
for line in r.iter_lines():
    if line:
        line_str = line.decode('utf-8', errors='ignore')
        chunk_count += 1
        try:
            if line_str.startswith('data: '):
                data = line_str[6:]
                if data == '[DONE]':
                    print("\n[DONE]")
                    break
                j = json.loads(data)
                if j.get('done'):
                    print(f"\n[DONE in json] status={j.get('status')}")
                    break
                if 'content' in j and j['content']:
                    full_text += j['content']
                    print(j['content'], end='', flush=True)
        except Exception as e:
            pass

print(f"\n\n共 {chunk_count} 个chunk")
print(f"完整回复: {full_text[:300]}")
print(f"回复长度: {len(full_text)}")
