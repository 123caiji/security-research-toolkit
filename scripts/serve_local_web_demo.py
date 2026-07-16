# -*- coding: utf-8 -*-
"""
在固定端口启动只读 HTTP 服务，用于完全离线的 Web 演示页。

默认根目录：工程内 exports/local_web_demo/

用法
----
  python scripts/serve_local_web_demo.py

浏览器打开 http://127.0.0.1:8765/ ，另开终端执行：

  python scripts/download_spa_static_mirror.py --base-url http://127.0.0.1:8765/
"""
from __future__ import annotations

import http.server
import os
import socketserver
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8765


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    web = root / "exports" / "local_web_demo"
    web.mkdir(parents=True, exist_ok=True)
    os.chdir(web)
    handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), handler) as httpd:
        print(f"[OK] 根目录 {web}\n     http://{HOST}:{PORT}/  (Ctrl+C 停止)", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
