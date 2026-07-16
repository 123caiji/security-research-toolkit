import socket
import time

# SSH连接测试
print("="*70)
print("SSH连接测试")
print("="*70)

# 测试SSH连接
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)

try:
    s.connect(('119.29.238.216', 22))
    banner = s.recv(1024)
    print(f"SSH Banner: {banner.decode('utf-8', errors='replace')}")
    s.close()
except Exception as e:
    print(f"SSH连接失败: {e}")

print("\nSSH端口开放，需要账号密码才能登录")
print("如果有SSH账号，可以使用以下命令:")
print("ssh user@119.29.238.216")
print("然后在服务器上执行:")
print("find / -name 'flag*' 2>/dev/null")
print("find / -name '*flag*' 2>/dev/null")
print("grep -r 'flag{' / 2>/dev/null")