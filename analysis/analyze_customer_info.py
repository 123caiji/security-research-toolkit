#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析客户信息和贷款相关的敏感接口"""
import re

js_path = r'C:\Users\xianyv\AppData\Local\Temp\app_new.js'
with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

print("=" * 70)
print("=== 1. CUST_INFO 模块所有API ===")
print("=" * 70)

# 找出所有使用CUST_INFO模块的API
pattern = r'\{[^{}]*url\s*:\s*["\x27](sgp/[^"\x27]+)["\x27][^{}]*CUST_INFO[^{}]*\}'
matches = re.findall(pattern, code)
print(f"\nCUST_INFO模块API数: {len(matches)}")
for api in sorted(matches):
    print(f"  {api}")

print()
print("=" * 70)
print("=== 2. EC_IDEN 模块所有API (身份识别) ===")
print("=" * 70)

pattern = r'\{[^{}]*url\s*:\s*["\x27](sgp/[^"\x27]+)["\x27][^{}]*EC_IDEN[^{}]*\}'
matches = re.findall(pattern, code)
print(f"\nEC_IDEN模块API数: {len(matches)}")
for api in sorted(matches):
    print(f"  {api}")

print()
print("=" * 70)
print("=== 3. SSP_AUTH 模块所有API (认证) ===")
print("=" * 70)

pattern = r'\{[^{}]*url\s*:\s*["\x27](sgp/[^"\x27]+)["\x27][^{}]*SSP_AUTH[^{}]*\}'
matches = re.findall(pattern, code)
print(f"\nSSP_AUTH模块API数: {len(matches)}")
for api in sorted(matches):
    print(f"  {api}")

print()
print("=" * 70)
print("=== 4. IMPLEMENT 模块所有API (执行) ===")
print("=" * 70)

pattern = r'\{[^{}]*url\s*:\s*["\x27](sgp/[^"\x27]+)["\x27][^{}]*IMPLEMENT[^{}]*\}'
matches = re.findall(pattern, code)
print(f"\nIMPLEMENT模块API数: {len(matches)}")
for api in sorted(matches):
    print(f"  {api}")

print()
print("=" * 70)
print("=== 5. 客户信息相关接口详细分析 ===")
print("=" * 70)

# 搜索包含custNo、partyId、idCard等参数的调用
search_params = ['custNo', 'partyId', 'idCard', 'idcard', 'customerId', 'custId', 'userId']
for param in search_params:
    pattern = param + r'\s*[:=]'
    count = len(re.findall(pattern, code, re.IGNORECASE))
    print(f"  {param}: {count} 处")

print()
print("=" * 70)
print("=== 6. 搜索越权访问模式 (直接使用URL参数查询) ===")
print("=" * 70)

# 搜索从$route.query直接获取参数并传入API的模式
idor_patterns = [
    r'\$route\.query\.\w+\s*&&\s*\w+\s*\(',
    r'this\.\$route\.query\.\w+',
    r'getUrlParams\(\)',
    r'query\.\w+.*?\$post',
]

for pat in idor_patterns[:2]:
    matches = list(re.finditer(pat, code))
    print(f"\n模式: {pat} ({len(matches)} 处)")
    for m in matches[:5]:
        start = max(0, m.start() - 50)
        end = min(len(code), m.end() + 100)
        ctx = code[start:end]
        clean = re.sub(r'\s+', ' ', ctx).strip()
        print(f"  ...{clean[:200]}...")

print()
print("=" * 70)
print("=== 7. 分析selectPersonCust (个人客户查询) ===")
print("=" * 70)

# 搜索selectPersonCust的调用上下文
idx = 0
count = 0
while True:
    idx = code.find('selectPersonCust', idx)
    if idx == -1:
        break
    start = max(0, idx - 200)
    end = min(len(code), idx + 300)
    ctx = code[start:end]
    clean = re.sub(r'\s+', ' ', ctx).strip()
    if 'custNo' in clean or 'custId' in clean or 'query' in clean:
        print(f"\n--- 位置 {count+1} ---")
        print(f"  {clean[:400]}")
        count += 1
    idx += 1
    if count >= 8:
        break

print()
print("=" * 70)
print("=== 8. 分析updatePersonCust / updatePartyBaseInfo ===")
print("=" * 70)

for name in ['updatePersonCust', 'updatePartyBaseInfo', 'updatePartyDefaultInfo']:
    idx = code.find(name)
    if idx != -1:
        start = max(0, idx - 200)
        end = min(len(code), idx + 300)
        ctx = code[start:end]
        clean = re.sub(r'\s+', ' ', ctx).strip()
        print(f"\n{name}:")
        print(f"  {clean[:400]}")

print()
print("=== 完成 ===")
