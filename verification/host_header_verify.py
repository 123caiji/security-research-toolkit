"""
HTTP Host头攻击漏洞验证脚本
仅做被动检测，不影响业务运行
使用代理池保护IP
"""
import requests
import random
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 目标
TARGET_URL = "https://jf1.isdapp.shandong.gov.cn/"
TARGET_HOST = "jf1.isdapp.shandong.gov.cn"

# 代理池 - 请替换为实际代理IP
PROXY_POOL = [
    # "http://ip1:port",
    # "http://ip2:port",
    # "http://ip3:port",
]

# 测试用的异常Host头（不含攻击payload，仅检测是否被接受）
TEST_HOSTS = [
    "evil.example.com",           # 完全不同的域名
    "127.0.0.1",                  # IP地址
    "localhost",                  # localhost
    f"{TARGET_HOST}:443",         # 带端口
    f"{TARGET_HOST}.evil.com",    # 后缀注入
    "",                           # 空Host
]

HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def get_proxy():
    if not PROXY_POOL:
        return None
    proxy = random.choice(PROXY_POOL)
    return {"http": proxy, "https": proxy}


def check_host_header(host_value, proxy=None):
    """发送带异常Host头的请求，观察响应"""
    headers = {**HEADERS_BASE, "Host": host_value}
    proxies = proxy
    try:
        resp = requests.get(
            TARGET_URL,
            headers=headers,
            proxies=proxies,
            verify=False,
            timeout=15,
            allow_redirects=False,
        )
        return {
            "status_code": resp.status_code,
            "content_length": len(resp.content),
            "location": resp.headers.get("Location", ""),
            "server": resp.headers.get("Server", ""),
            "has_redirect": resp.is_redirect,
            "response_snippet": resp.text[:500] if resp.text else "",
        }
    except Exception as e:
        return {"error": str(e)}


def main():
    print(f"[*] 目标: {TARGET_URL}")
    print(f"[*] 正常Host: {TARGET_HOST}")
    print(f"[*] 代理池: {'已配置 ' + str(len(PROXY_POOL)) + ' 个' if PROXY_POOL else '未配置(直连)'}")
    print("=" * 60)

    # 1. 基线请求 - 正常Host
    print("\n[1] 基线请求 (正常Host):")
    proxy = get_proxy()
    baseline = check_host_header(TARGET_HOST, proxy)
    print(f"    状态码: {baseline.get('status_code')}")
    print(f"    内容长度: {baseline.get('content_length')}")
    print(f"    Server: {baseline.get('server')}")

    # 2. 异常Host头测试
    print("\n[2] 异常Host头测试:")
    results = []
    for test_host in TEST_HOSTS:
        proxy = get_proxy()
        print(f"\n  [*] Host: '{test_host}'")
        result = check_host_header(test_host, proxy)
        results.append((test_host, result))

        if "error" in result:
            print(f"    错误: {result['error']}")
        else:
            print(f"    状态码: {result.get('status_code')}")
            print(f"    内容长度: {result.get('content_length')}")
            print(f"    Location: {result.get('location', 'N/A')}")

        time.sleep(random.uniform(1, 3))  # 随机延迟，降低频率

    # 3. 分析结果
    print("\n" + "=" * 60)
    print("[3] 分析结论:")
    baseline_len = baseline.get("content_length", 0)
    baseline_code = baseline.get("status_code", 0)

    vulnerable = False
    for test_host, result in results:
        if "error" in result:
            continue
        resp_code = result.get("status_code", 0)
        resp_len = result.get("content_length", 0)

        # 判断条件:
        # a) 异常Host返回200且内容与基线相似 -> 可能未校验Host
        # b) 异常Host导致302重定向到攻击者域名 -> 存在Host头注入
        # c) 异常Host返回与正常不同的页面 -> 可能存在缓存投毒
        if resp_code == 200 and test_host != TARGET_HOST:
            if abs(resp_len - baseline_len) < baseline_len * 0.1:
                print(f"  [!] Host='{test_host}' 返回200且内容相似 -> 服务器未校验Host头")
                vulnerable = True
        if "evil" in result.get("location", "").lower():
            print(f"  [!] Host='{test_host}' 重定向到异常域名 -> 存在Host头注入")
            vulnerable = True

    if not vulnerable:
        print("  [*] 未检测到明显的Host头攻击漏洞")
        print("  [*] 可能原因: WAF拦截 / 服务器已配置server_name白名单 / 代理层已处理")
    else:
        print("\n  [!] 建议: 配置Nginx server_name白名单，启用UseCanonicalName")


if __name__ == "__main__":
    main()
