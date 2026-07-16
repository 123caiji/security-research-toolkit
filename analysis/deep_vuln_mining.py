#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度挖掘敏感业务接口和漏洞模式"""
import re
import json

js_path = r'C:\Users\xianyv\AppData\Local\Temp\app_new.js'
with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

print("=" * 70)
print("=== 1. 搜索客户信息/身份证/手机号相关API ===")
print("=" * 70)

# 搜索与客户信息相关的TranCode
customer_keywords = ['customer', 'cust', 'idcard', 'idCard', 'IdCard', 'IDCARD',
                     'phone', 'mobile', 'name', 'identity', 'person', 'client',
                     '查询客户', '客户信息', '身份证', '手机号', '姓名', '个人信息']

# 提取所有TranCode格式
pattern_trancode = r'["\x27]([A-Z]+-[A-Z]+/[a-zA-Z0-9]+)["\x27]'
trancodes = re.findall(pattern_trancode, code)
unique_trancodes = sorted(list(set(trancodes)))

# 按模块分组
modules = {}
for t in unique_trancodes:
    mod = t.split('/')[0]
    if mod not in modules:
        modules[mod] = []
    modules[mod].append(t)

print(f"\n总TranCode数: {len(unique_trancodes)}")
print(f"模块数: {len(modules)}")
print()

print("=== 模块列表 ===")
for mod in sorted(modules.keys()):
    print(f"  {mod}: {len(modules[mod])} 个API")

print()
print("=" * 70)
print("=== 2. 搜索敏感业务模块的所有API ===")
print("=" * 70)

sensitive_modules = ['EC-CUST', 'EC-LOAN', 'EC-FILE', 'SSP-AUTH', 'EC-BIZ', 
                     'EC-CREDIT', 'EC-ACCT', 'EC-ORG', 'EC-SYS', 'EC-USER']

for mod in sensitive_modules:
    if mod in modules:
        print(f"\n--- {mod} ---")
        for api in sorted(modules[mod]):
            print(f"  {api}")

print()
print("=" * 70)
print("=== 3. 搜索查询类API (可能存在SQL注入/越权) ===")
print("=" * 70)

query_patterns = ['query', 'Query', 'get', 'Get', 'list', 'List', 'find', 'Find',
                  'select', 'search', 'Search', 'detail', 'Detail', 'info', 'Info']

for mod in sorted(modules.keys()):
    query_apis = []
    for api in modules[mod]:
        api_name = api.split('/')[1]
        for pat in query_patterns:
            if pat in api_name:
                query_apis.append(api)
                break
    if query_apis:
        print(f"\n--- {mod} (查询类API: {len(query_apis)}) ---")
        for api in sorted(query_apis):
            print(f"  {api}")

print()
print("=" * 70)
print("=== 4. 搜索修改/删除/新增类API (业务逻辑漏洞) ===")
print("=" * 70)

modify_patterns = ['save', 'Save', 'update', 'Update', 'delete', 'Delete',
                   'add', 'Add', 'insert', 'Insert', 'create', 'Create',
                   'modify', 'Modify', 'edit', 'Edit', 'remove', 'Remove',
                   'submit', 'Submit', 'approve', 'Approve', 'audit', 'Audit']

for mod in sorted(modules.keys()):
    modify_apis = []
    for api in modules[mod]:
        api_name = api.split('/')[1]
        for pat in modify_patterns:
            if pat in api_name:
                modify_apis.append(api)
                break
    if modify_apis:
        print(f"\n--- {mod} (修改类API: {len(modify_apis)}) ---")
        for api in sorted(modify_apis):
            print(f"  {api}")

print()
print("=" * 70)
print("=== 5. 搜索文件相关API ===")
print("=" * 70)

file_patterns = ['file', 'File', 'upload', 'Upload', 'download', 'Download',
                 'image', 'Image', 'pdf', 'PDF', 'attach', 'Attach', 'doc', 'Doc']

for mod in sorted(modules.keys()):
    file_apis = []
    for api in modules[mod]:
        api_name = api.split('/')[1]
        for pat in file_patterns:
            if pat in api_name:
                file_apis.append(api)
                break
    if file_apis:
        print(f"\n--- {mod} (文件类API: {len(file_apis)}) ---")
        for api in sorted(file_apis):
            print(f"  {api}")

print()
print("=" * 70)
print("=== 6. 搜索OCR/人脸识别/生物识别相关API ===")
print("=" * 70)

ocr_patterns = ['ocr', 'OCR', 'face', 'Face', 'bio', 'Bio', 'identify', 'Identify',
                'recognize', 'Recognize', 'verification', 'Verification', 'liveness',
                '活体', '人脸', '识别', '比对', '身份证']

for mod in sorted(modules.keys()):
    ocr_apis = []
    for api in modules[mod]:
        api_name = api.split('/')[1]
        for pat in ocr_patterns:
            if pat in api_name:
                ocr_apis.append(api)
                break
    if ocr_apis:
        print(f"\n--- {mod} (OCR/生物识别API: {len(ocr_apis)}) ---")
        for api in sorted(ocr_apis):
            print(f"  {api}")

print()
print("=" * 70)
print("=== 7. 搜索非SGP接口 (直接URL访问) ===")
print("=" * 70)

# 搜索http://或http/开头的API路径
http_patterns = re.findall(r'["\x27]((?:http[\\/]|[a-z]+[\\/])[a-zA-Z0-9\\/\-]+)["\x27]', code)
unique_http = sorted(list(set(http_patterns)))
print(f"发现 {len(unique_http)} 个非SGP API路径:")
for path in unique_http[:50]:
    print(f"  {path}")
if len(unique_http) > 50:
    print(f"  ... 还有 {len(unique_http) - 50} 个")

print()
print("=" * 70)
print("=== 8. 搜索可能的SQL注入关键字 ===")
print("=" * 70)

# 搜索拼接SQL的模式
sql_injection_patterns = [
    r'\+\s*["\x27]\s*(?:SELECT|select|INSERT|insert|UPDATE|update|DELETE|delete)\b',
    r'\.concat\s*\(\s*["\x27]\s*(?:SELECT|select)',
    r'["\x27]\s*\+\s*\w+\s*\+\s*["\x27]\s*(?:WHERE|where|AND|and|OR|or)\b',
    r'sql\s*[=:]\s*["\x27]',
    r'query\s*[=:]\s*["\x27]',
]

found_sqli = False
for pat in sql_injection_patterns:
    matches = re.findall(pat, code)
    if matches:
        found_sqli = True
        print(f"\n模式: {pat}")
        for m in matches[:10]:
            print(f"  {m[:100]}")

if not found_sqli:
    print("  前端代码中未发现明显SQL拼接（符合前后端分离架构预期）")

print()
print("=" * 70)
print("=== 9. 搜索密码学弱点 ===")
print("=" * 70)

crypto_issues = [
    r'ECB\b',
    r'md5\b',
    r'sha1\b',
    r'base64.*password',
    r'password.*base64',
    r'hardcode.*key',
    r'key.*hardcode',
]

for pat in crypto_issues:
    matches = re.findall(pat, code, re.IGNORECASE)
    if matches:
        print(f"\n{pat}: {len(matches)} 处匹配")

print()
print("=== SM4 ECB模式 ===")
ecb_matches = re.findall(r'sm4.*?ecb|ecb.*?sm4', code, re.IGNORECASE)
print(f"  ECB模式使用: {len(ecb_matches)} 处")

print()
print("=" * 70)
print("=== 完成 ===")
print("=" * 70)
