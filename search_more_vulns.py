#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""搜索更多潜在的高价值漏洞点"""
import re

js_path = r'C:\Users\xianyv\AppData\Local\Temp\app_new.js'
with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

print("=" * 70)
print("=== 1. 搜索验证码相关 (短信、图形、滑块) ===")
print("=" * 70)

sms_keywords = ['smsCode', 'verifyCode', 'verificationCode', 'captcha', 'sms']
for kw in sms_keywords:
    count = len(re.findall(kw, code, re.IGNORECASE))
    print(f"  {kw}: {count} 处")

print()
print("=" * 70)
print("=== 2. 搜索密码相关 (加密、编码、存储) ===")
print("=" * 70)

pwd_keywords = ['encodePwd', 'encryptPwd', 'password', 'passwd', 'pwd', 'encodeSM3']
for kw in pwd_keywords:
    count = len(re.findall(kw, code, re.IGNORECASE))
    print(f"  {kw}: {count} 处")

# 分析encodePwd
encode_idx = code.find('encodePwd')
if encode_idx != -1:
    start = max(0, encode_idx - 200)
    end = min(len(code), encode_idx + 500)
    ctx = code[start:end]
    clean = re.sub(r'\s+', ' ', ctx).strip()
    print(f"\nencodePwd上下文:")
    print(f"  {clean[:500]}")

print()
print("=" * 70)
print("=== 3. 搜索角色权限相关 ===")
print("=" * 70)

role_keywords = ['roleId', 'roleIds', 'permission', 'auth', 'authorize']
for kw in role_keywords:
    count = len(re.findall(kw, code, re.IGNORECASE))
    print(f"  {kw}: {count} 处")

print()
print("=" * 70)
print("=== 4. 搜索订单/贷款相关敏感接口 ===")
print("=" * 70)

loan_endpoints = [
    'createOrder', 'deleteOrder', 'editOrder', 'queryOrder',
    'createContract', 'signAgreement', 'signature',
    'createPersonCustSop', 'updatePersonCust',
    'queryLoan', 'queryCredit',
]

for ep in loan_endpoints:
    idx = code.find(ep)
    if idx != -1:
        # 找API定义
        pat = r'\{[^{}]*url\s*:\s*["\x27]sgp/' + re.escape(ep) + r'["\x27][^{}]*\}'
        matches = re.findall(pat, code)
        if matches:
            clean = re.sub(r'\s+', ' ', matches[0]).strip()
            print(f"  {ep}: {clean}")

print()
print("=" * 70)
print("=== 5. 搜索支付/银行卡相关 ===")
print("=" * 70)

pay_keywords = ['debitCard', 'bankCard', 'pay', 'payment', 'account', 'balance', 'cardBin']
for kw in pay_keywords:
    count = len(re.findall(kw, code, re.IGNORECASE))
    if count > 0:
        print(f"  {kw}: {count} 处")

print()
print("=" * 70)
print("=== 6. 搜索社工库/信息查询接口 ===")
print("=" * 70)

social_keywords = ['socIns', 'social', 'houseFund', 'housePrice', 'idCardVerify', 'nameVerify']
for kw in social_keywords:
    count = len(re.findall(kw, code, re.IGNORECASE))
    if count > 0:
        print(f"  {kw}: {count} 处")

# 详细分析socInsDataQuery
soc_idx = code.find('socInsDataQuery')
if soc_idx != -1:
    start = max(0, soc_idx - 200)
    end = min(len(code), soc_idx + 400)
    ctx = code[start:end]
    clean = re.sub(r'\s+', ' ', ctx).strip()
    print(f"\nsocInsDataQuery上下文:")
    print(f"  {clean[:400]}")

# 详细分析verifyName
verifyname_idx = code.find('verifyName')
if verifyname_idx != -1:
    start = max(0, verifyname_idx - 200)
    end = min(len(code), verifyname_idx + 400)
    ctx = code[start:end]
    clean = re.sub(r'\s+', ' ', ctx).strip()
    print(f"\nverifyName上下文:")
    print(f"  {clean[:400]}")

print()
print("=" * 70)
print("=== 7. 搜索硬编码的敏感值 ===")
print("=" * 70)

# 搜索硬编码的密码、密钥等
hardcoded_patterns = [
    (r'["\x27]800000["\x27]', 'BranchId=800000'),
    (r'["\x27]10000["\x27]', 'LegalRepCode=10000'),
    (r'["\x27]39["\x27]', 'Channel=39'),
    (r'["\x27]1111["\x27]', 'SourceSysId=1111'),
]

for pat, name in hardcoded_patterns:
    count = len(re.findall(pat, code))
    if count > 0:
        print(f"  {name}: {count} 处")

print()
print("=== 完成 ===")
