#!/usr/bin/env python3
"""Step 4: CVE-2020-0796 (SMBGhost) + PrintNightmare + CVE-2021-1675 exploitation"""
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

# 1. CVE-2020-0796 SMBGhost check
print("=" * 60)
print("[1] CVE-2020-0796 (SMBGhost) detection")
print("=" * 60)
out = run_kali(
    f"echo kali | sudo -S nmap -p 445 --script smb-protocols 192.168.233.129 2>&1 && "
    f"echo '---' && "
    f"python3 -c \""
    f"import socket,struct;"
    f"s=socket.socket();"
    f"s.settimeout(5);"
    f"s.connect(('192.168.233.129',445));"
    f"pkt=b'\\\\x00\\\\x00\\\\x00\\\\xc4\\\\xfeSMB\\\\x40\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x01\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x24\\\\x00\\\\x05\\\\x00\\\\x01\\\\x00\\\\x00\\\\x00\\\\x7f\\\\x00\\\\x00\\\\x00' + b'\\\\xff\\\\xff\\\\xff\\\\xff\\\\xff\\\\xff\\\\xff\\\\xff' + b'\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00' + b'\\\\x02\\\\x02\\\\x10\\\\x02\\\\x00\\\\x03\\\\x02\\\\x03\\\\x11\\\\x03';"
    f"s.send(pkt);"
    f"r=s.recv(4096);"
    f"print('Response:',r.hex()[:200]);"
    f"print('Dialect:',hex(struct.unpack('<H',r[68:70])[0]) if len(r)>70 else 'N/A');"
    f"s.close()"
    f"\" 2>&1",
    timeout=60
)
print(out)

# 2. Check Windows version precisely
print("\n" + "=" * 60)
print("[2] Precise Windows version via SMB")
print("=" * 60)
out = run_kali(
    f"echo kali | sudo -S nmap -O --osscan-guess 192.168.233.129 2>&1",
    timeout=60
)
print(out)

# 3. Search for CVE-2020-0796 exploit
print("\n" + "=" * 60)
print("[3] Search SMBGhost exploits")
print("=" * 60)
out = run_kali("searchsploit smbghost 2>&1; echo '---'; searchsploit CVE-2020-0796 2>&1", timeout=30)
print(out)

# 4. Download and run SMBGhost checker
print("\n" + "=" * 60)
print("[4] SMBGhost exploit attempt")
print("=" * 60)
out = run_kali(
    "cd /tmp && "
    "git clone https://github.com/danigargu/CVE-2020-0796.git 2>&1 && "
    "cd CVE-2020-0796 && "
    "python3 smbghost_scanner.py -t 192.168.233.129 2>&1 || "
    "echo 'Scanner failed, trying manual check...' && "
    "pip3 install scapy 2>/dev/null && "
    "python3 -c '"
    "from scapy.all import *;"
    "import struct;"
    "target=\"192.168.233.129\";"
    "print(\"Checking SMB3.1.1 compression...\");"
    "pkt=IP(dst=target)/TCP(dport=445)/Raw(load=bytes.fromhex(\"000000c4fe534d424000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000024000500010000007f000000ffffffffffffffff000000000000000002021002000302031103\"));"
    "resp=sr1(pkt,timeout=5);"
    "print(\"Response:\",resp);"
    "' 2>&1",
    timeout=120
)
print(out)

# 5. Check for other Win10 CVEs
print("\n" + "=" * 60)
print("[5] Check for CVE-2021-1675 (PrintNightmare)")
print("=" * 60)
out = run_kali(
    f"echo kali | sudo -S nmap -p 445 --script smb2-capabilities 192.168.233.129 2>&1 && "
    f"echo '---' && "
    f"rpcclient -U '' -N 192.168.233.129 -c 'enumprinters' 2>&1",
    timeout=60
)
print(out)

# 6. Try to find Windows build number
print("\n" + "=" * 60)
print("[6] Get Windows build via SMB")
print("=" * 60)
out = run_kali(
    "python3 -c \""
    "from impacket.smb import SMB;"
    "from impacket.smbconnection import SMBConnection;"
    "try:"
    "  c=SMBConnection('192.168.233.129','192.168.233.129');"
    "  print('OS:',c.getServerOS());"
    "  print('OSMajor:',c.getServerOSMajor());"
    "  print('OSMinor:',c.getServerOSMinor());"
    "  print('OSBuild:',c.getServerOSBuild());"
    "  print('ServerName:',c.getServerName());"
    "  c.logoff();"
    "except Exception as e:"
    "  print('Error:',e)"
    "\" 2>&1",
    timeout=30
)
print(out)

# 7. EternalRomance check
print("\n" + "=" * 60)
print("[7] EternalRomance (CVE-2017-0145) check")
print("=" * 60)
out = run_kali(
    f"echo kali | sudo -S nmap -p 445 --script smb-vuln-ms17-010 192.168.233.129 2>&1",
    timeout=60
)
print(out)

# 8. Try anonymous IPC$ 
print("\n" + "=" * 60)
print("[8] Anonymous IPC$ access")
print("=" * 60)
out = run_kali(
    f"smbclient //192.168.233.129/IPC$ -N -c 'ls' 2>&1 && "
    f"echo '---' && "
    f"net rpc share -I 192.168.233.129 -U '%' 2>&1 && "
    f"echo '---' && "
    f"nmblookup -B 192.168.233.129 -S DESKTOP-A0LQ308 2>&1",
    timeout=30
)
print(out)

print("\n" + "=" * 60)
print("CVE SCAN COMPLETE")
print("=" * 60)
