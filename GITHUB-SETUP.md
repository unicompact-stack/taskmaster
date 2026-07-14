# GitHub Setup — шаблон для новых проектов

## Токен
Смотри `.env` файл или спроси у MiMo Code.

## Настройка нового репозитория

```bash
# 1. Инициализация
cd /путь/к/проекту
git init
git remote add origin https://github.com/unicompact-stack/ИМЯ_РЕПО.git
git config user.name "TaskMaster Bot"
git config user.email "bot@taskmaster.local"

# 2. Авторизация (один раз)
git config credential.helper store
# При первом push ввести логин и токен

# 3. Первый коммит
git add .
git commit -m "🚀 Initial commit"
git push -u origin main

# 4. GitHub Pages (если нужен сайт)
# Settings → Pages → Deploy from branch → main → / (root)
```

## Быстрый доступ
- GitHub: https://github.com/unicompact-stack
- Текущий дашборд: https://unicompact-stack.github.io/taskmaster/
