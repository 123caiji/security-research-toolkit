#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""确认getNoPwdByPhoneNo的isSgp属性和其他关键端点"""
import re

js_path = r'C:\Users\xianyv\AppData\Local\Temp\app_new.js'
with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

print("=" * 70)
print("=== 1. getNoPwdByPhoneNo 完整API定义 ===")
print("=" * 70)

# 找到包含getNoPwdByPhoneNo的API定义对象
# 方法: 找到url:"sgp/getNoPwdByPhoneNo", 然后向前找{, 向后找}
pattern = r'\{[^{}]*url\s*:\s*["\x27]sgp/getNoPwdByPhoneNo["\x27][^{}]*\}'
matches = re.findall(pattern, code)
for i, m in enumerate(matches):
    clean = re.sub(r'\s+', ' ', m).strip()
    print(f"\n[{i+1}] {clean}")

print()
print("=" * 70)
print("=== 2. 搜索所有没有isSgp属性的端点 ===")
print("=" * 70)

# 找所有API定义，然后筛选没有isSgp的
all_api_pattern = r'\{[^{}]*url\s*:\s*["\x27](sgp/[^"\x27]+)["\x27][^{}]*\}'
all_matches = re.findall(all_api_pattern, code)
unique_apis = sorted(list(set(all_matches)))
print(f"\n总共有 {len(unique_apis)} 个sgp API端点")

# 找有isSgp:!1的
isSgp_false_pattern = r'\{[^{}]*url\s*:\s*["\x27](sgp/[^"\x27]+)["\x27][^{}]*isSgp\s*:\s*!1[^{}]*\}'
isSgp_false = set(re.findall(isSgp_false_pattern, code))
print(f"isSgp=false的: {len(isSgp_false)} 个")

# 找有isSgp:!0的
isSgp_true_pattern = r'\{[^{}]*url\s*:\s*["\x27](sgp/[^"\x27]+)["\x27][^{}]*isSgp\s*:\s*!0[^{}]*\}'
isSgp_true = set(re.findall(isSgp_true_pattern, code))
print(f"isSgp=true的: {len(isSgp_true)} 个")

# 没有明确isSgp的
no_isSgp = set(unique_apis) - isSgp_false - isSgp_true
print(f"没有明确isSgp属性的: {len(no_isSgp)} 个")
print()
print("没有isSgp属性的端点列表:")
for api in sorted(no_isSgp)[:50]:
    print(f"  {api}")
if len(no_isSgp) > 50:
    print(f"  ... 还有 {len(no_isSgp) - 50} 个")

print()
print("=" * 70)
print("=== 3. 关键高风险端点验证 ===")
print("=" * 70)

key_endpoints = [
    'sgp/getNoPwdByPhoneNo',
    'sgp/sendLoginSmsCode',
    'sgp/queryVerificationCode.auth',
    'sgp/sgpTellerLogin.auth',
    'sgp/selectPersonCust',
    'sgp/queryIdentificationCardInfo',
    'sgp/queryTellerById',
    'sgp/download',
]

for ep in key_endpoints:
    # 找完整的API定义
    pat = r'\{[^{}]*url\s*:\s*["\x27]' + re.escape(ep) + r'["\x27][^{}]*\}'
    matches = re.findall(pat, code)
    if matches:
        clean = re.sub(r'\s+', ' ', matches[0]).strip()
        # 检查isSgp
        has_isSgp = 'isSgp' in clean
        is_false = 'isSgp:!1' in clean
        is_true = 'isSgp:!0' in clean
        print(f"\n{ep}:")
        print(f"  完整定义: {clean}")
        print(f"  isSgp: {'false' if is_false else 'true' if is_true else '未设置(默认?)'}")
    else:
        print(f"\n{ep}: 未找到完整定义")

print()
print("=" * 70)
print("=== 4. sendLoginSmsCode 详细分析 ===")
print("=" * 70)

sms_idx = code.find('sendLoginSmsCode')
if sms_idx != -1:
    start = max(0, sms_idx - 300)
    end = min(len(code), sms_idx + 500)
    ctx = code[start:end]
    clean = re.sub(r'\s+', ' ', ctx).strip()
    print(f"\n{clean[:600]}")

print()
print("=" * 70)
print("=== 5. 滑块验证 slideCheck/slideInfo ===")
print("=" * 70)

for name in ['slideCheck', 'slideInfo', 'checkSilderImg']:
    idx = code.find(name)
    if idx != -1:
        start = max(0, idx - 200)
        end = min(len(code), idx + 300)
        ctx = code[start:end]
        clean = re.sub(r'\s+', ' ', ctx).strip()
        print(f"\n{name}: {clean[:400]}")

print()
print("=== 完成 ===")
