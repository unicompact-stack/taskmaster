#!/usr/bin/env python3
"""Создание бэкапа tasks.json с датой в имени."""
import json, shutil, os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
TASKS_FILE = os.path.join(DATA_DIR, 'tasks.json')

def backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    dest = os.path.join(BACKUP_DIR, f'tasks_{ts}.json')
    shutil.copy2(TASKS_FILE, dest)
    print(f'✅ Бэкап создан: {dest}')

def restore(backup_file):
    if not os.path.exists(backup_file):
        print(f'❌ Файл не найден: {backup_file}')
        return
    with open(backup_file) as f:
        data = json.load(f)
    if not isinstance(data, list):
        print('❌ Неверный формат: ожидается список задач')
        return
    shutil.copy2(TASKS_FILE, TASKS_FILE + '.before-restore')
    with open(TASKS_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'✅ Восстановлено {len(data)} задач из {backup_file}')

def list_backups():
    if not os.path.exists(BACKUP_DIR):
        print('Бэкапов нет')
        return
    files = sorted(os.listdir(BACKUP_DIR))
    for f in files:
        print(f'  📄 {f}')

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        backup()
    elif sys.argv[1] == 'list':
        list_backups()
    elif sys.argv[1] == 'restore' and len(sys.argv) > 2:
        restore(sys.argv[2])
    else:
        print('Использование:')
        print('  python3 backup.py          — создать бэкап')
        print('  python3 backup.py list     — список бэкапов')
        print('  python3 backup.py restore <файл> — восстановить')
