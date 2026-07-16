#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取spgKeys和所有API定义"""
import re
import json

with open(r"C:\Users\xianyv\AppData\Local\Temp\app_new.js", 'r', encoding='utf-8') as f:
    code = f.read()

# 1. 提取spgKeys映射
print("="*60)
print("1. spgKeys 模块名映射")
print("="*60)

# 找 spgKeys: { ... } 
# 先找开始位置
start = code.find('spgKeys:{')
if start < 0:
    start = code.find('spgKeys:{')
if start < 0:
    # 找 spgKeys = {
    start = code.find('spgKeys={')
if start < 0:
    start = code.find('.spgKeys={')
    
print(f"spgKeys start at: {start}")

if start > 0:
    # 找到匹配的闭合花括号
    depth = 0
    i = code.find('{', start)
    start_obj = i
    for i in range(start_obj, min(start_obj + 5000, len(code))):
        if code[i] == '{':
            depth += 1
        elif code[i] == '}':
            depth -= 1
            if depth == 0:
                spg_keys_obj = code[start_obj:i+1]
                print(f"Length: {len(spg_keys_obj)} chars")
                # 提取键值对
                pairs = re.findall(r'(\w+):\s*"([^"]+)"', spg_keys_obj)
                print(f"\nFound {len(pairs)} module mappings:")
                for k, v in sorted(pairs):
                    print(f"  {k} = {v}")
                break

# 2. 提取所有API定义
print("\n" + "="*60)
print("2. 所有API定义 (SGP和非SGP)")
print("="*60)

# 找包含 url: 和 TranCode: 的对象
# 模式: apiName:{url:"...",TranCode:"...",isSgp:!0}
api_pattern = r'(\w+):\{url:"([^"]+)"[^}]*TranCode:"([^"]*)"[^}]*(isSgp:\!0|isSgp:\!1)?[^}]*\}'
matches = re.findall(api_pattern, code)
print(f"Found {len(matches)} API definitions")

apis_sgp = []
apis_non_sgp = []
for name, url, trancode, sgp_flag in matches:
    is_sgp = sgp_flag != 'isSgp:!1'  # 默认是SGP
    if is_sgp:
        apis_sgp.append((name, url, trancode))
    else:
        apis_non_sgp.append((name, url, trancode))

print(f"\nSGP APIs ({len(apis_sgp)}):")
for name, url, trancode in sorted(apis_sgp, key=lambda x: x[0])[:30]:
    print(f"  {name}: url={url}, TranCode={trancode}")

print(f"\nNon-SGP APIs ({len(apis_non_sgp)}):")
for name, url, trancode in sorted(apis_non_sgp, key=lambda x: x[0]):
    print(f"  {name}: url={url}, TranCode={trancode}")

# 3. 提取CUST_INFO模块的API
print("\n" + "="*60)
print("3. CUST_INFO 模块 API (客户信息)")
print("="*60)

# 找所有TranCode包含CUST-INFO的
cust_pattern = r'(\w+):\{[^}]*TranCode:"[^"]*CUST[^"]*"[^}]*\}'
cust_matches = re.findall(cust_pattern, code)
print(f"CUST-related APIs: {len(cust_matches)}")
for m in cust_matches[:20]:
    print(f"  {m}")

# 4. 提取EC-FILE-MGR模块的API
print("\n" + "="*60)
print("4. EC-FILE-MGR 模块 API (文件管理)")
print("="*60)

file_pattern = r'(\w+):\{[^}]*TranCode:"[^"]*FILE[^"]*"[^}]*\}'
file_matches = re.findall(file_pattern, code)
print(f"File-related APIs: {len(file_matches)}")
for m in file_matches[:20]:
    print(f"  {m}")

# 5. 直接找 fileUpload 和 minioDownload 完整URL
print("\n" + "="*60)
print("5. 文件上传下载服务地址")
print("="*60)

# 找 fileUrl 配置
for kw in ['fileUrl', 'upLoadFileService', 'getFileService', 'fileUploadList']:
    idx = code.find(kw)
    if idx > 0:
        context = code[max(0,idx-200):idx+200]
        print(f"\n'{kw}' at {idx}:")
        print(f"  {context[:400]}")

# 6. 提取完整的API定义文件部分
print("\n" + "="*60)
print("6. 查找src/api/index.js 部分")
print("="*60)

idx = code.find('"./src/api/index.js"')
if idx > 0:
    context = code[idx:idx+5000]
    print(f"Found at {idx}, context:")
    print(context[:3000])

# 7. 找 upload 端点
print("\n" + "="*60)
print("7. upload 端点")
print("="*60)

idx = code.find('url:"upload"')
if idx > 0:
    context = code[max(0,idx-100):idx+300]
    print(context[:400])

# 8. 更多非SGP端点 - 找所有 isSgp:!1
print("\n" + "="*60)
print("8. 所有非SGP端点详细列表")
print("="*60)

# 用更宽的上下文
non_sgp_pattern = r'(\w+):\{([^{}]*isSgp:\!1[^{}]*)\}'
non_sgp_matches = re.findall(non_sgp_pattern, code)
print(f"Total non-SGP endpoint objects: {len(non_sgp_matches)}")
seen = set()
for name, body in non_sgp_matches:
    url_match = re.search(r'url:\s*"([^"]+)"', body)
    tc_match = re.search(r'TranCode:\s*"([^"]*)"', body)
    url = url_match.group(1) if url_match else "N/A"
    tc = tc_match.group(1) if tc_match else "N/A"
    key = f"{name}|{url}"
    if key not in seen:
        seen.add(key)
        print(f"  {name}: url={url}, TranCode={tc}")

print("\n分析完成")
