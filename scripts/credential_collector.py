import os
import re
import subprocess
import sys

def collect_credentials(target_ip=None):
    print("[*] 凭证收集模块")
    
    credential_paths = [
        "/home/*/.ssh/id_rsa",
        "/home/*/.ssh/id_dsa",
        "/home/*/.ssh/authorized_keys",
        "/root/.ssh/id_rsa",
        "/root/.ssh/id_dsa",
        "/root/.ssh/authorized_keys",
        "/etc/passwd",
        "/etc/shadow",
        "/etc/my.cnf",
        "/etc/mysql/my.cnf",
        "/var/lib/mysql/mysql/user.frm",
        "/opt/*/conf/application.yml",
        "/opt/*/conf/application.properties",
        "/usr/local/*/conf/application.yml",
        "~/.bash_history",
        "/root/.bash_history",
        "/home/*/.bash_history",
        "/etc/nginx/nginx.conf",
        "/etc/httpd/conf/httpd.conf",
        "/var/www/html/.env",
        "/var/www/html/config.php"
    ]
    
    if target_ip:
        print(f"[*] 目标主机: {target_ip}")
        print("[*] 请在目标主机上检查以下路径:")
        for path in credential_paths:
            print(f"    {path}")
        return
    
    print("[*] 本地凭证文件扫描:")
    for path_pattern in credential_paths:
        try:
            expanded = os.path.expanduser(path_pattern)
            if '*' in expanded:
                import glob
                files = glob.glob(expanded)
                for f in files[:5]:
                    check_file(f)
            else:
                check_file(expanded)
        except Exception as e:
            pass
    
    print("\n[*] 环境变量扫描:")
    env_vars = os.environ
    sensitive_keys = ['password', 'pass', 'secret', 'token', 'api', 'key', 'credential']
    for key, value in env_vars.items():
        if any(sk in key.lower() for sk in sensitive_keys):
            masked = value[:10] + '***' if len(value) > 10 else '***'
            print(f"    [*] {key}={masked}")
    
    print("\n[*] 历史命令扫描:")
    history_path = os.path.expanduser("~/.bash_history")
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r', errors='ignore') as f:
                history = f.read()
                
            sensitive_patterns = [
                r'(password|pass|secret|token)\s*[=:]\s*(\S+)',
                r'(ssh|mysql|psql)\s+.*?(-p\s*\S+|--password=\S+)',
                r'(curl|wget)\s+.*?(Authorization:\s*\S+)'
            ]
            
            for pattern in sensitive_patterns:
                matches = re.findall(pattern, history, re.IGNORECASE)
                for match in matches[:5]:
                    print(f"    [*] 发现敏感命令: {match}")
        except Exception as e:
            print(f"    [-] 读取历史命令失败: {e}")

def check_file(filepath):
    if os.path.exists(filepath):
        try:
            size = os.path.getsize(filepath)
            if size > 100000:
                print(f"    [*] 大文件: {filepath} ({size} bytes)")
            else:
                with open(filepath, 'r', errors='ignore') as f:
                    content = f.read()
                
                sensitive_patterns = [
                    r'(password|secret|token|api.*key)\s*[=:]\s*["\']?(\S+)["\']?',
                    r'(mysql|postgres|redis)\s*://.*?:(\S+)@'
                ]
                
                found = False
                for pattern in sensitive_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        found = True
                        break
                
                if found:
                    print(f"    [!] 包含敏感信息: {filepath}")
                else:
                    print(f"    [*] 存在: {filepath}")
        except Exception as e:
            print(f"    [-] 无法读取: {filepath} - {e}")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        collect_credentials(sys.argv[1])
    else:
        collect_credentials()