import requests
import urllib3
import gzip

urllib3.disable_warnings()

target = "http://www.pingdu.qdjcy.gov.cn/"

print("测试1: 使用原始请求头 (Firefox 5.0 on Linux")
headers1 = {
    "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:1.9.6.20) Gecko/ Firefox/5.0",
    "Accept": "*/*",
    "Accept-Language": "en",
    "Accept-Encoding": "gzip",
    "Connection": "close",
}
try:
    r = requests.get(target, headers=headers1, timeout=15, verify=False)
    print(f"  状态码: {r.status_code}")
    print(f"  响应头: {dict(r.headers)}")
    print(f"  响应内容前1000字符:")
    print(r.text[:1000])
except Exception as e:
    print(f"  错误: {e}")

print("\n" + "="*60)
print("测试2: 使用Chrome UA")
headers2 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close",
}
try:
    r = requests.get(target, headers=headers2, timeout=15, verify=False)
    print(f"  状态码: {r.status_code}")
    print(f"  响应头: {dict(r.headers)}")
    print(f"  响应内容前1000字符:")
    print(r.text[:1000])
except Exception as e:
    print(f"  错误: {e}")

print("\n" + "="*60)
print("测试3: 使用curl命令")
import subprocess
try:
    result = subprocess.run(
        ["curl", "-v", "-A", "Mozilla/5.0 (X11; Linux i686; rv:1.9.6.20) Gecko/ Firefox/5.0",
         "--compressed", target],
        capture_output=True, text=True, timeout=15
    )
    print("  STDOUT前500字符:")
    print(result.stdout[:500])
    print("  STDERR前500字符:")
    print(result.stderr[:500])
except Exception as e:
    print(f"  错误: {e}")
