import requests
import json
import time
import re

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

def get_models():
    """获取所有可用模型列表"""
    r = requests.get(api_base + "/chat/models", headers=headers, timeout=15, proxies=proxies, verify=False)
    return r.json()

def chat_with_model(model, messages, cookies=None, stream=True):
    """
    调用AI模型对话
    
    Args:
        model: 模型ID，如 gpt-3.5-turbo, gpt-5.5, claude-sonnet-4-5-20250929
        messages: 消息列表，如 [{"role": "user", "content": "你好"}]
        cookies: 登录后的cookie字典
        stream: 是否流式输出
    
    Returns:
        流式返回时逐行yield，非流式返回完整响应
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream
    }
    
    s = requests.Session()
    s.verify = False
    if cookies:
        s.cookies.update(cookies)
    
    r = s.post(api_base + "/chat/stream", json=payload, headers=headers, 
                timeout=60, proxies=proxies, stream=stream)
    
    if r.status_code != 200:
        raise Exception(f"请求失败: {r.status_code} - {r.text}")
    
    if stream:
        for line in r.iter_lines():
            if line:
                line_str = line.decode('utf-8', errors='ignore')
                if line_str.startswith('data: '):
                    data = line_str[6:]
                    if data == '[DONE]':
                        break
                    try:
                        yield json.loads(data)
                    except:
                        yield line_str
                else:
                    yield line_str
    else:
        yield r.json()

def register_account(email, password, username, code):
    """
    注册账号（需要验证码）
    
    Args:
        email: 邮箱
        password: 密码
        username: 用户名
        code: 邮箱验证码
    
    Returns:
        注册结果
    """
    payload = {
        "email": email,
        "password": password,
        "username": username,
        "code": code
    }
    
    r = requests.post(api_base + "/auth/register", json=payload, 
                      headers=headers, timeout=15, proxies=proxies, verify=False)
    return r.json()

def send_verification_code(email, code_type="register"):
    """发送验证码"""
    payload = {
        "email": email,
        "type": code_type
    }
    
    r = requests.post(api_base + "/auth/send-code", json=payload, 
                      headers=headers, timeout=15, proxies=proxies, verify=False)
    return r.json()

def login_account(email, password):
    """
    登录账号，返回session和cookies
    
    Returns:
        (session对象, cookie字典)
    """
    s = requests.Session()
    s.verify = False
    s.headers.update(headers)
    
    payload = {"email": email, "password": password}
    r = s.post(api_base + "/auth/login", json=payload, 
               timeout=15, proxies=proxies, verify=False)
    
    if r.status_code != 200:
        raise Exception(f"登录失败: {r.status_code} - {r.text}")
    
    cookies = {c.name: c.value for c in s.cookies}
    return s, cookies

if __name__ == "__main__":
    print("=" * 60)
    print("KULA AI API 调用示例")
    print("=" * 60)
    
    # 配置区域 =========================================
    # 从浏览器复制的cookies，填入下面的字典
    cookies = {
        # "cookie_name": "cookie_value",
        # 示例：
        # "session": "your_session_token",
    }
    # ===================================================
    
    print("1. 获取模型列表（无需登录）")
    models = get_models()
    print(f"   找到 {len(models)} 个模型分组:")
    for g in models[:3]:
        print(f"   - {g['name']}: {len(g['subModels'])} 个子模型")
    print()
    
    if not cookies:
        print("提示：请先配置cookies才能使用聊天功能")
        print("步骤：")
        print("  1. 访问 https://kulaai.cn 注册并登录")
        print("  2. F12 → Application → Cookies")
        print("  3. 复制所有cookie到脚本中的 cookies 字典")
    else:
        print("2. 测试聊天功能")
        try:
            print("   调用 gpt-3.5-turbo...")
            result = ""
            for chunk in chat_with_model(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "你好，请用一句话介绍你自己"}],
                cookies=cookies,
                stream=True
            ):
                if isinstance(chunk, dict):
                    if 'content' in chunk:
                        result += chunk['content']
                        print(chunk['content'], end='', flush=True)
                elif isinstance(chunk, str) and 'content' in chunk:
                    pass
            print()
            print(f"   完整回答: {result[:200]}...")
        except Exception as e:
            print(f"   失败: {e}")
