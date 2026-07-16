#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度分析app_new.js，提取关键漏洞信息"""
import re
import json

with open(r"C:\Users\xianyv\AppData\Local\Temp\app_new.js", 'r', encoding='utf-8') as f:
    code = f.read()

print(f"File size: {len(code)} chars")
print(f"Lines: {code.count(chr(10)) + 1}")

# 1. 提取K_E/K_S/K_P和getVueAppString上下文
print("\n" + "="*60)
print("1. 加密密钥相关代码")
print("="*60)

# 找K_E的赋值
for key in ['K_E', 'K_S', 'K_P']:
    # 找 window.globalConfig.K_E = ... 模式
    pattern = rf'globalConfig\.{key}.*?\)'
    matches = re.findall(pattern, code)
    if matches:
        for m in matches[:3]:
            print(f"\n[{key}] {m[:200]}")

# 找getVueAppString函数定义
pattern = r'getVueAppString.*?\}'
matches = re.findall(pattern, code)
if matches:
    print(f"\ngetVueAppString found: {len(matches)} occurrences")
    for m in matches[:2]:
        print(f"  {m[:300]}")

# 2. 提取API端点定义
print("\n" + "="*60)
print("2. API端点定义")
print("="*60)

# 找 spgKeys 或 apis 对象
for pattern_str in [r'spgKeys\s*=\s*\{([^}]{500,}?)\}', 
                    r'apis\s*[:=]\s*\{([^}]{1000,}?)\}',
                    r'url:\s*"[^"]*"[^}]*TranCode:']:
    matches = re.findall(pattern_str, code)
    if matches:
        print(f"\nPattern '{pattern_str[:30]}': {len(matches)} matches")
        for m in matches[:2]:
            print(f"  {m[:500]}")
            break

# 3. 找所有isSgp:false的端点
print("\n" + "="*60)
print("3. 非SGP端点 (isSgp:!1 / isSgp:false)")
print("="*60)

# 用更宽的模式找
pattern = r'\{[^}]{0,300}isSgp:\!1[^}]{0,300}\}'
matches = re.findall(pattern, code)
print(f"Found {len(matches)} non-SGP endpoints")
for i, m in enumerate(matches[:20]):
    # 提取url和TranCode
    url_match = re.search(r'url:\s*"([^"]+)"', m)
    tran_match = re.search(r'TranCode:\s*"([^"]+)"', m)
    url = url_match.group(1) if url_match else "N/A"
    tran = tran_match.group(1) if tran_match else "N/A"
    print(f"  [{i+1}] url={url} | TranCode={tran}")

# 4. 找文件上传/下载相关
print("\n" + "="*60)
print("4. 文件上传/下载相关接口")
print("="*60)

upload_keywords = ['upload', 'download', 'file', 'minio', 'oss', '附件', '图片', '协议']
for kw in upload_keywords:
    pattern = rf'[^a-zA-Z]{kw}[^a-zA-Z][^"]{{0,100}}TranCode:\s*"([^"]+)"'
    matches = re.findall(pattern, code, re.IGNORECASE)
    if matches:
        print(f"\n  '{kw}' related TranCodes ({len(matches)}):")
        for t in list(set(matches))[:10]:
            print(f"    - {t}")

# 5. 找敏感业务接口
print("\n" + "="*60)
print("5. 敏感业务接口关键词")
print("="*60)

sensitive_keywords = ['cust', 'customer', 'account', 'balance', 'loan', 'credit', 
                      '查询', '客户', '账户', '余额', '贷款', '授信', '身份证',
                      'queryCust', 'getCust', 'Customer', 'userInfo', '个人信息',
                      '交易', 'transfer', 'payment', '支付', '转账']
for kw in sensitive_keywords:
    pattern = rf'"([A-Z]+-[A-Z]+/{kw}[^"]*"|[^"]*TranCode:\s*"[^"]*{kw}[^"]*)'
    matches = re.findall(pattern, code, re.IGNORECASE)
    if matches:
        unique = list(set(matches))[:8]
        print(f"\n  '{kw}' ({len(matches)} hits):")
        for t in unique:
            print(f"    - {t[:100]}")

# 6. 找登录/认证相关
print("\n" + "="*60)
print("6. 登录/认证相关接口")
print("="*60)

auth_keywords = ['login', 'Logout', 'token', 'auth', '验证码', 'verification']
for kw in auth_keywords:
    pattern = rf'[^a-zA-Z]{kw}[^a-zA-Z][^"]{{0,200}}TranCode:\s*"([^"]+)"'
    matches = re.findall(pattern, code, re.IGNORECASE)
    if matches:
        unique = list(set(matches))[:8]
        print(f"\n  '{kw}' ({len(matches)} hits):")
        for t in unique:
            print(f"    - {t}")

# 7. 找DH密钥协商和加密API列表
print("\n" + "="*60)
print("7. 密钥协商和加密配置")
print("="*60)

# 找initUserKeyGroup上下文
idx = code.find('initUserKeyGroup')
if idx > 0:
    context = code[max(0,idx-500):idx+1000]
    print(f"initUserKeyGroup context:\n{context[:800]}")

# 找isApiUseEncryptionList
idx = code.find('isApiUseEncryptionList')
if idx > 0:
    context = code[max(0,idx-300):idx+800]
    print(f"\nisApiUseEncryptionList context:\n{context[:600]}")

# 8. 找SM2/SM4加密实现
print("\n" + "="*60)
print("8. SM2/SM4加密实现")
print("="*60)

for keyword in ['sm2', 'sm3', 'sm4', 'SM2', 'SM3', 'SM4', '国密', 'gmssl', 'GmSSL']:
    idx = code.find(keyword)
    if idx > 0:
        context = code[max(0,idx-100):idx+300]
        print(f"\n'{keyword}' at pos {idx}:\n  {context[:400]}")

# 9. 找所有TranCode
print("\n" + "="*60)
print("9. 所有TranCode统计 (前50个)")
print("="*60)

pattern = r'TranCode:\s*"([^"]+)"'
matches = re.findall(pattern, code)
unique = list(set(matches))
print(f"Total unique TranCodes: {len(unique)}")
sorted_codes = sorted(unique)
for i, t in enumerate(sorted_codes[:50]):
    print(f"  {i+1:3d}. {t}")

print(f"\n... and {len(unique) - 50} more")

# 保存所有TranCode
with open(r"e:\BaiduNetdiskDownload\1\all_trancodes.txt", 'w', encoding='utf-8') as f:
    for t in sorted_codes:
        f.write(t + '\n')
print(f"\nSaved all {len(unique)} TranCodes to all_trancodes.txt")
