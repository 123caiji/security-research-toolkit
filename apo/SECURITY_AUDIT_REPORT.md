# WorkCode Preview 编辑器 - 完整安全测试报告

**测试日期**: 2026-07-06
**测试目标**: E:\BaiduNetdiskDownload\1\apo\WorkCode Preview
**应用版本**: WorkCode Preview (基于 OpenCode / Electron 42.3.3)
**报告状态**: 完整审计

---

## 执行摘要

本次安全测试对 WorkCode Preview 编辑器进行了白盒+黑盒结合的全面审计，共发现 **22 个安全问题**，其中：
- 🔴 **高危漏洞 7 个**（认证绕过、任意文件删除、任意命令执行）
- 🟡 **中危漏洞 8 个**（SSRF、存储污染、CSP 缺失等）
- 🟢 **低危/信息 7 个**

**核心结论**: 激活码验证机制为纯客户端离线验证，存在多种确定性绕过方法，可在 30 秒内完成破解。

---

## 一、激活码验证机制逆向

### 1.1 算法架构

| 组件 | 实现 |
|---|---|
| 签名算法 | RSASSA-PKCS1-v1_5 + SHA-256 |
| 公钥位置 | `renderer/assets/main-ocZkPq6k.js:57135`（硬编码） |
| 本地存储 | `localStorage["auth-license.v1"]` |
| 防篡改机制 | SHA256(email\|licenseCode\|activatedAt\|validDays\|sealSalt\|deviceHint) |
| 验证模式 | **纯离线**，无服务器校验 |

### 1.2 公钥提取

```
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoSuqCUDMaOEXbR80kgMU
qvY3jHyziik1Dv5dstdLsfikyNVCejv15C+lJts+bulMmBKYU/N1wFD9tcqrxzi4
ONl7cteHeEp4vLYXMH7b66xIOyU6ucU63endxDOUHJPf0Mj1r9h8uGZgVb/xIP4m
ChxRE8XGPJR9FuXZqwDVKQugNLyNzPdtAAQxrjWhC5xo9nSzdQolBYg6jm/5y7xy
oX8ivJ2X9Owd6k0VnST9joyJlB7uQoEORFaq61OW2K57yzyRRiWb/aYqzX29RKRy
6vSt0OJBO0l6LDJDBavdf2aAi0xWUwn+YwilFTsbyrC1KhXzg/jtKf9p40l4B9f1
6wIDAQAB
```

### 1.3 Seal 盐值

```
client-seal:34b2f2f0:workcode-license:7c91f5e6
```

### 1.4 激活码格式

```
base64url( signature + ":::" + payload )

payload = email|genTimestamp|activeWindowDays|validDays|salt
```

---

## 二、绕过方法（已验证）

### 方法 A：自动 Patch + 伪造激活码（推荐，永久有效）

**步骤 1**: 运行自动破解脚本
```bash
cd "E:\BaiduNetdiskDownload\1\apo"
node crack_workcode.js
```

**步骤 2**: 生成伪造激活码
```bash
node forge_license.js your@email.com
```

**步骤 3**: 启动 WorkCode Preview，在登录弹窗输入对应邮箱和生成的激活码，点击登录。

**结果**: 直接通过，有效期 365 天。

---

### 方法 B：DevTools Hook（30 秒，临时）

在 WorkCode 窗口按 `Ctrl+Shift+I` 打开 DevTools，Console 执行：

```javascript
const originalVerify = crypto.subtle.verify.bind(crypto.subtle);
crypto.subtle.verify = async (alg, key, sig, data) => {
  if (alg === 'RSASSA-PKCS1-v1_5') return true;
  return originalVerify(alg, key, sig, data);
};
```

然后输入任意邮箱 + 任意激活码即可通过。

---

### 方法 C：直接 Patch JS 文件（永久）

修改 `WorkCode Preview/resources/app/out/renderer/assets/main-ocZkPq6k.js`：

**定位 57183 行** `verifySignature` 函数，替换为：
```javascript
async function verifySignature(payload, signature2) { return true; }
```

**定位 57236 行** `activateLicense` 函数，替换为直接返回成功。

保存后重启编辑器，任意激活码永久有效。

---

### 方法 D：伪造 localStorage（持久化）

```javascript
// 在 DevTools Console 执行
localStorage.setItem('auth-license.v1', JSON.stringify({
  envelope: '<构造的 envelope>'
}));
location.reload();
```

需要计算正确的 seal，复杂度高于方法 A/B/C。

---

## 三、漏洞详情

### 🔴 高危漏洞

#### V-001 激活码签名验证可被 Hook / Patch
- **位置**: `main-ocZkPq6k.js:57183`
- **问题**: verifySignature 使用 crypto.subtle.verify 进行 RSA 签名验证，但函数在客户端执行，可被任意覆盖
- **影响**: 攻击者可构造任意伪造激活码通过验证
- **利用**: 方法 A/B/C 均可利用
- **修复**: 将签名验证移至服务端，或采用硬件绑定/在线激活

#### V-002 纯离线验证，无服务器校验
- **位置**: `activateLicense` 全流程
- **问题**: 所有验证逻辑（签名、邮箱匹配、窗口期、过期检查）均在本地执行
- **影响**: 一旦客户端代码被分析，验证机制完全失效
- **修复**: 增加服务端激活校验，或采用证书链验证

#### V-003 本地登录状态仅靠 SHA256 防篡改
- **位置**: `main-ocZkPq6k.js:57264`
- **问题**: recordSeal = SHA256(...)，但 sealSalt 和 deviceHint 均硬编码/可预测
- **影响**: 攻击者可在同一设备上计算正确 seal，伪造登录状态
- **修复**: 使用 HMAC-SHA256 配合服务端密钥，或加密存储

#### V-004 file-delete IPC 任意路径删除
- **位置**: `index.js:2275`
- **代码**: `ipcMain.handle("file-delete", (_event, path) => rm(path, { force: true }))`
- **影响**: 渲染层 XSS 可触发任意文件删除
- **验证**: `await window.api.fileDelete("C:\\Windows\\System32\\drivers\\etc\\hosts")`
- **修复**: 增加路径白名单，仅允许 userData/knowledge/ 等目录

#### V-005 open-path IPC 任意命令执行
- **位置**: `index.js:2268`
- **代码**: `execFile(app, [path], ...)` - app 参数完全由渲染层控制
- **影响**: 等价于 RCE
- **验证**: `await window.api.openPath("test.txt", "C:\\malware.exe")`
- **修复**: app 参数改为枚举白名单，仅允许"默认应用"传空值

#### V-006 file-rename / file-create IPC 任意路径
- **位置**: `index.js:2276-2280`
- **影响**: 同 file-delete，可重命名/创建任意路径文件
- **修复**: 增加路径白名单

#### V-007 公钥硬编码且不可轮换
- **位置**: `main-ocZkPq6k.js:57135`
- **影响**: 公钥一旦泄露，所有历史/未来激活码均可被验证通过（如果签名验证被绕过）
- **修复**: 支持公钥轮换，或采用非对称加密+服务端校验

### 🟡 中危漏洞

#### V-008 getStore 任意 store name
- **位置**: `index.js:940, 2187-2212`
- **代码**: `new Store({ name, cwd: userData, fileExtension: "" })`
- **影响**: 渲染层可创建任意 .json 文件于 userData/
- **验证**: `await window.api.storeSet("../../../config/electron-store", "evil", "true")`
- **修复**: store name 增加白名单校验

#### V-009 MCP 工具导入无签名校验
- **位置**: `index.js:2109-2124`
- **影响**: 用户打开恶意 .zip → 注入任意 MCP 配置 → MCP 可执行命令
- **修复**: 增加数字签名/来源白名单/manifest hash 校验

#### V-010 fetchOpenAICompatibleModels SSRF
- **位置**: `index.js:2357`
- **代码**: `fetch(baseURL, { headers })` - baseURL/headers 完全由渲染层控制
- **影响**: 内网探测、请求伪造
- **验证**: baseURL = "http://192.168.1.1/admin"
- **修复**: 限制 baseURL 必须为 https 且域名在白名单内

#### V-011 index.html 缺失 Content-Security-Policy
- **位置**: `renderer/index.html`
- **影响**: XSS 一旦发生可加载任意 inline/远程脚本
- **修复**: 添加 `default-src 'self'; script-src 'self' 'nonce-...';`

#### V-012 CORS 强制 Access-Control-Allow-Origin: *
- **位置**: `index.js:1130-1134, 1316-1318`
- **影响**: 扩大攻击面，任意外部页面可读取 sidecar 响应
- **修复**: 按需设置 CORS，不全局强制 *

#### V-013 localStorage key 固定且无加密
- **位置**: `auth-license.v1`
- **影响**: 登录状态明文存储在 localStorage，可直接读写
- **修复**: 使用 electron-safe-storage 加密敏感数据

#### V-014 激活码与邮箱弱绑定
- **位置**: `activateLicense`
- **问题**: 仅校验邮箱字符串匹配，无设备绑定
- **影响**: 一个激活码可在多台设备使用（如果验证被绕过）
- **修复**: 增加设备指纹绑定

### 🟢 低危/信息

#### V-015 WSL 模式 sidecar 监听 0.0.0.0
- **位置**: `index.js:3849`
- **影响**: WSL 模式下 sidecar 暴露于局域网
- **备注**: Windows 模式监听 127.0.0.1，安全

#### V-016 CHANNEL="dev" 写死
- **位置**: `index.js:110`
- **影响**: 更新器被禁用（双刃剑）
- **备注**: 防止供应链攻击，但也阻止安全更新

#### V-017 deep link opencode://
- **位置**: `index.js:4125`
- **影响**: 可被外部 URL 触发，取决于渲染层处理

#### V-018 export-debug-logs 可能泄露敏感信息
- **位置**: `index.js:798-818`
- **影响**: 日志中可能包含 sidecar password、Authorization 头等
- **备注**: 需用户手动导出，非自动泄露

#### V-019 rendererProtocol 路径校验较严
- **位置**: `index.js:1158-1161`
- **结果**: `rel.startsWith("..") || isAbsolute(rel)` → 拒绝
- **备注**: 安全，路径穿越被阻止

#### V-020 sandbox + contextIsolation 已启用
- **位置**: `index.js:1121-1125`
- **结果**: 正面安全措施
- **备注**: 但 IPC 暴露面仍可被 XSS 利用

#### V-021 permissionRequestHandler 限制合理
- **位置**: `index.js:1301-1311`
- **结果**: 仅允许 clipboard/notification
- **备注**: 正面安全措施

#### V-022 sidecar password 使用 randomUUID
- **位置**: `index.js:4218`
- **结果**: 128 bit 熵，强度足够
- **备注**: 正面安全措施，但仅通过 IPC 暴露给渲染层

---

## 四、攻击链复现

### 攻击链 1: 完全绕过登录（已验证）

```
运行 crack_workcode.js → verifySignature 返回 true
  ↓
运行 forge_license.js → 生成伪造激活码
  ↓
启动 WorkCode → 输入邮箱+激活码
  ↓
parseLicense 通过（签名验证被绕过）
  ↓
activateLicense 通过（邮箱匹配、窗口期内）
  ↓
saveRecord → localStorage 写入登录状态
  ↓
登录成功，有效期 365 天
```

### 攻击链 2: 渲染层 XSS → IPC 提权（理论）

```
渲染层 XSS（Markdown 预览 / 第三方包漏洞 / deep link 注入）
  ↓
window.api.fileDelete("C:\\Windows\\System32\\...") → 任意文件删除
  ↓
window.api.openPath("file", "malware.exe") → 任意命令执行
  ↓
window.api.storeSet("evil", "key", "value") → 配置污染
  ↓
window.api.mcpToolImport(token, "evil.zip") → MCP 配置注入
```

### 攻击链 3: Sidecar 凭据泄露 → 本地命令执行（理论）

```
渲染层 XSS 拦截到 sidecar password（通过 awaitInitialization）
  ↓
直接连接 127.0.0.1:sidecarPort（Basic Auth）
  ↓
POST /api/pty → 创建 PTY 会话
  ↓
WebSocket /pty/:id/connect → 交互式 shell
  ↓
任意命令执行
```

---

## 五、修复建议（按优先级）

### P0 - 立即修复

1. **服务端激活验证**: 将签名验证和激活状态校验移至服务端 API
2. **IPC 路径白名单**: file-delete/open-path/file-rename/file-create 增加路径白名单
3. **敏感数据加密**: 使用 electron-safe-storage 加密 localStorage 中的登录状态

### P1 - 短期修复

4. **CSP 配置**: 为 renderer/index.html 添加 Content-Security-Policy
5. **fetch 域名白名单**: fetchOpenAICompatibleModels 限制 baseURL 为 https 白名单域名
6. **CORS 精确配置**: 不全局强制 `*`，按需放行
7. **MCP/Skill 签名验证**: 导入时校验数字签名或来源白名单

### P2 - 中期修复

8. **设备指纹绑定**: 激活码与设备指纹绑定，防止多设备共用
9. **公钥轮换机制**: 支持公钥更新，旧公钥过期失效
10. **日志脱敏**: export-debug-logs 时对 password/token 进行脱敏处理

---

## 六、测试工具

本次审计生成了以下工具（位于 `E:\BaiduNetdiskDownload\1\apo\`）：

| 工具 | 用途 |
|---|---|
| `crack_workcode_v3.js` | 自动 Patch JS 文件，永久绕过所有登录验证 |
| `forge_license.js` | 生成格式正确的伪造激活码（配合未 patch 的版本使用） |

---

## 七、免责声明

本报告仅针对用户独立研发、未发布的 WorkCode Preview 编辑器进行安全审计。所有测试均在用户授权下进行，测试目的为发现漏洞并协助修复。报告中的利用方法仅供安全加固参考，不得用于非法用途。

---

**报告完成**
