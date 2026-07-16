#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度分析isSgp为false的端点和getNoPwdByPhoneNo"""
import re

js_path = r'C:\Users\xianyv\AppData\Local\Temp\app_new.js'
with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

print("=" * 70)
print("=== 1. 找出所有isSgp:!1的端点 (非SGP转发) ===")
print("=" * 70)

# 模式: {url:"sgp/xxx", ... isSgp:!1}
# 提取每个API定义的完整对象
api_def_pattern = r'\{[^}]*url\s*:\s*["\x27]([^"\x27]+)["\x27][^}]*isSgp\s*:\s*!1[^}]*\}'
matches = re.findall(api_def_pattern, code)

print(f"\n找到 {len(matches)} 个isSgp=false的端点:")
for url in sorted(matches):
    print(f"  {url}")

print()
print("=" * 70)
print("=== 2. getNoPwdByPhoneNo 详细分析 ===")
print("=" * 70)

# 搜索getNoPwdByPhoneNo周围的代码
idx = 0
count = 0
while True:
    idx = code.find('getNoPwdByPhoneNo', idx)
    if idx == -1:
        break
    start = max(0, idx - 300)
    end = min(len(code), idx + 500)
    context = code[start:end]
    clean = re.sub(r'\s+', ' ', context).strip()
    print(f"\n--- 出现位置 {count+1} ---")
    print(f"  {clean[:500]}")
    count += 1
    idx += 1
    if count >= 10:
        break

print()
print("=" * 70)
print("=== 3. FreeLogin 免密登录页面分析 ===")
print("=" * 70)

# 搜索FreeLogin组件
freelogin_idx = code.find('FreeLogin')
if freelogin_idx != -1:
    start = max(0, freelogin_idx - 200)
    end = min(len(code), freelogin_idx + 2000)
    context = code[start:end]
    clean = re.sub(r'\s+', ' ', context).strip()
    print(f"\nFreeLogin组件上下文:")
    print(f"  {clean[:1500]}")

print()
print("=" * 70)
print("=== 4. 分析登录流程和认证逻辑 ===")
print("=" * 70)

# 搜索登录相关逻辑
login_patterns = [
    r'login\s*:\s*function',
    r'sgpTellerLogin',
    r'Bearer\s+',
    r'Authorization.*token',
    r'token.*Authorization',
]

for pat in login_patterns:
    matches = list(re.finditer(pat, code))
    if matches:
        print(f"\n模式: {pat} ({len(matches)} 处)")
        for m in matches[:3]:
            start = max(0, m.start() - 100)
            end = min(len(code), m.end() + 200)
            ctx = code[start:end]
            clean = re.sub(r'\s+', ' ', ctx).strip()
            print(f"  ...{clean[:250]}...")

print()
print("=" * 70)
print("=== 5. 分析默认token和硬编码认证信息 ===")
print("=" * 70)

# 搜索987654321
token_9876 = code.find('987654321')
if token_9876 != -1:
    start = max(0, token_9876 - 200)
    end = min(len(code), token_9876 + 200)
    ctx = code[start:end]
    clean = re.sub(r'\s+', ' ', ctx).strip()
    print(f"\n987654321默认token上下文:")
    print(f"  {clean[:400]}")

print()
print("=" * 70)
print("=== 6. 分析queryHousePrice (FRMC/houseassets) ===")
print("=" * 70)

# 搜索houseassets
house_idx = code.find('houseassets')
if house_idx != -1:
    start = max(0, house_idx - 300)
    end = min(len(code), house_idx + 300)
    ctx = code[start:end]
    clean = re.sub(r'\s+', ' ', ctx).strip()
    print(f"\nhouseassets上下文:")
    print(f"  {clean[:500]}")

print()
print("=== 完成 ===")
