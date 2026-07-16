import requests
import json
from urllib.parse import urljoin

requests.packages.urllib3.disable_warnings()

TARGET = "https://zhiqiapi.com"
TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://zhiqiapi.com",
    "Referer": "https://zhiqiapi.com/",
}

session = requests.Session()
session.verify = False
session.headers.update(HEADERS)


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_api_endpoint(path, method="GET", data=None, desc=""):
    """测试API端点的访问控制"""
    url = urljoin(TARGET, path)
    try:
        if method == "GET":
            r = session.get(url, timeout=TIMEOUT)
        else:
            r = session.post(url, json=data, timeout=TIMEOUT)
        
        status = r.status_code
        content_type = r.headers.get("Content-Type", "")
        length = len(r.content)
        
        result = f"  [{status}] {method} {path}"
        if desc:
            result += f" - {desc}"
        result += f" ({length} bytes)"
        
        if status == 200 and "application/json" in content_type:
            try:
                data_json = r.json()
                if isinstance(data_json, dict):
                    if data_json.get("success") == False:
                        result += f" | 错误: {data_json.get('message', '未知')[:50]}"
                    elif data_json.get("data") is not None:
                        result += " | ⚠️  返回数据！"
            except:
                pass
        elif status == 401:
            result += " | ✅ 需要认证"
        elif status == 403:
            result += " | ⚠️  禁止访问"
        
        print(result)
        return r
    except Exception as e:
        print(f"  [ERR] {path}: {e}")
        return None


def check_unauthenticated_apis():
    """检查未授权可访问的API端点"""
    print_section("8. 未授权API端点访问测试")
    
    api_paths = [
        ("/api/user/self", "GET", None, "当前用户信息"),
        ("/api/user/models", "GET", None, "用户模型列表"),
        ("/api/dashboard/users", "GET", None, "用户管理(后台)"),
        ("/api/system-settings/auth", "GET", None, "系统设置-认证"),
        ("/api/system-settings/site", "GET", None, "系统设置-站点"),
        ("/api/chat/models", "GET", None, "聊天模型列表"),
        ("/api/user/register", "POST", {"email": "test@test.com", "password": "test123456"}, "注册接口"),
        ("/api/user/login", "POST", {"username": "admin", "password": "admin"}, "登录接口"),
        ("/api/user/logout", "POST", None, "登出接口"),
        ("/api/oauth/state", "GET", None, "OAuth状态"),
        ("/api/custom-oauth-provider/", "GET", None, "自定义OAuth提供商"),
        ("/api/custom-oauth-provider/discovery", "GET", None, "OAuth发现"),
        ("/api/v1/user", "GET", None, "v1用户信息"),
        ("/api/v3/user", "GET", None, "v3用户信息"),
        ("/api/v4/user", "GET", None, "v4用户信息"),
        ("/_authenticated/system-settings", "GET", None, "认证系统设置"),
        ("/_authenticated/dashboard", "GET", None, "认证仪表盘"),
        ("/_authenticated/users/", "GET", None, "认证用户管理"),
        ("/_authenticated/models/", "GET", None, "认证模型管理"),
        ("/_authenticated/keys/", "GET", None, "认证密钥管理"),
        ("/_authenticated/playground/", "GET", None, "认证 playground"),
        ("/api/chat/display-models", "GET", None, "显示模型列表"),
        ("/api/subscription/plans", "GET", None, "订阅计划"),
        ("/api/payment/methods", "GET", None, "支付方式"),
        ("/api/auth/site-config", "GET", None, "站点配置"),
    ]
    
    for path, method, data, desc in api_paths:
        test_api_endpoint(path, method, data, desc)


def check_admin_paths():
    """检查管理后台路径"""
    print_section("9. 管理后台路径探测")
    
    admin_paths = [
        "/admin",
        "/admin/login",
        "/admin/index",
        "/admin/dashboard",
        "/admin/users",
        "/admin/settings",
        "/swagger",
        "/swagger-ui",
        "/swagger-ui.html",
        "/api-docs",
        "/v1/api-docs",
        "/v2/api-docs",
        "/docs",
        "/docs/api",
        "/redoc",
        "/graphql",
        "/graphiql",
        "/playground",
    ]
    
    for path in admin_paths:
        url = urljoin(TARGET, path)
        try:
            r = session.get(url, timeout=TIMEOUT, allow_redirects=False)
            status = r.status_code
            length = len(r.content)
            
            if status in [200, 401, 403]:
                print(f"  [{status}] {path} ({length} bytes)")
                if status == 200 and length > 2000:
                    content_type = r.headers.get("Content-Type", "")
                    print(f"         Content-Type: {content_type}")
            elif status in [301, 302]:
                print(f"  [{status}] {path} -> {r.headers.get('Location', '?')}")
        except Exception as e:
            pass


def check_default_credentials():
    """检查默认凭据"""
    print_section("10. 默认凭据测试")
    
    login_endpoints = [
        "/api/user/login",
        "/api/login",
        "/admin/login",
    ]
    
    default_creds = [
        ("admin", "admin"),
        ("admin", "admin123"),
        ("admin", "password"),
        ("root", "root"),
        ("test", "test"),
    ]
    
    for endpoint in login_endpoints:
        print(f"\n  测试: {endpoint}")
        for username, password in default_creds:
            url = urljoin(TARGET, endpoint)
            try:
                r = session.post(url, json={
                    "username": username,
                    "password": password,
                    "email": username,
                }, timeout=TIMEOUT)
                
                if r.status_code == 200:
                    try:
                        data = r.json()
                        if data.get("success") or data.get("token"):
                            print(f"    ⚠️  [{r.status_code}] {username}/{password} - 可能成功！")
                        else:
                            print(f"    [{r.status_code}] {username}/{password}: {data.get('message', '无消息')[:40]}")
                    except:
                        print(f"    [{r.status_code}] {username}/{password} (非JSON响应)")
                else:
                    print(f"    [{r.status_code}] {username}/{password}")
            except Exception as e:
                print(f"    [ERR] {e}")


def check_rate_limit():
    """检查速率限制"""
    print_section("11. 速率限制测试")
    
    url = urljoin(TARGET, "/api/user/login")
    print(f"\n  目标: {url}")
    print(f"  连续发送10次请求...")
    
    statuses = []
    for i in range(10):
        try:
            r = session.post(url, json={
                "email": f"test{i}@test.com",
                "password": "wrongpassword123"
            }, timeout=TIMEOUT)
            statuses.append(r.status_code)
            limit = r.headers.get('X-RateLimit-Limit', 'N/A')
            remaining = r.headers.get('X-RateLimit-Remaining', 'N/A')
            print(f"    请求 {i+1}: [{r.status_code}] 剩余: {remaining}/{limit}")
        except Exception as e:
            print(f"    请求 {i+1}: [ERR] {e}")
    
    unique_statuses = set(statuses)
    print(f"\n  状态码分布: {dict(zip(unique_statuses, [statuses.count(s) for s in unique_statuses]))}")


def main():
    print("*" * 60)
    print("  ZHIQIAPI.COM 深度安全检测")
    print("  目标: " + TARGET)
    print("*" * 60)
    
    check_unauthenticated_apis()
    check_admin_paths()
    check_default_credentials()
    check_rate_limit()
    
    print_section("检测完成")
    print("\n  ⚠️  免责声明:")
    print("  本检测仅用于安全配置自查，不涉及漏洞利用")
    print("  检测结果仅供参考，请结合实际业务进行评估")
    print()


if __name__ == "__main__":
    main()
