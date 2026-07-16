#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从app_new.js提取所有API端点、参数、test端点、加密配置等信息"""

import re
import json

js_path = r'C:\Users\xianyv\AppData\Local\Temp\app_new.js'
with open(js_path, 'r', encoding='utf-8') as f:
    c = f.read()

print(f"=== 文件大小: {len(c)} 字节 ===\n")

# 1. 提取所有TranCode (格式: MODULE-NAME/apiName)
print("=" * 60)
print("=== 所有TranCode (模块/API名) ===")
print("=" * 60)
trancodes = set()
# 匹配 "XXX-YYY/zzz" 格式
for m in re.finditer(r'["\']([A-Z][A-Z_-]+[A-Z])/([a-zA-Z][a-zA-Z0-9_]+)["\']', c):
    full = f"{m.group(1)}/{m.group(2)}"
    trancodes.add((m.group(1), m.group(2), full))

# 按模块分组
modules = {}
for mod, api, full in sorted(trancodes):
    if mod not in modules:
        modules[mod] = []
    modules[mod].append(api)

for mod in sorted(modules.keys()):
    print(f"\n[{mod}] ({len(modules[mod])} APIs)")
    for api in sorted(modules[mod]):
        print(f"  - {api}")

print(f"\n总计: {len(trancodes)} 个API端点, {len(modules)} 个模块")

# 2. test端点
print("\n" + "=" * 60)
print("=== test端点 ===")
print("=" * 60)
for m in re.finditer(r'(test/[a-zA-Z0-9_]+)', c):
    s = max(0, m.start() - 80)
    e = min(len(c), m.end() + 80)
    print(f"\n{c[s:e]}")

# 3. isSgp配置
print("\n" + "=" * 60)
print("=== isSpg配置 (不走SGP转发的端点) ===")
print("=" * 60)
for m in re.finditer(r'isSpg\s*:\s*!1', c):
    s = max(0, m.start() - 200)
    e = min(len(c), m.end() + 50)
    print(f"\n{c[s:e]}")
    print("---")

# 4. spgKeys映射
print("\n" + "=" * 60)
print("=== spgKeys映射 ===")
print("=" * 60)
for m in re.finditer(r'spgKeys', c):
    s = max(0, m.start() - 20)
    e = min(len(c), m.end() + 500)
    print(c[s:e])
    print("---")
    break  # 只取第一个

# 5. K_E相关
print("\n" + "=" * 60)
print("=== K_E / K_S / K_P 密钥相关 ===")
print("=" * 60)
for m in re.finditer(r'K_[ESP]\s*[=:]', c):
    s = max(0, m.start() - 60)
    e = min(len(c), m.end() + 200)
    print(f"\n{c[s:e]}")
    print("---")

# 6. globalConfig
print("\n" + "=" * 60)
print("=== globalConfig初始化 ===")
print("=" * 60)
for m in re.finditer(r'globalConfig', c):
    s = max(0, m.start() - 30)
    e = min(len(c), m.end() + 300)
    print(f"\n{c[s:e]}")
    print("---")

# 7. 寻找其他URL路径（非sgp/transferRequest）
print("\n" + "=" * 60)
print("=== 其他URL路径 (非sgp/transferRequest) ===")
print("=" * 60)
urls = set()
for m in re.finditer(r'["\']/?(dlydjd/[a-zA-Z0-9/_-]+)["\']', c):
    urls.add(m.group(1))
for u in sorted(urls):
    print(f"  /{u}")

# 8. 寻找可能的文件下载/上传端点
print("\n" + "=" * 60)
print("=== 文件相关API ===")
print("=" * 60)
for keyword in ['download', 'upload', 'file', 'File', 'export', 'Export', 'import', 'Import']:
    for m in re.finditer(rf'["\']([a-zA-Z]*{keyword}[a-zA-Z]*)["\']', c):
        word = m.group(1)
        if len(word) > 4 and len(word) < 30:
            s = max(0, m.start() - 50)
            e = min(len(c), m.end() + 50)
            ctx = c[s:e].replace('\n', ' ')
            print(f"  {word}: ...{ctx}...")
            break  # 每个keyword只取第一个

print("\n=== 完成 ===")
