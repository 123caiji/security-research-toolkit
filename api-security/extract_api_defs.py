#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取API定义并构造SM4加密请求测试"""
import re, json, base64, binascii, urllib.request, ssl

# ===== 1. 从app_new.js提取API定义 =====
js_path = r'C:\Users\xianyv\AppData\Local\Temp\app_new.js'
with open(js_path, 'r', encoding='utf-8') as f:
    c = f.read()

print("=" * 60)
print("=== 提取API定义 ===")
print("=" * 60)

# 搜索buildNonceToken的定义
for keyword in ['buildNonceToken', 'negotiate', 'sgpTellerLogin', 'freeLogin', 'test/Login']:
    print(f"\n--- {keyword} ---")
    for m in re.finditer(rf'["\']?{re.escape(keyword)}["\']?\s*[:=]', c):
        s = max(0, m.start() - 100)
        e = min(len(c), m.end() + 300)
        print(f"  {c[s:e]}")
        print()

# 搜索api对象定义（通常包含所有API的URL/TranCode映射）
print("\n=== 搜索API对象定义 ===")
# 搜索 buildNonceToken 周围更大的上下文
for m in re.finditer(r'buildNonceToken', c):
    s = max(0, m.start() - 500)
    e = min(len(c), m.end() + 200)
    ctx = c[s:e]
    # 找到包含URL或TranCode的行
    if 'sgpKeys' in ctx or 'TranCode' in ctx or 'url' in ctx.lower() or 'isSgp' in ctx:
        print(f"\n--- buildNonceToken上下文 ---")
        print(ctx)
        print()

# 搜索 negotiate 周围的上下文
print("\n=== negotiate上下文 ===")
for m in re.finditer(r'negotiate', c):
    s = max(0, m.start() - 300)
    e = min(len(c), m.end() + 300)
    ctx = c[s:e]
    if 'TranCode' in ctx or 'url' in ctx.lower() or 'isSgp' in ctx or 'api' in ctx.lower():
        print(f"\n{ctx}")
        print()

# 搜索 sgpTellerLogin 上下文
print("\n=== sgpTellerLogin上下文 ===")
for m in re.finditer(r'sgpTellerLogin', c):
    s = max(0, m.start() - 300)
    e = min(len(c), m.end() + 300)
    print(f"\n{c[s:e]}")
    print()

# 搜索 authentication 模块的API定义
print("\n=== authentication模块API定义 ===")
for m in re.finditer(r'authentication\s*[:=]\s*\{', c):
    s = max(0, m.start() - 50)
    e = min(len(c), m.end() + 1000)
    print(f"\n{c[s:e]}")
    print()
    break

# 搜索 freeLogin 的定义
print("\n=== freeLogin上下文 ===")
for m in re.finditer(r'freeLogin', c):
    s = max(0, m.start() - 200)
    e = min(len(c), m.end() + 200)
    ctx = c[s:e]
    if 'isSgp' in ctx or 'url' in ctx.lower() or 'TranCode' in ctx:
        print(f"\n{ctx}")
        print()

# 搜索 test/ 端点定义
print("\n=== test端点定义 ===")
for m in re.finditer(r'test/(?:Login|Logout|test\d)', c):
    s = max(0, m.start() - 200)
    e = min(len(c), m.end() + 200)
    print(f"\n{c[s:e]}")
    print()

# 搜索所有 isSgp:!1 的端点（不走SGP转发的端点）
print("\n=== isSgp:!1 端点（不走SGP转发）===")
for m in re.finditer(r'isSgp\s*:\s*!1', c):
    s = max(0, m.start() - 300)
    e = min(len(c), m.end() + 50)
    ctx = c[s:e]
    # 提取API名称
    api_match = re.search(r'["\']([^"\']+)["\']\s*:\s*\{[^}]*isSgp\s*:\s*!1', ctx + 'isSgp:!1')
    if api_match:
        print(f"  API: {api_match.group(1)}")
    # 也打印URL或TranCode
    url_match = re.search(r'(?:url|TranCode)\s*:\s*["\']([^"\']+)["\']', ctx)
    if url_match:
        print(f"    URL/TranCode: {url_match.group(1)}")

print("\n=== 完成 ===")
