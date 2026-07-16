#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZLMediaKit 安全信息收集脚本
- 只调用查询类接口（GET请求）
- 不做任何破坏性操作
- 限速请求，避免影响服务
"""

import requests
import json
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET = "http://58.220.222.66:8090"
SECRET = "035c73f7-bb6b-4889-a715-d9eb2d1925cc"

# 安全的查询接口列表（只读，不影响服务）
SAFE_APIS = [
    ("版本信息", "/index/api/version", {}),
    ("服务器统计", "/index/api/getStatistic", {}),
    ("服务器配置", "/index/api/getServerConfig", {}),
    ("媒体列表", "/index/api/getMediaList", {}),
    ("RTP服务器列表", "/index/api/listRtpServer", {}),
    ("线程负载", "/index/api/getThreadsLoad", {}),
    ("工作线程负载", "/index/api/getWorkThreadsLoad", {}),
]

SENSITIVE_KEYWORDS = [
    "password", "passwd", "pwd", "secret", "token", "key",
    "api_key", "apikey", "access_key", "secret_key",
    "admin", "root", "数据库", "database", "mysql",
    "redis", "mongo", "账号", "用户名", "密码", "密钥"
]

print("=" * 70)
print("  ZLMediaKit 安全信息收集")
print("  目标: " + TARGET)
print("  说明: 仅调用只读查询接口，不影响服务正常运行")
print("=" * 70)
print()

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json,*/*",
})

found_sensitive = []

for name, path, params in SAFE_APIS:
    url = f"{TARGET}{path}"
    full_params = {"secret": SECRET, **params}
    
    print(f"[+] 正在获取: {name}")
    print(f"    接口: {path}")
    
    try:
        time.sleep(0.5)  # 限速，避免压力
        response = session.get(url, params=full_params, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                code = data.get("code", -1)
                
                if code == 0:
                    result_data = data.get("data", data)
                    print(f"    状态: ✅ 获取成功")
                    
                    # 检查敏感信息
                    data_str = json.dumps(result_data, ensure_ascii=False).lower()
                    for keyword in SENSITIVE_KEYWORDS:
                        if keyword.lower() in data_str:
                            found_sensitive.append((name, keyword, path))
                    
                    # 显示内容摘要
                    if isinstance(result_data, dict):
                        keys = list(result_data.keys())
                        print(f"    字段数: {len(keys)}个")
                        if len(keys) <= 15:
                            for k in keys[:15]:
                                v = str(result_data[k])[:80]
                                # 对疑似敏感字段打码
                                is_sensitive = any(kw in k.lower() for kw in SENSITIVE_KEYWORDS)
                                if is_sensitive:
                                    v = "*** (疑似敏感，已打码) ***"
                                print(f"      - {k}: {v}")
                        else:
                            print(f"      (字段较多，已省略)")
                            
                            # 单独检查并显示疑似敏感字段
                            for k in keys:
                                if any(kw in k.lower() for kw in SENSITIVE_KEYWORDS):
                                    print(f"      ⚠️  疑似敏感字段: {k}")
                    
                    elif isinstance(result_data, list):
                        print(f"    数据项: {len(result_data)}条")
                        if len(result_data) > 0:
                            first = result_data[0]
                            if isinstance(first, dict):
                                print(f"    首项字段: {list(first.keys())}")
                    
                else:
                    msg = data.get("msg", "未知错误")
                    print(f"    状态: ⚠️  返回错误 (code={code}, msg={msg})")
            
            except json.JSONDecodeError:
                print(f"    状态: ⚠️  响应非JSON")
                print(f"    内容: {response.text[:200]}")
        else:
            print(f"    状态: ❌ HTTP {response.status_code}")
    
    except Exception as e:
        print(f"    状态: ❌ 异常: {e}")
    
    print()

print("=" * 70)
print("  敏感信息检测结果")
print("=" * 70)
print()

if found_sensitive:
    print(f"⚠️  发现 {len(found_sensitive)} 处疑似敏感信息:")
    print()
    for i, (api_name, keyword, path) in enumerate(found_sensitive):
        print(f"  {i+1}. {api_name} ({path})")
        print(f"     匹配关键词: {keyword}")
        print()
else:
    print("✅ 未在返回数据中发现明显的密码/密钥字段")
    print("   （但配置中可能有其他敏感信息，建议人工复核）")

print()
print("=" * 70)
print("  测试完成")
print("  说明: 以上测试均为只读查询，未对服务做任何修改")
print("=" * 70)
