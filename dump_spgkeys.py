#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取sgp.keys.js配置"""
import re

js_path = r"C:\Users\xianyv\AppData\Local\Temp\app_new.js"
with open(js_path, "r", encoding="utf-8") as f:
    code = f.read()

# 找 sgp.keys.js
pattern = r'\./src/config/sgp\.keys\.js["\']?\s*:\s*function\s*\([^)]+\)\s*\{'
match = re.search(pattern, code)
if not match:
    print("未找到 sgp.keys.js")
    exit()

start = match.start()
# 找配对的 }
depth = 0
end = start
for i in range(match.end()-1, min(len(code), start+200000)):
    if code[i] == "{":
        depth += 1
    elif code[i] == "}":
        depth -= 1
        if depth == 0:
            end = i + 1
            break

print(f"sgp.keys.js 模块长度: {end-start}")

# 解析所有的 key: "value" 映射
content = code[start:end]
print(content[:5000])
print("...")
print(content[-2000:])