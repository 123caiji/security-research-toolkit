#!/usr/bin/env python3
"""
Probe ports 5040 and 7680 for service identification
Also test RPC endpoints on 49664-49674
"""
import socket
import time

target = '192.168.233.129'

def probe_port(port):
    """Send probe data and read banner"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((target, port))
        
        # Try reading banner first (some services send data first)
        try:
            s.settimeout(1)
            banner = s.recv(1024)
            if banner:
                print(f"  [{port}] Banner received: {banner[:100]}")
                s.close()
                return
        except:
            pass
        
        # Send HTTP GET
        s.settimeout(2)
        s.send(b'GET / HTTP/1.1\r\nHost: ' + target.encode() + b'\r\n\r\n')
        try:
            resp = s.recv(4096)
            if resp:
                print(f"  [{port}] HTTP response: {resp[:200]}")
        except:
            pass
        
        # Try SMB negotiate
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((target, port))
        s.settimeout(2)
        smb_neg = b'\x00\x00\x00\x2f\xff\x53\x4d\x42\x72\x00\x00\x00\x00\x18\x53\xc8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x31\x02\x4e\x54\x20\x4c\x4d\x20\x30\x2e\x31\x32\x00\x02\x02\x00\x00\x00\x00\x00\x00'
        s.send(smb_neg)
        try:
            resp = s.recv(4096)
            if resp:
                print(f"  [{port}] SMB response: {resp[:60].hex()}")
        except:
            pass
        
        s.close()
    except Exception as e:
        print(f"  [{port}] Error: {e}")

def test_rpc_endpoint(port):
    """Test if port is an RPC endpoint"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((target, port))
        
        # RPC Bind Request to EPM
        rpc_bind = bytes.fromhex(
            '05000b03100000004800000001000000'
            'b81d7c4fa88a4beac6c2e5c8d4dcd4d4'  # EPM UUID
            '03000000045d888a'
        )
        s.settimeout(2)
        s.send(rpc_bind)
        try:
            resp = s.recv(4096)
            if resp and len(resp) > 16:
                # Check for RPC Bind Ack
                if resp[:2] == b'\x05\x00':
                    print(f"  [{port}] RPC response ({len(resp)} bytes): {resp[:40].hex()}")
                    if resp[2:3] == b'\x0c':
                        print(f"  [{port}] RPC Bind ACK received!")
        except:
            pass
        s.close()
    except Exception as e:
        pass

if __name__ == '__main__':
    print(f"[*] Probing special ports on {target}")
    print()
    
    # Probe port 5040
    print("[*] Port 5040:")
    probe_port(5040)
    
    # Probe port 7680
    print("\n[*] Port 7680:")
    probe_port(7680)
    
    # Test RPC ports
    print("\n[*] Testing RPC endpoints (49664-49674):")
    for p in [49664, 49665, 49666, 49667, 49668, 49669, 49674]:
        test_rpc_endpoint(p)
    
    print("\n[*] Done")