#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查找getVueAppString函数的完整实现"""

import re

js_path = r'C:\Users\xianyv\AppData\Local\Temp\app_new.js'
with open(js_path, 'r', encoding='utf-8') as f:
    c = f.read()

# 搜索 t.getVueAppString=m 的位置，然后向前搜索 m 的定义
print("=== 搜索 getVueAppString 模块定义 ===\n")

# 找到 "t.getVueAppString=m" 的位置
idx = c.find("t.getVueAppString=m")
if idx == -1:
    idx = c.find("getVueAppString=m")

if idx != -1:
    # 向前搜索，找到模块函数的开始
    # 在webpack中，模块格式通常是: function(e,t,s){...}
    # 找到最近的模块开始
    search_start = max(0, idx - 5000)
    chunk = c[search_start:idx+100]
    
    # 搜索函数 m 的定义
    # m 可能定义为: var m=function 或 function m( 或 m=function
    for pat in [r'var\s+m\s*=\s*function', r'm\s*=\s*function\s*\(', r'function\s+m\s*\(', r'm\s*=\s*function']:
        for m in re.finditer(pat, chunk):
            s = max(0, m.start() - 50)
            e = min(len(chunk), m.end() + 500)
            print(f"--- 匹配: {pat} ---")
            print(chunk[s:e])
            print()

# 另一种方法：搜索包含 atob 和 charCodeAt 的代码段（Base64解码 + XOR）
print("\n=== 搜索 Base64解码+XOR 代码 ===\n")
for m in re.finditer(r'atob', c):
    s = max(0, m.start() - 200)
    e = min(len(c), m.end() + 500)
    ctx = c[s:e]
    if 'charCodeAt' in ctx or 'fromCharCode' in ctx or 'xor' in ctx.lower() or '^' in ctx:
        print(f"--- 位置 {m.start()} ---")
        print(ctx)
        print()

# 搜索包含 ^ (XOR操作符) 和 charCodeAt 的代码
print("\n=== 搜索 XOR + charCodeAt 代码 ===\n")
for m in re.finditer(r'charCodeAt.*\^|fromCharCode', c):
    s = max(0, m.start() - 200)
    e = min(len(c), m.end() + 200)
    ctx = c[s:e]
    if 'atob' in ctx or 'base64' in ctx.lower() or 'btoa' in ctx:
        print(f"--- 位置 {m.start()} ---")
        print(ctx)
        print()

# 搜索 VUEAPP 相关的解码逻辑
print("\n=== 搜索 VUEAPP 解码逻辑 ===\n")
for keyword in ['VUEAPPE', 'VUEAPPS', 'VUEAPPP', 'VUEAPPDHM', 'VUEAPPSUK']:
    for m in re.finditer(rf'["\']({keyword})["\']', c):
        s = max(0, m.start() - 300)
        e = min(len(c), m.end() + 100)
        ctx = c[s:e]
        if 'function' in ctx or 'return' in ctx or 'charCode' in ctx:
            print(f"--- {keyword} ---")
            print(ctx)
            print()
            break

print("=== 完成 ===")
