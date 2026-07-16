import subprocess
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

TARGET = "http://www.chengyang.qdjcy.gov.cn"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def check_path(path):
    url = TARGET + path
    cmd = [
        "curl", "-s", "-o", "nul", "-w", "%{http_code}:%{size_download}",
        "-A", UA, "--compressed", "--max-time", "8", url
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        out = result.stdout.strip()
        parts = out.split(":")
        status = parts[0] if parts else "?"
        size = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        return path, status, size
    except:
        return path, "ERROR", 0

def main():
    print("=" * 60)
    print("  目录扫描 - 查找 iweboffice 及相关路径")
    print("=" * 60)
    
    paths = []
    
    # iweboffice 相关
    iweb_variants = [
        "iweboffice", "iWebOffice", "IWebOffice", "Iweboffice",
        "iweboffice2015", "iWebOffice2015", "iweboffice6", "iWebOffice6",
        "iweboffice2009", "iWebOffice2009", "iweboffice.net",
        "weboffice", "WebOffice", "webOffice",
        "office_server", "OfficeServer", "officeserver",
        "office_server.php", "OfficeServer.php", "officeserver.php",
        "iweb", "IWeb",
        "oa", "OA", "office_auto",
    ]
    
    for v in iweb_variants:
        paths.append(f"/{v}/")
        paths.append(f"/{v}/officeserver.php")
        paths.append(f"/{v}/OfficeServer.php")
        paths.append(f"/{v}/office.php")
        paths.append(f"/{v}/index.php")
    
    # 常见CMS路径
    cms_paths = [
        "/index.php",
        "/admin/",
        "/admin/index.php",
        "/admin/login.php",
        "/phpmyadmin/",
        "/phpMyAdmin/",
        "/manager/",
        "/manage/",
        "/system/",
        "/api/",
        "/api.php",
        "/config.php",
        "/config.ini",
        "/install/",
        "/install.php",
        "/upgrade/",
        "/data/",
        "/cache/",
        "/template/",
        "/templates/",
        "/themes/",
        "/theme/",
        "/upload/",
        "/uploadfile/",
        "/uploads/",
        "/files/",
        "/attachment/",
        "/attachments/",
        "/statics/",
        "/static/",
        "/public/",
        "/res/",
        "/resource/",
        "/resources/",
        "/common/",
        "/include/",
        "/includes/",
        "/lib/",
        "/libs/",
        "/vendor/",
        "/runtime/",
        "/app/",
        "/application/",
        "/thinkphp/",
        "/phpcms/",
        "/dedecms/",
        "/dede/",
        "/wordpress/",
        "/wp-admin/",
        "/wp-content/",
        "/wp-includes/",
        "/discuz/",
        "/forum/",
        "/bbs/",
        "/ucenter/",
    ]
    
    paths.extend(cms_paths)
    
    # 去重
    paths = list(set(paths))
    print(f"\n共测试 {len(paths)} 个路径...\n")
    
    results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(check_path, p): p for p in paths}
        for future in as_completed(futures):
            path, status, size = future.result()
            if status in ("200", "301", "302", "403", "500") and size > 0:
                results.append((status, size, path))
                print(f"  [{status}] {size:6d}B  {path}")
    
    print(f"\n共发现 {len(results)} 个非404路径")
    
    # 按状态码排序
    results.sort(key=lambda x: (x[0], -x[1]))
    print("\n按状态码排序:")
    for status, size, path in results:
        print(f"  [{status}] {size:6d}B  {path}")

if __name__ == "__main__":
    main()
