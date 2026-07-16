# -*- coding: utf-8 -*-
"""
从 SPA 入口页抓取 index.html 及同站引用的 JS/CSS，保存到本工程目录（低速、可审计）。

典型场景
--------
- **本地演示**：`http://127.0.0.1:8765/`（配合 `serve_local_web_demo.py`）无需额外开关。
- **授权内网/竞赛靶标**：显式传入 `--base-url`，并加 `--i-confirm-authorized-target`。

合规
----
- 默认拒绝向「非本机」地址下载，除非带上 `--i-confirm-authorized-target`（表示你已完成书面/清单授权自检）。
- 同一主机请求之间默认 sleep，避免高频拉取静态资源。

用法
----
  python scripts/download_spa_static_mirror.py --base-url http://127.0.0.1:8765/
  python scripts/download_spa_static_mirror.py --base-url https://x.example.com/ --i-confirm-authorized-target

后续
----
  python scripts/analyze_frontend_crypto_in_file.py <下载目录中的某个.js>
"""
from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SCRIPT_RE = re.compile(
    r"""<script[^>]+src\s*=\s*(?P<q>['"])(?P<src>[^'"]+)(?P=q)""",
    re.IGNORECASE,
)
LINK_CSS_RE = re.compile(
    r"""<link[^>]+href\s*=\s*(?P<q>['"])(?P<href>[^'"]+\.css[^'"]*)(?P=q)""",
    re.IGNORECASE,
)


def _is_loopback(url: str) -> bool:
    try:
        p = urllib.parse.urlparse(url)
        host = (p.hostname or "").lower()
        return host in ("127.0.0.1", "localhost", "::1")
    except Exception:
        return False


def _fetch(url: str, timeout: float = 30.0) -> tuple[bytes, str | None]:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "spa-static-mirror/1.0 (local lab)"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        raw = resp.read()
        ctype = resp.headers.get("Content-Type")
    return raw, ctype


def _same_site(base: urllib.parse.ParseResult, target: urllib.parse.ParseResult) -> bool:
    if not target.netloc:
        return True
    return (target.hostname or "").lower() == (base.hostname or "").lower()


def _local_name(url: str) -> str:
    path = urllib.parse.urlparse(url).path or "/"
    if path in ("/", ""):
        return "index.html"
    name = path.rstrip("/").split("/")[-1] or "index.html"
    if "." not in name:
        return name + ".bin"
    return name


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description="Mirror SPA index + same-origin JS/CSS into project folder.")
    ap.add_argument("--base-url", required=True, help="入口 URL，须以 / 结尾或可接受自动补全")
    ap.add_argument(
        "--out-dir",
        default="",
        help="输出目录（默认 exports/local_mirrors_spa/<host>_<port>/）",
    )
    ap.add_argument("--max-files", type=int, default=32, help="最多下载多少个资源（含 index.html）")
    ap.add_argument("--delay", type=float, default=0.5, help="每次 HTTP 请求间隔秒数")
    ap.add_argument("--include-css", action="store_true", help="同时下载 link rel=stylesheet 的 .css")
    ap.add_argument(
        "--allow-external-cdn",
        action="store_true",
        help="允许下载与 base 不同主机的 script/link（默认仅同主机）",
    )
    ap.add_argument(
        "--i-confirm-authorized-target",
        action="store_true",
        help="确认当前 base-url 已在指挥部/清单授权内（非本机时必须）",
    )
    args = ap.parse_args()

    base_url = args.base_url.strip()
    if not base_url.endswith("/"):
        base_url += "/"
    base = urllib.parse.urlparse(base_url)
    if base.scheme not in ("http", "https") or not base.hostname:
        print("[ERR] base-url 须为 http(s) 且含主机名", file=sys.stderr)
        return 2

    if not _is_loopback(base_url) and not args.i_confirm_authorized_target:
        print(
            "[ERR] 对非本机地址下载须加 --i-confirm-authorized-target（并完成书面授权自检）。",
            file=sys.stderr,
        )
        return 2

    if args.out_dir:
        out = Path(args.out_dir).resolve()
    else:
        slug_host = re.sub(r"[^\w\-.]+", "_", base.hostname or "host")
        port = base.port or (443 if base.scheme == "https" else 80)
        out = root / "exports" / "local_mirrors_spa" / f"{slug_host}_{port}"
    out.mkdir(parents=True, exist_ok=True)

    manifest: list[dict] = []

    def save(url: str, data: bytes) -> Path:
        fname = _local_name(url)
        dest = out / fname
        if dest.exists():
            stem, suf = dest.stem, dest.suffix
            for i in range(1, 1000):
                cand = out / f"{stem}_{i}{suf}"
                if not cand.exists():
                    dest = cand
                    break
        dest.write_bytes(data)
        manifest.append({"url": url, "path": str(dest.relative_to(root))})
        return dest

    # 1) index
    try:
        html_bytes, _ = _fetch(base_url)
    except urllib.error.HTTPError as e:
        print(f"[ERR] GET {base_url} -> HTTP {e.code}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERR] GET {base_url} -> {e}", file=sys.stderr)
        return 1

    save(base_url, html_bytes)
    html = html_bytes.decode("utf-8", errors="replace")

    urls: list[str] = []
    for m in SCRIPT_RE.finditer(html):
        u = urllib.parse.urljoin(base_url, m.group("src").strip())
        urls.append(u)
    if args.include_css:
        for m in LINK_CSS_RE.finditer(html):
            u = urllib.parse.urljoin(base_url, m.group("href").strip())
            urls.append(u)

    seen: set[str] = set()
    deduped: list[str] = []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        deduped.append(u)

    count = 1
    for u in deduped:
        if count >= args.max_files:
            break
        pu = urllib.parse.urlparse(u)
        if not args.allow_external_cdn and not _same_site(base, pu):
            continue
        time.sleep(max(0.0, args.delay))
        try:
            data, _ = _fetch(u)
        except Exception as e:
            manifest.append({"url": u, "error": str(e)})
            continue
        save(u, data)
        count += 1

    meta = {
        "base_url": base_url,
        "out_dir": str(out.relative_to(root)),
        "max_files": args.max_files,
        "delay_s": args.delay,
        "include_css": args.include_css,
        "allow_external_cdn": args.allow_external_cdn,
    }
    (out / "MANIFEST.json").write_text(
        json.dumps({"meta": meta, "assets": manifest}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] 已写入 {out} ，共 {len(manifest)} 条记录（见 MANIFEST.json）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
