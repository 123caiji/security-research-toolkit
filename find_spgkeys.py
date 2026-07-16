#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取真实的spgKeys配置"""
import re

js_path = r"C:\Users\xianyv\AppData\Local\Temp\app_new.js"
with open(js_path, "r", encoding="utf-8") as f:
    code = f.read()

# 查找 config/index.js 的模块定义
# webpack打包后格式: "./src/config/index.js":function(e,t,s){...}
pattern = r'\./src/config/index\.js["\']?\s*:\s*function\s*\([^)]+\)\s*\{'
match = re.search(pattern, code)
if not match:
    pattern2 = r'\./config/index\.js["\']?\s*:\s*function\s*\([^)]+\)\s*\{'
    match = re.search(pattern2, code)

if match:
    start = match.start()
    print(f"找到 config/index.js 模块: {start}")
    # 提取3000字符查看
    print(code[start:start+3000])
else:
    print("未找到 config/index.js 模块")
    # 尝试找 spgKeys: 模式
    idx = code.find("spgKeys")
    print(f"spgKeys位置: {idx}")
    # 向前找最近的function
    func_idx = code.rfind("function(", 0, idx)
    if func_idx > 0:
        print(f"前一个function: {func_idx}")
        # 找到对应的 {
        brace_idx = code.find("{", func_idx)
        if brace_idx > 0 and brace_idx < idx:
            print(f"从 {brace_idx} 开始提取")
            print(code[brace_idx:brace_idx+5000])