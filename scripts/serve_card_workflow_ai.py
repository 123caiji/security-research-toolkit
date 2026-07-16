# -*- coding: utf-8 -*-
"""Serve and execute the local card workflow AI tool."""
from __future__ import annotations

import argparse
import http.server
import json
import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 8788
CREATE_NEW_CONSOLE = 0x00000010 if sys.platform.startswith("win") else 0


class CardWorkflowHandler(http.server.SimpleHTTPRequestHandler):
    root_dir: Path

    def do_GET(self) -> None:
        if self.path.split("?", 1)[0] == "/api/tools":
            self._send_tools()
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path.split("?", 1)[0] == "/api/execute":
            self._execute_tool()
            return
        self.send_error(404, "Not found")

    def _send_tools(self) -> None:
        self._send_json(self._load_tools())

    def _execute_tool(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
            payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
        except Exception as exc:
            self._send_json({"ok": False, "error": f"invalid request json: {exc}"}, status=400)
            return

        tool_name = str(payload.get("toolName", "")).strip()
        target = str(payload.get("target", "")).strip()
        tools = self._load_tools()
        tool = self._find_registered_tool(tools, tool_name, target)
        if not tool:
            self._send_json({"ok": False, "error": "tool is not registered in config/tools.json"}, status=403)
            return

        ok, message, command = self._launch_registered_tool(tool)
        self._send_json({
            "ok": ok,
            "message": message,
            "command": command,
            "tool": {
                "name": tool.get("name", ""),
                "category": tool.get("category", ""),
                "type": tool.get("type", ""),
                "path": tool.get("path", ""),
                "url": tool.get("url", ""),
            },
        }, status=200 if ok else 500)

    def _load_tools(self) -> list[dict]:
        tools_file = self.root_dir / "config" / "tools.json"
        try:
            tools = json.loads(tools_file.read_text(encoding="utf-8"))
            return tools if isinstance(tools, list) else []
        except Exception:
            return []

    def _find_registered_tool(self, tools: list[dict], name: str, target: str) -> dict | None:
        target_norm = self._norm_target(target)
        if target_norm:
            for tool in tools:
                if not isinstance(tool, dict):
                    continue
                registered_target = str(tool.get("url") or tool.get("path") or "").strip()
                if self._norm_target(registered_target) == target_norm:
                    return tool
        for tool in tools:
            if not isinstance(tool, dict):
                continue
            if str(tool.get("name", "")).strip() != name:
                continue
            registered_target = str(tool.get("url") or tool.get("path") or "").strip()
            if not target_norm or self._norm_target(registered_target) == target_norm:
                return tool
        return None

    def _launch_registered_tool(self, tool: dict) -> tuple[bool, str, list[str] | str]:
        tool_type = str(tool.get("type", "")).strip()
        raw_path = str(tool.get("path", "")).strip()
        params = str(tool.get("params", "")).strip()
        url = str(tool.get("url", "")).strip()

        try:
            if tool_type == "网页":
                if not url:
                    return False, "registered web tool has no url", []
                webbrowser.open(url)
                return True, f"opened web tool: {url}", ["webbrowser.open", url]

            abs_path = self._resolve_tool_path(raw_path)
            if not abs_path:
                return False, "registered tool has no executable path", []
            if not self._is_inside_root(abs_path):
                return False, "tool path is outside local project root", []
            if not abs_path.exists():
                return False, f"tool path does not exist: {abs_path}", []

            if tool_type == "Python":
                python_exe = self._python_exe()
                command = [python_exe, str(abs_path)]
                if params:
                    command.extend(params.split())
                self._popen(command, cwd=abs_path.parent)
                return True, f"started python tool: {tool.get('name', '')}", command

            if tool_type.startswith("JAVA"):
                java_exe = self._java_exe("11" if "11" in tool_type else "8")
                command = [str(java_exe)]
                if params:
                    command.extend(params.split())
                command.extend(["-jar", str(abs_path)])
                self._popen(command, cwd=abs_path.parent)
                return True, f"started java tool: {tool.get('name', '')}", command

            if tool_type in {"GUI应用", "命令行", "批处理", "PowerShell"} or tool_type:
                if tool_type == "PowerShell":
                    command = ["powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", str(abs_path)]
                else:
                    command = [str(abs_path)]
                if params:
                    command.extend(params.split())
                self._popen(command, cwd=abs_path.parent)
                return True, f"started local tool: {tool.get('name', '')}", command

            return False, f"unsupported tool type: {tool_type}", []
        except Exception as exc:
            return False, str(exc), []

    def _popen(self, command: list[str], *, cwd: Path) -> None:
        if sys.platform.startswith("win"):
            subprocess.Popen(command, cwd=str(cwd), creationflags=CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(command, cwd=str(cwd))

    def _resolve_tool_path(self, raw_path: str) -> Path | None:
        if not raw_path:
            return None
        cleaned = raw_path.replace("\\", "/").strip()
        if cleaned.startswith("/tools/"):
            return (self.root_dir / cleaned.lstrip("/")).resolve()
        path = Path(raw_path)
        if path.is_absolute():
            return path.resolve()
        return (self.root_dir / path).resolve()

    def _is_inside_root(self, path: Path) -> bool:
        try:
            path.relative_to(self.root_dir.resolve())
            return True
        except ValueError:
            return False

    def _python_exe(self) -> str:
        local_python = self.root_dir / "python3" / "python.exe"
        if local_python.exists():
            return str(local_python)
        return sys.executable or "python"

    def _java_exe(self, version: str) -> Path:
        java_dir = self.root_dir / ("Java_path/Java_11_win/bin" if version == "11" else "Java_path/Java_8_win/bin")
        javaw = java_dir / "javaw.exe"
        java = java_dir / "java.exe"
        if javaw.exists():
            return javaw
        if java.exists():
            return java
        return Path("java")

    def _norm_target(self, value: str) -> str:
        if not value:
            return ""
        parsed = urlparse(value)
        if parsed.scheme in {"http", "https"}:
            return value.rstrip("/")
        return value.replace("\\", "/").strip().lower()

    def _send_json(self, data, *, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the local card workflow AI app.")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", default=PORT, type=int)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    web = root / "exports" / "card_workflow_ai"
    os.chdir(web)
    CardWorkflowHandler.root_dir = root
    httpd_cls = http.server.ThreadingHTTPServer
    httpd_cls.allow_reuse_address = True
    with httpd_cls((args.host, args.port), CardWorkflowHandler) as httpd:
        print(f"[OK] Card workflow AI: http://{args.host}:{args.port}/", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
