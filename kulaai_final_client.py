import requests
import json
import hashlib
import hmac
import uuid
import time
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


def register_temp_email():
    """注册mail.tm临时邮箱"""
    domains_resp = requests.get("https://api.mail.tm/domains", timeout=10, proxies=proxies, verify=False)
    domains = domains_resp.json().get('hydra:member', [])
    domain = domains[0]['domain']
    
    username = 'kula' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email_addr = f"{username}@{domain}"
    mail_pwd = "TempMail2024!"
    
    requests.post("https://api.mail.tm/accounts", json={
        "address": email_addr,
        "password": mail_pwd
    }, timeout=10, proxies=proxies, verify=False)
    
    token_resp = requests.post("https://api.mail.tm/token", json={
        "address": email_addr,
        "password": mail_pwd
    }, timeout=10, proxies=proxies, verify=False)
    
    mail_token = token_resp.json().get('token')
    return email_addr, mail_pwd, mail_token


def wait_for_code(mail_token):
    """等待验证码"""
    mail_headers = {"Authorization": f"Bearer {mail_token}"}
    for _ in range(20):
        time.sleep(3)
        try:
            msgs_resp = requests.get("https://api.mail.tm/messages", headers=mail_headers, timeout=10, proxies=proxies, verify=False)
            if msgs_resp.status_code == 200:
                messages = msgs_resp.json().get('hydra:member', [])
                for msg in messages:
                    msg_id = msg.get('id')
                    detail_resp = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=mail_headers, timeout=10, proxies=proxies, verify=False)
                    if detail_resp.status_code == 200:
                        detail = detail_resp.json()
                        text = detail.get('text', '') or detail.get('html', '') or str(detail.get('intro', ''))
                        codes = re.findall(r'\b[0-9]{4,8}\b', text)
                        if codes:
                            return codes[0]
        except:
            pass
    return None


def register_kula_account():
    """自动注册KULA AI账号"""
    print("  注册临时邮箱...")
    email, mail_pwd, mail_token = register_temp_email()
    print(f"  邮箱: {email}")
    
    print("  发送验证码...")
    url = f"{API_BASE}/auth/send-code"
    body = json.dumps({"email": email, "type": "register"})
    headers = signed_headers("POST", url, body)
    r = requests.post(url, data=body, headers=headers, timeout=15, proxies=proxies, verify=False)
    if r.status_code not in [200, 201]:
        raise Exception(f"发送验证码失败: {r.status_code} {r.text}")
    
    print("  等待验证码...")
    code = wait_for_code(mail_token)
    if not code:
        raise Exception("未收到验证码")
    print(f"  验证码: {code}")
    
    print("  注册账号...")
    kula_pwd = "KulaTest2024!"
    username = "kula" + ''.join(random.choices(string.digits, k=8))
    url = f"{API_BASE}/auth/register"
    body = json.dumps({"email": email, "password": kula_pwd, "code": code, "username": username})
    headers = signed_headers("POST", url, body)
    r = requests.post(url, data=body, headers=headers, timeout=15, proxies=proxies, verify=False)
    if r.status_code not in [200, 201]:
        raise Exception(f"注册失败: {r.status_code} {r.text}")
    
    data = r.json()
    token = data.get("token", "")
    print(f"  注册成功！用户ID: {data.get('user', {}).get('id')}")
    
    return {
        "email": email,
        "password": kula_pwd,
        "username": username,
        "token": token,
        "user_id": data.get('user', {}).get('id'),
        "mail_token": mail_token,
    }


class KulaAIClient:
    def __init__(self, token):
        self.token = token
        self.session = requests.Session()
        self.session.verify = False
    
    def chat(self, display_model_id, messages, model="chatgpt", stream=False):
        """发送聊天请求"""
        url = f"{API_BASE}/chat/stream"
        payload = {
            "model": model,
            "displayModelId": display_model_id,
            "messages": messages,
            "stream": stream,
        }
        body = json.dumps(payload)
        headers = signed_headers("POST", url, body, self.token)
        
        r = self.session.post(url, data=body, headers=headers, timeout=120, stream=stream, proxies=proxies, verify=False)
        
        if not r.ok:
            try:
                err = r.json()
                raise Exception(f"API错误: {err.get('error', err.get('message', r.text))}")
            except:
                raise Exception(f"请求失败: {r.status_code} {r.text}")
        
        if not stream:
            return r.json()
        
        return r
    
    def chat_sync(self, display_model_id, messages, model="chatgpt"):
        """同步获取完整回复"""
        r = self.chat(display_model_id, messages, model, stream=True)
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
                            raise Exception(j['error'])
                        if 'content' in j and j['content']:
                            full_text += j['content']
                    except:
                        pass
        return full_text
    
    def get_models(self, capability="chat"):
        """获取模型列表"""
        url = f"{API_BASE}/chat/display-models?capability={capability}"
        headers = signed_headers("GET", url, "", self.token)
        r = self.session.get(url, headers=headers, timeout=15, proxies=proxies, verify=False)
        if r.status_code == 200:
            return r.json()
        raise Exception(f"获取模型失败: {r.status_code} {r.text}")
    
    def get_quota(self):
        """获取配额"""
        url = f"{API_BASE}/subscription/quota"
        headers = signed_headers("GET", url, "", self.token)
        r = self.session.get(url, headers=headers, timeout=15, proxies=proxies, verify=False)
        if r.status_code == 200:
            return r.json()
        raise Exception(f"获取配额失败: {r.status_code} {r.text}")
    
    def get_rate_limit_info(self):
        """获取速率限制信息（通过发一个测试请求）"""
        url = f"{API_BASE}/subscription/quota"
        headers = signed_headers("GET", url, "", self.token)
        r = self.session.get(url, headers=headers, timeout=15, proxies=proxies, verify=False)
        return {
            "limit": r.headers.get('X-RateLimit-Limit'),
            "remaining": r.headers.get('X-RateLimit-Remaining'),
            "reset": r.headers.get('X-RateLimit-Reset'),
        }


class MultiAccountPool:
    """多账号池，用于绕过速率限制"""
    def __init__(self, accounts=None):
        self.clients = []
        self.current_index = 0
        if accounts:
            for acc in accounts:
                if isinstance(acc, dict) and 'token' in acc:
                    self.clients.append(KulaAIClient(acc['token']))
                elif isinstance(acc, str):
                    self.clients.append(KulaAIClient(acc))
    
    def add_account(self, token):
        self.clients.append(KulaAIClient(token))
    
    def add_account_from_register(self, account_info):
        self.clients.append(KulaAIClient(account_info['token']))
    
    def next_client(self):
        """轮询获取下一个客户端"""
        if not self.clients:
            raise Exception("没有可用的账号")
        client = self.clients[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.clients)
        return client
    
    def chat_rotate(self, display_model_id, messages, model="chatgpt"):
        """使用轮询账号发送消息"""
        client = self.next_client()
        return client.chat_sync(display_model_id, messages, model)
    
    def get_all_quotas(self):
        """获取所有账号的配额"""
        results = []
        for i, client in enumerate(self.clients):
            try:
                quota = client.get_quota()
                results.append({
                    "index": i,
                    "plan": quota.get('plan', {}).get('name'),
                    "normal_used": quota.get('normalModel', {}).get('used'),
                    "normal_quota": quota.get('normalModel', {}).get('quota'),
                    "normal_period": quota.get('normalModel', {}).get('period'),
                })
            except Exception as e:
                results.append({"index": i, "error": str(e)})
        return results


if __name__ == "__main__":
    print("=" * 70)
    print("KULA AI - 自动注册 & API客户端 & 速率限制测试")
    print("=" * 70)
    
    # 1. 加载现有账号
    print("\n[1] 加载现有账号...")
    accounts_file = r"e:\BaiduNetdiskDownload\1\kulaai_accounts.json"
    accounts = []
    
    try:
        with open(accounts_file, "r", encoding="utf-8") as f:
            accounts = json.load(f)
        print(f"  已加载 {len(accounts)} 个账号")
    except:
        print("  无现有账号")
    
    # 2. 再注册2个新账号（用于测试多账号）
    print("\n[2] 注册新账号...")
    new_accounts = []
    for i in range(2):
        print(f"\n  注册第 {i+1} 个账号:")
        try:
            acc = register_kula_account()
            new_accounts.append(acc)
            accounts.append(acc)
        except Exception as e:
            print(f"  ❌ 失败: {e}")
    
    # 保存所有账号
    with open(accounts_file, "w", encoding="utf-8") as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)
    print(f"\n  已保存 {len(accounts)} 个账号到 kulaai_accounts.json")
    
    # 3. 创建账号池
    print("\n[3] 创建账号池...")
    pool = MultiAccountPool(accounts)
    print(f"  账号池大小: {len(pool.clients)}")
    
    # 4. 查看所有账号配额
    print("\n[4] 查看各账号配额:")
    quotas = pool.get_all_quotas()
    for q in quotas:
        if 'error' in q:
            print(f"  账号{q['index']}: ❌ {q['error']}")
        else:
            print(f"  账号{q['index']}: {q['plan']} - 普通模型 {q['normal_used']}/{q['normal_quota']} ({q['normal_period']})")
    
    # 5. 测试单账号API调用
    print("\n[5] 测试API调用（单账号）...")
    if pool.clients:
        client = pool.clients[0]
        
        # 获取模型
        print("  获取模型列表...")
        models = client.get_models()
        print(f"  模型总数: {len(models)}")
        
        # 找一个免费模型
        free_model = None
        for m in models:
            if m.get('enabled') and m.get('showInFrontend') and m.get('tier') == 'free':
                free_model = m
                break
        if not free_model and models:
            free_model = models[0]
        
        if free_model:
            print(f"  使用模型: {free_model['name']} (ID: {free_model['id']})")
            
            # 测试聊天
            reply = client.chat_sync(
                free_model['id'],
                [{"role": "user", "content": "你好，请用一句话介绍你自己"}]
            )
            print(f"  回复: {reply[:100]}")
            print(f"  ✅ 单账号API调用成功！")
    
    # 6. 测试速率限制
    print("\n[6] 测试速率限制:")
    if pool.clients:
        client = pool.clients[0]
        for i in range(5):
            info = client.get_rate_limit_info()
            print(f"  请求 {i+1}: 剩余 {info['remaining']}/{info['limit']}, 重置 {info['reset']}s")
    
    # 7. 测试多账号轮询
    print("\n[7] 测试多账号轮询:")
    if len(pool.clients) >= 2:
        for i in range(5):
            try:
                reply = pool.chat_rotate(
                    models[0]['id'] if models else 'c4bfbb2b-62c4-417f-9fe3-ea0b52f441ab',
                    [{"role": "user", "content": f"测试消息 {i+1}"}]
                )
                print(f"  请求 {i+1}: 使用账号 {pool.current_index - 1 if pool.current_index > 0 else len(pool.clients)-1} - {reply[:30]}...")
            except Exception as e:
                print(f"  请求 {i+1}: ❌ {e}")
    
    print("\n" + "=" * 70)
    print("全部测试完成！")
    print("=" * 70)
