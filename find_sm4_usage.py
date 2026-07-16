#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查找前端SM4加密的实际用法"""
import re

js_path = r"C:\Users\xianyv\AppData\Local\Temp\app_new.js"
with open(js_path, "r", encoding="utf-8") as f:
    code = f.read()

# 找sm4.encrypt
print("="*70)
print("查找sm4.encrypt的使用")
print("="*70)

# 查找sm4.encrypt或sm4_encrypt
patterns = [
    r"sm4\.encrypt",
    r"sm4_encrypt",
    r"SM4\.encrypt",
    r"encryptBySM4",
    r"sm3\.encrypt",
    r"sm2\.encrypt"
]

for pat in patterns:
    matches = list(re.finditer(pat, code))
    print(f"\n{pat}: {len(matches)} 处")
    for m in matches[:3]:
        start = max(0, m.start() - 100)
        end = min(len(code), m.end() + 200)
        ctx = code[start:end]
        clean = re.sub(r"\s+", " ", ctx).strip()
        print(f"  ...{clean[:300]}...")

# 找sm4相关的函数定义
print("\n" + "="*70)
print("查找SM4相关函数定义")
print("="*70)

# 找function中的sm4
sm4_func_patterns = [
    r"function\s+\w*[Ss]m4\w*\s*\(",
    r"sm4\s*:\s*function",
    r"\w+\.sm4\s*=\s*function",
    r"sm4\s*=\s*function",
    r"sm4\s*=\s*\w+\.encrypt"
]

for pat in sm4_func_patterns:
    matches = re.finditer(pat, code)
    found = list(matches)
    if found:
        print(f"\n{pat}: {len(found)} 处")
        for m in found[:2]:
            start = max(0, m.start() - 50)
            end = min(len(code), m.end() + 300)
            ctx = code[start:end]
            clean = re.sub(r"\s+", " ", ctx).strip()
            print(f"  ...{clean[:400]}...")

# 找K_E的赋值和使用
print("\n" + "="*70)
print("查找K_E的使用")
print("="*70)

k_e_idx = code.find("K_E")
if k_e_idx > 0:
    print(f"K_E出现位置: {k_e_idx}")
    print("上下文:")
    print(code[max(0, k_e_idx-300):k_e_idx+500])

# 找globalConfig相关
print("\n" + "="*70)
print("查找globalConfig定义")
print("="*70)

gc_idx = code.find("globalConfig")
if gc_idx > 0:
    print("globalConfig出现位置:")
    for m in re.finditer(r"globalConfig", code):
        print(f"  位置: {m.start()}")
        if m.start() > 0:
            ctx = code[max(0, m.start()-100):m.end()+300]
            clean = re.sub(r"\s+", " ", ctx).strip()
            print(f"  上下文: {clean[:500]}")