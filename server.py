#!/usr/bin/env python3
"""
TaskMaster Dashboard Server
Запуск: python3 server.py
Откроется на http://localhost:8080
"""

import json
import os
import subprocess
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TASKS_FILE = DATA_DIR / "tasks.json"
SESSIONS_FILE = BASE_DIR / "sessions.json"
PLAN_FILE = DATA_DIR / "weekly-plan.md"
SYNC_SCRIPT = BASE_DIR / "sync_sessions.py"

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/tasks":
            self._json_response(self._read_json(TASKS_FILE, []))
        elif path == "/api/sessions":
            self._sync_and_return_sessions()
        elif path == "/api/plan":
            self._text_response(self._read_text(PLAN_FILE, ""))
        elif path == "/manifest.json":
            self._json_response(self._read_json(BASE_DIR / "manifest.json", {}))
        elif path == "/sw.js":
            body = self._read_text(BASE_DIR / "sw.js", "").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.send_header("Service-Worker-Allowed", "/")
            self._cors_headers()
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/tasks":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                self._write_json(TASKS_FILE, data)
                self._json_response({"ok": True, "count": len(data)})
            except json.JSONDecodeError:
                self._json_response({"ok": False, "error": "Invalid JSON"}, 400)
        elif path == "/api/sync":
            # POST: принять сессии от клиента и сохранить
            length = int(self.headers.get("Content-Length", 0))
            if length > 0:
                body = self.rfile.read(length)
                try:
                    data = json.loads(body)
                    self._write_json(SESSIONS_FILE, data)
                    self._json_response({"ok": True, "count": len(data)})
                except json.JSONDecodeError:
                    self._json_response({"ok": False, "error": "Invalid JSON"}, 400)
            else:
                # Без тела — запустить локальную синхронизацию
                self._sync_and_return_sessions()
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def _json_response(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _text_response(self, text, status=200):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _read_json(self, path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def _write_json(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _read_text(self, path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return default

    def _sync_and_return_sessions(self):
        if SYNC_SCRIPT.exists():
            try:
                subprocess.run(
                    [sys.executable, str(SYNC_SCRIPT)],
                    capture_output=True, timeout=10
                )
            except Exception:
                pass
        sessions = self._read_json(SESSIONS_FILE, [])
        self._json_response(sessions)

    def log_message(self, format, *args):
        # Quieter logging
        if "/api/" in str(args[0]) if args else False:
            return
        super().log_message(format, *args)


def main():
    DATA_DIR.mkdir(exist_ok=True)
    if not TASKS_FILE.exists():
        TASKS_FILE.write_text("[]", encoding="utf-8")

    server = HTTPServer(("0.0.0.0", PORT), DashboardHandler)
    print(f"✨ TaskMaster Dashboard запущен:")
    print(f"   http://localhost:{PORT}")
    print(f"   http://127.0.0.1:{PORT}")
    print(f"   Задачи: {TASKS_FILE}")
    print(f"   Нажми Ctrl+C для остановки")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
        server.server_close()


if __name__ == "__main__":
    main()
