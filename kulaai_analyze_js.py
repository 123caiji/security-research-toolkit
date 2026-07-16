import requests
import re
import json

requests.packages.urllib3.disable_warnings()

import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

proxies = {"http": None, "https": None}

# 下载JS文件
js_url = "https://kulaai.cn/assets/index-CMjn12iu.js"
print("下载JS文件...")
r = requests.get(js_url, timeout=30, proxies=proxies, verify=False)
content = r.text
print(f"JS文件大小: {len(content)} 字符")

# 保存到本地
with open(r"e:\BaiduNetdiskDownload\1\kulaai_main.js", "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "=" * 60)
print("搜索签名相关代码")
print("=" * 60)

# 搜索X-Signature, X-Timestamp, X-Nonce
patterns = [
    r'X-Signature',
    r'x-signature',
    r'X-Timestamp',
    r'x-timestamp',
    r'X-Nonce',
    r'x-nonce',
    r'signature',
    r'Signature',
]

for pat in patterns:
    count = len(re.findall(pat, content))
    if count > 0:
        print(f"  {pat}: {count} 次")

# 提取X-Signature附近的上下文
print("\n" + "=" * 60)
print("提取X-Signature上下文")
print("=" * 60)

sig_positions = [m.start() for m in re.finditer(r'[Xx]-[Ss]ignature', content)]
print(f"找到 {len(sig_positions)} 个位置")

for i, pos in enumerate(sig_positions[:5]):
    start = max(0, pos - 200)
    end = min(len(content), pos + 300)
    context = content[start:end]
    print(f"\n[{i+1}] 位置 {pos}:")
    print(f"  {context}")

# 搜索签名计算函数
print("\n" + "=" * 60)
print("搜索签名计算相关代码")
print("=" * 60)

# 搜索SHA256
sha256_positions = [m.start() for m in re.finditer(r'sha256|SHA256|Sha256', content)]
print(f"\nSHA256出现 {len(sha256_positions)} 次")
for i, pos in enumerate(sha256_positions[:5]):
    start = max(0, pos - 100)
    end = min(len(content), pos + 150)
    context = content[start:end]
    print(f"\n  [{i+1}] {context}")

# 搜索HMAC
hmac_positions = [m.start() for m in re.finditer(r'hmac|HMAC|Hmac', content)]
print(f"\nHMAC出现 {len(hmac_positions)} 次")
for i, pos in enumerate(hmac_positions[:5]):
    start = max(0, pos - 100)
    end = min(len(content), pos + 150)
    context = content[start:end]
    print(f"\n  [{i+1}] {context}")

# 搜索crypto.subtle
crypto_positions = [m.start() for m in re.finditer(r'crypto\.subtle|subtle\.digest', content)]
print(f"\ncrypto.subtle出现 {len(crypto_positions)} 次")
for i, pos in enumerate(crypto_positions[:5]):
    start = max(0, pos - 150)
    end = min(len(content), pos + 200)
    context = content[start:end]
    print(f"\n  [{i+1}] {context}")

# 搜索签名生成函数的模式
print("\n" + "=" * 60)
print("搜索请求拦截器")
print("=" * 60)

interceptor_patterns = [
    r'interceptors\.request\.use',
    r'axios\.interceptors',
    r'\.interceptors\.request',
    r'config\.headers\[',
    r'config\.headers\.',
]

for pat in interceptor_patterns:
    positions = [m.start() for m in re.finditer(pat, content)]
    if positions:
        print(f"\n{pat}: {len(positions)} 次")
        for pos in positions[:3]:
            start = max(0, pos - 100)
            end = min(len(content), pos + 400)
            print(f"  ...{content[start:end]}...")

# 搜索UUID生成 (nonce)
print("\n" + "=" * 60)
print("搜索UUID/Nonce生成")
print("=" * 60)

uuid_patterns = [
    r'crypto\.randomUUID',
    r'randomUUID',
    r'uuid',
    r'UUID',
]

for pat in uuid_patterns:
    positions = [m.start() for m in re.finditer(pat, content)]
    if positions:
        print(f"\n{pat}: {len(positions)} 次")
        for pos in positions[:3]:
            start = max(0, pos - 50)
            end = min(len(content), pos + 100)
            print(f"  ...{content[start:end]}...")

# 搜索 Date.now (timestamp)
print("\n" + "=" * 60)
print("搜索时间戳生成")
print("=" * 60)

date_now_pos = [m.start() for m in re.finditer(r'Date\.now\(\)', content)]
print(f"Date.now() 出现 {len(date_now_pos)} 次")
for i, pos in enumerate(date_now_pos[:5]):
    start = max(0, pos - 100)
    end = min(len(content), pos + 100)
    print(f"\n  [{i+1}] ...{content[start:end]}...")
