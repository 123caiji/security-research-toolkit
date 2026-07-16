# -*- coding: utf-8 -*-
"""
常见密码加密算法枚举与对照工具（纯本地，不联网）。

功能：
1. 分析常见密码加密算法（MD5、SHA256、Base64 等）
2. 根据密文特征猜测算法类型
3. 提供算法演示输出
"""

from __future__ import annotations

import base64
import hashlib
import hmac


class PasswordEncoderAnalyzer:
    """密码加密算法分析器"""

    def __init__(self) -> None:
        self.algorithms = [
            "md5",
            "md5_upper",
            "sha1",
            "sha256",
            "sha512",
            "base64",
            "md5_md5",
            "md5_sha1",
            "sha256_salt",
            "md5_salt",
            "hmac_md5",
            "hmac_sha256",
        ]

    def md5(self, password: str) -> str:
        return hashlib.md5(password.encode("utf-8")).hexdigest()

    def md5_upper(self, password: str) -> str:
        return hashlib.md5(password.encode("utf-8")).hexdigest().upper()

    def sha1(self, password: str) -> str:
        return hashlib.sha1(password.encode("utf-8")).hexdigest()

    def sha256(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def sha512(self, password: str) -> str:
        return hashlib.sha512(password.encode("utf-8")).hexdigest()

    def base64_encode(self, password: str) -> str:
        return base64.b64encode(password.encode("utf-8")).decode("utf-8")

    def md5_md5(self, password: str) -> str:
        inner = hashlib.md5(password.encode("utf-8")).hexdigest()
        return hashlib.md5(inner.encode("utf-8")).hexdigest()

    def md5_sha1(self, password: str) -> str:
        inner = hashlib.md5(password.encode("utf-8")).hexdigest()
        return hashlib.sha1(inner.encode("utf-8")).hexdigest()

    def md5_salt(self, password: str, salt: str = "demo") -> str:
        return hashlib.md5((password + salt).encode("utf-8")).hexdigest()

    def sha256_salt(self, password: str, salt: str = "demo") -> str:
        return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

    def hmac_md5(self, password: str, key: str = "demo_secret_key") -> str:
        return hmac.new(key.encode("utf-8"), password.encode("utf-8"), hashlib.md5).hexdigest()

    def hmac_sha256(self, password: str, key: str = "demo_secret_key") -> str:
        return hmac.new(key.encode("utf-8"), password.encode("utf-8"), hashlib.sha256).hexdigest()

    def analyze_all(self, password: str) -> dict[str, str]:
        results: dict[str, str] = {}
        print(f"\n[*] 分析密码: '{password}' 的各种加密结果")
        print("-" * 80)

        for algo in self.algorithms:
            try:
                if algo == "base64":
                    result = self.base64_encode(password)
                elif algo == "md5":
                    result = self.md5(password)
                elif algo == "md5_upper":
                    result = self.md5_upper(password)
                elif algo == "sha1":
                    result = self.sha1(password)
                elif algo == "sha256":
                    result = self.sha256(password)
                elif algo == "sha512":
                    result = self.sha512(password)
                elif algo == "md5_md5":
                    result = self.md5_md5(password)
                elif algo == "md5_sha1":
                    result = self.md5_sha1(password)
                elif algo == "md5_salt":
                    result = self.md5_salt(password)
                elif algo == "sha256_salt":
                    result = self.sha256_salt(password)
                elif algo == "hmac_md5":
                    result = self.hmac_md5(password)
                elif algo == "hmac_sha256":
                    result = self.hmac_sha256(password)
                else:
                    continue

                results[algo] = result
                preview = result[:64] + ("..." if len(result) > 64 else "")
                print(f"{algo:20} -> {preview}")
            except Exception as exc:
                print(f"{algo:20} -> ERROR: {exc}")

        return results

    def guess_algorithm(self, encrypted_password: str) -> list[str]:
        print("\n[*] 尝试猜测加密算法")
        print("-" * 80)

        length = len(encrypted_password)
        is_hex = all(c in "0123456789abcdefABCDEF" for c in encrypted_password)
        clues: list[str] = []

        if length == 32 and is_hex:
            clues.append("可能是 MD5")
        elif length == 40 and is_hex:
            clues.append("可能是 SHA1")
        elif length == 64 and is_hex:
            clues.append("可能是 SHA256")
        elif length == 128 and is_hex:
            clues.append("可能是 SHA512")
        elif any(ch in encrypted_password for ch in "=+/"):
            clues.append("可能是 Base64")

        if encrypted_password.isupper():
            clues.append("加密结果为大写")
        elif encrypted_password.islower():
            clues.append("加密结果为小写")

        if clues:
            print("检测到的特征:")
            for clue in clues:
                print(f"  - {clue}")
        else:
            print("无法确定加密算法")

        return clues


def main() -> None:
    print("=" * 80)
    print("密码加密算法分析工具（本地演示）")
    print("=" * 80)

    analyzer = PasswordEncoderAnalyzer()
    analyzer.analyze_all("demo_password")
    analyzer.guess_algorithm("5f4dcc3b5aa765d61d8327deb882cf99")

    print("\n常用加密算法总结:")
    print("-" * 60)
    print("| 算法       | 输出长度 | 特征                     |")
    print("|-----------|---------|--------------------------|")
    print("| MD5       | 32位    | 纯十六进制               |")
    print("| SHA1      | 40位    | 纯十六进制               |")
    print("| SHA256    | 64位    | 纯十六进制               |")
    print("| SHA512    | 128位   | 纯十六进制               |")
    print("| Base64    | 变长    | 包含+/=字符              |")
    print("| HMAC-MD5  | 32位    | 需要密钥，纯十六进制      |")
    print("-" * 60)


if __name__ == "__main__":
    main()
