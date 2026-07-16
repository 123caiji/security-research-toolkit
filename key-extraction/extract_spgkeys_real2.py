#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取spgKeys真实配置"""
import re
import json

js_path = r"C:\Users\xianyv\AppData\Local\Temp\app_new.js"
with open(js_path, "r", encoding="utf-8") as f:
    code = f.read()

print("="*70)
print("提取spgKeys真实配置")
print("="*70)

# 查找spgKeys对象 - 用更宽松的匹配
# 寻找 "spgKeys = {" 或 spgKeys:{ 或 var spgKeys
match = re.search(r'spgKeys\s*[=:]\s*\{', code)
if not match:
    print("未找到spgKeys")
    exit()

print(f"spgKeys定义位置: {match.start()}")

# 提取完整对象
start = match.end() - 1  # 在 { 处
depth = 0
end = start
for i in range(start, min(start + 100000, len(code))):
    if code[i] == "{":
        depth += 1
    elif code[i] == "}":
        depth -= 1
        if depth == 0:
            end = i + 1
            break

spgkeys_str = code[start:end]
print(f"spgKeys对象长度: {len(spgkeys_str)} 字符")

# 显示前3000字符
print(f"\nspgKeys对象前3000字符:")
print(spgkeys_str[:3000])

# 解析所有映射
pattern = r'(\w+)\s*:\s*["\']([^"\']+)["\']'
matches = re.findall(pattern, spgkeys_str)

print(f"\n找到 {len(matches)} 个配置项")

# 过滤掉一些非配置的内容（值太短或包含特殊字符的）
config = {}
for key, value in matches:
    if len(key) > 1 and len(value) > 1 and not key.startswith("_"):
        config[key] = value

print(f"\n有效配置: {len(config)} 个")
for key, value in config.items():
    print(f"  {key} = {value}")

# 保存
with open("vuln_evidence/spgkeys_config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
print(f"\n✅ 已保存到: vuln_evidence/spgkeys_config.json")