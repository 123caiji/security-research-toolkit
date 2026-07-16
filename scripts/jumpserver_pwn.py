import requests
import sys
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def jumpserver_login(url, username, password):
    session = requests.Session()
    session.verify = False
    
    targets = [url, f"{url}/jumpserver"]
    
    for target in targets:
        try:
            login_url = f"{target}/api/v1/authentication/auth/"
            data = {
                'username': username,
                'password': password
            }
            
            resp = session.post(login_url, json=data, timeout=10)
            
            if resp.status_code == 200:
                result = resp.json()
                if 'token' in result:
                    token = result['token']
                    print(f"[+] Jumpserver登录成功: {target}")
                    print(f"[*] Token: {token[:50]}...")
                    
                    session.headers['Authorization'] = f"Bearer {token}"
                    
                    user_info = session.get(f"{target}/api/v1/users/users/", timeout=10)
                    if user_info.status_code == 200:
                        users = user_info.json()
                        print(f"[+] 获取用户列表成功")
                        for user in users.get('results', [])[:5]:
                            print(f"    - {user.get('username')} ({user.get('role')})")
                    
                    asset_info = session.get(f"{target}/api/v1/assets/assets/", timeout=10)
                    if asset_info.status_code == 200:
                        assets = asset_info.json()
                        print(f"[+] 获取资产列表成功")
                        for asset in assets.get('results', [])[:5]:
                            print(f"    - {asset.get('hostname')} ({asset.get('ip')})")
                    
                    return True
                else:
                    print(f"[-] Jumpserver登录失败: {result.get('detail', '未知错误')}")
            else:
                print(f"[-] Jumpserver登录请求失败: {resp.status_code}")
        except Exception as e:
            print(f"[-] 连接失败: {target} - {e}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python jumpserver_pwn.py <url> <username> <password>")
        print("Example: python jumpserver_pwn.py http://192.168.80.148:8080 admin password123")
        sys.exit(1)
    
    url = sys.argv[1].rstrip('/')
    username = sys.argv[2]
    password = sys.argv[3]
    
    jumpserver_login(url, username, password)