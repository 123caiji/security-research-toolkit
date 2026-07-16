#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度分析 - 改进的TranCode提取和SOP端点分析"""
import re
import json

js_path = r'C:\Users\xianyv\AppData\Local\Temp\app_new.js'
with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

print("=" * 70)
print("=== 1. 提取所有TranCode (改进模式) ===")
print("=" * 70)

# 更宽松的TranCode模式: 模块名/接口名
patterns = [
    r'TranCode["\x27\s:]+([A-Za-z0-9\-]+/[A-Za-z0-9]+)',
    r'tranCode["\x27\s:]+([A-Za-z0-9\-]+/[A-Za-z0-9]+)',
    r'serviceCode["\x27\s:]+([A-Za-z0-9\-]+/[A-Za-z0-9]+)',
    r'ServiceName["\x27\s:]+([A-Za-z0-9\-]+/[A-Za-z0-9]+)',
    r'["\x27]([A-Z]{2,5}-[A-Z]{2,8}/[a-zA-Z][a-zA-Z0-9]+)["\x27]',
]

all_trancodes = set()
for pat in patterns:
    matches = re.findall(pat, code)
    for m in matches:
        all_trancodes.add(m)

unique_trancodes = sorted(list(all_trancodes))
print(f"\n总TranCode数: {len(unique_trancodes)}")

# 按模块分组
modules = {}
for t in unique_trancodes:
    mod = t.split('/')[0]
    if mod not in modules:
        modules[mod] = []
    modules[mod].append(t)

print(f"模块数: {len(modules)}")
print()
print("=== 所有模块 ===")
for mod in sorted(modules.keys()):
    print(f"  {mod}: {len(modules[mod])} 个API")

print()
print("=" * 70)
print("=== 2. 所有模块的API列表 ===")
print("=" * 70)

for mod in sorted(modules.keys()):
    print(f"\n--- {mod} ({len(modules[mod])} APIs) ---")
    for api in sorted(modules[mod]):
        print(f"  {api}")

print()
print("=" * 70)
print("=== 3. SGP SOP端点分析 (直接URL访问) ===")
print("=" * 70)

# 提取sgp/开头的端点
sgp_endpoints = re.findall(r'["\x27]sgp/([A-Za-z0-9]+)["\x27]', code)
sgp_unique = sorted(list(set(sgp_endpoints)))
print(f"\n发现 {len(sgp_unique)} 个SGP SOP端点:")
for ep in sgp_unique:
    print(f"  sgp/{ep}")

print()
print("=" * 70)
print("=== 4. 文件相关接口详细分析 ===")
print("=" * 70)

file_endpoints = re.findall(r'["\x27](http/[a-zA-Z0-9/\-]+)["\x27]', code)
file_unique = sorted(list(set(file_endpoints)))
print(f"\n发现 {len(file_unique)} 个http/开头的接口:")
for ep in file_unique:
    print(f"  {ep}")

print()
print("=" * 70)
print("=== 5. gateway/admin接口分析 ===")
print("=" * 70)

gw_endpoints = re.findall(r'["\x27](gateway/[a-zA-Z0-9/\-]+)["\x27]', code)
gw_unique = sorted(list(set(gw_endpoints)))
print(f"\n发现 {len(gw_unique)} 个gateway接口:")
for ep in gw_unique:
    print(f"  {ep}")

print()
print("=" * 70)
print("=== 6. 搜索MD5使用 (弱哈希) ===")
print("=" * 70)

md5_matches = re.findall(r'.{0,80}md5.{0,80}', code, re.IGNORECASE)
print(f"\nMD5使用场景: {len(md5_matches)} 处")
for i, m in enumerate(md5_matches[:10]):
    # 清理换行
    clean = re.sub(r'\s+', ' ', m).strip()
    print(f"\n  [{i+1}] ...{clean[:150]}...")

print()
print("=" * 70)
print("=== 7. 搜索Base64+密码组合 ===")
print("=" * 70)

base64_pwd = re.findall(r'.{0,100}(?:base64|Base64|btoa|atob).{0,100}password.{0,100}|.{0,100}password.{0,100}(?:base64|Base64|btoa|atob).{0,100}', code, re.IGNORECASE)
print(f"\nBase64+密码组合: {len(base64_pwd)} 处")
for i, m in enumerate(base64_pwd[:5]):
    clean = re.sub(r'\s+', ' ', m).strip()
    print(f"\n  [{i+1}] ...{clean[:200]}...")

print()
print("=" * 70)
print("=== 完成 ===")
print("=" * 70)
