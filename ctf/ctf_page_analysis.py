import requests
import re
import json

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

session = requests.Session()
session.verify = False
session.headers.update(HEADERS)


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def get_page(url):
    """获取页面内容"""
    try:
        r = session.get(url, timeout=TIMEOUT)
        return r.text
    except:
        return ""


def analyze_page(url, description):
    """分析页面内容"""
    print_section(f"{description} - {url}")
    
    html = get_page(url)
    if not html:
        print("  无法获取页面")
        return
    
    # 提取表单
    forms = re.findall(r'<form[^>]*>(.*?)</form>', html, re.DOTALL)
    if forms:
        print(f"\n  发现 {len(forms)} 个表单")
        for i, form in enumerate(forms):
            print(f"\n  --- 表单 {i+1} ---")
            print(form)
            
            # 提取输入字段
            inputs = re.findall(r'<input[^>]*>', form)
            print("\n  输入字段:")
            for inp in inputs:
                name = re.search(r'name=["\']([^"\']+)["\']', inp)
                type_attr = re.search(r'type=["\']([^"\']+)["\']', inp)
                value = re.search(r'value=["\']([^"\']+)["\']', inp)
                placeholder = re.search(r'placeholder=["\']([^"\']+)["\']', inp)
                
                name_val = name.group(1) if name else "无名称"
                type_val = type_attr.group(1) if type_attr else "text"
                value_val = value.group(1) if value else ""
                placeholder_val = placeholder.group(1) if placeholder else ""
                
                print(f"    <input type='{type_val}' name='{name_val}' value='{value_val}' placeholder='{placeholder_val}'>")
    
    # 提取按钮
    buttons = re.findall(r'<button[^>]*>(.*?)</button>', html)
    if buttons:
        print(f"\n  按钮: {buttons}")
    
    # 提取链接
    links = re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html)
    if links:
        print(f"\n  链接 ({len(links)}):")
        for href, text in links[:20]:
            print(f"    {text}: {href}")
    
    # 提取脚本
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    if scripts:
        print(f"\n  内联脚本 ({len(scripts)}):")
        for script in scripts:
            if len(script) > 10:
                print(f"    {script[:200]}")
    
    # 提取文本内容
    text_content = re.sub(r'<[^>]+>', ' ', html)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    print(f"\n  文本内容预览: {text_content[:200]}")


def main():
    print("*" * 70)
    print("  CTF页面详细分析")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    pages = [
        ("/", "首页"),
        ("/login", "登录页面"),
        ("/include?page=welcome", "文件包含"),
        ("/search?q=SQL", "SQL注入"),
        ("/upload", "文件上传"),
        ("/message", "XSS"),
        ("/ping", "命令执行1"),
        ("/backup", "命令执行2"),
        ("/dashboard", "控制台"),
    ]
    
    for path, desc in pages:
        url = f"{TARGET}{path}"
        analyze_page(url, desc)
    
    print_section("分析完成")


if __name__ == "__main__":
    main()