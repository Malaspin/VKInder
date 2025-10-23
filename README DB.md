# 🗄️ Система управления базой данных PostgreSQL для VKinder Bot

## 📋 Описание

Полноценная система для работы с базой данных PostgreSQL, включающая:
- **Интерфейс базы данных** - основной класс для работы с БД
- **CLI интерфейс** - командная строка для управления БД
- **API** - простые функции для интеграции с кодом
- **Автоматический запуск PostgreSQL**
- **Документация** - подробные руководства и примеры

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка базы данных
```bash
# Создайте файл .env с настройками БД
cp env.example .env
# Отредактируйте .env файл
```

### 3. Автоматический запуск PostgreSQL
```bash
# PostgreSQL запустится автоматически при первом использовании
# Или запустите вручную:
python db_cli.py postgres-start
```

### 4. Создание таблиц
```bash
python db_cli.py create
```

### 5. Запуск примеров
```bash
python database_examples.py
```

### 6. Просмотр информации о БД
```bash
python db_cli.py info
```

## 📁 Структура проекта

```
├── database_interface.py          # Основной интерфейс БД
├── db_api.py                      # API для интеграции
├── db_cli.py                      # CLI интерфейс
├── database_examples.py           # Примеры использования
├── test_database_simulation.py    # Тестовая симуляция
├── requirements.txt               # Зависимости
├── .env                          # Настройки БД
├── env.example                   # Пример настроек
├── .gitignore                    # Исключения Git
└── README.md                     # Документация
```

## 🔧 Основные компоненты

### DatabaseInterface
Основной класс для работы с PostgreSQL:
- Подключение к базе данных
- CRUD операции
- Управление таблицами
- Обработка ошибок
- **Автоматический запуск PostgreSQL**

### PostgreSQLManager
Менеджер для управления PostgreSQL:
- Проверка статуса PostgreSQL
- Автоматический запуск через Homebrew
- Создание базы данных
- Получение информации о PostgreSQL

### CLI интерфейс (db_cli.py)
Командная строка для управления БД:

#### Основные команды
```bash
# Информация о БД
python db_cli.py info

# Создание таблиц
python db_cli.py create

# Удаление всех таблиц (с подтверждением)
python db_cli.py drop

# Очистка конкретной таблицы
python db_cli.py clear <table>

# Очистка всех таблиц (с подтверждением)
python db_cli.py clear-all

# Добавление тестовых данных
python db_cli.py test-data

# Просмотр логов
python db_cli.py logs --limit 10
python db_cli.py logs --user 123456
python db_cli.py logs --level error

# Просмотр сообщений пользователя
python db_cli.py messages 123456 --limit 20

# Просмотр избранных пользователя
python db_cli.py favorites 123456
```

#### Команды PostgreSQL
```bash
# Управление PostgreSQL
python db_cli.py postgres-start     # Запуск PostgreSQL
python db_cli.py postgres-stop      # Остановка PostgreSQL
python db_cli.py postgres-restart   # Перезапуск PostgreSQL
python db_cli.py postgres-status    # Статус PostgreSQL
python db_cli.py postgres-info      # Информация о PostgreSQL
```

### API (db_api.py)
Простые функции для интеграции:

#### Управление базой данных
```python
from db_api import *

# Тестирование подключения
if test_database():
    print("✅ БД работает")

# Создание всех таблиц
create_database()

# Удаление всех таблиц
drop_database()

# Очистка конкретной таблицы
clear_table("bot_logs")

# Очистка всех таблиц
clear_all_tables()

# Информация о БД
info = get_database_info()
print(f"Таблиц: {info['total_tables']}")
```

#### Управление пользователями
```python
# Добавление пользователя
add_user(123456, "Иван", "Петров", 30, 2, "Москва", "Россия", "photo_url")

# Получение пользователя
user = get_user(123456)
if user:
    print(f"Найден: {user['first_name']} {user['last_name']}")

# Обновление пользователя
update_user(123456, age=31, city="СПб")

# Удаление пользователя
delete_user(123456)
```

#### Логирование
```python
# Системные логи
log_info("Система запущена")
log_error("Ошибка подключения")
log_debug("Отладочная информация")
log_warning("Предупреждение")

# Логи пользователей
log_info("Пользователь зашел в бота", 123456)
log_debug("Начало поиска", 123456)

# Получение логов
logs = get_logs(user_id=123456, limit=10)
error_logs = get_logs(level="error", limit=5)
```

#### Сообщения
```python
# Добавление сообщений
add_message(123456, "command", "/start")
add_message(123456, "response", "Привет!")

# Получение сообщений
messages = get_user_messages(123456, limit=20)
```

#### Избранное
```python
# Добавление в избранное
add_favorite(123456, 789012)

# Получение избранных
favorites = get_favorites(123456)

# Удаление из избранного
remove_favorite(123456, 789012)
```

#### Управление PostgreSQL
```python
# Запуск PostgreSQL
start_postgresql()

# Проверка статуса
check_postgresql_status()

# Получение информации
get_postgresql_info()

# Гарантия готовности
ensure_postgresql_ready()
```

## 📊 Структура базы данных

### Таблицы:
1. **vk_users** - Пользователи VK
2. **photos** - Фотографии пользователей
3. **favorites** - Избранные пользователи
4. **blacklisted** - Черный список
5. **search_history** - История поиска
6. **user_settings** - Настройки пользователей
7. **bot_logs** - Логи бота
8. **bot_messages** - Сообщения бота

### Основные поля:
- **vk_users**: vk_user_id, first_name, last_name, age, sex, city, country, photo_url
- **bot_logs**: vk_user_id, log_level, log_message, created_at
- **bot_messages**: vk_user_id, message_type, message_text, sent_at
- **favorites**: user_vk_id, favorite_vk_id, created_at

### Типы данных

#### Параметры пользователя
- `vk_user_id`: `int` - ID пользователя VK
- `first_name`: `str` - Имя
- `last_name`: `str` - Фамилия
- `age`: `int` - Возраст (опционально)
- `sex`: `int` - Пол: 1 - женский, 2 - мужской (опционально)
- `city`: `str` - Город (опционально)
- `country`: `str` - Страна (опционально)
- `photo_url`: `str` - URL фотографии (опционально)

#### Типы сообщений
- `"command"` - Команда пользователя
- `"response"` - Ответ бота
- `"error"` - Сообщение об ошибке

#### Уровни логирования
- `"info"` - Информация
- `"debug"` - Отладка
- `"error"` - Ошибка
- `"warning"` - Предупреждение

## 🧪 Тестирование

### Запуск примеров
```bash
python database_examples.py
```

### Симуляция работы системы
```bash
python test_database_simulation.py
```

### CLI команды для тестирования
```bash
python db_cli.py info
python db_cli.py logs --limit 5
python db_cli.py messages 123456
```

## 🔍 Отладка и мониторинг

### Просмотр логов:
```bash
# Все логи
python db_cli.py logs

# Логи конкретного пользователя
python db_cli.py logs --user 123456

# Логи определенного уровня
python db_cli.py logs --level error
```

### Просмотр сообщений:
```bash
# Сообщения пользователя
python db_cli.py messages 123456 --limit 10
```

### Статистика базы данных:
```bash
python db_cli.py info
```

## ⚙️ Настройка

### Файл .env
```env
# PostgreSQL настройки
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vkinder_db
DB_USER=vkinder_user
DB_PASSWORD=vkinder123
```

### Создание базы данных
```bash
# Создание пользователя и базы
createdb vkinder_db
createuser vkinder_user
psql -c "ALTER USER vkinder_user PASSWORD 'vkinder123';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE vkinder_db TO vkinder_user;"
```

## 🛠️ Управление

### Создание таблиц
```bash
python db_cli.py create
```

### Очистка данных
```bash
python db_cli.py clear bot_logs
python db_cli.py clear-all
```

### Удаление таблиц
```bash
python db_cli.py drop
```

## 📝 Примеры использования

### 1. Добавление нового пользователя
```python
from db_api import add_user, log_info

# Добавляем пользователя
success = add_user(
    vk_user_id=123456,
    first_name="Анна",
    last_name="Иванова",
    age=25,
    sex=1,  # 1 - женский, 2 - мужской
    city="Москва"
)

if success:
    log_info("Новый пользователь добавлен", 123456)
```

### 2. Логирование работы бота
```python
from db_api import log_info, log_error, log_debug

# Системные логи
log_info("Бот запущен")
log_debug("Инициализация завершена")

# Логи пользователей
log_info("Пользователь начал поиск", user_id)
log_error("Ошибка поиска пользователей", user_id)
```

### 3. Сохранение сообщений
```python
from db_api import add_message

# Команда пользователя
add_message(user_id, "command", "/start")

# Ответ бота
add_message(user_id, "response", "Привет! Добро пожаловать в VKinder Bot!")
```

### 4. Работа с избранным
```python
from db_api import add_favorite, get_favorites, remove_favorite

# Добавление в избранное
add_favorite(user_id, favorite_id)

# Получение списка избранных
favorites = get_favorites(user_id)
for fav in favorites:
    print(f"Избранный: {fav['favorite_vk_id']}")

# Удаление из избранного
remove_favorite(user_id, favorite_id)
```

## 🔧 Интеграция с основным кодом

### В main.py или других файлах:
```python
from db_api import log_info, log_error, add_user, add_message

# Логирование
log_info("Бот запущен")
log_error("Ошибка подключения к VK API")

# Работа с пользователями
add_user(user_id, first_name, last_name, age, sex, city)
add_message(user_id, "response", "Привет! Добро пожаловать в VKinder Bot!")
```

## 🆘 Решение проблем

### Ошибка подключения
```bash
# Проверьте статус PostgreSQL
brew services list | grep postgresql
brew services start postgresql

# Или используйте CLI команды
python db_cli.py postgres-status
python db_cli.py postgres-start
```

### Ошибки прав доступа
```bash
# Создайте пользователя БД
python setup_postgresql_auto.py
```

### Пересоздание таблиц
```bash
python db_cli.py drop
python db_cli.py create
```

## ⚠️ Важные замечания

1. **Подключение к БД**: Убедитесь, что PostgreSQL запущен и настроен
2. **Права доступа**: Пользователь должен иметь права на создание/удаление таблиц
3. **Резервное копирование**: Делайте бэкапы перед очисткой таблиц
4. **Сессии SQLAlchemy**: Все операции выполняются в контексте сессий
5. **Обработка ошибок**: Все функции возвращают bool или None при ошибках

## 📈 Возможности

- ✅ **Полноценный CRUD** для всех сущностей
- ✅ **Логирование** в базу данных
- ✅ **CLI интерфейс** для управления
- ✅ **API** для интеграции
- ✅ **Обработка ошибок** и исключений
- ✅ **Документация** и примеры
- ✅ **Тестирование** и симуляция
- ✅ **Автоматический запуск PostgreSQL**
- ✅ **Управление PostgreSQL через API**
- ✅ **CLI команды для PostgreSQL**
- ✅ **Автоматическое создание БД**

## 🆘 Быстрая помощь

### Проверка подключения
```bash
python db_cli.py info
```

### Просмотр логов
```bash
python db_cli.py logs --limit 10
```

### Запуск примеров
```bash
python database_examples.py
```

### Справка по CLI
```bash
python db_cli.py --help
```

---