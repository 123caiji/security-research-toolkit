import requests
import time

def check_tomcat_manager(url, rate_limit=5):
    """
    验证 Tomcat Manager 是否存在
    :param url: 目标URL
    :param rate_limit: 每秒最大请求数
    """
    results = []
    
    endpoints = [
        url,
        url.rstrip('/'),
        url.replace('host-manager', 'manager'),
        url.replace('host-manager', 'manager').rstrip('/'),
    ]
    
    # 不使用代理
    session = requests.Session()
    session.trust_env = False
    
    for endpoint in endpoints:
        try:
            print(f"正在检查: {endpoint}")
            response = session.get(endpoint, timeout=10)
            
            result = {
                "url": endpoint,
                "status_code": response.status_code,
                "content_length": len(response.content),
                "server": response.headers.get('Server', 'Unknown'),
                "contains_tomcat": "tomcat" in response.text.lower() or "tomcat" in response.headers.get('Server', '').lower(),
                "contains_manager": "manager" in response.text.lower(),
                "requires_auth": response.status_code == 401,
            }
            results.append(result)
            
            if response.status_code == 401:
                print(f"  → 需要认证 (401) - 可能存在 Tomcat Manager")
            elif response.status_code == 200:
                print(f"  → 可访问 (200)")
                if "tomcat" in response.text.lower():
                    print(f"    ✓ 页面包含 Tomcat 相关内容")
            else:
                print(f"  → 状态码: {response.status_code}")
                
            time.sleep(1 / rate_limit)
            
        except requests.exceptions.RequestException as e:
            print(f"  → 请求失败: {str(e)}")
            results.append({
                "url": endpoint,
                "error": str(e)
            })
            time.sleep(1 / rate_limit)
    
    return results

if __name__ == "__main__":
    target_url = "http://www.zbjcy.gov.cn//host-manager/html/"
    print(f"开始验证目标: {target_url}")
    print(f"速率限制: 最多 {5} 请求/秒")
    print("=" * 60)
    
    results = check_tomcat_manager(target_url)
    
    print("=" * 60)
    print("验证结果汇总:")
    for r in results:
        if 'error' in r:
            print(f"✗ {r['url']} - {r['error']}")
        else:
            status = "✓" if r.get('contains_tomcat') or r.get('requires_auth') else "?"
            print(f"{status} {r['url']} - 状态码: {r['status_code']}, 服务器: {r['server']}")