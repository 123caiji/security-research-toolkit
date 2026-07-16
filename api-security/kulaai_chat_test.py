import requests
import json

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

with open(r"e:\BaiduNetdiskDownload\1\kulaai_account.json", "r", encoding="utf-8") as f:
    account = json.load(f)

email = account["kula_ai"]["email"]
password = account["kula_ai"]["password"]

print("=" * 60)
print("KULA AI 登录 & 聊天测试")
print("=" * 60)

# 登录获取token
print(f"\n[1] 登录账号: {email}")
session = requests.Session()
session.verify = False
session.headers.update(headers)

r = session.post(api_base + "/auth/login", json={
    "email": email,
    "password": password
}, timeout=15, proxies=proxies, verify=False)

print(f"  状态码: {r.status_code}")
login_data = r.json()
token = login_data.get("token", "")
user_info = login_data.get("user", {})

print(f"  用户ID: {user_info.get('id')}")
print(f"  昵称: {user_info.get('nickname')}")
print(f"  角色: {user_info.get('role')}")
print(f"  Token长度: {len(token)}")

# 保存token
account["kula_ai"]["token"] = token
with open(r"e:\BaiduNetdiskDownload\1\kulaai_account.json", "w", encoding="utf-8") as f:
    json.dump(account, f, ensure_ascii=False, indent=2)

print(f"  ✅ 登录成功！")

# 测试不同认证方式
print(f"\n[2] 测试认证方式...")

# 方式1: Bearer Token
auth_headers = headers.copy()
auth_headers["Authorization"] = f"Bearer {token}"

test_models = ["gpt-3.5-turbo", "gpt-4o-mini", "gemini-3.1-flash", "deepseek-v3.2", "qwen3.5-flash"]

print(f"\n[3] 测试多个模型聊天")
print("=" * 60)

for model in test_models:
    try:
        print(f"\n模型: {model}")
        r = session.post(api_base + "/chat/stream", json={
            "model": model,
            "messages": [{"role": "user", "content": "你好"}],
            "stream": False
        }, headers=auth_headers, timeout=30, proxies=proxies, verify=False)
        
        print(f"  状态码: {r.status_code}")
        if r.status_code == 200:
            ct = r.headers.get('Content-Type', '')
            print(f"  Content-Type: {ct}")
            if 'json' in ct.lower():
                try:
                    data = r.json()
                    content = data.get('content', str(data)[:200])
                    print(f"  回复: {content[:150]}")
                except:
                    print(f"  响应: {r.text[:200]}")
            else:
                print(f"  响应长度: {len(r.text)}")
                print(f"  前200字: {r.text[:200]}")
            print(f"  ✅ 成功！")
        elif r.status_code == 401:
            print(f"  ❌ 未授权")
        elif r.status_code == 403:
            print(f"  ❌ 无权限")
        else:
            print(f"  响应: {r.text[:200]}")
    except Exception as e:
        print(f"  ❌ 失败: {e}")

# 测试流式输出
print(f"\n[4] 测试流式输出 (gpt-3.5-turbo)")
print("=" * 60)

try:
    r = session.post(api_base + "/chat/stream", json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "用一句话介绍Python"}],
        "stream": True
    }, headers=auth_headers, timeout=30, proxies=proxies, verify=False, stream=True)
    
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        full_text = ""
        chunk_count = 0
        print("流式输出: ", end='', flush=True)
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
        print(f"\n✅ 流式输出正常！共 {chunk_count} 个chunk")
        print(f"完整回复: {full_text[:300]}")
    else:
        print(f"失败: {r.text[:200]}")
except Exception as e:
    print(f"❌ 失败: {e}")

# 测试模型列表（登录后是否有更多信息）
print(f"\n[5] 获取登录后的模型列表")
print("=" * 60)

try:
    r = session.get(api_base + "/chat/models", headers=auth_headers, timeout=15, proxies=proxies, verify=False)
    if r.status_code == 200:
        models_data = r.json()
        total = sum(len(g.get('subModels', [])) for g in models_data)
        print(f"模型分组: {len(models_data)} 个")
        print(f"模型总数: {total} 个")
        print()
        for g in models_data:
            default = g.get('defaultModel', 'N/A')
            subs = g.get('subModels', [])
            print(f"【{g['name']}】(默认: {default}, 共{len(subs)}个)")
            for m in subs[:3]:
                print(f"  - {m.get('actualModelId')} (提供商: {m.get('providerName')}, 等级: {m.get('tier')})")
            if len(subs) > 3:
                print(f"  ... 还有 {len(subs)-3} 个")
            print()
except Exception as e:
    print(f"❌ 失败: {e}")

# 测试图片生成
print(f"\n[6] 测试图片生成")
print("=" * 60)

try:
    r = session.post(api_base + "/image/generate", json={
        "model": "dall-e-3",
        "prompt": "a beautiful sunset",
        "n": 1,
        "size": "1024x1024"
    }, headers=auth_headers, timeout=30, proxies=proxies, verify=False)
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.text[:300]}")
except Exception as e:
    print(f"❌ 失败: {e}")

print()
print("=" * 60)
print("测试完成！")
print("=" * 60)
