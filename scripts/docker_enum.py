import subprocess
import sys
import os

def docker_enum(target_ip=None):
    print("[*] Docker容器枚举")
    
    commands = [
        "docker ps -a",
        "docker images",
        "docker info",
        "ls -la /var/run/docker.sock",
        "cat /etc/docker/daemon.json 2>/dev/null || echo 'No daemon.json'",
        "docker network ls",
        "docker volume ls"
    ]
    
    if target_ip:
        print(f"[*] 目标主机: {target_ip}")
        print("[*] 请在目标主机上执行以下命令:")
        for cmd in commands:
            print(f"    {cmd}")
        return
    
    print("[*] 本地Docker信息收集:")
    for cmd in commands:
        print(f"\n[+] 执行: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.stdout:
                print(result.stdout.strip())
            if result.stderr:
                print(f"stderr: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print("[-] 命令超时")
        except Exception as e:
            print(f"[-] 执行失败: {e}")
    
    print("\n[*] Docker逃逸检测:")
    escape_checks = [
        ("Docker Socket权限", "/var/run/docker.sock"),
        ("Docker组权限", "/etc/group"),
        ("SUID容器工具", "/usr/bin/docker"),
        ("Mount命名空间", "/proc/self/mounts")
    ]
    
    for check_name, path in escape_checks:
        print(f"\n[+] 检查: {check_name}")
        if os.path.exists(path):
            try:
                stat_info = os.stat(path)
                print(f"    [*] 路径存在: {path}")
                print(f"    [*] 权限: {oct(stat_info.st_mode)[-4:]}")
                if path == "/var/run/docker.sock":
                    print("    [!] Docker Socket可被利用进行容器逃逸")
            except Exception as e:
                print(f"    [-] 获取信息失败: {e}")
        else:
            print(f"    [-] 路径不存在: {path}")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        docker_enum(sys.argv[1])
    else:
        docker_enum()