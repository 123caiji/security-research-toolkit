#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度分析app_new.js v2 - 提取更多漏洞信息"""
import re
import json

with open(r"C:\Users\xianyv\AppData\Local\Temp\app_new.js", 'r', encoding='utf-8') as f:
    code = f.read()

print(f"File size: {len(code)} chars")

# 1. 提取所有TranCode - 用更灵活的模式
print("\n" + "="*60)
print("1. 所有TranCode (完整提取)")
print("="*60)

# 匹配 "XXX-XXX/xxx" 格式的TranCode
pattern = r'["\']([A-Z]+-[A-Z]+\/[a-zA-Z0-9]+)["\']'
matches = re.findall(pattern, code)
unique = sorted(list(set(matches)))
print(f"Total module-API format TranCodes: {len(unique)}")
for i, t in enumerate(unique[:80]):
    print(f"  {i+1:3d}. {t}")

# 按模块分组
modules = {}
for t in unique:
    mod = t.split('/')[0]
    if mod not in modules:
        modules[mod] = []
    modules[mod].append(t)

print(f"\nModules ({len(modules)}):")
for mod, apis in sorted(modules.items()):
    print(f"  {mod}: {len(apis)} APIs")

# 2. 大文件上传接口详细分析
print("\n" + "="*60)
print("2. 大文件上传接口详细分析")
print("="*60)

for keyword in ['largeFile', 'sliceUpload', 'getUploadId', 'mergeFile', 'uploadByBase64']:
    idx = 0
    count = 0
    while True:
        idx = code.find(keyword, idx)
        if idx == -1 or count >= 3:
            break
        context = code[max(0,idx-200):idx+400]
        print(f"\n--- {keyword} occurrence {count+1} at {idx} ---")
        print(context[:500])
        idx += 1
        count += 1

# 3. 文件上传相关
print("\n" + "="*60)
print("3. fileUpload / minioDownload 相关")
print("="*60)

for keyword in ['fileUpload', 'minioDownload', 'uploadFile', 'queryFile', 'fileId', 'file_name']:
    count = code.count(keyword)
    if count > 0:
        idx = code.find(keyword)
        context = code[max(0,idx-150):idx+300]
        print(f"\n'{keyword}' ({count} occurrences) - first at {idx}:")
        print(f"  {context[:400]}")

# 4. 客户信息/敏感数据接口
print("\n" + "="*60)
print("4. 客户信息相关API")
print("="*60)

for kw in ['CUST', 'CUST-INFO', 'custInfo', 'customerInfo', 'queryCustomer', 'getCustomer',
           'queryCust', 'CUST_INFO', 'CUST-QUERY', 'queryPerson']:
    idx = code.find(kw)
    if idx > 0:
        context = code[max(0,idx-100):idx+200]
        print(f"\n'{kw}' at {idx}:")
        print(f"  {context[:300]}")

# 5. 贷款/业务相关
print("\n" + "="*60)
print("5. 贷款业务相关API")
print("="*60)

for kw in ['LOAN', 'loanApply', 'queryLoan', 'FUND-LOAN', 'CREDIT', 'creditApply',
           '查询贷款', '贷款申请', '授信', '额度']:
    count = code.count(kw)
    if count > 0:
        print(f"  '{kw}': {count} occurrences")

# 6. SM4解密 - 身份证/姓名解密
print("\n" + "="*60)
print("6. SM4解密逻辑 - 敏感数据解密")
print("="*60)

idx = code.find('sm4.decrypt')
while idx > 0:
    context = code[max(0,idx-200):idx+300]
    print(f"\n  at {idx}:")
    print(f"  {context[:450]}")
    idx = code.find('sm4.decrypt', idx+1)
    if idx > 1000000:  # 只找前1M内的
        break

# 7. DH密钥协商完整流程
print("\n" + "="*60)
print("7. DH密钥协商 (Diffie-Hellman)")
print("="*60)

for kw in ['getDiffieHellman', 'generateKeys', 'computeSecret', 'getPublicKey', 'dhObj', 'initUserKeyGroup']:
    idx = code.find(kw)
    if idx > 0:
        context = code[max(0,idx-100):idx+250]
        print(f"\n'{kw}' at {idx}:")
        print(f"  {context[:350]}")

# 8. 未授权接口 - guest / 游客
print("\n" + "="*60)
print("8. Guest/游客接口 (可能未授权)")
print("="*60)

for kw in ['Guest', 'guest', '游客', 'queryMenuTreeBySysIdRoleIdWithGuest', 'isApiUseEncryptionList']:
    count = code.count(kw)
    if count > 0:
        idx = code.find(kw)
        context = code[max(0,idx-100):idx+250]
        print(f"\n  '{kw}' ({count} occurrences):")
        print(f"  {context[:300]}")

# 9. 提取全部API定义对象
print("\n" + "="*60)
print("9. API定义对象搜索")
print("="*60)

# 找 spgKeys 或 api 对象
for obj_name in ['spgKeys', 'apiKey', '$api', 'apiObj', 'apiMap']:
    idx = code.find(obj_name)
    if idx > 0:
        context = code[max(0,idx-50):idx+500]
        print(f"\n'{obj_name}' at {idx}:")
        print(f"  {context[:550]}")

# 10. SQL注入风险点
print("\n" + "="*60)
print("10. 潜在SQL注入风险 (字符串拼接)")
print("="*60)

risk_patterns = [
    r'\+\s*["\']?\w+["\']?\s*\+',  # 字符串拼接
    r"template\s*=\s*`",  # JS模板字符串
    r"query.*\+.*param",  # 查询参数拼接
]
# 搜索含SQL关键词的字符串
for kw in ['select ', 'SELECT ', 'insert ', 'INSERT ', 'update ', 'UPDATE ', 
           'delete ', 'DELETE ', ' where ', ' WHERE ', ' from ', ' FROM ']:
    count = code.count(kw)
    if count > 0:
        idx = code.find(kw)
        context = code[max(0,idx-50):idx+150]
        print(f"  '{kw.strip()}': {count} occurrences | sample: {context[:200]}")

print("\n" + "="*60)
print("分析完成")
print("="*60)
