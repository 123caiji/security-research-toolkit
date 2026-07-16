#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证所有密钥并输出正确值"""
import base64
from gmssl import sm4

def getVueAppString(encoded_b64, xor_key):
    decoded = base64.b64decode(encoded_b64)
    result = bytearray()
    key_bytes = xor_key.encode('utf-8')
    for i, b in enumerate(decoded):
        result.append(b ^ key_bytes[i % len(key_bytes)])
    return result.decode('utf-8')

# 解码所有密钥
K_E_hex = getVueAppString('YWRxI2ZncTNjJnZpZndiYHB2ZDRxbmNwczJjfGFidiU=', 'VUEAPPE')
K_S_hex = getVueAppString('NGYheDNkYmA3cXZmY2U3ZHV1MjZrbzYhJTM2MmJlIyJlNmQ3MyciZDIxYGUneDZhNmQwIXRhYDJgNHd4aGE1ZQ==', 'VUEAPPS')
K_P_hex = getVueAppString('ZmF1I2RhZWZnIHlmMWhiMyN0ZGRhZWEhdDVkMmM2fCM0MTFlYCYiYjM0Z2VwdjViNmU3dnQxNGVlZiN0YjFiN2EhdmBjMTdsIHY0Z2luZXNzMWgyMDRzIGMzNTI3ISc1MzMyNyZwNmdkNzMgeDQzNjQ0dHZmYWVvbHJyMmFpb2QnJA==', 'VUEAPPP')
DH_MOD = getVueAppString('OzohMWE=', 'VUEAPPDHM')

print('=== 密钥解码结果 ===')
print()
print('K_E (SM4密钥) - hex字符串:')
print(f'  {K_E_hex}')
print(f'  长度: {len(K_E_hex)} chars = {len(bytes.fromhex(K_E_hex))} bytes')
print()
print('K_S (SM2私钥) - hex字符串:')
print(f'  {K_S_hex}')
print(f'  长度: {len(K_S_hex)} chars = {len(bytes.fromhex(K_S_hex))} bytes')
print()
print('K_P (SM2公钥) - hex字符串:')
print(f'  {K_P_hex}')
print(f'  长度: {len(K_P_hex)} chars = {len(bytes.fromhex(K_P_hex))} bytes')
k_p_bytes = bytes.fromhex(K_P_hex)
print(f'  首字节: 0x{k_p_bytes[0]:02x} (SM2未压缩公钥以04开头)')
print()
print('DH模数组名:')
print(f'  {DH_MOD}')
print()

# 验证SM4加密
print('=== SM4加密验证 ===')
key_bytes = bytes.fromhex(K_E_hex)
crypt = sm4.CryptSM4()
crypt.set_key(key_bytes, sm4.SM4_ENCRYPT)

test_cases = [
    'modp1',
    'sfs01003001303031',
]
for tc in test_cases:
    enc = crypt.crypt_ecb(tc.encode('utf-8'))
    print(f'  SM4("{tc}") = {enc.hex()}')

print()
print('=== 结论 ===')
print('所有密钥成功从前端JS代码中解码')
print(f'K_E (SM4): {K_E_hex} (128位)')
print(f'K_S (SM2私钥): {K_S_hex} (256位)')
print(f'K_P (SM2公钥): 以0x{k_p_bytes[0]:02x}开头, {len(k_p_bytes)}字节')
print(f'DH组: {DH_MOD} (768位 - 弱密码学参数)')
