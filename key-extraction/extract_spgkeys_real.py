#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取spgKeys真实配置 - 这是所有TranCode的真实映射"""
import re
import json

js_path = r"C:\Users\xianyv\AppData\Local\Temp\app_new.js"
with open(js_path, "r", encoding="utf-8") as f:
    code = f.read()

print("="*70)
print("提取spgKeys真实配置")
print("="*70)

# 查找spgKeys定义
idx = code.find("spgKeys")
if idx == -1:
    print("未找到spgKeys")
    exit()

# 找到spgKeys对象定义的开始
# 查找 spgKeys: { 或 spgKeys={
search_start = idx
while search_start < len(code):
    if code[search_start:search_start+10] in ["spgKeys: {", "spgKeys:{"]:
        break
    search_start += 1

print(f"spgKeys定义开始位置: {search_start}")

# 提取spgKeys对象
depth = 0
start_pos = -1
for i in range(search_start, min(search_start + 50000, len(code))):
    if code[i] == "{":
        if depth == 0:
            start_pos = i
        depth += 1
    elif code[i] == "}":
        depth -= 1
        if depth == 0:
            end_pos = i + 1
            break

if start_pos > 0:
    spgkeys_str = code[start_pos:end_pos]
    print(f"spgKeys对象长度: {len(spgkeys_str)} 字符")

    # 解析所有的 key:value 映射
    # 格式: KEY_NAME: "value"
    pattern = r'(\w+)\s*:\s*["\x27]([^"\x27]+)["\x27]'
    matches = re.findall(pattern, spgkeys_str)

    print(f"\n找到 {len(matches)} 个配置项:")
    for key, value in matches:
        print(f"  {key} = {value}")

    # 保存为JSON
    config = {k: v for k, v in matches}
    with open("vuln_evidence/spgkeys_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 配置已保存到: vuln_evidence/spgkeys_config.json")

    # 提取重要的TranCode值
    important_keys = [
        "SSP_AUTH", "CUST_INFO", "EC_IDEN", "EC_FILE_MGR",
        "AGRE_AGRE", "IMPLEMENT", "EC_PROD", "TRAD_OPRO",
        "PAYM_PPRO", "HOUSE_CREDIT", "OMP_CMGR"
    ]
    print(f"\n关键TranCode值:")
    for k in important_keys:
        if k in config:
            print(f"  {k} = \"{config[k]}\"")