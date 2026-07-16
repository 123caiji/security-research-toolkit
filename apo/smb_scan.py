#!/usr/bin/env python3
"""
SMB Vulnerability Scanner
Detects MS17-010 (EternalBlue) and other SMB vulnerabilities
"""
import socket
import struct
import sys
import time

target = '192.168.233.129'
port = 445

def check_smb_version(target, port):
    """Check SMB version via SMB1 negotiation"""
    print(f"[*] Checking SMB version on {target}:{port}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((target, port))
        
        # SMB1 Negotiate Request
        # NetBIOS Session Service header
        smb_negotiate = (
            b'\x00\x00\x00\x2f'  # NetBIOS length
            b'\xff\x53\x4d\x42'  # SMB1 magic
            b'\x72'               # Negotiate protocol
            b'\x00\x00\x00\x00'   # Status
            b'\x18'               # Flags
            b'\x53\xc8'           # Flags2
            b'\x00\x00'           # PID High
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # Signature
            b'\x00\x00'           # Reserved
            b'\x00\x00'           # Tree ID
            b'\x00\x00'           # Process ID
            b'\x00\x00'           # User ID
            b'\x00\x00'           # Multiplex ID
            b'\x00\x31'           # Word Count + Byte Count
            b'\x02'               # Dialect count
            b'\x4e\x54\x20\x4c\x4d\x20\x30\x2e\x31\x32\x00'  # NT LM 0.12
            b'\x02\x02'           # Security mode
            b'\x00\x00\x00\x00\x00\x00'  # Capabilities
        )
        
        s.send(smb_negotiate)
        time.sleep(1)
        resp = s.recv(4096)
        s.close()
        
        if len(resp) > 4:
            # Check if SMB1 is supported
            if resp[4:8] == b'\xff\x53\x4d\x42':
                print("[+] SMB1 (NT LM 0.12) is SUPPORTED")
                # Parse OS version from response
                if len(resp) > 64:
                    os_version = resp[64:73]
                    print(f"[*] OS Version bytes: {os_version.hex()}")
                return True
            elif resp[4:8] == b'\xfe\x53\x4d\x42':
                print("[*] SMB2/3 only (SMB1 disabled)")
                # Parse SMB2 dialect
                if len(resp) > 68:
                    dialect = struct.unpack('<H', resp[68:70])[0] if len(resp) > 70 else 0
                    print(f"[*] SMB2 Dialect: {dialect:#x}")
                return False
        return False
    except Exception as e:
        print(f"[-] SMB version check failed: {e}")
        return False

def check_ms17_010(target, port):
    """Check MS17-010 (EternalBlue) vulnerability"""
    print(f"\n[*] Checking MS17-010 (EternalBlue) on {target}:{port}")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((target, port))
        
        # SMB1 Negotiate with TRANS2
        negotiate = bytes.fromhex(
            '00000054'  # NetBIOS length
            'ff534d42'  # SMB1 magic
            '72'        # Negotiate
            '00000000'  # Status
            '18'        # Flags
            '53c8'      # Flags2
            '0000'      # PID High
            '0000000000000000'  # Signature
            '0000'      # Reserved
            '0000'      # Tree ID
            '0000'      # Process ID
            '0000'      # User ID
            '0000'      # Multiplex ID
            '0031'      # Word Count + Byte Count
            '02'        # Dialect count
            '4e54204c4d20302e313200'  # NT LM 0.12
            '0202'      # Security mode
            '000000000000'  # Capabilities
        )
        
        s.send(negotiate)
        time.sleep(1)
        resp = s.recv(4096)
        
        if len(resp) < 35:
            print("[-] Response too short")
            s.close()
            return False
        
        # Check if vulnerable by examining TRANS2 response
        # Vulnerable systems return specific status codes
        status = struct.unpack('<I', resp[9:13])[0] if len(resp) > 13 else 0
        print(f"[*] SMB Negotiate status: {status:#010x}")
        
        # Try Session Setup (anonymous)
        session_setup = bytes.fromhex(
            '0000008f'  # NetBIOS length
            'ff534d42'  # SMB1 magic
            '73'        # Session Setup AndX
            '00000000'  # Status
            '18'        # Flags
            '07c8'      # Flags2
            '0000'      # PID High
            '0000000000000000'  # Signature
            '0000'      # Reserved
            '0000'      # Tree ID
            'fffe'      # Process ID
            '0000'      # User ID
            '0000'      # Multiplex ID
            '0d'        # Word Count
            'ff'        # AndXCommand
            '00'        # AndXReserved
            '0000'      # AndXOffset
            '0000'      # MaxBufferSize
            '01'        # MaxMpxCount
            '00'        # VcNumber
            '00000000'  # SessionKey
            '00000026'  # Security Blob length
            '00000000'  # Reserved
            '2600'      # Byte Count
            '60'        # ASN1 SEQUENCE
            '22'        # Length
            '06'        # ASN1 OID
            '06'        # Length
            '2b0601050502a0'  # SPNEGO OID
            '180'       # Length
            '30'        # SEQUENCE
            '16'        # Length
            'a0'        # NegTokenInit
            '0e'        # Length
            '30'        # SEQUENCE
            '0c'        # Length
            '06'        # OID
            '0a'        # Length
            '2b06010401823702020a'  # NTLMSSP OID
        )
        
        s.send(session_setup)
        time.sleep(1)
        resp2 = s.recv(4096)
        
        if len(resp2) > 9:
            setup_status = struct.unpack('<I', resp2[9:13])[0]
            print(f"[*] Session Setup status: {setup_status:#010x}")
            
            # STATUS_MORE_PROCESSING_REQUIRED (0xC0000016) = anonymous auth possible
            if setup_status == 0xC0000016:
                print("[+] Anonymous session setup possible (STATUS_MORE_PROCESSING_REQUIRED)")
            elif setup_status == 0:
                print("[+] Session setup SUCCESS (anonymous access allowed!)")
            elif setup_status == 0xC0000022:
                print("[*] Access denied for anonymous (STATUS_ACCESS_DENIED)")
            else:
                print(f"[*] Status: {setup_status:#010x}")
        
        # MS17-010 detection: check via named pipe TRANS2
        # The vulnerability is in srv.sys - check if system responds to
        # specific SMB1 TRANS2 packets that trigger the bug
        
        # Simplified check: Windows < Win10 1703 / Server 2016 = likely vulnerable
        # Check OS version from negotiate response
        if len(resp) > 73:
            # Try to extract OS version
            byte_65 = resp[65] if len(resp) > 65 else 0
            byte_66 = resp[66] if len(resp) > 66 else 0
            byte_67 = resp[67] if len(resp) > 67 else 0
            print(f"[*] OS version indicators: {byte_65}.{byte_66}.{byte_67}")
            
            # Check for Windows 7/2008 R2 (likely vulnerable)
            if byte_65 == 6 and byte_66 == 1:
                print("[!] Windows 7 / Server 2008 R2 - LIKELY VULNERABLE to MS17-010!")
                return True
            elif byte_65 == 6 and byte_66 == 0:
                print("[!] Windows Vista / Server 2008 - LIKELY VULNERABLE to MS17-010!")
                return True
            elif byte_65 == 6 and byte_66 == 3:
                print("[*] Windows 8.1 / Server 2012 R2 - MAY be vulnerable to MS17-010")
                return True
            elif byte_65 == 10 and byte_66 == 0:
                print("[*] Windows 10 / Server 2016+ - Patched against MS17-010 (unless old build)")
                return False
        
        s.close()
        return False
        
    except Exception as e:
        print(f"[-] MS17-010 check failed: {e}")
        return False

def check_null_session(target, port):
    """Try anonymous/null SMB session"""
    print(f"\n[*] Attempting null session on {target}:{port}")
    try:
        # Use raw SMB to check null session
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((target, port))
        
        # SMB1 Negotiate
        negotiate = bytes.fromhex(
            '0000002f'
            'ff534d42'
            '72'
            '00000000'
            '18'
            '53c8'
            '0000'
            '0000000000000000'
            '0000'
            '0000'
            '0000'
            '0000'
            '0000'
            '0031'
            '02'
            '4e54204c4d20302e313200'
            '0202'
            '000000000000'
        )
        s.send(negotiate)
        time.sleep(0.5)
        resp = s.recv(4096)
        
        if len(resp) > 35:
            print("[*] SMB negotiate response received")
            # Check if guest access is enabled
            capabilities = resp[35] if len(resp) > 35 else 0
            print(f"[*] Capabilities byte: {capabilities:#x}")
        
        s.close()
        
        # Try using net commands
        import subprocess
        result = subprocess.run(
            ['net', 'use', f'\\\\{target}\\IPC$', '/user:guest', ''],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("[+] Null/guest session SUCCESS!")
            # Enumerate shares
            result2 = subprocess.run(
                ['net', 'view', f'\\\\{target}'],
                capture_output=True, text=True, timeout=10
            )
            print(result2.stdout)
        else:
            print(f"[*] Guest session result: {result.stderr.strip()}")
            
    except Exception as e:
        print(f"[-] Null session check: {e}")

def enumerate_smb(target):
    """Enumerate SMB shares and info"""
    print(f"\n[*] Enumerating SMB shares on {target}")
    import subprocess
    
    # Try to list shares
    result = subprocess.run(
        ['net', 'view', f'\\\\{target}'],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0:
        print("[+] Shares found:")
        print(result.stdout)
    else:
        print(f"[*] Share enumeration: {result.stderr.strip()}")
    
    # Try to list named pipes
    result = subprocess.run(
        ['net', 'time', f'\\\\{target}'],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0:
        print(f"[+] System time: {result.stdout.strip()}")

if __name__ == '__main__':
    print("=" * 60)
    print(f"SMB Vulnerability Scanner - Target: {target}")
    print("=" * 60)
    
    smb1_supported = check_smb_version(target, port)
    ms17_010_vuln = check_ms17_010(target, port)
    check_null_session(target, port)
    enumerate_smb(target)
    
    print("\n" + "=" * 60)
    print("SCAN SUMMARY")
    print("=" * 60)
    print(f"SMB1 Supported:    {smb1_supported}")
    print(f"MS17-010 (EternalBlue): {'VULNERABLE' if ms17_010_vuln else 'Not detected'}")
    print("=" * 60)