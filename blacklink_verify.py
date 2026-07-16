import requests
import re
import os

requests.packages.urllib3.disable_warnings()

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

proxies = {"http": None, "https": None}

target_js = "http://zsj.changchun.gov.cn/images/jquery.SuperSlide.2.1.1-2025.js"
blacklink_domain = "http://www.SuperSlide2.com/"

pc_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"

print("=" * 60)
print("[1] 检查目标JS文件是否包含黑链引用")
print("=" * 60)

try:
    resp = requests.get(target_js, headers={"User-Agent": pc_ua}, timeout=10, proxies=proxies, verify=False)
    print(f"状态码: {resp.status_code}")
    print(f"内容长度: {len(resp.text)} 字符")
    
    if "SuperSlide2.com" in resp.text or "superslide2.com" in resp.text.lower():
        print("\n[!] 发现 SuperSlide2.com 引用！")
        matches = re.findall(r'.{0,50}SuperSlide2\.com.{0,50}', resp.text, re.IGNORECASE)
        for m in matches:
            print(f"  - {m.strip()}")
    else:
        print("\n[✓] 未在JS文件中找到 SuperSlide2.com 引用")
        
    if "http://" in resp.text or "https://" in resp.text:
        urls = re.findall(r'https?://[^\s"\'<>]+', resp.text)
        print(f"\nJS文件中包含的外部链接:")
        for u in set(urls):
            print(f"  - {u}")
            
except Exception as e:
    print(f"访问失败: {e}")

print()
print("=" * 60)
print("[2] PC端UA访问 SuperSlide2.com")
print("=" * 60)

try:
    resp_pc = requests.get(blacklink_domain, headers={"User-Agent": pc_ua}, timeout=10, proxies=proxies, verify=False, allow_redirects=True)
    print(f"状态码: {resp_pc.status_code}")
    print(f"最终URL: {resp_pc.url}")
    print(f"内容长度: {len(resp_pc.text)} 字符")
    
    title = re.search(r'<title>(.*?)</title>', resp_pc.text, re.IGNORECASE | re.DOTALL)
    if title:
        print(f"页面标题: {title.group(1).strip()}")
    
    keywords = ["影视", "电影", "电视剧", "综艺", "动漫", "最新", "热播", "免费"]
    found_kw = [kw for kw in keywords if kw in resp_pc.text]
    if found_kw:
        print(f"[!] 发现影视相关关键词: {found_kw}")
    else:
        print(f"[✓] 未发现影视相关关键词")
        
except Exception as e:
    print(f"访问失败: {e}")

print()
print("=" * 60)
print("[3] 手机端UA访问 SuperSlide2.com")
print("=" * 60)

try:
    resp_mobile = requests.get(blacklink_domain, headers={"User-Agent": mobile_ua}, timeout=10, proxies=proxies, verify=False, allow_redirects=True)
    print(f"状态码: {resp_mobile.status_code}")
    print(f"最终URL: {resp_mobile.url}")
    print(f"内容长度: {len(resp_mobile.text)} 字符")
    
    title = re.search(r'<title>(.*?)</title>', resp_mobile.text, re.IGNORECASE | re.DOTALL)
    if title:
        print(f"页面标题: {title.group(1).strip()}")
    
    keywords = ["影视", "电影", "电视剧", "综艺", "动漫", "最新", "热播", "免费"]
    found_kw = [kw for kw in keywords if kw in resp_mobile.text]
    if found_kw:
        print(f"[!] 发现影视相关关键词: {found_kw}")
    else:
        print(f"[✓] 未发现影视相关关键词")
        
except Exception as e:
    print(f"访问失败: {e}")

print()
print("=" * 60)
print("[4] 对比PC和手机端差异")
print("=" * 60)

try:
    pc_len = len(resp_pc.text)
    mobile_len = len(resp_mobile.text)
    diff = abs(pc_len - mobile_len)
    diff_pct = (diff / max(pc_len, mobile_len)) * 100 if max(pc_len, mobile_len) > 0 else 0
    
    print(f"PC端内容长度: {pc_len}")
    print(f"手机端内容长度: {mobile_len}")
    print(f"差异: {diff} 字符 ({diff_pct:.1f}%)")
    
    if diff_pct > 30:
        print("[!] 内容差异巨大 (>30%)，存在UA针对性黑链特征")
    elif diff_pct > 10:
        print("[!] 内容存在一定差异 (>10%)")
    else:
        print("[✓] 内容差异较小")
        
    pc_title = re.search(r'<title>(.*?)</title>', resp_pc.text, re.IGNORECASE | re.DOTALL)
    mobile_title = re.search(r'<title>(.*?)</title>', resp_mobile.text, re.IGNORECASE | re.DOTALL)
    
    if pc_title and mobile_title:
        if pc_title.group(1).strip() != mobile_title.group(1).strip():
            print("[!] PC端和手机端页面标题不同，存在UA针对性内容")
            print(f"  PC端标题: {pc_title.group(1).strip()}")
            print(f"  手机端标题: {mobile_title.group(1).strip()}")
            
except NameError:
    print("无法对比（部分请求失败）")

print()
print("=" * 60)
print("[5] 验证结论")
print("=" * 60)

try:
    has_blacklink_in_js = "SuperSlide2.com" in resp.text or "superslide2.com" in resp.text.lower()
    has_movie_mobile = any(kw in resp_mobile.text for kw in ["影视", "电影", "电视剧", "免费"])
    has_ua_diff = diff_pct > 30 if 'diff_pct' in dir() else False
    
    score = 0
    if has_blacklink_in_js:
        score += 30
        print("✓ JS文件中包含 SuperSlide2.com 引用 (+30分)")
    if has_movie_mobile:
        score += 40
        print("✓ 手机端访问返回影视类内容 (+40分)")
    if has_ua_diff:
        score += 20
        print("✓ PC端与手机端内容差异巨大 (+20分)")
    
    if score >= 50:
        print(f"\n[结论] 黑链告警成立 (置信度: {score}%)")
    else:
        print(f"\n[结论] 证据不足，需进一步验证 (置信度: {score}%)")
        
except Exception as e:
    print(f"结论生成失败: {e}")
