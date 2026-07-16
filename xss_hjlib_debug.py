#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hjlib.cn 深度探测 - 检查所有参数的反射情况
"""

import requests
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,*/*",
})

url = "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do"
marker = "MARKER123TEST"

params_list = ["q", "filterDynasty", "filterReignTitle", "filterValue", "recordcode", "type", "keyword"]

for param in params_list:
    try:
        resp = session.get(url, params={param: marker}, timeout=8, verify=False)
        if marker in resp.text:
            idx = resp.text.find(marker)
            ctx = resp.text[max(0,idx-100):idx+100]
            print(f"✅ [{param}] 反射!")
            print(f"   上下文: {ctx}")
            print()
        else:
            print(f"❌ [{param}] 不反射")
    except Exception as e:
        print(f"❌ [{param}] {e}")
    time.sleep(0.2)

# 试试多个参数组合
print("\n--- 多参数组合 ---")
combinations = [
    {"q": marker, "type": "1"},
    {"filterDynasty": marker, "type": "1"},
    {"q": "test", "filterDynasty": marker},
    {"q": marker, "filterValue": marker},
]
for combo in combinations:
    try:
        resp = session.get(url, params=combo, timeout=8, verify=False)
        count = resp.text.count(marker)
        if count > 0:
            print(f"✅ 组合 {list(combo.keys())}: 出现 {count} 次")
            idx = resp.text.find(marker)
            print(f"   {resp.text[max(0,idx-80):idx+80]}")
        else:
            print(f"❌ 组合 {list(combo.keys())}: 不反射")
    except Exception as e:
        print(f"❌ {e}")
    time.sleep(0.2)

# 试试不带参数，检查原始页面是否已经有某些内容
print("\n--- 原始页面分析 ---")
resp = session.get(url, timeout=8, verify=False)
body = resp.text
# 搜索value=属性中的内容
import re
values = re.findall(r'value=["\']([^"\']*)["\']', body)
print(f"value属性值: {values[:10]}")

# 搜索type=text的input
inputs = re.findall(r'<input[^>]*>', body)
for inp in inputs[:10]:
    print(f"input标签: {inp}")
