#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析SGP SOP端点的调用方式和认证要求"""
import re

js_path = r'C:\Users\xianyv\AppData\Local\Temp\app_new.js'
with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

print("=" * 70)
print("=== 1. 分析SGP请求调用方式 ===")
print("=" * 70)

# 搜索调用sgp端点的代码模式
# 模式1: axios.post('/sgp/xxx', ...)
post_patterns = [
    r'post\s*\(\s*["\x27](sgp/[A-Za-z0-9]+)["\x27]',
    r'url\s*:\s*["\x27](sgp/[A-Za-z0-9]+)["\x27]',
    r'["\x27](sgp/[A-Za-z0-9]+)["\x27]\s*,\s*\{',
]

all_sgp_calls = {}
for pat in post_patterns:
    matches = re.findall(pat, code)
    for m in matches:
        if m not in all_sgp_calls:
            all_sgp_calls[m] = 0
        all_sgp_calls[m] += 1

print(f"\n找到 {len(all_sgp_calls)} 个SGP端点调用")
print()

# 高敏感端点列表
sensitive_endpoints = [
    'sgp/getNoPwdByPhoneNo',
    'sgp/sendLoginSmsCode',
    'sgp/queryIdentificationCardInfo',
    'sgp/idcardOCR',
    'sgp/getOcrIdCardResult',
    'sgp/QueryIdentityInfoSop',
    'sgp/selectPersonCust',
    'sgp/selectPersonCustSop',
    'sgp/queryCustComponentDetail',
    'sgp/queryCustRequestDetail',
    'sgp/selectCustPrivateManageInfoListSop',
    'sgp/SelectLoanInformation',
    'sgp/SelectLoanApplicationInfoSop',
    'sgp/SelectCreditApplyInfoSop',
    'sgp/queryOrderDetail',
    'sgp/queryOrderBasicInfo',
    'sgp/getFaceParam',
    'sgp/getFaceValidate',
    'sgp/getPersonFaceResult',
    'sgp/queryFaceToken',
    'sgp/download',
    'sgp/onlinePreview',
    'sgp/queryAllApproveTask',
    'sgp/queryTellerById',
    'sgp/authentication',
    'sgp/signatureCheck',
    'sgp/queryConsumerPostalAddress',
    'sgp/queryDebitCardByPartyId',
    'sgp/queryPartyBonusPoints',
    'sgp/socInsDataQuery',
    'sgp/queryHousePrice',
    'sgp/queryBankCardsBinInfo',
]

print("=== 2. 高敏感端点详细分析 ===")
print("=" * 70)

for ep in sensitive_endpoints:
    if ep in all_sgp_calls:
        # 找到端点的上下文
        ep_name = ep.replace('sgp/', '')
        # 搜索包含此端点的代码上下文
        context_pattern = r'.{0,200}' + re.escape(ep_name) + r'.{0,300}'
        matches = re.findall(context_pattern, code)
        if matches:
            print(f"\n{'='*60}")
            print(f"端点: {ep}")
            print(f"{'='*60}")
            for i, m in enumerate(matches[:3]):
                # 清理多余空格
                clean = re.sub(r'\s+', ' ', m).strip()
                print(f"\n  上下文 [{i+1}]:")
                print(f"    {clean[:300]}")

print()
print("=" * 70)
print("=== 3. 分析getNoPwdByPhoneNo (高风险) ===")
print("=" * 70)

# 详细分析getNoPwdByPhoneNo
no_pwd_pattern = r'.{0,500}getNoPwdByPhoneNo.{0,500}'
matches = re.findall(no_pwd_pattern, code)
for i, m in enumerate(matches[:5]):
    clean = re.sub(r'\s+', ' ', m).strip()
    print(f"\n[{i+1}] {clean[:500]}")

print()
print("=" * 70)
print("=== 4. 分析SGP请求的认证方式 ===")
print("=" * 70)

# 搜索sgp请求的headers和认证信息
auth_patterns = [
    r'sgp.{0,200}Authorization',
    r'Authorization.{0,200}sgp',
    r'sgp.{0,200}token',
    r'token.{0,200}sgp',
    r'sgp/transferRequest',
]

for pat in auth_patterns:
    matches = re.findall(pat, code, re.IGNORECASE)
    if matches:
        print(f"\n模式: {pat}")
        for m in matches[:3]:
            clean = re.sub(r'\s+', ' ', m).strip()
            print(f"  {clean[:200]}")

print()
print("=" * 70)
print("=== 5. 分析SOP端点的通用调用函数 ===")
print("=" * 70)

# 搜索可能的SOP请求封装函数
sop_patterns = [
    r'function\s+\w*[Ss]op\w*\s*\(',
    r'sopRequest|sopApi|callSop',
    r'SopService|sopService',
]

for pat in sop_patterns:
    matches = re.findall(pat, code)
    if matches:
        print(f"\n模式: {pat}")
        for m in matches[:10]:
            print(f"  {m}")

print()
print("=== 完成 ===")
