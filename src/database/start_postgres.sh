#!/bin/bash

# Скрипт для запуска PostgreSQL на порту 5433
# Использование: ./start_postgres.sh

echo "🚀 Запуск PostgreSQL на порту 5433..."

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Проверяем, запущен ли уже PostgreSQL
if pg_ctl -D DB_BASE/vkinder_cluster status > /dev/null 2>&1; then
    echo "✅ PostgreSQL уже запущен на порту 5433"
    echo "📊 Статус:"
    pg_ctl -D DB_BASE/vkinder_cluster status
else
    echo "🔄 Запускаем PostgreSQL..."
    pg_ctl -D DB_BASE/vkinder_cluster -l DB_BASE/vkinder_cluster/logfile start
    
    if [ $? -eq 0 ]; then
        echo "✅ PostgreSQL успешно запущен на порту 5433"
        echo ""
        echo "📋 Параметры подключения для DBeaver:"
        echo "   Host: localhost"
        echo "   Port: 5433"
        echo "   Database: vkinder_db"
        echo "   Username: vkinder_user"
        echo "   Password: vkinder123"
        echo ""
        echo "🔗 Теперь вы можете подключиться к базе данных!"
    else
        echo "❌ Ошибка запуска PostgreSQL"
        echo "📋 Проверьте логи: tail -f DB_BASE/vkinder_cluster/logfile"
        exit 1
    fi
fi
