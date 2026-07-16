import requests
import json
import hashlib
import hmac
import uuid
import time
import re

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
    """生成请求签名"""
    path = url
    if path.startswith("http"):
        from urllib.parse import urlparse
        path = urlparse(url).path
    
    body_sha256 = hashlib.sha256(body.encode() if body else b"").hexdigest()
    sign_string = f"{method.upper()}\n{path}\n{timestamp}\n{nonce}\n{body_sha256}"
    
    signature = hmac.new(
        SIGN_SECRET.encode(),
        sign_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def signed_headers(method, url, body="", token=None):
    """生成带签名的请求头"""
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


class KulaAIClient:
    def __init__(self, token=None, email=None, password=None):
        self.token = token
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.session.verify = False
        
        if not token and email and password:
            self.login()
    
    def login(self):
        """登录获取token"""
        url = f"{API_BASE}/auth/login"
        body = json.dumps({"email": self.email, "password": self.password})
        headers = signed_headers("POST", url, body)
        
        r = self.session.post(url, data=body, headers=headers, timeout=15, proxies=proxies, verify=False)
        if r.status_code in [200, 201]:
            data = r.json()
            self.token = data.get("token", "")
            return data
        raise Exception(f"登录失败: {r.status_code} {r.text}")
    
    def get_models(self, capability=None):
        """获取模型列表"""
        url = f"{API_BASE}/chat/display-models"
        if capability:
            url += f"?capability={capability}"
        
        headers = signed_headers("GET", url, "", self.token)
        r = self.session.get(url, headers=headers, timeout=15, proxies=proxies, verify=False)
        if r.status_code == 200:
            return r.json()
        raise Exception(f"获取模型失败: {r.status_code} {r.text}")
    
    def chat_stream(self, model, messages, sub_model=None, conversation_id=None, display_model_id=None):
        """流式聊天"""
        url = f"{API_BASE}/chat/stream"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        if sub_model:
            payload["subModel"] = sub_model
        if conversation_id:
            payload["conversationId"] = conversation_id
        if display_model_id:
            payload["displayModelId"] = display_model_id
        
        body = json.dumps(payload)
        headers = signed_headers("POST", url, body, self.token)
        
        r = self.session.post(url, data=body, headers=headers, timeout=60, stream=True, proxies=proxies, verify=False)
        
        if not r.ok:
            raise Exception(f"聊天失败: {r.status_code} {r.text}")
        
        return r
    
    def chat(self, model, messages, sub_model=None, conversation_id=None, display_model_id=None):
        """非流式聊天（收集完整回复）"""
        r = self.chat_stream(model, messages, sub_model, conversation_id, display_model_id)
        
        full_content = ""
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
                        if 'content' in j and j['content']:
                            full_content += j['content']
                    except:
                        pass
        
        return full_content
    
    def get_quota(self):
        """获取用户配额"""
        url = f"{API_BASE}/subscription/quota"
        headers = signed_headers("GET", url, "", self.token)
        r = self.session.get(url, headers=headers, timeout=15, proxies=proxies, verify=False)
        if r.status_code == 200:
            return r.json()
        raise Exception(f"获取配额失败: {r.status_code} {r.text}")
    
    def generate_image(self, prompt, model="dall-e-3", size="1024x1024", n=1):
        """生成图片"""
        url = f"{API_BASE}/image/generate"
        payload = {"prompt": prompt, "model": model, "size": size, "n": n}
        body = json.dumps(payload)
        headers = signed_headers("POST", url, body, self.token)
        
        r = self.session.post(url, data=body, headers=headers, timeout=60, proxies=proxies, verify=False)
        if r.status_code == 200:
            return r.json()
        raise Exception(f"图片生成失败: {r.status_code} {r.text}")


if __name__ == "__main__":
    print("=" * 60)
    print("KULA AI API 客户端测试")
    print("=" * 60)
    
    # 加载账号
    with open(r"e:\BaiduNetdiskDownload\1\kulaai_account.json", "r", encoding="utf-8") as f:
        account = json.load(f)
    
    token = account["kula_ai"]["token"]
    email = account["kula_ai"]["email"]
    password = account["kula_ai"]["password"]
    
    client = KulaAIClient(token=token)
    
    # 测试1: 获取配额
    print("\n[1] 获取用户配额...")
    try:
        quota = client.get_quota()
        print(f"  套餐: {quota.get('plan', {}).get('name')}")
        print(f"  普通模型: {quota.get('normalModel', {}).get('used')}/{quota.get('normalModel', {}).get('quota')} ({quota.get('normalModel', {}).get('period')})")
        print(f"  高级模型: {quota.get('premiumModel', {}).get('used')}/{quota.get('premiumModel', {}).get('quota')} ({quota.get('premiumModel', {}).get('period')})")
        print(f"  积分: {quota.get('credits', {}).get('remaining')}")
    except Exception as e:
        print(f"  ❌ 失败: {e}")
    
    # 测试2: 获取模型列表
    print("\n[2] 获取模型列表...")
    try:
        models = client.get_models()
        total = sum(len(g.get('subModels', [])) for g in models)
        print(f"  模型分组: {len(models)} 个")
        print(f"  模型总数: {total} 个")
        for g in models[:3]:
            subs = g.get('subModels', [])
            print(f"  【{g['name']}】(默认: {g.get('defaultModel')}, 共{len(subs)}个)")
            for m in subs[:2]:
                print(f"    - {m.get('actualModelId')} (提供商: {m.get('providerName')})")
    except Exception as e:
        print(f"  ❌ 失败: {e}")
    
    # 测试3: 聊天测试
    print("\n[3] 测试聊天 (gpt-3.5-turbo)...")
    try:
        reply = client.chat(
            model="chatgpt",
            sub_model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "用一句话介绍Python编程"}]
        )
        print(f"  回复: {reply[:200]}")
        print(f"  ✅ 成功！")
    except Exception as e:
        print(f"  ❌ 失败: {e}")
    
    # 测试4: 测试多个模型
    print("\n[4] 测试多个模型...")
    test_models = [
        ("GPT-3.5", "chatgpt", "gpt-3.5-turbo"),
        ("Gemini Flash", "gemini", "gemini-3.1-flash"),
        ("DeepSeek V3", "deepseek", "deepseek-v3.2"),
        ("Qwen 3.5", "qwen", "qwen3.5-flash"),
    ]
    
    for name, model, sub in test_models:
        try:
            reply = client.chat(
                model=model,
                sub_model=sub,
                messages=[{"role": "user", "content": "你好"}]
            )
            print(f"  ✅ {name}: {reply[:30]}...")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
