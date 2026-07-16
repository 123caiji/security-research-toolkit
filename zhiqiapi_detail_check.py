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


def check_endpoint_detail(path, method="GET", data=None):
    """详细检查API端点"""
    url = urljoin(TARGET, path)
    try:
        if method == "GET":
            r = session.get(url, timeout=TIMEOUT)
        else:
            r = session.post(url, json=data, timeout=TIMEOUT)
        
        print(f"\n  {method} {path}")
        print(f"  状态码: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('Content-Type', 'N/A')}")
        print(f"  响应头:")
        for key, value in r.headers.items():
            if key.lower() not in ['date', 'server', 'content-length', 'connection']:
                print(f"    {key}: {value[:80]}")
        
        if r.content and len(r.content) < 2000:
            try:
                data_json = r.json()
                print(f"  响应体 (JSON):")
                print(json.dumps(data_json, indent=2, ensure_ascii=False)[:500])
            except:
                print(f"  响应体 (文本):")
                print(r.text[:300])
        
        return r
    except Exception as e:
        print(f"  [ERR] {e}")
        return None


def main():
    print("*" * 60)
    print("  ZHIQIAPI.COM 关键端点详细检测")
    print("  目标: " + TARGET)
    print("*" * 60)
    
    print_section("1. OAuth 状态接口 (未授权访问)")
    check_endpoint_detail("/api/oauth/state")
    
    print_section("2. 注册接口 (邮箱验证配置)")
    check_endpoint_detail("/api/user/register", "POST", {
        "email": "test@example.com",
        "password": "TestPass123!",
        "username": "testuser"
    })
    
    print_section("3. 登录接口 (错误信息泄露)")
    check_endpoint_detail("/api/user/login", "POST", {
        "username": "nonexistent_user",
        "password": "wrongpass"
    })
    
    print_section("4. 用户模型列表 (需要认证)")
    check_endpoint_detail("/api/user/models")
    
    print_section("5. 订阅计划 (需要认证)")
    check_endpoint_detail("/api/subscription/plans")
    
    print_section("6. 自定义OAuth提供商 (需要认证)")
    check_endpoint_detail("/api/custom-oauth-provider/")
    
    print_section("检测完成")
    print()


if __name__ == "__main__":
    main()
