#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hjlib.cn 页面分析 + XSS测试
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
    "Accept-Language": "zh-CN,zh;q=0.9",
})

# 第1步：获取页面内容，找参数名
urls = [
    "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do",
    "http://www.hjlib.cn:8088/navigation/newNavigationFacet.do",
    "http://thg.hjlib.cn:8088/navigation/oldNavigationFacet.do",
    "http://thg.hjlib.cn:8088/navigation/newNavigationFacet.do",
]

print("=" * 70)
print("  hjlib.cn 页面分析")
print("=" * 70)

for url in urls:
    print(f"\n  URL: {url}")
    try:
        resp = session.get(url, timeout=10, verify=False)
        print(f"  状态码: {resp.status_code} | 长度: {len(resp.content)}")
        print(f"  Server: {resp.headers.get('Server', 'N/A')}")

        body = resp.text

        # 提取所有form
        forms = re.findall(r'<form[^>]*action=["\']?([^"\'>\s]*)[^>]*>(.*?)</form>', body, re.DOTALL)
        if forms:
            for action, content in forms:
                inputs = re.findall(r'<input[^>]*name=["\']?(\w+)', content)
                print(f"  表单: action={action} | 参数: {inputs}")

        # 提取所有input
        inputs = re.findall(r'<input[^>]*name=["\']?(\w+)', body)
        if inputs:
            print(f"  Input字段: {inputs}")

        # 提取所有a标签href中的参数
        hrefs = re.findall(r'href=["\'][^"\']*\?([^"\']*)', body)
        if hrefs:
            params = set()
            for h in hrefs:
                for p in h.split("&"):
                    if "=" in p:
                        params.add(p.split("=")[0])
            if params:
                print(f"  URL参数: {list(params)}")

        # 提取script中的参数名
        scripts = re.findall(r'(?:name|param|keyword|query)["\s:=]+["\'](\w+)', body)
        if scripts:
            print(f"  Script参数: {scripts}")

        # 搜索search相关的form
        search_forms = re.findall(r'<form[^>]*(?:search|query|keyword)[^>]*>(.*?)</form>', body, re.DOTALL | re.IGNORECASE)
        if search_forms:
            for content in search_forms:
                print(f"  搜索表单内容: {content[:200]}")

        # 输出页面前500字符看看结构
        print(f"\n  页面前300字符:")
        print(f"  {body[:300]}")

    except Exception as e:
        print(f"  ❌ {e}")

# 第2步：用发现的参数名测试XSS
print(f"\n\n{'='*70}")
print("  XSS测试（用发现的参数名）")
print("=" * 70)

# 从原始告报文中，注入点是URL参数中的值
# 试试直接在URL中注入
xss_tests = [
    # 试试带POST方法
    {
        "method": "GET",
        "url": "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "params": {"keyword": "test", "catalogId": "1 web_xss_in_tag=85f7210c blah="},
    },
    {
        "method": "GET",
        "url": "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "params": {"keyword": "test", "facet": "1 web_xss_in_tag=85f7210c blah="},
    },
    # 试试直接拼接到URL后面
    {
        "method": "GET",
        "url": "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do?keyword=test%20web_xss_in_tag%3D85f7210c%20blah%3D",
        "params": {},
    },
    {
        "method": "GET",
        "url": "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do?catalogId=1%20web_xss_in_tag%3D85f7210c%20blah%3D",
        "params": {},
    },
    # POST方法
    {
        "method": "POST",
        "url": "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "data": {"keyword": "test web_xss_in_tag=85f7210c blah="},
    },
    {
        "method": "POST",
        "url": "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "data": {"q": "test web_xss_in_tag=85f7210c blah="},
    },
]

for test in xss_tests:
    try:
        if test["method"] == "GET":
            resp = session.get(test["url"], params=test.get("params", {}), timeout=8, verify=False)
        else:
            resp = session.post(test["url"], data=test.get("data", {}), timeout=8, verify=False)

        if "web_xss_in_tag" in resp.text:
            idx = resp.text.find("web_xss_in_tag")
            ctx = resp.text[max(0,idx-60):idx+80]
            print(f"  ✅ {test['method']} {test['url'][:60]}")
            print(f"     反射: {ctx[:120]}")
        elif "85f7210c" in resp.text:
            print(f"  ✅ 标记反射: {test['url'][:60]}")
        else:
            print(f"  ❌ 未反射: {test['method']} {test['url'][:60]} ({resp.status_code})")
    except Exception as e:
        print(f"  ❌ {test['method']} -> {e}")

    time.sleep(0.3)
