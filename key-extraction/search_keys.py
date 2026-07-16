import re

with open(r'C:\Users\xianyv\AppData\Local\Temp\app_new.js', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Search for K_E/K_S/K_P definitions
print("=== K_E/K_S/K_P definitions ===")
for m in re.finditer(r'K_[ESP][^a-zA-Z0-9]', c):
    s = max(0, m.start()-40)
    e = min(len(c), m.end()+200)
    print(repr(c[s:e]))
    print()

# 2. Search for globalConfig initialization
print("\n=== globalConfig init ===")
for m in re.finditer(r'globalConfig\s*[=:]\s*[^;]{1,300}', c):
    print(repr(m.group()[:250]))
    print()

# 3. Search for getSecretKey
print("\n=== getSecretKey ===")
for m in re.finditer(r'getSecretKey[^;]{1,200}', c):
    print(repr(m.group()[:200]))
    print()

# 4. Search for queryCustComponentDetail params
print("\n=== queryCustComponentDetail ===")
for m in re.finditer(r'queryCustComponentDetail[^}]{1,400}', c):
    print(repr(m.group()[:300]))
    print()

# 5. All TranCodes
print("\n=== All TranCodes ===")
trancodes = set()
for m in re.finditer(r'TranCode["\']?\s*[:=]\s*["\']([^"\']+)["\']', c):
    trancodes.add(m.group(1))
for tc in sorted(trancodes):
    print(tc)

# 6. Search for spgKeys mapping
print("\n=== spgKeys ===")
for m in re.finditer(r'spgKeys[^}]{1,500}', c):
    print(repr(m.group()[:400]))
    print()

# 7. Search for isEncryption config
print("\n=== isEncryption ===")
for m in re.finditer(r'isEncryption[^,}]{1,50}', c):
    print(repr(m.group()[:50]))
    print()
