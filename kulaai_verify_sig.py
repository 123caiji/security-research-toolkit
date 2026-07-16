import hashlib
import hmac
import json

# 样本数据
timestamp = "1782883022520"
nonce = "28d27402-7f1a-4120-ad0c-7f74f077e3f6"
target_sig = "c0d8bb7bb72b39eae887a04188be39079bb2d1fc5c9b0bc5cfa5327a9289e003"

body = '{"model":"chatgpt","subModel":"gpt-5.4-nano","displayModelId":"c4bfbb2b-62c4-417f-9fe3-ea0b52f441ab","conversationId":"a1986cc6-5ae9-419b-a7a4-61348cf5a786","messages":[{"role":"user","content":"你好"}]}'

method = "POST"
path = "/api/chat/stream"

# 密钥
secret_key = "ukj3OXO_crBZoBmMeYDUw_gLqL9BqgbgY27XXPzJqTiWf1cToYLAPtPQRfpzypBa"

print("=" * 60)
print("验证签名算法")
print("=" * 60)

# 1. 计算body的SHA256
body_sha256 = hashlib.sha256(body.encode()).hexdigest()
print(f"Body SHA256: {body_sha256}")

# 2. 构造签名字符串
sign_string = f"{method}\n{path}\n{timestamp}\n{nonce}\n{body_sha256}"
print(f"\n签名字符串:")
print(sign_string)
print()

# 3. 计算HMAC-SHA256
signature = hmac.new(
    secret_key.encode(),
    sign_string.encode(),
    hashlib.sha256
).hexdigest()

print(f"计算签名: {signature}")
print(f"目标签名: {target_sig}")
print(f"匹配: {'✅ 正确！' if signature == target_sig else '❌ 不匹配'}")
