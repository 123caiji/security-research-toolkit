#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证密钥解码"""
import base64
from gmssl import sm4

K_E_enc = 'YWRxI2ZncTNjJnZpZndiYHB2ZDRxbmNwczJjfGFidiU='
xor_key = 'VUEAPPE'

decoded = base64.b64decode(K_E_enc)
print('Base64 decoded (hex):', decoded.hex())
print('Base64 decoded (len):', len(decoded), 'bytes')

# XOR
result = bytearray()
key_bytes = xor_key.encode('utf-8')
for i, b in enumerate(decoded):
    result.append(b ^ key_bytes[i % len(key_bytes)])

print('XOR result (hex):', result.hex())
print('XOR result (str):', result.decode('utf-8', errors='replace'))
print('XOR result (len):', len(result), 'bytes')

# 把结果当作hex字符串解码
try:
    key_hex = result.decode('utf-8')
    key_bytes = bytes.fromhex(key_hex)
    print('Key bytes (from hex):', key_bytes.hex())
    print('Key bytes length:', len(key_bytes), 'bytes')
    
    # 验证SM4加密
    crypt = sm4.CryptSM4()
    crypt.set_key(key_bytes, sm4.SM4_ENCRYPT)
    encrypted = crypt.crypt_ecb(b'modp1')
    print('SM4("modp1") =', encrypted.hex())
    
    crypt_dec = sm4.CryptSM4()
    crypt_dec.set_key(key_bytes, sm4.SM4_DECRYPT)
    decrypted = crypt_dec.crypt_ecb(encrypted)
    print('Decrypted back:', decrypted.decode('utf-8'))
    
except Exception as e:
    print('Error:', e)
