import hashlib
import hmac

timestamp = "1782883352885"
nonce = "e51731cd-db69-43b3-9503-7983474081a5"
target_sig = "e93e6682a0fe595f574a2f404af5649e8e5d42dcab79caae872e53325ac5e5c7"

secret_key = "ukj3OXO_crBZoBmMeYDUw_gLqL9BqgbgY27XXPzJqTiWf1cToYLAPtPQRfpzypBa"

method = "POST"

# 完整body
body = '{"model":"chatgpt","subModel":"gpt-5.4-nano","displayModelId":"c4bfbb2b-62c4-417f-9fe3-ea0b52f441ab","conversationId":"a1986cc6-5ae9-419b-a7a4-61348cf5a786","messages":[{"role":"user","content":"你好"},{"role":"assistant","content":"你好！很高兴见到你～  \\n请问有什么我可以帮你的吗？"},{"role":"user","content":"hi"}],"stream":true}'

print("=" * 60)
print("验证签名 - 完整body")
print("=" * 60)
print(f"Body长度: {len(body)}")
print(f"Target: {target_sig}")

body_sha256 = hashlib.sha256(body.encode()).hexdigest()
print(f"Body SHA256: {body_sha256}")

# 测试不同路径
paths = [
    ("/api/chat/stream", "pathname"),
    ("https://api.877ai.cn/api/chat/stream", "full url"),
]

for path, label in paths:
    sign_string = f"{method}\n{path}\n{timestamp}\n{nonce}\n{body_sha256}"
    signature = hmac.new(
        secret_key.encode(),
        sign_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    match = "✅ 正确！" if signature == target_sig else "❌"
    print(f"\n{match} 路径: {label}")
    print(f"  签名字符串:\n{sign_string}")
    print(f"  签名: {signature}")

# 再测试一下body中的换行符处理
print("\n" + "=" * 60)
print("测试body中换行符的影响")
print("=" * 60)

# JS中body是JSON.stringify的结果，其中换行是 \\n 还是 \n？
# 原始body里 content 里的是 \\n 还是 \n？
body_variants = [
    ("原始body", body),
    ("\\n 改为 \\\\n", body.replace("\\n", "\\\\n")),
]

for label, b in body_variants:
    bs = hashlib.sha256(b.encode()).hexdigest()
    sign_string = f"{method}\n{paths[0][0]}\n{timestamp}\n{nonce}\n{bs}"
    sig = hmac.new(secret_key.encode(), sign_string.encode(), hashlib.sha256).hexdigest()
    match = "✅" if sig == target_sig else "  "
    print(f"{match} {label}: {sig[:20]}...")
