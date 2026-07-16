import urllib.request
import urllib.error
import os
import datetime

proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)

def fetch_url(url):
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        req.add_header('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
        resp = opener.open(req, timeout=15)
        return resp.status, dict(resp.headers.items()), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers.items()), e.read()
    except Exception as e:
        return None, None, str(e).encode('utf-8')

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
        'name': '03_sdskb_login',
        'url': 'http://124.128.231.226:8888/sdskb/',
        'title': '山东省职业技能综合评价信息管理平台 - 登录页',
        'system': '山东省职业技能综合评价信息管理平台'
    },
]

for item in urls:
    print('Processing: ' + item['name'])
    status, headers, body = fetch_url(item['url'])
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
    status_text = '存在Java错误信息泄露 (高危)' if has_struts_error else ('HTTP ' + str(status))
    
    full_html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>''' + item['title'] + '''</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
            background-color: #f0f2f5;
            color: #333;
            line-height: 1.6;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
        }
        .header h1 {
            font-size: 20px;
            margin-bottom: 8px;
        }
        .header .system-name {
            font-size: 14px;
            opacity: 0.9;
        }
        .url-bar {
            background-color: #fff;
            border-bottom: 1px solid #e8e8e8;
            padding: 12px 30px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .url-label {
            background-color: #e8f4fd;
            color: #1890ff;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 500;
            white-space: nowrap;
        }
        .url-value {
            font-family: Consolas, Monaco, monospace;
            font-size: 13px;
            color: #555;
            word-break: break-all;
            flex: 1;
        }
        .info-bar {
            background-color: #fff;
            border-bottom: 1px solid #e8e8e8;
            padding: 10px 30px;
            display: flex;
            gap: 30px;
            font-size: 13px;
        }
        .info-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .info-label {
            color: #888;
        }
        .info-value {
            color: #333;
            font-weight: 500;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            color: white;
            font-weight: 600;
            font-size: 12px;
            background-color: ''' + status_color + ''';
        }
        .content {
            padding: 20px 30px;
        }
        .content-frame {
            background-color: #fff;
            border: 1px solid #e8e8e8;
            border-radius: 8px;
            padding: 25px;
            min-height: 400px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            overflow: auto;
        }
        .content-frame h2 {
            color: #d4380d;
            margin-bottom: 15px;
        }
        .content-frame pre {
            background-color: #f6f8fa;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 12px;
            line-height: 1.5;
        }
        .footer {
            text-align: center;
            padding: 15px;
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>''' + item['title'] + '''</h1>
        <div class="system-name">''' + item['system'] + '''</div>
    </div>
    <div class="url-bar">
        <span class="url-label">访问URL</span>
        <span class="url-value">''' + item['url'] + '''</span>
    </div>
    <div class="info-bar">
        <div class="info-item">
            <span class="info-label">验证状态:</span>
            <span class="status-badge">''' + status_text + '''</span>
        </div>
        <div class="info-item">
            <span class="info-label">HTTP状态:</span>
            <span class="info-value">''' + str(status) + '''</span>
        </div>
        <div class="info-item">
            <span class="info-label">服务器:</span>
            <span class="info-value">''' + server + '''</span>
        </div>
        <div class="info-item">
            <span class="info-label">验证时间:</span>
            <span class="info-value">''' + now + '''</span>
        </div>
    </div>
    <div class="content">
        <div class="content-frame">
''' + html + '''
        </div>
    </div>
    <div class="footer">
        安全漏洞验证截图 - 仅用于授权安全测试
    </div>
</body>
</html>'''
    
    filepath = os.path.join(output_dir, item['name'] + '.html')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print('  Saved to: ' + filepath)

print('\nDone! All HTML files generated.')
