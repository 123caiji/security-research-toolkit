import urllib.request
import urllib.error
import time

proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)

test_cases = [
    {'path': '/web/getTopLinksPortalCategoriesAction.action', 'desc': 'single slash'},
    {'path': '/web//getTopLinksPortalCategoriesAction.action', 'desc': 'double slash'},
    {'path': '/web///getTopLinksPortalCategoriesAction.action', 'desc': 'triple slash'},
    {'path': '/web/./getTopLinksPortalCategoriesAction.action', 'desc': 'dot path'},
    {'path': '/sdskb/web/getTopLinksPortalCategoriesAction.action', 'desc': 'sdskb web'},
    {'path': '/sdosta/web/getTopLinksPortalCategoriesAction.action', 'desc': 'sdosta web'},
    {'path': '/sdostanet/web/getTopLinksPortalCategoriesAction.action', 'desc': 'sdostanet web'},
]

for tc in test_cases:
    url = 'http://124.128.231.226:8888' + tc['path'] + '?siteId=test'
    print('Testing [' + tc['desc'] + ']: ' + url)
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        req.add_header('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
        req.add_header('Referer', 'http://124.128.231.226:8888/')
        resp = opener.open(req, timeout=10)
        print('  Status: ' + str(resp.status))
        body = resp.read()
        print('  Body length: ' + str(len(body)))
        if b'Struts Problem Report' in body:
            print('  [FOUND] Struts Problem Report detected!')
            body_text = body.decode('utf-8', errors='replace')
            print('  Preview: ' + body_text[:300])
    except urllib.error.HTTPError as e:
        print('  Status: ' + str(e.code))
        body = e.read()
        print('  Body length: ' + str(len(body)))
        if b'Struts Problem Report' in body:
            print('  [FOUND] Struts Problem Report detected!')
            body_text = body.decode('utf-8', errors='replace')
            print('  Preview: ' + body_text[:300])
    except Exception as e:
        print('  Error: ' + str(e))
    print()
    time.sleep(1)
