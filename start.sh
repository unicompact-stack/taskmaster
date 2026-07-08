#!/bin/bash
# Запуск дашборда с автосинхронизацией сессий MiMo Code
# Использование: bash dashboard/start.sh

cd "$(dirname "$0")"

echo "🚀 Запуск дашборда..."
echo "📊 Дашборд: http://localhost:8080"
echo "🔄 Автосинхронизация: каждые 30 сек"
echo "⛔ Остановка: Ctrl+C"
echo ""

# Первая синхронизация
echo "⏳ Первая синхронизация..."
python3 sync_sessions.py

# Фоновый процесс: синхронизация каждые 30 сек
(
  while true; do
    sleep 30
    python3 sync_sessions.py > /dev/null 2>&1
  done
) &
SYNC_PID=$!
echo "✅ Синхронизация запущена (PID: $SYNC_PID)"

# Запуск HTTP-сервера (server.py с API)
echo ""
python3 server.py 8080

# При завершении убиваем фоновый процесс
kill $SYNC_PID 2>/dev/null
