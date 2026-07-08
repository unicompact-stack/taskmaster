# Автосинхронизация через GitHub

## Как это работает

```
Ты общаешься с MiMo → checkpoint.md
→ cron (каждые 5 мин) → sync_sessions.py
→ коммитит sessions.json в GitHub
→ дашборд на GitHub Pages читает из репозитория
```

## Настройка (один раз)

### 1. Создай репозиторий на GitHub

1. Заходишь на **github.com**
2. **New repository** → имя: `taskmaster` (или любое)
3. **Public** (для бесплатного GitHub Pages)
4. Заливаешь папку `dashboard/` через drag-and-drop

### 2. Включи GitHub Pages

1. В репозитории: **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** / `/ (root)`
4. Сохрани
5. Через минуту сайт живёт по адресу `https://твоё-имя.github.io/taskmaster/`

### 3. Настрой cron на своём компьютере

Открой терминал, выполни:
```bash
crontab -e
```

Добавь строку:
```
*/5 * * * * cd "/mnt/c/Users/User/Pictures/ВС код/dashboard" && python3 sync_sessions.py >> sync.log 2>&1
```

Сохрани (Ctrl+O, Enter, Ctrl+X).

### 4. Обнови GITHUB_RAW в index.html

В `index.html` найди строку:
```javascript
const GITHUB_RAW = 'https://raw.githubusercontent.com/taskmaster/main/sessions.json';
```

Замени `taskmaster` на имя своего репозитория.

### 5. Запусти первую синхронизацию

```bash
cd "/mnt/c/Users/User/Pictures/ВС код/dashboard"
python3 sync_sessions.py
git add sessions.json
git commit -m "Initial sessions sync"
git push
```

Готово! Теперь каждые 5 минут сессии обновляются автоматически.

## Что работает

- Дашборд на GitHub Pages — полностью бесплатно
- Сессии MiMo — синхронизируются каждые 5 минут
- Задачи — в localStorage (каждое устройство отдельно)
- Календарь, чат-бот, голос — всё работает

## Что НЕ работает

- API-эндпоинты (server.py не запущен) — задачи только в localStorage
- Импорт плана из weekly-plan.md (нужен server.py)
