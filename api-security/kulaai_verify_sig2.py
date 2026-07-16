import hashlib
import hmac
import json

timestamp = "1782883022520"
nonce = "28d27402-7f1a-4120-ad0c-7f74f077e3f6"
target_sig = "c0d8bb7bb72b39eae887a04188be39079bb2d1fc5c9b0bc5cfa5327a9289e003"

secret_key = "ukj3OXO_crBZoBmMeYDUw_gLqL9BqgbgY27XXPzJqTiWf1cToYLAPtPQRfpzypBa"

method = "POST"

# 注意：JS中stream是!0 (true)，而且键的顺序很重要
# JS代码中的顺序: model, subModel, displayModelId, conversationId, roleplay, messages, stream

# 从抓包获取的body (注意可能少了stream)
captured_body = '{"model":"chatgpt","subModel":"gpt-5.4-nano","displayModelId":"c4bfbb2b-62c4-417f-9fe3-ea0b52f441ab","conversationId":"a1986cc6-5ae9-419b-a7a4-61348cf5a786","messages":[{"role":"user","content":"你好"}]}'

print("=" * 60)
print("验证签名算法 - 修正版")
print("=" * 60)

# 测试不同的body变体
body_variants = [
    ("抓包body (无stream)", captured_body),
    ("加stream: true (末尾)", captured_body[:-1] + ',"stream":true}'),
    ("加stream: !0", captured_body[:-1] + ',"stream":!0}'),
    ("加roleplay: null, stream: true", captured_body[:-1] + ',"roleplay":null,"stream":true}'),
]

# 测试不同的URL path
path_variants = [
    ("/api/chat/stream", "pathname"),
    ("https://api.877ai.cn/api/chat/stream", "full url"),
    ("api/chat/stream", "no leading slash"),
]

for path_label, path in path_variants:
    print(f"\n--- 路径: {path_label} ---")
    for body_label, body in body_variants:
        body_sha256 = hashlib.sha256(body.encode()).hexdigest()
        sign_string = f"{method}\n{path}\n{timestamp}\n{nonce}\n{body_sha256}"
        signature = hmac.new(
            secret_key.encode(),
            sign_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        match = "✅" if signature == target_sig else "  "
        print(f"{match} {body_label}")
        if signature == target_sig:
            print(f"   找到正确组合！")
            print(f"   Body SHA256: {body_sha256}")
            print(f"   签名字符串:\n{sign_string}")
            print(f"   签名: {signature}")
            break
    else:
        continue
    break

# 再试一下 GET 请求的签名（无body）
print("\n\n--- 测试无body的情况 ---")
empty_body_hash = hashlib.sha256("".encode()).hexdigest()
print(f"空字符串 SHA256: {empty_body_hash}")

# 看看 m(n||``) - 当n为undefined时，n||`` 是 ``
# 所以 body 为空字符串时的sha256
