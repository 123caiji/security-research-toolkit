#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robots.txt / sitemap.xml 信息泄露深度分析
"""

import requests
import re
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
})

# ============================================================
# 1. robots.txt 分析
# ============================================================
print("=" * 80)
print("  [1] robots.txt 分析")
print("=" * 80)

try:
    r = session.get("https://www.hbwfjt.com/robots.txt", timeout=15)
    print(f"  状态码: {r.status_code}")
    print(f"  Content-Type: {r.headers.get('Content-Type', 'N/A')}")
    print(f"  Content-Length: {len(r.content)} bytes")
    
    if r.status_code == 200:
        print(f"\n  完整内容:")
        print(f"  {'-'*70}")
        for line in r.text.split("\n"):
            if line.strip():
                print(f"  {line.strip()}")
        print(f"  {'-'*70}")
        
        # 解析 Disallow 路径
        disallow_paths = re.findall(r'Disallow:\s*(.*)', r.text, re.IGNORECASE)
        if disallow_paths:
            print(f"\n  Disallow 路径 ({len(disallow_paths)}个):")
            for p in disallow_paths:
                p = p.strip()
                if p:
                    print(f"    {p}")
        
        # 解析 Sitemap
        sitemaps = re.findall(r'Sitemap:\s*(.*)', r.text, re.IGNORECASE)
        if sitemaps:
            print(f"\n  Sitemap 地址:")
            for s in sitemaps:
                print(f"    {s.strip()}")
        
        # 解析 Allow 路径
        allow_paths = re.findall(r'Allow:\s*(.*)', r.text, re.IGNORECASE)
        if allow_paths:
            print(f"\n  Allow 路径:")
            for p in allow_paths:
                p = p.strip()
                if p:
                    print(f"    {p}")
        
        # 解析 User-agent
        user_agents = re.findall(r'User-agent:\s*(.*)', r.text, re.IGNORECASE)
        if user_agents:
            print(f"\n  User-agent: {', '.join([u.strip() for u in user_agents])}")
except Exception as e:
    print(f"  获取失败: {e}")

# ============================================================
# 2. sitemap.xml 分析
# ============================================================
print(f"\n{'='*80}")
print("  [2] sitemap.xml 分析")
print("=" * 80)

try:
    r = session.get("https://www.hbwfjt.com/sitemap.xml", timeout=15)
    print(f"  状态码: {r.status_code}")
    print(f"  Content-Type: {r.headers.get('Content-Type', 'N/A')}")
    print(f"  Content-Length: {len(r.content)} bytes")
    
    if r.status_code == 200:
        # 解析所有URL
        urls = re.findall(r'<loc>(.*?)</loc>', r.text)
        print(f"\n  总URL数: {len(urls)}")
        
        # 按路径分类
        categories = {}
        for url in urls:
            path = url.replace("https://www.hbwfjt.com", "").split("?")[0]
            parts = path.strip("/").split("/")
            cat = parts[0] if parts else "root"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(path)
        
        print(f"\n  路径分类:")
        for cat, paths in sorted(categories.items(), key=lambda x: -len(x[1])):
            print(f"    /{cat}/ -> {len(paths)} 个")
        
        # 输出所有URL
        print(f"\n  所有URL:")
        print(f"  {'-'*70}")
        for i, url in enumerate(urls, 1):
            path = url.replace("https://www.hbwfjt.com", "")
            print(f"  {i:3d}. {path}")
            if i >= 100:
                print(f"  ... 还有 {len(urls)-100} 个")
                break
        print(f"  {'-'*70}")
        
        # 敏感路径检测
        sensitive_patterns = [
            "admin", "login", "manage", "system", "config", "api", 
            "upload", "backup", "test", "debug", "console", "swagger",
            "register", "user", "member", "account", "setting",
            "upload", "download", "file", "doc", "report",
            "order", "pay", "cart", "product", "goods",
        ]
        
        print(f"\n  敏感路径检测:")
        found_sensitive = []
        for url in urls:
            for pattern in sensitive_patterns:
                if pattern in url.lower():
                    found_sensitive.append(url)
                    break
        
        if found_sensitive:
            print(f"  发现 {len(found_sensitive)} 个敏感路径:")
            for url in found_sensitive[:20]:
                print(f"    ⚠️ {url.replace('https://www.hbwfjt.com', '')}")
        else:
            print(f"  未发现明显敏感路径")
        
        # 文件类型统计
        exts = {}
        for url in urls:
            path = url.split("?")[0]
            if "." in path.split("/")[-1]:
                ext = path.split("/")[-1].split(".")[-1].lower()
                exts[ext] = exts.get(ext, 0) + 1
        
        if exts:
            print(f"\n  文件类型统计:")
            for ext, count in sorted(exts.items(), key=lambda x: -x[1]):
                print(f"    .{ext}: {count}个")
except Exception as e:
    print(f"  获取失败: {e}")

# ============================================================
# 3. 其他常见信息泄露文件
# ============================================================
print(f"\n{'='*80}")
print("  [3] 其他常见信息泄露文件")
print("=" * 80)

info_files = [
    ("/.well-known/security.txt", "安全联系信息"),
    ("/humans.txt", "网站开发者信息"),
    ("/.git/HEAD", "Git源码泄露"),
    ("/.svn/entries", "SVN源码泄露"),
    ("/.DS_Store", "Mac目录信息"),
    ("/crossdomain.xml", "跨域策略"),
    ("/WEB-INF/web.xml", "Java配置"),
    ("/.env", "环境配置"),
    ("/config.json", "配置文件"),
    ("/package.json", "Node.js配置"),
    ("/composer.json", "PHP配置"),
    ("/Gemfile", "Ruby配置"),
    ("/wp-config.php.bak", "WordPress备份"),
    ("/config.php.bak", "PHP配置备份"),
    ("/database.yml", "数据库配置"),
    ("/application.properties", "Spring配置"),
    ("/application.yml", "Spring配置"),
    ("/backup.sql", "数据库备份"),
    ("/dump.sql", "数据库导出"),
    ("/db.sql", "数据库文件"),
    ("/site.zip", "网站备份"),
    ("/www.zip", "网站备份"),
    ("/backup.zip", "备份文件"),
    ("/wwwroot.zip", "网站备份"),
]

for path, desc in info_files:
    try:
        time.sleep(0.3)
        r = session.get(f"https://www.hbwfjt.com{path}", timeout=5, allow_redirects=False)
        if r.status_code == 200 and len(r.content) > 10:
            content_type = r.headers.get("Content-Type", "")
            # 排除HTML错误页面
            is_html_error = ("text/html" in content_type and 
                           len(r.content) < 500 and 
                           ("404" in r.text or "not found" in r.text.lower() or "error" in r.text.lower()))
            if not is_html_error:
                print(f"  ✅ {path} -> {r.status_code} | {len(r.content)} bytes | {desc}")
                print(f"     Content-Type: {content_type[:40]}")
                # 预览内容
                preview = r.text[:200].replace("\n", " ").strip()
                if preview:
                    print(f"     预览: {preview[:100]}...")
        elif r.status_code == 403:
            print(f"  🔒 {path} -> 403 (路径存在但拒绝) | {desc}")
    except:
        pass

# ============================================================
# 4. 从sitemap中挑选路径进行深入探测
# ============================================================
print(f"\n{'='*80}")
print("  [4] sitemap路径深入探测")
print("=" * 80)

try:
    r = session.get("https://www.hbwfjt.com/sitemap.xml", timeout=15)
    if r.status_code == 200:
        urls = re.findall(r'<loc>(.*?)</loc>', r.text)
        
        # 选一些有代表性的路径进行深入探测
        test_paths = []
        for url in urls[:50]:
            path = url.replace("https://www.hbwfjt.com", "")
            if path and path != "/" and path not in test_paths:
                test_paths.append(path)
        
        print(f"  从sitemap中选取 {len(test_paths)} 个路径进行深入探测:")
        
        for path in test_paths[:20]:
            try:
                time.sleep(0.3)
                url = f"https://www.hbwfjt.com{path}"
                r = session.get(url, timeout=8, allow_redirects=False)
                
                if r.status_code == 200:
                    content_type = r.headers.get("Content-Type", "")
                    title = ""
                    if "text/html" in content_type:
                        t = re.search(r'<title>(.*?)</title>', r.text[:5000], re.DOTALL)
                        if t:
                            title = t.group(1).strip()[:60]
                    
                    # 检查页面中是否有敏感信息
                    body = r.text
                    sensitive_info = []
                    
                    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', body)
                    if emails:
                        sensitive_info.append(f"邮箱:{len(emails)}个")
                    
                    phones = re.findall(r'(?:1[3-9]\d{9}|0\d{2,3}-?\d{7,8})', body)
                    if phones:
                        sensitive_info.append(f"电话:{len(phones)}个")
                    
                    ids = re.findall(r'\d{17}[\dXx]', body)
                    if ids:
                        sensitive_info.append(f"身份证:{len(ids)}个")
                    
                    internal_ips = re.findall(r'(?:10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)', body)
                    if internal_ips:
                        sensitive_info.append(f"内网IP:{list(set(internal_ips))}")
                    
                    info_str = " | ".join(sensitive_info) if sensitive_info else ""
                    print(f"  ✅ {path} -> {r.status_code} | {len(r.content)} bytes | {title or content_type[:30]} {info_str}")
                
                elif r.status_code in [301, 302]:
                    loc = r.headers.get("Location", "")
                    print(f"  ↪️  {path} -> {r.status_code} -> {loc[:60]}")
            except:
                pass
except Exception as e:
    print(f"  探测失败: {e}")

print(f"\n{'='*80}")
print("  分析完成")
print(f"{'='*80}")
