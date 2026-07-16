#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青岛市人民检察院 www.qdjcy.gov.cn 异常流量告警复现脚本
告警类型: HTTP URL中存在伪装协议访问行为 (file:// 协议)
告警来源: YisouSpider 爬虫抓取到 WPS Office 生成的网页资源清单

用法: python reproduce_alert.py
依赖: pip install requests
注意: 如需走 Burp 代理，修改下方 PROXIES 配置
"""

import requests
import urllib.parse
import sys

# ===== 配置区 =====
TARGET_HOST = "http://www.qdjcy.gov.cn"
# 如需走 Burp 代理，取消下行注释
# PROXIES = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
PROXIES = None

# 是否绕过系统代理（直连，避免环境代理返回503）
# 通过设置 NO_PROXY 环境变量实现，requests 会自动绕过系统代理
import os
os.environ["NO_PROXY"] = "*"

HEADERS = {
    "User-Agent": "YisouSpider",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "connection": "close",
}

# 告警中的原始 URL 参数（完整资源清单）
ORIGINAL_URL_PARAM = (
    "SCRIPT*http://www.qdjcy.gov.cn/statics/js/jquery.min.js;"
    "SCRIPT*http://www.qdjcy.gov.cn/statics/js/qingjian/public.js;"
    "SCRIPT*http://www.qdjcy.gov.cn/api.php?op=count&id=1671&modelid=1;"
    "SCRIPT*http://dcs.conac.cn/js/16/235/0000/60233518/CA162350000602335180001.js;"
    "SCRIPT*http://www.qdjcy.gov.cn/statics/js/qingjian/jquery.hoverdir.js;"
    "IMG*file:///C:/Users/123/AppData/Local/Temp/ksohtml7640/wps1.png;"  # ← 触发告警的 file:// 协议
    "IMG*http://www.qdjcy.gov.cn/statics/images/qingjian/link-11.jpg;"
    "IMG*http://www.qdjcy.gov.cn/statics/images/qingjian/qdwb.jpg;"
    "IMG*http://www.qdjcy.gov.cn/statics/images/qingjian/qdwx.jpg;"
    "LINK*http://www.qdjcy.gov.cn/statics/css/qingjian/bootstrap.css;"
    "LINK*http://www.qdjcy.gov.cn/statics/css/qingjian/css.css;"
    "LINK*http://www.qdjcy.gov.cn/statics/css/qingjian/details.css;"
    "&localurl=http://www.qdjcy.gov.cn/html/zdal/20200605/1/1671.html"
)

ORIGINAL_PATH = "/html/zdal/20200605/1/brmidyrvj.php"
ORIGINAL_REFERER = "http://www.qdjcy.gov.cn/html/zdal/20200605/1/1671.html"


def send_request(path, url_param=None, referer=None, desc=""):
    """发送 HTTP GET 请求"""
    url = TARGET_HOST + path
    headers = HEADERS.copy()
    if referer:
        headers["Referer"] = referer

    params = {}
    if url_param is not None:
        params["url"] = url_param

    print(f"\n{'='*70}")
    print(f"[测试] {desc}")
    print(f"{'='*70}")
    print(f"URL: {url}")
    if params:
        # 显示完整请求 URL（参数未编码，便于复现）
        full_url = url + "?url=" + url_param if url_param else url
        print(f"完整请求: {full_url[:200]}{'...' if len(full_url) > 200 else ''}")

    try:
        resp = requests.get(
            url,
            params=params,
            headers=headers,
            proxies=PROXIES,
            verify=False,
            timeout=15,
            allow_redirects=False,
        )
        print(f"\n响应:")
        print(f"  HTTP状态码: {resp.status_code}")
        print(f"  响应大小: {len(resp.content)} 字节")
        print(f"  Server: {resp.headers.get('Server', 'N/A')}")
        print(f"  ETag: {resp.headers.get('ETag', 'N/A')}")
        print(f"  Content-Type: {resp.headers.get('Content-Type', 'N/A')}")

        # 显示响应体（截断）
        body = resp.text.strip()
        if len(body) > 300:
            print(f"\n响应体 (前300字符):")
            print(f"  {body[:300]}...")
        else:
            print(f"\n响应体:")
            print(f"  {body}")

        # 检查是否命中告警特征
        flags = []
        if resp.status_code == 404:
            flags.append("404 Not Found")
        if "5b4d57de-41" in resp.headers.get("ETag", ""):
            flags.append("ETag匹配(nginx自定义404页面)")
        if "window.location.href" in body:
            flags.append("JS重定向到首页")
        if flags:
            print(f"\n[匹配特征] {' | '.join(flags)}")

        return resp
    except requests.exceptions.ConnectionError as e:
        print(f"\n[!] 连接失败(可能被WAF拦截): {e}")
        return None
    except requests.exceptions.Timeout:
        print(f"\n[!] 请求超时")
        return None
    except Exception as e:
        print(f"\n[!] 异常: {e}")
        return None


def main():
    print("#" * 70)
    print("# 异常流量告警复现 - www.qdjcy.gov.cn")
    print("# 告警: HTTP URL中存在伪装协议访问行为 (file:// 协议)")
    print("#" * 70)

    # ===== 测试1: 复现告警原始请求 =====
    send_request(
        ORIGINAL_PATH,
        url_param=ORIGINAL_URL_PARAM,
        referer=ORIGINAL_REFERER,
        desc="复现告警原始请求 (完整资源清单含file://)",
    )

    # ===== 测试2: 仅保留触发告警的file://部分 =====
    send_request(
        ORIGINAL_PATH,
        url_param="IMG*file:///C:/Users/123/AppData/Local/Temp/ksohtml7640/wps1.png;&localurl=http://www.qdjcy.gov.cn/html/zdal/20200605/1/1671.html",
        referer=ORIGINAL_REFERER,
        desc="仅保留file://触发部分",
    )

    # ===== 测试3: 测试简单file://是否被WAF拦截 =====
    send_request(
        ORIGINAL_PATH,
        url_param="file:///etc/passwd",
        desc="简单file://协议(WAF应拦截)",
    )

    # ===== 测试4: 不带任何参数访问brmidyrvj.php =====
    send_request(
        ORIGINAL_PATH,
        desc="不带参数访问brmidyrvj.php(确认404是文件不存在导致)",
    )

    # ===== 测试5: 访问原始页面1671.html(确认页面存在) =====
    send_request(
        "/html/zdal/20200605/1/1671.html",
        desc="访问被爬取的原页面1671.html(应返回200)",
    )

    # ===== 测试6: URL编码的file:// =====
    send_request(
        ORIGINAL_PATH,
        url_param="file%3A%2F%2F%2FC%3A%2Ftest",
        desc="URL编码的file://协议",
    )

    # ===== 测试7: 其他伪协议测试 =====
    send_request(
        ORIGINAL_PATH,
        url_param="javascript:alert(1)",
        desc="javascript:协议测试",
    )

    # ===== 总结 =====
    print("\n" + "#" * 70)
    print("# 复现总结")
    print("#" * 70)
    print("""
告警场景还原:
  1. 有人使用 WPS Office 打开页面 1671.html 并"另存为网页"
  2. WPS 在临时目录(ksohtml7640)生成网页快照，本地图片以
     file:///C:/Users/123/AppData/Local/Temp/ksohtml7640/wps1.png 形式引用
  3. 该资源清单被提交至 brmidyrvj.php?url=... (此PHP文件已不存在)
  4. 神马搜索爬虫(YisouSpider)抓取到这个URL并访问
  5. URL参数中包含 file:// 协议，触发XDR"伪装协议访问"告警
  6. 服务器返回404 + JS重定向到首页

关键证据:
  - brmidyrvj.php 不存在，nginx返回固定404页面(ETag: "5b4d57de-41")
  - file:// 参数未被服务器解析使用，仅作为URL字符串
  - 简单file://会被WAF拦截，但嵌套在复杂字符串中可绕过WAF规则匹配
  - User-Agent为YisouSpider(神马搜索爬虫)，非攻击工具
  - Referer指向合法页面 1671.html

结论: 误报(false positive)
  - 攻击结果: 攻击失败(告警已标注)
  - 威胁可信度: 低(告警已标注)
  - 实际场景: WPS Office生成的网页快照资源清单被爬虫抓取
  - 建议: 可安全关闭此告警
""")
    print("#" * 70)


if __name__ == "__main__":
    main()
