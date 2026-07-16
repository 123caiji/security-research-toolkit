import hashlib
import hmac
import json

# 样本数据
timestamp = "1782883022520"
nonce = "28d27402-7f1a-4120-ad0c-7f74f077e3f6"
target_sig = "c0d8bb7bb72b39eae887a04188be39079bb2d1fc5c9b0bc5cfa5327a9289e003"

body = '{"model":"chatgpt","subModel":"gpt-5.4-nano","displayModelId":"c4bfbb2b-62c4-417f-9fe3-ea0b52f441ab","conversationId":"a1986cc6-5ae9-419b-a7a4-61348cf5a786","messages":[{"role":"user","content":"你好"}]}'

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZWU1ZTg1Ny03NmM1LTQ4NmQtOTJiZS1lMTA4M2IwYzdiZGYiLCJlbWFpbCI6Imt1bGFhaXRlc3RtcTk4bjhnaEB3ZWItbGlicmFyeS5uZXQiLCJyb2xlIjoidXNlciIsImlhdCI6MTc4Mjg4Mjk2MSwiZXhwIjoxNzgzNDg3NzYxfQ.ePzfIXwRLDA1Pn7WWFgXO25mVQG-R5FZbCuJWgsRSrE"

url_path = "/api/chat/stream"
method = "POST"

print("=" * 60)
print("分析签名算法")
print("=" * 60)
print(f"目标签名: {target_sig}")
print(f"签名长度: {len(target_sig)} (SHA256 = 64 chars hex)")
print()

def test_sha256(data, label):
    sig = hashlib.sha256(data.encode()).hexdigest()
    match = "✅" if sig == target_sig else "  "
    print(f"{match} {label}")
    if sig == target_sig:
        print(f"   找到！签名 = {sig}")
        return True
    return False

def test_hmac_sha256(key, data, label):
    sig = hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()
    match = "✅" if sig == target_sig else "  "
    print(f"{match} {label}")
    if sig == target_sig:
        print(f"   找到！签名 = {sig}")
        return True
    return False

# 测试1: 简单拼接
print("[1] 简单拼接 SHA256")
found = False
combos = [
    (timestamp + nonce, "ts + nonce"),
    (nonce + timestamp, "nonce + ts"),
    (timestamp + nonce + body, "ts + nonce + body"),
    (nonce + timestamp + body, "nonce + ts + body"),
    (body + timestamp + nonce, "body + ts + nonce"),
    (body + nonce + timestamp, "body + nonce + ts"),
    (method + url_path + timestamp + nonce, "method + path + ts + nonce"),
    (method + url_path + timestamp + nonce + body, "method + path + ts + nonce + body"),
    (url_path + timestamp + nonce, "path + ts + nonce"),
    (url_path + timestamp + nonce + body, "path + ts + nonce + body"),
]

for data, label in combos:
    if test_sha256(data, label):
        found = True
        break

if not found:
    print()

# 测试2: 带分隔符的拼接
print("[2] 带分隔符的拼接 SHA256")
delimiters = [".", ":", "|", "&", "\n", ""]
components_list = [
    ["POST", url_path, timestamp, nonce],
    ["POST", url_path, timestamp, nonce, body],
    [url_path, timestamp, nonce],
    [url_path, timestamp, nonce, body],
    [timestamp, nonce, body],
    [timestamp, nonce],
    [method, timestamp, nonce],
    [method, timestamp, nonce, body],
]

for components in components_list:
    for delim in delimiters:
        data = delim.join(components)
        label = f"{' + '.join(components[:3])}... (delim='{delim}')"
        if test_sha256(data, label):
            found = True
            break
    if found:
        break

if not found:
    print()

# 测试3: Token相关
print("[3] Token相关的 SHA256")
token_combos = [
    (token + timestamp + nonce, "token + ts + nonce"),
    (timestamp + nonce + token, "ts + nonce + token"),
    (token + timestamp + nonce + body, "token + ts + nonce + body"),
    (token + "." + timestamp + "." + nonce, "token.ts.nonce"),
    (timestamp + "." + nonce + "." + token, "ts.nonce.token"),
    (token + method + url_path + timestamp + nonce, "token + method + path + ts + nonce"),
    (token + method + url_path + timestamp + nonce + body, "token + method + path + ts + nonce + body"),
]

for data, label in token_combos:
    if test_sha256(data, label):
        found = True
        break

if not found:
    print()

# 测试4: HMAC with token as key
print("[4] HMAC-SHA256 (token作为key)")
hmac_combos = [
    (timestamp + nonce, "ts + nonce"),
    (nonce + timestamp, "nonce + ts"),
    (method + url_path + timestamp + nonce, "method + path + ts + nonce"),
    (url_path + timestamp + nonce, "path + ts + nonce"),
    (timestamp + nonce + body, "ts + nonce + body"),
    (method + url_path + timestamp + nonce + body, "method + path + ts + nonce + body"),
    (url_path + timestamp + nonce + body, "path + ts + nonce + body"),
    (body, "body"),
    (url_path + body, "path + body"),
    (method + url_path + body, "method + path + body"),
]

for data, label in hmac_combos:
    if test_hmac_sha256(token, data, f"HMAC(token, {label})"):
        found = True
        break

if not found:
    print()

# 测试5: HMAC with 固定密钥
print("[5] HMAC-SHA256 (常见固定密钥)")
common_keys = [
    "877ai", "kulaai", "kula", "kul",
    "secret", "key", "appkey", "app_secret",
    "api_key", "apikey", "api_secret",
    "x-sign-key", "sign_key", "signkey",
    "chatgpt", "aichat",
]

for key in common_keys:
    for data, label in [(timestamp + nonce, "ts+nonce"), (method + url_path + timestamp + nonce, "method+path+ts+nonce")]:
        if test_hmac_sha256(key, data, f"HMAC({key}, {label})"):
            found = True
            break
    if found:
        break

if not found:
    print()

# 测试6: body的md5 + 其他
print("[6] body的MD5参与签名")
body_md5 = hashlib.md5(body.encode()).hexdigest()
print(f"  body MD5: {body_md5}")

md5_combos = [
    (timestamp + nonce + body_md5, "ts + nonce + bodyMD5"),
    (method + url_path + timestamp + nonce + body_md5, "method + path + ts + nonce + bodyMD5"),
]
for data, label in md5_combos:
    if test_sha256(data, label):
        found = True
        break

if not found:
    print()

# 测试7: 小写/大写的影响
print("[7] 大小写测试")
for data, label in [(timestamp.lower() + nonce.lower(), "ts.lower + nonce.lower")]:
    if test_sha256(data, label):
        found = True
        break

if not found:
    print()

# 测试8: URL路径变体
print("[8] URL路径变体")
path_variants = [
    "https://api.877ai.cn/api/chat/stream",
    "api.877ai.cn/api/chat/stream",
    "/api/chat/stream",
    "api/chat/stream",
]

for path in path_variants:
    for data, label in [(method + path + timestamp + nonce, f"method + {path} + ts + nonce")]:
        if test_sha256(data, label):
            found = True
            break
    if found:
        break

if not found:
    print("\n未找到匹配的签名算法。需要更多样本或深入JS分析。")
