#!/usr/bin/env python3
"""
Автосинхронизация сессий MiMo Code → GitHub
Запуск: python3 auto_sync.py (или двойной клик по start_sync.bat)
Остановка: stop_sync.bat
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

DIR = Path(__file__).parent
SYNC_SCRIPT = DIR / "sync_sessions.py"
PID_FILE = DIR / "auto_sync.pid"
LOG_FILE = DIR / "sync.log"
INTERVAL = 600  # 10 минут


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def write_pid():
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")


def remove_pid():
    if PID_FILE.exists():
        PID_FILE.unlink()


def is_running():
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, ValueError):
        return False


def sync():
    try:
        result = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT)],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout.strip()
        if result.returncode == 0:
            log(f"OK: {output}")
        else:
            log(f"ERROR: {result.stderr.strip()}")
    except Exception as e:
        log(f"EXCEPTION: {e}")


def main():
    if is_running():
        print("Уже запущен! Останови через stop_sync.bat")
        return

    write_pid()
    log("Автосинхронизация запущена (каждые 10 минут)")

    try:
        while True:
            sync()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        log("Остановлен пользователем")
    finally:
        remove_pid()


if __name__ == "__main__":
    main()
