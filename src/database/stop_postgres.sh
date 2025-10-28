#!/bin/bash

# Скрипт для остановки PostgreSQL на порту 5433
# Использование: ./stop_postgres.sh

echo "🛑 Остановка PostgreSQL на порту 5433..."

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Проверяем, запущен ли PostgreSQL
if pg_ctl -D DB_BASE/vkinder_cluster status > /dev/null 2>&1; then
    echo "🔄 Останавливаем PostgreSQL..."
    pg_ctl -D DB_BASE/vkinder_cluster stop
    
    if [ $? -eq 0 ]; then
        echo "✅ PostgreSQL успешно остановлен"
    else
        echo "❌ Ошибка остановки PostgreSQL"
        exit 1
    fi
else
    echo "ℹ️ PostgreSQL не запущен на порту 5433"
fi
