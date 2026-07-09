#!/usr/bin/env python3
"""
Синхронизация сессий MiMo Code → dashboard/sessions.json
+ отправка на удалённый сервер (если настроен)
+ коммит в GitHub (если настроен)
Запуск: python3 sync_sessions.py
"""

import os
import json
import re
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

SESSIONS_DIR = Path.home() / ".local/share/mimocode/memory/sessions"
OUTPUT_FILE = Path(__file__).parent / "sessions.json"
CONFIG_FILE = Path(__file__).parent / "sync_config.json"
REPO_DIR = Path(__file__).parent


def parse_checkpoint(filepath: str) -> dict:
    """Парсит checkpoint.md и возвращает структурированные данные."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    result = {
        "topic": "",
        "active_intent": "",
        "next_action": "",
        "current_work": "",
        "files_touched": [],
        "learnings": [],
        "errors": [],
    }

    # Topic (первая строка)
    topic_match = re.search(r"^Topic:\s*(.+)$", content, re.MULTILINE)
    if topic_match:
        result["topic"] = topic_match.group(1).strip()

    # Active intent
    intent_match = re.search(
        r"§1 Active intent.*?>\s*\"(.+?)\"", content, re.DOTALL
    )
    if intent_match:
        result["active_intent"] = intent_match.group(1).strip()[:200]

    # Next action
    action_match = re.search(r"§2 Next concrete action\s*\n(.+?)(?=\n##|\Z)", content, re.DOTALL)
    if action_match:
        text = action_match.group(1).strip()
        # Убираем markdown-ссылки и форматирование
        text = re.sub(r"_.*?_", "", text).strip()
        result["next_action"] = text[:300]

    # Current work
    work_match = re.search(r"§5 Current work\s*\n(.+?)(?=\n##|\Z)", content, re.DOTALL)
    if work_match:
        result["current_work"] = work_match.group(1).strip()[:500]

    # Files
    files_match = re.search(r"§6 Files and code sections\s*\n(.+?)(?=\n##|\Z)", content, re.DOTALL)
    if files_match:
        file_lines = files_match.group(1)
        for line in file_lines.split("\n"):
            file_match = re.search(r"`([^`]+)`", line)
            if file_match:
                result["files_touched"].append(file_match.group(1))

    # Learnings
    learn_match = re.search(r"§7 Discovered knowledge.*?\n(.+?)(?=\n##|\Z)", content, re.DOTALL)
    if learn_match:
        learn_text = learn_match.group(1)
        for line in learn_text.split("\n"):
            line = line.strip()
            if line.startswith("- **") or line.startswith("- "):
                learning = re.sub(r"^- ", "", line).strip()
                if learning:
                    result["learnings"].append(learning[:200])

    # Errors
    errors_match = re.search(r"§8 Errors and fixes\s*\n(.+?)(?=\n##|\Z)", content, re.DOTALL)
    if errors_match:
        for line in errors_match.group(1).split("\n"):
            line = line.strip()
            if line.startswith("- "):
                result["errors"].append(line[2:200])

    return result


def get_session_time(session_dir: str) -> str:
    """Получает время модификации checkpoint.md."""
    checkpoint = os.path.join(session_dir, "checkpoint.md")
    if os.path.exists(checkpoint):
        mtime = os.path.getmtime(checkpoint)
        return datetime.fromtimestamp(mtime).isoformat()
    return ""


def main():
    sessions = []

    if not SESSIONS_DIR.exists():
        print(f"Папка сессий не найдена: {SESSIONS_DIR}")
        return

    for session_name in sorted(os.listdir(SESSIONS_DIR)):
        session_path = os.path.join(SESSIONS_DIR, session_name)
        if not os.path.isdir(session_path):
            continue

        checkpoint_file = os.path.join(session_path, "checkpoint.md")
        if not os.path.exists(checkpoint_file):
            continue

        try:
            data = parse_checkpoint(checkpoint_file)
            data["id"] = session_name
            data["timestamp"] = get_session_time(session_path)
            data["files_count"] = len(data["files_touched"])
            sessions.append(data)
        except Exception as e:
            print(f"Ошибка чтения {session_name}: {e}")

    # Сортируем по времени (новые первые)
    sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    # Записываем
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

    print(f"Синхронизировано {len(sessions)} сессий → {OUTPUT_FILE}")

    # Отправка на удалённый сервер
    _push_to_remote(sessions)

    # Коммит в GitHub
    _git_commit()


def _push_to_remote(sessions):
    """Отправляет сессии на удалённый сервер (если настроен)."""
    if not CONFIG_FILE.exists():
        return

    try:
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        remote_url = config.get("remote_url", "")
    except (json.JSONDecodeError, OSError):
        return

    if not remote_url:
        return

    # Убираем trailing slash
    remote_url = remote_url.rstrip("/")

    try:
        data = json.dumps(sessions, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            f"{remote_url}/api/sync",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                print(f"✅ Отправлено на сервер: {remote_url}")
            else:
                print(f"⚠️ Сервер ответил {resp.status}")
    except urllib.error.URLError as e:
        print(f"⚠️ Не удалось отправить на сервер: {e}")
    except Exception as e:
        print(f"⚠️ Ошибка отправки: {e}")


def _git_commit():
    """Коммитит и пушит sessions.json + weekly-plan.md в GitHub."""
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True, text=True, cwd=str(REPO_DIR)
        )
        if "origin" not in result.stdout:
            return

        files_to_commit = []
        for f in ["sessions.json", "data/weekly-plan.md"]:
            diff = subprocess.run(
                ["git", "diff", "--quiet", f],
                capture_output=True, cwd=str(REPO_DIR)
            )
            if diff.returncode != 0:
                files_to_commit.append(f)

        status = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, cwd=str(REPO_DIR)
        )
        for f in ["sessions.json", "data/weekly-plan.md"]:
            if f in status.stdout and f not in files_to_commit:
                files_to_commit.append(f)

        if not files_to_commit:
            return

        for f in files_to_commit:
            subprocess.run(["git", "add", f], cwd=str(REPO_DIR), check=True)

        ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        subprocess.run(
            ["git", "commit", "-m", f"🔄 Auto-sync {ts}"],
            cwd=str(REPO_DIR), check=True
        )
        subprocess.run(["git", "push"], cwd=str(REPO_DIR), check=True)
        print(f"✅ Закоммичено: {', '.join(files_to_commit)}")
    except subprocess.CalledProcessError:
        pass
    except Exception as e:
        print(f"⚠️ Ошибка git: {e}")


if __name__ == "__main__":
    main()
