# Инструкция: Deploy дашборда на Render.com

## Шаг 1: Регистрация

1. Открой браузер
2. Перейди на **https://dashboard.render.com**
3. Нажми **"Get Started for Free"**
4. Выбери **"GitHub"** — войди через аккаунт GitHub
5. Разреши доступ к репозиториям

## Шаг 2: Загрузка на GitHub

1. Заходишь на **https://github.com**
2. Нажми **"New repository"** (кнопка "+" в правом верхнем углу)
3. Имя: `taskmaster` (или любое)
4. **Public** или **Private** — неважно
5. Нажми **"Create repository"**
6. Нажми **"uploading an existing file"**
7. Перетащи **всю папку `dashboard/`** в область загрузки
8. Нажми **"Commit changes"**

## Шаг 3: Создание сервиса на Render

1. Заходишь на **https://dashboard.render.com**
2. Нажми **"New +"** → **"Web Service"**
3. Выбери репозиторий `taskmaster`
4. Настройки:
   - **Name:** `taskmaster` (или любое)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt` (если нет — оставь пустым)
   - **Start Command:** `python3 server.py`
   - **Port:** `8080`
5. Нажми **"Create Web Service"**

## Шаг 4: Ожидание

1. Render собирает и запускает (~2-3 минуты)
2. Когда статус станет **"Live"** — скопируй ссылку (вид: `https://taskmaster-xxxxx.onrender.com`)
3. Открой в браузере — дашборд работает

## Шаг 5: Автосинхронизация (cron)

После деплоя получишь ссылку вида `https://taskmaster-xxxxx.onrender.com`.

Теперь настрой автосинхронизацию:

1. Открой файл `dashboard/sync_config.json`
2. Впиши адрес сервера:
   ```json
   {"remote_url": "https://taskmaster-xxxxx.onrender.com"}
   ```
3. Сохрани

Запусти cron (синхронизация каждые 5 минут):
```bash
crontab -e
```
Добавь строку:
```
*/5 * * * * cd "/mnt/c/Users/User/Pictures/ВС код/dashboard" && python3 sync_sessions.py >> sync.log 2>&1
```

Сохрани (Ctrl+O, Enter, Ctrl+X).

Готово — сессии синхронизируются автоматически каждые 5 минут.

## Шаг 6: Открытие с телефона

1. На телефоне открой браузер
2. Вставь ссылку в адресную строку
3. Дашборд загружен и работает

## Важно

- Первый запуск после простоя может занять ~30 сек (Render "засыпает")
- Бесплатный тариф: 750 часов/мес, хватит на 24/7
- Данные задач хранятся в `data/tasks.json` на сервере
- Сессии MiMo синхронизируются автоматически

## Готово!

Дашборд доступен по ссылке с любого устройства.
