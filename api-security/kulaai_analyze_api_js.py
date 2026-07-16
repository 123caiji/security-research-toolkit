import requests
import re

requests.packages.urllib3.disable_warnings()

import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

proxies = {"http": None, "https": None}

# 下载api相关的JS
api_js_url = "https://kulaai.cn/assets/api-B0xuzE-o.js"
print("下载api.js...")
r = requests.get(api_js_url, timeout=30, proxies=proxies, verify=False)
content = r.text
print(f"文件大小: {len(content)} 字符")

with open(r"e:\BaiduNetdiskDownload\1\kulaai_api.js", "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "=" * 60)
print("搜索签名相关关键词")
print("=" * 60)

keywords = [
    'signature', 'Signature', 'SIGNATURE',
    'sign', 'Sign', 'SIGN',
    'timestamp', 'Timestamp', 'TIMESTAMP',
    'nonce', 'Nonce', 'NONCE',
    'X-Sign', 'x-sign',
    'X-Timestamp', 'x-timestamp',
    'X-Nonce', 'x-nonce',
    'sha256', 'SHA256', 'Sha256',
    'hmac', 'HMAC', 'Hmac',
    'crypto', 'Crypto',
    'digest', 'Digest',
    'encrypt', 'Encrypt',
    'hash', 'Hash',
]

for kw in keywords:
    count = content.count(kw)
    if count > 0:
        print(f"  {kw}: {count} 次")

# 搜索X-Signature上下文
print("\n" + "=" * 60)
print("搜索签名头上下文")
print("=" * 60)

patterns = [
    r'[Xx]-[Ss]ignature',
    r'[Xx]-[Tt]imestamp',
    r'[Xx]-[Nn]once',
]

for pat in patterns:
    positions = [m.start() for m in re.finditer(pat, content)]
    if positions:
        print(f"\n{pat}: {len(positions)} 次")
        for pos in positions[:5]:
            start = max(0, pos - 150)
            end = min(len(content), pos + 200)
            print(f"\n  位置 {pos}:")
            print(f"  {content[start:end]}")

# 搜索interceptor
print("\n" + "=" * 60)
print("搜索请求拦截器")
print("=" * 60)

intercept_pats = [
    r'interceptors',
    r'request\.use',
    r'config\.headers',
]

for pat in intercept_pats:
    positions = [m.start() for m in re.finditer(pat, content)]
    if positions:
        print(f"\n{pat}: {len(positions)} 次")
        for pos in positions[:3]:
            start = max(0, pos - 100)
            end = min(len(content), pos + 500)
            print(f"\n  ...{content[start:end]}...")

# 搜索完整函数
print("\n" + "=" * 60)
print("搜索签名函数")
print("=" * 60)

# 找到包含signature的更大上下文
sig_pos = content.find('signature')
if sig_pos > 0:
    start = max(0, sig_pos - 500)
    end = min(len(content), sig_pos + 500)
    print(f"\n包含signature的大上下文:")
    print(content[start:end])

# 打印整个文件的前2000字符
print("\n" + "=" * 60)
print("文件前2000字符")
print("=" * 60)
print(content[:2000])
