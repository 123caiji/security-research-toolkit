#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取getVueAppString函数实现并解码K_E/K_S/K_P密钥"""

import re
import base64

js_path = r'C:\Users\xianyv\AppData\Local\Temp\app_new.js'
with open(js_path, 'r', encoding='utf-8') as f:
    c = f.read()

# 1. 找到getVueAppString函数定义
print("=" * 60)
print("=== getVueAppString 函数定义 ===")
print("=" * 60)

# 搜索函数定义
patterns = [
    r'getVueAppString\s*[:=]\s*function',
    r'function\s+getVueAppString',
    r'getVueAppString\s*[:=]\s*\(',
    r'"getVueAppString"',
    r"'getVueAppString'",
]

for pat in patterns:
    for m in re.finditer(pat, c):
        s = max(0, m.start() - 100)
        e = min(len(c), m.end() + 800)
        print(f"\n--- 匹配: {pat} ---")
        print(c[s:e])
        print()

# 2. 搜索getVueAppString的导入/定义模块
print("\n" + "=" * 60)
print("=== getVueAppString 模块定义 ===")
print("=" * 60)
for m in re.finditer(r'(getVueAppString)', c):
    s = max(0, m.start() - 200)
    e = min(len(c), m.end() + 200)
    ctx = c[s:e]
    if 'function' in ctx or 'export' in ctx or 'module' in ctx:
        print(f"\n{ctx}")
        print("---")

# 3. 尝试解码Base64值
print("\n" + "=" * 60)
print("=== 尝试解码Base64值 ===")
print("=" * 60)

encoded_values = {
    'K_E': ('YWRxI2ZncTNjJnZpZndiYHB2ZDRxbmNwczJjfGFidiU=', 'VUEAPPE'),
    'K_S': ('NGYheDNkYmA3cXZmY2U3ZHV1MjZrbzYhJTM2MmJlIyJlNmQ3MyciZDIxYGUneDZhNmQwIXRhYDJgNHd4aGE1ZQ==', 'VUEAPPS'),
    'K_P': ('ZmF1I2RhZWZnIHlmMWhiMyN0ZGRhZWEhdDVkMmM2fCM0MTFlYCYiYjM0Z2VwdjViNmU3dnQxNGVlZiN0YjFiN2EhdmBjMTdsIHY0Z2luZXNzMWgyMDRzIGMzNTI3ISc1MzMyNyZwNmdkNzMgeDQzNjQ0dHZmYWVvbHJyMmFpb2QnJA==', 'VUEAPPP'),
    'VUEAPPSUK': ('ZmB2eWliNmB5bmInImlhN2UvYGwnd2Y2ZjRyY2chdTI=', 'VUEAPPSUK'),
}

for name, (encoded, key) in encoded_values.items():
    print(f"\n--- {name} (key={key}) ---")
    try:
        decoded = base64.b64decode(encoded)
        print(f"  Base64解码(raw bytes): {decoded}")
        print(f"  Base64解码(hex): {decoded.hex()}")
        try:
            print(f"  Base64解码(utf-8): {decoded.decode('utf-8', errors='replace')}")
        except:
            pass
        
        # 尝试XOR解密 (用key重复填充)
        key_bytes = key.encode('utf-8')
        result = bytearray()
        for i, b in enumerate(decoded):
            result.append(b ^ key_bytes[i % len(key_bytes)])
        try:
            print(f"  XOR解密(utf-8): {result.decode('utf-8', errors='replace')}")
        except:
            pass
        print(f"  XOR解密(hex): {result.hex()}")
        
        # 尝试只用key的第一个字符XOR
        first_char = ord(key[0])
        result2 = bytearray()
        for b in decoded:
            result2.append(b ^ first_char)
        try:
            print(f"  XOR首字符解密(utf-8): {result2.decode('utf-8', errors='replace')}")
        except:
            pass
            
    except Exception as e:
        print(f"  解码错误: {e}")

# 4. 搜索其他可能的解码函数
print("\n" + "=" * 60)
print("=== 搜索可能的解码/解密函数 ===")
print("=" * 60)
for keyword in ['decodeStr', 'decryptStr', 'xorDecode', 'base64Decode', 'fromBase64', 'decodeString']:
    for m in re.finditer(rf'{keyword}\s*[:=]?\s*function?\s*\(', c):
        s = max(0, m.start() - 50)
        e = min(len(c), m.end() + 500)
        print(f"\n--- {keyword} ---")
        print(c[s:e])
        print()

# 5. 搜索VUEAPP相关
print("\n" + "=" * 60)
print("=== VUEAPP相关代码 ===")
print("=" * 60)
for m in re.finditer(r'VUEAPP', c):
    s = max(0, m.start() - 150)
    e = min(len(c), m.end() + 150)
    ctx = c[s:e]
    if 'function' in ctx or 'getVueApp' in ctx or 'decode' in ctx or 'xor' in ctx.lower():
        print(f"\n{ctx}")
        print("---")

print("\n=== 完成 ===")
