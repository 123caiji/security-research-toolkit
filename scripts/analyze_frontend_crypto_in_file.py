# -*- coding: utf-8 -*-
"""
对「本地已保存」的前端 JS 文件做密码/加密相关静态扫描（不联网、不访问任何 URL）。

用法：
  python scripts/analyze_frontend_crypto_in_file.py path/to/saved_chunk.js

典型用途（授权环境内）：
  1. 浏览器 Sources 中另存为 app.*.js / chunk-vendors.*.js 到本机；
  2. 将绝对路径作为参数传入本脚本；
  3. 根据输出关键字在 IDE 中继续人工确认。

禁止：将本脚本用于未授权目标的自动爬取或批量拉取 JS。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# 关键字与说明（教学/审计用）
PATTERNS: list[tuple[str, str]] = [
    (r"login|/api/submit|/api/login", "提交/登录请求相关字符串"),
    (r"password|passwd|pwd", "密码字段命名"),
    (r"encrypt|decrypt|cipher", "加解密通用词"),
    (r"CryptoJS|crypto-js", "CryptoJS 库"),
    (r"JSEncrypt|jsencrypt", "RSA 常见库"),
    (r"RSA|OAEP|PKCS", "RSA 相关"),
    (r"md5|MD5", "MD5"),
    (r"sha1|SHA-?1|sha256|SHA-?256", "SHA 族"),
    (r"btoa|atob|Base64", "Base64"),
    (r"subtle\.|crypto\.subtle", "Web Crypto API"),
    (r"publicKey|privateKey|setPublicKey", "RSA 密钥配置常见命名"),
    (r"axios\.(post|create)|fetch\(", "HTTP 客户端"),
]


def main() -> None:
    if len(sys.argv) < 2:
        print("用法: python scripts/analyze_frontend_crypto_in_file.py <本地.js文件路径>", file=sys.stderr)
        sys.exit(2)
    p = Path(sys.argv[1]).resolve()
    if not p.is_file():
        print(f"[ERR] 不是文件: {p}", file=sys.stderr)
        sys.exit(1)
    text = p.read_text(encoding="utf-8", errors="replace")
    print(f"[FILE] {p}  ({len(text)} chars)\n")

    for pat, desc in PATTERNS:
        rx = re.compile(pat, re.IGNORECASE)
        hits = list(rx.finditer(text))
        print(f"## {desc}  (`{pat}`)  — 命中 {len(hits)} 次")
        shown = 0
        for m in hits[:12]:
            a = max(0, m.start() - 60)
            b = min(len(text), m.end() + 80)
            snippet = text[a:b].replace("\n", " ")
            print(f"  ... {snippet} ...")
            shown += 1
        if len(hits) > shown:
            print(f"  ... 其余 {len(hits) - shown} 处略")
        print("")


if __name__ == "__main__":
    main()
