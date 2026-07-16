#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用SM4加密构造真实请求"""
import requests
import json
import urllib3
from gmssl import sm4
import binascii

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET_URL = "https://dl.brcloud.bankofchina.com/dlydjd"
DEFAULT_TOKEN = "987654321"
K_E_HEX = "714b674e6c796245574d48652b39773d"

def create_session():
    session = requests.Session()
    session.trust_env = False
    session.proxies = {}
    return session

def sm4_encrypt(data_str):
    """SM4加密 - ECB模式 + PKCS7填充"""
    key = binascii.unhexlify(K_E_HEX)
    crypt = sm4.CryptSM4()
    crypt.set_key(key, sm4.SM4_ENCRYPT)

    data = data_str.encode("utf-8")
    # PKCS7填充
    pad_len = 16 - (len(data) % 16)
    data += bytes([pad_len] * pad_len)
    encrypted = crypt.crypt_ecb(data)
    return encrypted.hex().upper()

def sm4_decrypt(encrypted_hex):
    """SM4解密"""
    key = binascii.unhexlify(K_E_HEX)
    crypt = sm4.CryptSM4()
    crypt.set_key(key, sm4.SM4_DECRYPT)
    encrypted = binascii.unhexlify(encrypted_hex)
    decrypted = crypt.crypt_ecb(encrypted)
    # 去除填充
    pad_len = decrypted[-1]
    if pad_len <= 16:
        decrypted = decrypted[:-pad_len]
    return decrypted.decode("utf-8", errors="ignore")

def call_api_with_encrypt(session, tran_code, body_data, encrypt_data=True):
    """调用API，可选SM4加密"""
    url = f"{TARGET_URL}/sgp/transferRequest"
    headers = {
        "Content-Type": "application/json",
        "Authorization": DEFAULT_TOKEN,
        "User-Agent": "Mozilla/5.0"
    }

    body = {
        "Header": {
            "CurrentPageNum": 1,
            "PageTotalNum": 10,
            "NoRetCode": True,
            "BranchId": "800000",
            "LegalRepCode": "10000",
            "TranTeller": "",
            "TranCode": tran_code,
            "TranDate": "20260716",
            "TranTime": "120000000",
            "ServiceName": tran_code.split("-")[-1] if "-" in tran_code else tran_code,
            "ServiceCode": "D20190130",
            "AuthFlag": "0",
            "AuthrTellerNo": "1",
            "Channel": "39",
            "ConsumerId": "1",
            "GlobalSeq": "1",
            "GlobalSeqNo": "1",
            "KeyId": "1",
            "LocalLang": "1",
            "Mac": "1",
            "SourceSysId": "1111",
            "TerminalCode": "1121",
            "TranSeq": "1",
            "TranSeqNo": "1",
            "TranTellerNo": "1",
            "ExtendContent": "1",
            "TotalNum": "0"
        }
    }

    if encrypt_data and body_data:
        # 加密整个body或指定字段
        data_str = json.dumps(body_data, ensure_ascii=False, separators=(",", ":"))
        encrypted = sm4_encrypt(data_str)
        body["Body"] = {"encData": encrypted}
    else:
        body["Body"] = body_data or {}

    try:
        resp = session.post(url, headers=headers, json=body, verify=False, timeout=30)
        return resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def test_agreement_template():
    """测试协议模板接口（已知需要加密）"""
    session = create_session()

    print("="*70)
    print("测试1: 不加密调用 AGRE-AGRE/queryAgreementTemplateList")
    print("="*70)
    result = call_api_with_encrypt(session, "AGRE-AGRE/queryAgreementTemplateList", {}, encrypt_data=False)
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)[:1000]}")

    print("\n" + "="*70)
    print("测试2: SM4加密调用 AGRE-AGRE/queryAgreementTemplateList")
    print("="*70)
    # 简单的body
    test_body = {"agreementType": "test"}
    result = call_api_with_encrypt(session, "AGRE-AGRE/queryAgreementTemplateList", test_body, encrypt_data=True)
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)[:2000]}")

    print("\n" + "="*70)
    print("测试3: SM4加密调用 CUST-INFO/selectPersonCust")
    print("="*70)
    test_body = {"custNo": "TEST001"}
    result = call_api_with_encrypt(session, "CUST-INFO/selectPersonCust", test_body, encrypt_data=True)
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)[:2000]}")

    print("\n" + "="*70)
    print("测试4: SM4加密调用 CUST-INFO/addIdentificationCardInfo")
    print("="*70)
    test_body = {
        "custNo": "TEST001",
        "idCardNo": "110101199001011234",
        "custName": "张三"
    }
    result = call_api_with_encrypt(session, "CUST-INFO/addIdentificationCardInfo", test_body, encrypt_data=True)
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)[:2000]}")

    # 尝试协议类型列表 - 不加密但加入参数
    print("\n" + "="*70)
    print("测试5: AGRE-AGRE/queryAgreementTypeList 携带参数")
    print("="*70)
    result = call_api_with_encrypt(session, "AGRE-AGRE/queryAgreementTypeList",
                                   {"agreementType": "all"}, encrypt_data=False)
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)[:2000]}")

    # 不同的字段加密方式
    print("\n" + "="*70)
    print("测试6: 使用Data字段加密（尝试不同方式）")
    print("="*70)
    url = f"{TARGET_URL}/sgp/transferRequest"
    headers = {
        "Content-Type": "application/json",
        "Authorization": DEFAULT_TOKEN
    }

    # 方式1: Data.encData
    test_body = {"Data": {"encData": sm4_encrypt("{}")}}
    body = {
        "Header": {
            "TranCode": "CUST-INFO/selectPersonCust",
            "BranchId": "800000",
            "Channel": "39",
            "TranDate": "20260716",
            "TranTime": "120000000",
            "ServiceName": "selectPersonCust"
        },
        "Data": {"encData": sm4_encrypt('{"custNo":"TEST001"}')}
    }
    try:
        resp = session.post(url, headers=headers, json=body, verify=False, timeout=30)
        print(f"状态: {resp.status_code}")
        result = resp.json()
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)[:1500]}")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_agreement_template()