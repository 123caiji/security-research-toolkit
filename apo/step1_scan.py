#!/usr/bin/env python3
"""Step 1: Nmap quick scan via vmrun"""
import subprocess
import os

VMRUN = r'D:\software\vmware\tool\vmrun.exe'
VMX = r'E:\BaiduNetdiskDownload\kali-linux-2026.1-vmware-amd64.vmwarevm\kali-linux-2026.1-vmware-amd64.vmx'
TEMP = os.environ.get('TEMP', r'C:\Users\xianyv\AppData\Local\Temp')

def run_kali(cmd, timeout=120):
    """Run command in Kali and get output"""
    # Write script
    script_path = os.path.join(TEMP, 'kali_cmd.sh')
    with open(script_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'#!/bin/bash\n{cmd}\n')
    
    # Copy to guest
    r = subprocess.run([VMRUN, '-T', 'ws', '-gu', 'kali', '-gp', 'kali',
                        'copyFileFromHostToGuest', VMX,
                        script_path, '/tmp/kali_cmd.sh'],
                       capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return f"[COPY ERROR] {r.stderr}"
    
    # Run synchronously
    r = subprocess.run([VMRUN, '-T', 'ws', '-gu', 'kali', '-gp', 'kali',
                        'runProgramInGuest', VMX,
                        '/bin/bash', '-c',
                        f'chmod +x /tmp/kali_cmd.sh && timeout {timeout} /tmp/kali_cmd.sh > /tmp/kali_out.txt 2>&1'],
                       capture_output=True, text=True, timeout=timeout + 30)
    
    # Get output
    out_path = os.path.join(TEMP, 'kali_out.txt')
    subprocess.run([VMRUN, '-T', 'ws', '-gu', 'kali', '-gp', 'kali',
                    'copyFileFromGuestToHost', VMX,
                    '/tmp/kali_out.txt', out_path],
                   capture_output=True, text=True, timeout=30)
    
    try:
        with open(out_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return "[READ ERROR]"

print("=" * 60)
print("STEP 1: Nmap quick scan")
print("=" * 60)
out = run_kali(f"sudo nmap -sS -sV --top-ports 1000 -T4 192.168.233.129", timeout=90)
print(out)

print("\n" + "=" * 60)
print("STEP 2: SMB vulnerability scan")
print("=" * 60)
out = run_kali(f"sudo nmap -p 445 --script=smb-vuln* --script-args unsafe=1 192.168.233.129", timeout=120)
print(out)

print("\n" + "=" * 60)
print("STEP 3: Enum4linux")
print("=" * 60)
out = run_kali(f"enum4linux -a 192.168.233.129 2>&1 | head -300", timeout=90)
print(out)
