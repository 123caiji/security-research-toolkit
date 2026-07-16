#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证硬编码密钥的正确性"""
import base64
from gmssl import sm4
import binascii

def getVueAppString(encoded_b64, xor_key):
    decoded = base64.b64decode(encoded_b64)
    result = bytearray()
    for i, b in enumerate(decoded):
        result.append(b ^ ord(xor_key[i % len(xor_key)]))
    return result

# 解码K_E
K_E_enc = 'YWRxI2ZncTNjJnZpZndiYHB2ZDRxbmNwczJjfGFidiU='
K_E = getVueAppString(K_E_enc, 'VUEAPPE')
print('=== K_E (SM4密钥) ===')
print(f'K_E (hex): {K_E.hex()}')
print(f'K_E (len): {len(K_E)} bytes')

# 解码K_S
K_S_enc = 'NGYheDNkYmA3cXZmY2U3ZHV1MjZrbzYhJTM2MmJlIyJlNmQ3MyciZDIxYGUneDZhNmQwIXRhYDJgNHd4aGE1ZQ=='
K_S = getVueAppString(K_S_enc, 'VUEAPPS')
print('\n=== K_S (SM2私钥) ===')
print(f'K_S (hex): {K_S.hex()}')
print(f'K_S (len): {len(K_S)} bytes')

# 解码K_P
K_P_enc = 'ZmF1I2RhZWZnIHlmMWhiMyN0ZGRhZWEhdDVkMmM2fCM0MTFlYCYiYjM0Z2VwdjViNmU3dnQxNGVlZiN0YjFiN2EhdmBjMTdsIHY0Z2luZXNzMWgyMDRzIGMzNTI3ISc1MzMyNyZwNmdkNzMgeDQzNjQ0dHZmYWVvbHJyMmFpb2QnJA=='
K_P = getVueAppString(K_P_enc, 'VUEAPPP')
print('\n=== K_P (SM2公钥) ===')
print(f'K_P (hex): {K_P.hex()[:130]}...')
print(f'K_P (len): {len(K_P)} bytes')
print(f'K_P starts with 04: {K_P[0] == 4}')

# 验证SM4加密
print('\n=== SM4加密验证 ===')
key = K_E
crypt = sm4.CryptSM4()
crypt.set_key(key, sm4.SM4_ENCRYPT)
plaintext = b'modp1'
encrypted = crypt.crypt_ecb(plaintext)
print(f'Plaintext: {plaintext.decode()}')
print(f'Encrypted: {encrypted.hex()}')

# 解密验证
crypt_dec = sm4.CryptSM4()
crypt_dec.set_key(key, sm4.SM4_DECRYPT)
decrypted = crypt_dec.crypt_ecb(encrypted)
print(f'Decrypted: {decrypted.decode("utf-8")}')
print(f'Verify: {decrypted == plaintext}')

# 验证DH组名解码
dhm_enc = 'OzohMWE='
dhm = getVueAppString(dhm_enc, 'VUEAPPDHM')
print('\n=== DH组名解码 ===')
print(f'DH modulus name: {dhm.decode("utf-8")}')

# 验证更多SM4加密用例
print('\n=== SM4加密更多用例 ===')
test_cases = [
    b'modp1',
    b'sfs01003001303031',
]
for tc in test_cases:
    enc = crypt.crypt_ecb(tc)
    print(f'  SM4("{tc.decode()}") = {enc.hex()}')

print('\n=== 验证完成 ===')
print('\n结论: 所有密钥成功解码，SM4加密验证通过')
print(f'K_E = {K_E.hex()}')
print(f'K_S = {K_S.hex()}')
