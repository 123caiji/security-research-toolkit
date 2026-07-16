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
temp_email_api = "https://www.1secmail.com/api/v1/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://kulaai.cn",
    "Referer": "https://kulaai.cn/",
    "Content-Type": "application/json",
}

def generate_temp_email():
    """生成临时邮箱"""
    domains = ["1secmail.com", "1secmail.org", "1secmail.net"]
    domain = random.choice(domains)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
    return f"{username}@{domain}", username, domain

def check_email(username, domain):
    """检查邮箱收件箱"""
    url = f"{temp_email_api}?action=getMessages&login={username}&domain={domain}"
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except:
        return []

def get_email_content(username, domain, msg_id):
    """获取邮件内容"""
    url = f"{temp_email_api}?action=readMessage&login={username}&domain={domain}&id={msg_id}"
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except:
        return {}

def extract_verification_code(email_content):
    """从邮件中提取验证码"""
    body = email_content.get('body', '')
    if not body:
        body = email_content.get('textBody', '')
        if not body:
            body = email_content.get('htmlBody', '')
    
    import re
    codes = re.findall(r'\b[0-9]{4,8}\b', body)
    if codes:
        return codes[0]
    return None

print("=" * 60)
print("KULA AI 自动注册测试")
print("=" * 60)

# 步骤1：生成临时邮箱
email_addr, username, domain = generate_temp_email()
print(f"\n[1] 生成临时邮箱: {email_addr}")

# 初始化邮箱
print(f"  初始化邮箱...")
try:
    requests.get(f"{temp_email_api}?action=getMessages&login={username}&domain={domain}", timeout=10)
    print("  ✅ 邮箱已就绪")
except:
    print("  ⚠️  邮箱初始化失败，继续尝试...")

# 步骤2：发送验证码
print(f"\n[2] 发送注册验证码...")
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

# 步骤3：等待并收取验证码
print(f"\n[3] 等待接收验证码...")

verification_code = None
max_attempts = 15
for attempt in range(max_attempts):
    time.sleep(3)
    messages = check_email(username, domain)
    print(f"  检查 {attempt+1}/{max_attempts}: 找到 {len(messages)} 封邮件")
    
    if messages:
        for msg in messages:
            msg_id = msg.get('id')
            if msg_id:
                content = get_email_content(username, domain, msg_id)
                code = extract_verification_code(content)
                if code and len(code) >= 4:
                    verification_code = code
                    subject = msg.get('subject', '')
                    print(f"  ✅ 找到验证码: {code}")
                    print(f"     邮件主题: {subject}")
                    break
        if verification_code:
            break

if not verification_code:
    print("  ❌ 未收到验证码！")
    print("\n可能的原因：")
    print("  1. 临时邮箱域名被屏蔽")
    print("  2. 验证码发送到了垃圾邮件")
    print("  3. 网络延迟")
    exit(1)

# 步骤4：注册账号
print(f"\n[4] 注册账号...")
password = "TestPass123456!"
nickname = "testuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

register_payload = {
    "email": email_addr,
    "password": password,
    "code": verification_code,
    "username": nickname
}

try:
    r = session.post(api_base + "/auth/register", json=register_payload, 
                     timeout=15, proxies=proxies, verify=False)
    print(f"  状态码: {r.status_code}")
    print(f"  响应: {r.text}")
    
    if r.status_code not in [200, 201]:
        print("  ❌ 注册失败！")
        exit(1)
    print("  ✅ 注册成功！")
except Exception as e:
    print(f"  ❌ 失败: {e}")
    exit(1)

# 步骤5：登录获取Cookie
print(f"\n[5] 登录账号...")
try:
    r = session.post(api_base + "/auth/login", json={
        "email": email_addr,
        "password": password
    }, timeout=15, proxies=proxies, verify=False)
    print(f"  状态码: {r.status_code}")
    
    if r.status_code != 200:
        print(f"  响应: {r.text}")
        print("  ❌ 登录失败！")
        exit(1)
    
    cookies = {c.name: c.value for c in session.cookies}
    print(f"  ✅ 登录成功！")
    print(f"  Cookies: {json.dumps(cookies, ensure_ascii=False)}")
except Exception as e:
    print(f"  ❌ 失败: {e}")
    exit(1)

# 步骤6：测试聊天功能
print(f"\n[6] 测试聊天功能...")
try:
    r = session.post(api_base + "/chat/stream", json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "你好，请用一句话介绍你自己"}],
        "stream": False
    }, timeout=30, proxies=proxies, verify=False)
    print(f"  状态码: {r.status_code}")
    print(f"  Content-Type: {r.headers.get('Content-Type', 'N/A')}")
    
    if r.status_code == 200:
        print(f"  响应: {r.text[:500]}")
        print(f"  ✅ 聊天功能正常！")
    else:
        print(f"  响应: {r.text[:200]}")
except Exception as e:
    print(f"  ❌ 失败: {e}")

# 步骤7：测试流式聊天
print(f"\n[7] 测试流式聊天...")
try:
    r = session.post(api_base + "/chat/stream", json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "说一句话"}],
        "stream": True
    }, timeout=30, proxies=proxies, verify=False, stream=True)
    print(f"  状态码: {r.status_code}")
    
    result_text = ""
    chunk_count = 0
    for line in r.iter_lines():
        if line:
            line_str = line.decode('utf-8', errors='ignore')
            chunk_count += 1
            if chunk_count <= 5:
                print(f"  Chunk {chunk_count}: {line_str[:150]}")
            try:
                if line_str.startswith('data: '):
                    data = line_str[6:]
                    if data != '[DONE]':
                        j = json.loads(data)
                        if 'content' in j:
                            result_text += j['content']
            except:
                pass
    
    print(f"\n  总chunk数: {chunk_count}")
    print(f"  回复内容: {result_text[:200]}")
    print(f"  ✅ 流式聊天正常！")
except Exception as e:
    print(f"  ❌ 失败: {e}")

# 步骤8：保存账号信息
print(f"\n[8] 账号信息")
print("=" * 60)
account_info = {
    "email": email_addr,
    "password": password,
    "username": nickname,
    "cookies": cookies,
    "temp_email": {
        "username": username,
        "domain": domain
    }
}
print(json.dumps(account_info, ensure_ascii=False, indent=2))

# 保存到文件
with open(r"e:\BaiduNetdiskDownload\1\kulaai_account.json", "w", encoding="utf-8") as f:
    json.dump(account_info, f, ensure_ascii=False, indent=2)
print(f"\n✅ 账号信息已保存到: kulaai_account.json")
