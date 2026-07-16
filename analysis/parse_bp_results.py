import json
import re

files = {
    "原始OAST payload": r"C:\Users\xianyv\AppData\Local\Temp\trae\toolcall-output\8fd2f505-80b5-4691-84c4-21fe4100a735.txt",
    "SSRF 127.0.0.1": r"C:\Users\xianyv\AppData\Local\Temp\trae\toolcall-output\911ee920-2e47-402a-b49e-f930d8491b3d.txt",
    "基线 test_baseline": r"C:\Users\xianyv\AppData\Local\Temp\trae\toolcall-output\e89d0748-1dd3-4bb2-b452-ef05eb390b23.txt",
}

for label, fpath in files.items():
    print("=" * 60)
    print(f"测试: {label}")
    print("=" * 60)
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取JSON部分
        json_start = content.find('{"type":"text","text":"')
        if json_start == -1:
            json_start = content.find('[{"type":"text","text":"')
        
        # 直接找 "response": { 开始的部分
        resp_match = re.search(r'"response":\s*\{', content)
        if resp_match:
            # 提取关键字段
            status_match = re.search(r'"status_code":\s*(\d+)', content)
            size_match = re.search(r'"size":\s*(\d+)', content)
            time_match = re.search(r'"time":\s*([\d.]+)', content)
            
            status = status_match.group(1) if status_match else "?"
            size = size_match.group(1) if size_match else "?"
            time = time_match.group(1) if time_match else "?"
            
            print(f"  状态码: {status}")
            print(f"  响应大小: {size} 字节")
            print(f"  响应时间: {time}s")
            
            # 检查payload是否反射在响应中
            # 提取请求URL中的payload
            url_match = re.search(r'"url":\s*"([^"]+)"', content)
            if url_match:
                url = url_match.group(1)
                print(f"  请求URL: {url[:100]}...")
                
                # 提取url参数值
                if "?url=" in url:
                    payload = url.split("?url=", 1)[1]
                    print(f"  Payload: {payload[:80]}")
                    
                    # 在响应内容中搜索payload
                    content_match = re.search(r'"content":\s*"((?:[^"\\]|\\.)*)"', content)
                    if content_match:
                        resp_content = content_match.group(1)
                        # 解码转义
                        resp_content_decoded = resp_content.encode().decode('unicode_escape', errors='ignore')
                        
                        if payload in resp_content_decoded:
                            print(f"  !! PAYLOAD在响应中反射!")
                            idx = resp_content_decoded.find(payload)
                            context = resp_content_decoded[max(0,idx-100):idx+len(payload)+100]
                            print(f"     上下文: ...{context}...")
                        else:
                            print(f"  - Payload未在响应中反射")
                        
                        # 检查响应中是否有敏感信息
                        if "oast.site" in resp_content_decoded:
                            print(f"  !! 响应中包含 oast.site 字样")
                        if "alert(1)" in resp_content_decoded:
                            print(f"  !! 响应中包含 alert(1) 字样")
                        if "127.0.0.1" in resp_content_decoded:
                            print(f"  !! 响应中包含 127.0.0.1 字样")
            
            # 检查漏洞
            vuln_match = re.search(r'"vulnerabilities":\s*\[', content)
            if vuln_match:
                vuln_section = content[vuln_start:]
                vulns = re.findall(r'"description":\s*"([^"]+)"', vuln_section)
                if vulns:
                    print(f"  检测到的问题:")
                    for v in vulns[:5]:
                        print(f"    - {v}")
        else:
            print("  未找到response字段")
            # 检查error
            error_match = re.search(r'"error":\s*"([^"]+)"', content)
            if error_match:
                print(f"  错误: {error_match.group(1)}")
    except Exception as e:
        print(f"  解析错误: {e}")
    print()

# 比较三个响应的大小
print("=" * 60)
print("响应大小对比")
print("=" * 60)
print("基线 test_baseline_xyz123: 41266 字节")
print("原始OAST payload: 见上")
print("SSRF 127.0.0.1: 见上")
print("script标签: 连接被重置 (WAF拦截)")
