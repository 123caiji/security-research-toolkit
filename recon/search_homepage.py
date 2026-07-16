import subprocess

TARGET = "http://www.chengyang.qdjcy.gov.cn"
UA = "Mozilla/5.0 (Debian; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

def curl_get(path):
    url = TARGET + path
    cmd = ["curl", "-s", "-A", UA, "--compressed", "--max-time", "15", url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    return result.stdout

body = curl_get("/")

print("搜索 'officeserver' 相关行:")
count = 0
for i, line in enumerate(body.split("\n")):
    if "officeserver" in line.lower() and len(line.strip()) < 500:
        count += 1
        print(f"  行{i}: {line.strip()[:300]}")
if count == 0:
    print("  未找到officeserver")

print("\n搜索 'loadfile' 相关行:")
count = 0
for i, line in enumerate(body.split("\n")):
    if "loadfile" in line.lower() and len(line.strip()) < 500:
        count += 1
        print(f"  行{i}: {line.strip()[:300]}")
if count == 0:
    print("  未找到loadfile")

print("\n搜索 'option' 相关行:")
count = 0
for i, line in enumerate(body.split("\n")):
    if "option=" in line.lower() and len(line.strip()) < 500:
        count += 1
        print(f"  行{i}: {line.strip()[:300]}")
if count == 0:
    print("  未找到option=")

print("\n搜索 'filename' 相关行:")
count = 0
for i, line in enumerate(body.split("\n")):
    if "filename=" in line.lower() and len(line.strip()) < 500:
        count += 1
        print(f"  行{i}: {line.strip()[:300]}")
if count == 0:
    print("  未找到filename=")

print("\n搜索 'iweb' 相关行:")
count = 0
for i, line in enumerate(body.split("\n")):
    if "iweb" in line.lower() and len(line.strip()) < 500:
        count += 1
        print(f"  行{i}: {line.strip()[:300]}")
if count == 0:
    print("  未找到iweb")

print("\n搜索 '.php' 相关行:")
count = 0
for i, line in enumerate(body.split("\n")):
    if ".php" in line.lower() and len(line.strip()) < 300:
        count += 1
        if count <= 20:
            print(f"  行{i}: {line.strip()[:200]}")
print(f"  共找到 {count} 行含.php")

print("\n搜索 'mysql' 相关行:")
count = 0
for i, line in enumerate(body.split("\n")):
    if "mysql" in line.lower() and len(line.strip()) < 300:
        count += 1
        print(f"  行{i}: {line.strip()[:200]}")
if count == 0:
    print("  未找到mysql")
