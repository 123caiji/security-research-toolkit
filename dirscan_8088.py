import requests
import threading
from concurrent.futures import ThreadPoolExecutor
import os

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 10
THREADS = 30

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

paths = [
    "/", "/login", "/admin", "/admin/", "/dashboard", "/upload", "/uploads", "/search",
    "/ping", "/backup", "/include", "/message", "/flag", "/flag.txt", "/FLAG",
    "/.env", "/config.py", "/app.py", "/main.py", "/server.py", "/run.py",
    "/robots.txt", "/.git/", "/.git/config", "/.git/HEAD", "/.gitignore",
    "/api", "/api/", "/api/v1", "/api/v2", "/api/flag", "/api/users",
    "/source", "/source-code", "/upload-source", "/ping-source", "/backup-source",
    "/full-source", "/all-source", "/app-source", "/server-source", "/main-source",
    "/config", "/settings", "/setup", "/install", "/test", "/debug",
    "/phpinfo", "/info", "/status", "/health", "/metrics", "/trace",
    "/.htaccess", "/.htpasswd", "/web.config", "/.well-known/security.txt",
    "/favicon.ico", "/sitemap.xml", "/humans.txt", "/manifest.json",
    "/static", "/static/", "/js", "/js/", "/css", "/css/", "/img", "/img/",
    "/secret", "/secrets", "/hidden", "/private", "/internal", "/dev",
    "/.bash_history", "/.mysql_history", "/.ssh/id_rsa", "/.ssh/authorized_keys",
    "/db.sql", "/database.sql", "/backup.sql", "/dump.sql", "/data.db",
    "/users", "/users.json", "/user", "/account", "/accounts",
    "/console", "/shell", "/cmd", "/exec", "/run",
    "/~admin", "/~root", "/~user", "/.DS_Store",
    "/swagger", "/swagger-ui", "/swagger.json", "/api-docs",
    "/actuator", "/actuator/health", "/actuator/env", "/actuator/configprops",
    "/ws", "/websocket", "/socket.io",
    "/graphql", "/graphiql",
    "/.svn/entries", "/.svn/wc.db", "/.hg/",
    "/ckeditor", "/fckeditor", "/kindeditor", "/ueditor",
    "/adminer", "/phpmyadmin", "/phpMyAdmin", "/pma",
    "/wp-admin", "/wp-login", "/wp-config.php",
    "/login.php", "/admin.php", "/index.php", "/config.php",
    "/login.aspx", "/admin.aspx", "/index.aspx",
    "/login.jsp", "/admin.jsp", "/index.jsp",
    "/.user.ini", "/user.ini", "/php.ini",
    "/error.log", "/access.log", "/debug.log", "/nohup.out",
    "/admin/login", "/admin/index", "/admin/dashboard", "/admin/config",
    "/manager", "/manager/html", "/host-manager",
    "/solr", "/elasticsearch", "/kibana", "/grafana",
    "/jenkins", "/gitlab", "/github", "/bitbucket",
    "/nacos", "/druid", "/api/jsonws",
    "/api.php", "/api.html", "/api.json", "/api.xml",
    "/rpc", "/jsonrpc", "/xmlrpc", "/soap",
    "/wsdl", "/api?wsdl", "/service?wsdl",
]

found = []
lock = threading.Lock()

def check_path(path):
    try:
        url = f"{TARGET}{path}"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False, allow_redirects=False)
        
        if r.status_code in [200, 201, 204, 301, 302, 307, 401, 403, 405, 500]:
            size = len(r.content)
            with lock:
                print(f"[{r.status_code}] {path} (size: {size})")
                found.append({"path": path, "status": r.status_code, "size": size, "content_type": r.headers.get('Content-Type', '')})
    except:
        pass

print("="*70)
print(f"目录扫描 - {TARGET}")
print("="*70)

with ThreadPoolExecutor(max_workers=THREADS) as executor:
    executor.map(check_path, paths)

print("\n" + "="*70)
print("发现的有趣路径:")
print("="*70)

for item in found:
    if item["status"] in [200, 201, 204] and item["size"] > 0:
        print(f"[{item['status']}] {item['path']} - {item['size']} bytes - {item['content_type']}")

print(f"\n总计发现: {len(found)} 个路径")
