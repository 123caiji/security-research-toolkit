#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取spgKeys和关键漏洞信息v3"""
import re
import json

with open(r"C:\Users\xianyv\AppData\Local\Temp\app_new.js", 'r', encoding='utf-8') as f:
    code = f.read()

# 1. 从 config/index.js 提取 spgKeys
print("="*60)
print("1. spgKeys 模块名映射 (从config)")
print("="*60)

# 找 spgKeys:{...} 
idx = code.find('spgKeys:')
if idx > 0:
    # 找到花括号开始
    brace_start = code.find('{', idx)
    if brace_start > 0:
        depth = 0
        end = brace_start
        for i in range(brace_start, min(brace_start + 3000, len(code))):
            if code[i] == '{':
                depth += 1
            elif code[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        spg_keys_str = code[brace_start:end]
        print(f"spgKeys block: {len(spg_keys_str)} chars")
        # 提取所有键值对
        pairs = re.findall(r'(\w+):\s*"([^"]+)"', spg_keys_str)
        print(f"Modules: {len(pairs)}")
        for k, v in sorted(pairs):
            print(f"  {k:20s} = {v}")
        
        # 保存
        with open(r"e:\BaiduNetdiskDownload\1\spg_keys.json", 'w', encoding='utf-8') as f:
            json.dump(dict(pairs), f, ensure_ascii=False, indent=2)
        print(f"\nSaved to spg_keys.json")

# 2. 提取ajaxConfig配置
print("\n" + "="*60)
print("2. ajaxConfig 配置 (fileUrl等)")
print("="*60)

idx = code.find('ajaxConfig:')
if idx > 0:
    brace_start = code.find('{', idx)
    if brace_start > 0:
        depth = 0
        end = brace_start
        for i in range(brace_start, min(brace_start + 2000, len(code))):
            if code[i] == '{':
                depth += 1
            elif code[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        config_str = code[brace_start:end]
        print(f"ajaxConfig: {len(config_str)} chars")
        print(config_str[:1500])

# 3. DH密钥完整流程
print("\n" + "="*60)
print("3. DH密钥协商完整代码")
print("="*60)

# 找 initUserKeyGroup 的action
for kw in ['initUserKeyGroup:', 'initUserKeyGroup:function', 'initNonceToken:']:
    idx = code.find(kw)
    if idx > 0:
        context = code[max(0,idx-100):idx+1500]
        print(f"\n--- {kw} at {idx} ---")
        print(context[:1200])

# 4. 加密API列表 (isApiUseEncryptionList)
print("\n" + "="*60)
print("4. isApiUseEncryptionList 接口")
print("="*60)

idx = code.find('isApiUseEncryptionList:')
if idx > 0:
    context = code[max(0,idx-50):idx+600]
    print(context[:600])

# 5. buildNonceToken 接口
print("\n" + "="*60)
print("5. buildNonceToken 接口")
print("="*60)

idx = code.find('buildNonceToken:')
if idx > 0:
    context = code[max(0,idx-50):idx+600]
    print(context[:600])

# 6. 文件上传接口完整分析
print("\n" + "="*60)
print("6. 文件上传接口完整分析")
print("="*60)

# 找文件上传相关的完整模块
idx = code.find('./src/api/image-upload/index.js')
if idx > 0:
    context = code[idx:idx+3000]
    print(f"image-upload module:")
    print(context[:2000])

# 7. 找 $uploadFile 的实现
print("\n" + "="*60)
print("7. $uploadFile 实现")
print("="*60)

idx = code.find('$uploadFile')
if idx > 0:
    context = code[max(0,idx-200):idx+800]
    print(context[:1000])

# 8. 所有模块名列表 - 从 spgKeys 提取后推断
# 先确认 spgKeys 的值
print("\n" + "="*60)
print("8. 所有API模块 (基于spgKeys)")
print("="*60)

# 搜索所有 spgKeys.XXX 引用
spg_refs = re.findall(r'spgKeys\.(\w+)', code)
unique_refs = sorted(list(set(spg_refs)))
print(f"Referenced spgKeys modules: {len(unique_refs)}")
for m in unique_refs:
    print(f"  {m}")

# 9. VUEAPPDHM 解码
print("\n" + "="*60)
print("9. VUEAPPDHM 解码 (DH modulus)")
print("="*60)

# getVueAppString("OzohMWE=","VUEAPPDHM")
encoded_dhm = "OzohMWE="
xor_key_dhm = "VUEAPPDHM"

import base64
decoded = base64.b64decode(encoded_dhm)
xor_result = bytearray()
for i, b in enumerate(decoded):
    xor_result.append(b ^ ord(xor_key_dhm[i % len(xor_key_dhm)]))

print(f"Encoded: {encoded_dhm}")
print(f"XOR key: {xor_key_dhm}")
print(f"Decoded bytes: {decoded.hex()}")
print(f"XOR result: {xor_result.decode('utf-8', errors='replace')}")
print(f"XOR hex: {xor_result.hex()}")

# 10. SM4加密使用场景统计
print("\n" + "="*60)
print("10. SM4加密/解密使用场景")
print("="*60)

for kw in ['.encrypt(', '.decrypt(', 'sm4.encrypt', 'sm4.decrypt', 'getSecretKey']:
    count = code.count(kw)
    if count > 0:
        idx = code.find(kw)
        context = code[max(0,idx-100):idx+200]
        print(f"\n'{kw}' ({count} occurrences) - first at {idx}:")
        print(f"  {context[:300]}")

print("\n分析完成")
