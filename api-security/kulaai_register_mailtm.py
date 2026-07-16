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

def test_temp_mail_service():
    """测试多个临时邮箱服务"""
    
    services = [
        {
            "name": "mail.tm",
            "url": "https://api.mail.tm",
            "register": True,
        },
        {
            "name": "guerrillamail",
            "url": "https://www.guerrillamail.com/ajax.php",
        },
        {
            "name": "tempmailo",
            "url": "https://tempmailo.com/api",
        },
    ]
    
    for svc in services:
        print(f"  测试 {svc['name']}...", end=' ')
        try:
            r = requests.get(svc['url'], timeout=5)
            print(f"[{r.status_code}]")
            if r.status_code < 500:
                return svc
        except Exception as e:
            print(f"[失败: {e}]")
    
    return None

print("=" * 60)
print("测试可用的临时邮箱服务")
print("=" * 60)

# 测试mail.tm
print("\n[1] 测试 mail.tm...")
try:
    domains_resp = requests.get("https://api.mail.tm/domains", timeout=10)
    if domains_resp.status_code == 200:
        domains = domains_resp.json().get('hydra:member', [])
        print(f"  ✅ 可用，共 {len(domains)} 个域名")
        for d in domains:
            print(f"    - {d['domain']}")
    else:
        print(f"  ❌ 不可用: {domains_resp.status_code}")
except Exception as e:
    print(f"  ❌ 失败: {e}")

# 使用mail.tm注册邮箱
print("\n" + "=" * 60)
print("使用 mail.tm 注册 KULA AI")
print("=" * 60)

try:
    # 获取域名
    domains_resp = requests.get("https://api.mail.tm/domains", timeout=10)
    domains = domains_resp.json().get('hydra:member', [])
    if not domains:
        print("❌ 没有可用域名")
        exit(1)
    
    domain = domains[0]['domain']
    username = 'kulaaitest' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    email_addr = f"{username}@{domain}"
    password = "TestPass123456!"
    
    print(f"\n[2] 邮箱地址: {email_addr}")
    
    # 创建邮箱账号
    print(f"  创建邮箱账号...")
    create_resp = requests.post("https://api.mail.tm/accounts", json={
        "address": email_addr,
        "password": password
    }, timeout=10)
    
    if create_resp.status_code not in [200, 201]:
        print(f"  ❌ 创建失败: {create_resp.status_code} - {create_resp.text[:200]}")
        exit(1)
    
    print(f"  ✅ 邮箱创建成功")
    
    # 获取token
    token_resp = requests.post("https://api.mail.tm/token", json={
        "address": email_addr,
        "password": password
    }, timeout=10)
    
    if token_resp.status_code != 200:
        print(f"  ❌ 获取token失败: {token_resp.status_code}")
        exit(1)
    
    mail_token = token_resp.json().get('token')
    print(f"  ✅ 获取token成功")
    
    mail_headers = {"Authorization": f"Bearer {mail_token}"}
    
except Exception as e:
    print(f"❌ 邮箱服务失败: {e}")
    exit(1)

# 发送注册验证码
print(f"\n[3] 发送 KULA AI 注册验证码...")
session = requests.Session()
session.verify = False
session.headers.update(headers)

try:
    r = session.post(api_base + "/auth/send-code", json={
        "email": email_addr,
        "type": "register"
    }, timeout=15, proxies=proxies, verify=False)
    print(f"  状态码: {r.status_code}")
    print(f"  响应: {r.text}")
    
    if r.status_code not in [200, 201]:
        print("  ❌ 验证码发送失败！")
        exit(1)
    print("  ✅ 验证码已发送")
except Exception as e:
    print(f"  ❌ 失败: {e}")
    exit(1)

# 等待验证码
print(f"\n[4] 等待接收验证码...")
verification_code = None

import re

for attempt in range(20):
    time.sleep(3)
    try:
        msgs_resp = requests.get("https://api.mail.tm/messages", headers=mail_headers, timeout=10)
        if msgs_resp.status_code == 200:
            messages = msgs_resp.json().get('hydra:member', [])
            print(f"  检查 {attempt+1}/20: 找到 {len(messages)} 封邮件")
            
            for msg in messages:
                msg_id = msg.get('id')
                subject = msg.get('subject', '')
                print(f"    - {subject}")
                
                if '验证码' in subject or 'verification' in subject.lower() or 'code' in subject.lower() or 'KULA' in subject or 'kula' in subject:
                    # 获取完整邮件内容
                    detail_resp = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=mail_headers, timeout=10)
                    if detail_resp.status_code == 200:
                        detail = detail_resp.json()
                        text = detail.get('text', '') or detail.get('html', '') or str(detail.get('intro', ''))
                        codes = re.findall(r'\b[0-9]{4,8}\b', text)
                        if codes:
                            verification_code = codes[0]
                            print(f"  ✅ 找到验证码: {verification_code}")
                            break
            
            if verification_code:
                break
    except Exception as e:
        print(f"  检查失败: {e}")

if not verification_code:
    print("  ❌ 未收到验证码！")
    exit(1)

# 注册账号
print(f"\n[5] 注册 KULA AI 账号...")
nickname = "testuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
kula_password = "KulaTest2024!"

try:
    r = session.post(api_base + "/auth/register", json={
        "email": email_addr,
        "password": kula_password,
        "code": verification_code,
        "username": nickname
    }, timeout=15, proxies=proxies, verify=False)
    print(f"  状态码: {r.status_code}")
    print(f"  响应: {r.text}")
    
    if r.status_code not in [200, 201]:
        print("  ❌ 注册失败！")
        exit(1)
    print("  ✅ 注册成功！")
except Exception as e:
    print(f"  ❌ 失败: {e}")
    exit(1)

# 登录
print(f"\n[6] 登录获取Cookie...")
try:
    r = session.post(api_base + "/auth/login", json={
        "email": email_addr,
        "password": kula_password
    }, timeout=15, proxies=proxies, verify=False)
    print(f"  状态码: {r.status_code}")
    
    if r.status_code != 200:
        print(f"  响应: {r.text}")
        print("  ❌ 登录失败！")
        exit(1)
    
    cookies = {c.name: c.value for c in session.cookies}
    print(f"  ✅ 登录成功！Cookie数: {len(cookies)}")
except Exception as e:
    print(f"  ❌ 失败: {e}")
    exit(1)

# 测试聊天
print(f"\n[7] 测试聊天功能...")
try:
    r = session.post(api_base + "/chat/stream", json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "你好，请用一句话介绍你自己"}],
        "stream": True
    }, timeout=60, proxies=proxies, verify=False, stream=True)
    print(f"  状态码: {r.status_code}")
    
    full_text = ""
    chunk_count = 0
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
    print(f"\n  ✅ 聊天测试成功！收到 {chunk_count} 个chunk")
    print(f"  回复: {full_text[:200]}")
except Exception as e:
    print(f"  ❌ 失败: {e}")

# 保存账号
print(f"\n[8] 保存账号信息")
print("=" * 60)
account_info = {
    "kula_ai": {
        "email": email_addr,
        "password": kula_password,
        "username": nickname,
        "cookies": cookies
    },
    "temp_email": {
        "provider": "mail.tm",
        "email": email_addr,
        "password": password,
        "token": mail_token
    }
}
print(json.dumps(account_info, ensure_ascii=False, indent=2))

with open(r"e:\BaiduNetdiskDownload\1\kulaai_account.json", "w", encoding="utf-8") as f:
    json.dump(account_info, f, ensure_ascii=False, indent=2)
print(f"\n✅ 账号已保存到: kulaai_account.json")
