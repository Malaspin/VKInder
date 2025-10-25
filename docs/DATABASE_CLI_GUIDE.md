# 🖥️ Руководство по CLI базы данных VKinder Bot

## 📋 Описание

CLI (Command Line Interface) для управления базой данных PostgreSQL в проекте VKinder Bot. Предоставляет полный набор команд для создания, управления, мониторинга и диагностики базы данных.

## 🚀 Быстрый старт

### Установка и настройка
```bash
# Перейдите в директорию проекта
cd /path/to/VKinder_Bot_Connect_Search

# Активируйте виртуальное окружение
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt
```

### Первый запуск
```bash
# Создайте таблицы базы данных
python src/database/db_cli.py create

# Проверьте статус
python src/database/db_cli.py info
```

## 📚 Полный справочник команд

### 🏗️ Управление структурой базы данных

#### `create` - Создание таблиц
```bash
python src/database/db_cli.py create
```
**Описание:** Создает все таблицы базы данных согласно моделям SQLAlchemy.

**Что создается:**
- `vk_users` - Пользователи VK
- `photos` - Фотографии пользователей
- `favorites` - Избранные пользователи
- `blacklisted` - Черный список
- `search_history` - История поиска
- `user_settings` - Настройки пользователей
- `bot_logs` - Логи системы
- `bot_messages` - Сообщения бота

**Пример вывода:**
```
🔨 Создание таблиц базы данных...
✅ Таблицы созданы успешно
```

#### `drop` - Удаление всех таблиц
```bash
python src/database/db_cli.py drop
```
**Описание:** Удаляет все таблицы базы данных (с подтверждением).

**⚠️ ВНИМАНИЕ:** Эта команда удаляет ВСЕ данные!

**Пример использования:**
```
🗑️ Удаление всех таблиц...
⚠️  Вы уверены? Это удалит ВСЕ данные! (yes/no): yes
✅ Таблицы удалены успешно
```

### 🧹 Управление данными

#### `clear <table_name>` - Очистка конкретной таблицы
```bash
python src/database/db_cli.py clear <table_name>
```

**Доступные таблицы:**
- `vk_users` - Пользователи
- `photos` - Фотографии
- `favorites` - Избранное
- `blacklisted` - Черный список
- `search_history` - История поиска
- `user_settings` - Настройки
- `bot_logs` - Логи
- `bot_messages` - Сообщения

**Примеры:**
```bash
# Очистка логов
python src/database/db_cli.py clear bot_logs

# Очистка сообщений
python src/database/db_cli.py clear bot_messages

# Очистка пользователей
python src/database/db_cli.py clear vk_users
```

#### `clear-all` - Очистка всех таблиц
```bash
python src/database/db_cli.py clear-all
```
**Описание:** Очищает все таблицы базы данных (с подтверждением).

**⚠️ ВНИМАНИЕ:** Эта команда удаляет ВСЕ данные из всех таблиц!

### 📊 Мониторинг и диагностика

#### `info` - Информация о базе данных
```bash
python src/database/db_cli.py info
```
**Описание:** Показывает подробную информацию о всех таблицах базы данных.

**Выводимая информация:**
- Количество записей в каждой таблице
- Модель SQLAlchemy для каждой таблицы
- Статус подключения к базе данных

**Пример вывода:**
```
📊 Информация о базе данных:
==================================================
📋 Всего таблиц: 8

  📄 vk_users
     - Записей: 25
     - Модель: VKUser

  📄 photos
     - Записей: 150
     - Модель: Photo

  📄 favorites
     - Записей: 15
     - Модель: Favorite
```

#### `logs` - Просмотр логов
```bash
python src/database/db_cli.py logs [опции]
```

**Опции:**
- `--user <user_id>` - Логи конкретного пользователя
- `--level <level>` - Фильтр по уровню (DEBUG, INFO, WARNING, ERROR)
- `--limit <n>` - Количество записей (по умолчанию 50)

**Примеры:**
```bash
# Все логи (последние 50)
python src/database/db_cli.py logs

# Логи конкретного пользователя
python src/database/db_cli.py logs --user 123456789

# Только ошибки
python src/database/db_cli.py logs --level ERROR --limit 10

# Последние 20 записей
python src/database/db_cli.py logs --limit 20
```

#### `messages <user_id>` - Сообщения пользователя
```bash
python src/database/db_cli.py messages <user_id> [опции]
```

**Опции:**
- `--limit <n>` - Количество сообщений (по умолчанию 50)

**Примеры:**
```bash
# Сообщения пользователя
python src/database/db_cli.py messages 123456789

# Последние 20 сообщений
python src/database/db_cli.py messages 123456789 --limit 20
```

#### `favorites <user_id>` - Избранные пользователя
```bash
python src/database/db_cli.py favorites <user_id>
```

**Описание:** Показывает список избранных пользователей для указанного пользователя.

**Пример:**
```bash
python src/database/db_cli.py favorites 123456789
```

### 🧪 Тестирование

#### `test-data` - Добавление тестовых данных
```bash
python src/database/db_cli.py test-data
```

**Описание:** Добавляет тестовые данные в базу для проверки работы системы.

**Что добавляется:**
- Тестовые пользователи
- Тестовые сообщения
- Тестовые логи

**Пример вывода:**
```
🧪 Добавление тестовых данных...
✅ Тестовые данные добавлены успешно
```

## 🐘 Управление PostgreSQL

### Команды PostgreSQL

#### `postgres-start` - Запуск PostgreSQL
```bash
python src/database/db_cli.py postgres-start
```
**Описание:** Запускает PostgreSQL сервер через Homebrew.

**Пример вывода:**
```
🚀 Запуск PostgreSQL...
✅ PostgreSQL запущен успешно
```

#### `postgres-stop` - Остановка PostgreSQL
```bash
python src/database/db_cli.py postgres-stop
```
**Описание:** Останавливает PostgreSQL сервер.

#### `postgres-restart` - Перезапуск PostgreSQL
```bash
python src/database/db_cli.py postgres-restart
```
**Описание:** Перезапускает PostgreSQL сервер.

#### `postgres-status` - Статус PostgreSQL
```bash
python src/database/db_cli.py postgres-status
```
**Описание:** Показывает текущий статус PostgreSQL сервера.

**Пример вывода:**
```
📊 Статус PostgreSQL:
✅ PostgreSQL запущен и доступен
🕒 Время работы: 2 часа 15 минут
💾 Использование памяти: 45 MB
```

#### `postgres-info` - Информация о PostgreSQL
```bash
python src/database/db_cli.py postgres-info
```
**Описание:** Показывает подробную информацию о PostgreSQL.

**Выводимая информация:**
- Версия PostgreSQL
- Путь к исполняемому файлу
- Порт подключения
- Статус сервера
- Информация о базе данных

## 🔧 Практические примеры

### Сценарий 1: Первоначальная настройка
```bash
# 1. Создание таблиц
python src/database/db_cli.py create

# 2. Проверка статуса
python src/database/db_cli.py info

# 3. Добавление тестовых данных
python src/database/db_cli.py test-data
```

### Сценарий 2: Очистка и перезапуск
```bash
# 1. Очистка всех данных
python src/database/db_cli.py clear-all

# 2. Пересоздание таблиц
python src/database/db_cli.py drop
python src/database/db_cli.py create

# 3. Проверка результата
python src/database/db_cli.py info
```

### Сценарий 3: Диагностика проблем
```bash
# 1. Проверка статуса PostgreSQL
python src/database/db_cli.py postgres-status

# 2. Просмотр ошибок в логах
python src/database/db_cli.py logs --level ERROR --limit 10

# 3. Проверка информации о БД
python src/database/db_cli.py info
```

### Сценарий 4: Мониторинг работы
```bash
# 1. Общая статистика
python src/database/db_cli.py info

# 2. Последние логи
python src/database/db_cli.py logs --limit 20

# 3. Сообщения пользователя
python src/database/db_cli.py messages 123456789 --limit 10
```

## 🚨 Устранение неполадок

### Частые проблемы и решения

#### 1. Ошибка подключения к базе данных
```bash
# Проверьте статус PostgreSQL
python src/database/db_cli.py postgres-status

# Если не запущен, запустите
python src/database/db_cli.py postgres-start
```

#### 2. Ошибка "table does not exist"
```bash
# Создайте таблицы
python src/database/db_cli.py create
```

#### 3. Ошибка "database does not exist"
```bash
# PostgreSQL должен быть запущен
python src/database/db_cli.py postgres-start

# Затем создайте таблицы
python src/database/db_cli.py create
```

#### 4. Проблемы с правами доступа
```bash
# Проверьте настройки в .env файле
cat .env

# Убедитесь, что PostgreSQL запущен
python src/database/db_cli.py postgres-status
```

### Диагностические команды

```bash
# Полная диагностика системы
python src/database/db_cli.py postgres-info
python src/database/db_cli.py info
python src/database/db_cli.py logs --level ERROR --limit 5
```

## 📋 Справочная таблица команд

| Команда | Параметры | Описание | Пример |
|---------|-----------|----------|--------|
| `create` | - | Создание всех таблиц | `python src/database/db_cli.py create` |
| `drop` | - | Удаление всех таблиц | `python src/database/db_cli.py drop` |
| `clear <table>` | `table` - название таблицы | Очистка таблицы | `python src/database/db_cli.py clear bot_logs` |
| `clear-all` | - | Очистка всех таблиц | `python src/database/db_cli.py clear-all` |
| `info` | - | Информация о БД | `python src/database/db_cli.py info` |
| `logs` | `--user <id>`, `--level <level>`, `--limit <n>` | Просмотр логов | `python src/database/db_cli.py logs --level ERROR` |
| `messages <user_id>` | `--limit <n>` | Сообщения пользователя | `python src/database/db_cli.py messages 123456` |
| `favorites <user_id>` | - | Избранные пользователя | `python src/database/db_cli.py favorites 123456` |
| `test-data` | - | Тестовые данные | `python src/database/db_cli.py test-data` |
| `postgres-start` | - | Запуск PostgreSQL | `python src/database/db_cli.py postgres-start` |
| `postgres-stop` | - | Остановка PostgreSQL | `python src/database/db_cli.py postgres-stop` |
| `postgres-restart` | - | Перезапуск PostgreSQL | `python src/database/db_cli.py postgres-restart` |
| `postgres-status` | - | Статус PostgreSQL | `python src/database/db_cli.py postgres-status` |
| `postgres-info` | - | Информация о PostgreSQL | `python src/database/db_cli.py postgres-info` |

## 🔗 Связанная документация

- **[DATABASE_API_GUIDE.md](DATABASE_API_GUIDE.md)** - Руководство по API базы данных
- **[README_BD.md](README_BD.md)** - Общая документация по базе данных
- **[README_BOT.md](README_BOT.md)** - Документация по боту

## 💡 Советы по использованию

### 1. **Регулярное обслуживание**
```bash
# Еженедельная очистка логов
python src/database/db_cli.py clear bot_logs

# Проверка статуса системы
python src/database/db_cli.py info
```

### 2. **Мониторинг производительности**
```bash
# Просмотр статистики
python src/database/db_cli.py info

# Анализ ошибок
python src/database/db_cli.py logs --level ERROR --limit 20
```

### 3. **Безопасность**
- Всегда делайте резервные копии перед `drop` или `clear-all`
- Используйте `--limit` для больших таблиц
- Проверяйте статус PostgreSQL перед операциями

### 4. **Отладка**
```bash
# Полная диагностика
python src/database/db_cli.py postgres-info
python src/database/db_cli.py info
python src/database/db_cli.py logs --level ERROR
```
