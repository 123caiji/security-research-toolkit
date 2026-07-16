import requests
import json
import string
import random
import time

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

def register_mailtm():
    """使用mail.tm注册临时邮箱"""
    domains_resp = requests.get("https://api.mail.tm/domains", timeout=10)
    domains = domains_resp.json().get('hydra:member', [])
    domain = domains[0]['domain']
    
    username = 'kulaaitest' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    email_addr = f"{username}@{domain}"
    password = "TempMail2024!"
    
    create_resp = requests.post("https://api.mail.tm/accounts", json={
        "address": email_addr,
        "password": password
    }, timeout=10)
    
    token_resp = requests.post("https://api.mail.tm/token", json={
        "address": email_addr,
        "password": password
    }, timeout=10)
    
    mail_token = token_resp.json().get('token')
    return email_addr, password, mail_token

def wait_for_verification_code(mail_token):
    """等待验证码邮件"""
    import re
    mail_headers = {"Authorization": f"Bearer {mail_token}"}
    
    for attempt in range(20):
        time.sleep(3)
        try:
            msgs_resp = requests.get("https://api.mail.tm/messages", headers=mail_headers, timeout=10)
            if msgs_resp.status_code == 200:
                messages = msgs_resp.json().get('hydra:member', [])
                print(f"    检查 {attempt+1}/20: {len(messages)} 封邮件", end='\r')
                
                for msg in messages:
                    msg_id = msg.get('id')
                    subject = msg.get('subject', '')
                    
                    if '验证码' in subject or 'code' in subject.lower():
                        detail_resp = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=mail_headers, timeout=10)
                        if detail_resp.status_code == 200:
                            detail = detail_resp.json()
                            text = detail.get('text', '') or detail.get('html', '') or str(detail.get('intro', ''))
                            codes = re.findall(r'\b[0-9]{4,8}\b', text)
                            if codes:
                                print()
                                return codes[0]
        except:
            pass
    print()
    return None

print("=" * 60)
print("KULA AI 自动注册 & 完整测试")
print("=" * 60)

# 步骤1：注册临时邮箱
print(f"\n[1] 注册临时邮箱...")
email_addr, mail_password, mail_token = register_mailtm()
print(f"  邮箱: {email_addr}")
print(f"  ✅ 邮箱注册成功")

# 步骤2：发送验证码
print(f"\n[2] 发送注册验证码...")
session = requests.Session()
session.verify = False
session.headers.update(headers)

r = session.post(api_base + "/auth/send-code", json={
    "email": email_addr,
    "type": "register"
}, timeout=15, proxies=proxies, verify=False)

print(f"  状态码: {r.status_code}")
if r.status_code not in [200, 201]:
    print(f"  ❌ 失败: {r.text}")
    exit(1)
print(f"  ✅ 验证码已发送")

# 步骤3：等待验证码
print(f"\n[3] 等待接收验证码...")
verification_code = wait_for_verification_code(mail_token)

if not verification_code:
    print("  ❌ 未收到验证码！")
    exit(1)
print(f"  ✅ 验证码: {verification_code}")

# 步骤4：注册账号
print(f"\n[4] 注册 KULA AI 账号...")
kula_password = "KulaTest2024!"
nickname = "kulaittest" + ''.join(random.choices(string.digits, k=6))

r = session.post(api_base + "/auth/register", json={
    "email": email_addr,
    "password": kula_password,
    "code": verification_code,
    "username": nickname
}, timeout=15, proxies=proxies, verify=False)

print(f"  状态码: {r.status_code}")
register_data = r.json()
if r.status_code not in [200, 201]:
    print(f"  ❌ 失败: {r.text}")
    exit(1)

token = register_data.get("token", "")
user_info = register_data.get("user", {})
print(f"  用户ID: {user_info.get('id')}")
print(f"  昵称: {user_info.get('nickname')}")
print(f"  ✅ 注册成功！")

# 保存账号信息
account_info = {
    "kula_ai": {
        "email": email_addr,
        "password": kula_password,
        "username": nickname,
        "token": token,
        "user_id": user_info.get('id')
    },
    "temp_email": {
        "provider": "mail.tm",
        "email": email_addr,
        "password": mail_password,
        "token": mail_token
    }
}

with open(r"e:\BaiduNetdiskDownload\1\kulaai_account.json", "w", encoding="utf-8") as f:
    json.dump(account_info, f, ensure_ascii=False, indent=2)
print(f"  ✅ 账号信息已保存")

# 步骤5：测试认证方式
print(f"\n[5] 测试认证方式...")
auth_headers = headers.copy()
auth_headers["Authorization"] = f"Bearer {token}"

# 步骤6：测试流式聊天
print(f"\n[6] 测试流式聊天 (gpt-3.5-turbo)...")
print("-" * 60)

try:
    r = session.post(api_base + "/chat/stream", json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "你好，请用一句话介绍你自己"}],
        "stream": True
    }, headers=auth_headers, timeout=60, proxies=proxies, verify=False, stream=True)
    
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        full_text = ""
        chunk_count = 0
        print()
        for line in r.iter_lines():
            if line:
                line_str = line.decode('utf-8', errors='ignore')
                chunk_count += 1
                try:
                    if line_str.startswith('data: '):
                        data = line_str[6:]
                        if data != '[DONE]':
                            j = json.loads(data)
                            if 'content' in j:
                                full_text += j['content']
                                print(j['content'], end='', flush=True)
                except:
                    pass
        
        print()
        print(f"\n✅ 流式聊天成功！共 {chunk_count} 个chunk")
        print(f"回复: {full_text[:300]}")
    else:
        print(f"❌ 失败: {r.text[:300]}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 步骤7：测试多个模型
print(f"\n[7] 测试多个模型")
print("=" * 60)

test_models = [
    ("GPT-3.5", "gpt-3.5-turbo"),
    ("Gemini Flash", "gemini-3.1-flash"),
    ("DeepSeek V3.2", "deepseek-v3.2"),
    ("Qwen 3.5 Flash", "qwen3.5-flash"),
    ("Doubao 1.6", "doubao-seed-1.6"),
    ("GLM 4 Flash", "glm-4-flash"),
]

for name, model_id in test_models:
    try:
        r = session.post(api_base + "/chat/stream", json={
            "model": model_id,
            "messages": [{"role": "user", "content": "你好"}],
            "stream": False
        }, headers=auth_headers, timeout=30, proxies=proxies, verify=False)
        
        status = "✅" if r.status_code == 200 else "❌"
        print(f"  {status} {name} ({model_id}): [{r.status_code}]")
        
        if r.status_code == 200 and len(r.text) < 500:
            try:
                data = r.json()
                if isinstance(data, dict) and 'content' in data:
                    print(f"       回复: {data['content'][:50]}...")
            except:
                pass
    except Exception as e:
        print(f"  ❌ {name}: {e}")

# 步骤8：测试速率限制
print(f"\n[8] 测试登录后速率限制")
print("=" * 60)

for i in range(5):
    try:
        r = session.post(api_base + "/chat/stream", json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "hi"}],
            "stream": False
        }, headers=auth_headers, timeout=10, proxies=proxies, verify=False)
        limit = r.headers.get('X-RateLimit-Limit', 'N/A')
        remaining = r.headers.get('X-RateLimit-Remaining', 'N/A')
        reset = r.headers.get('X-RateLimit-Reset', 'N/A')
        print(f"  请求 {i+1}: 剩余 {remaining}/{limit}, 重置 {reset}s")
    except:
        pass

print()
print("=" * 60)
print("全部测试完成！")
print("=" * 60)
print(f"\n账号信息已保存: kulaai_account.json")
print(f"邮箱: {email_addr}")
print(f"密码: {kula_password}")
print(f"Token 长度: {len(token)}")
