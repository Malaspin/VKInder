# 🗄️ Система управления базой данных PostgreSQL

## 📋 Описание

Полноценная система для работы с базой данных PostgreSQL в проекте VKinder Bot, включающая:
- **Интерфейс базы данных** - основной класс для работы с БД
- **CLI интерфейс** - командная строка для управления БД
- **API** - высокоуровневые функции для интеграции с ботом
- **Автоматизация** - автоматический запуск PostgreSQL и создание БД
- **Документация** - подробные руководства и примеры

## 📚 Документация

- **[DATABASE_API_GUIDE.md](DATABASE_API_GUIDE.md)** - Полное руководство по API базы данных
- **[DATABASE_CLI_GUIDE.md](DATABASE_CLI_GUIDE.md)** - Руководство по CLI базы данных
- **[README_BOT.md](README_BOT.md)** - Документация по боту

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

### 3. Создание таблиц
```bash
python db_cli.py create
```

### 4. Запуск примеров
```bash
python database_examples.py
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
```bash
# Основные команды
python db_cli.py info              # Информация о БД
python db_cli.py create            # Создание таблиц
python db_cli.py clear <table>     # Очистка таблицы
python db_cli.py logs --limit 10   # Просмотр логов

# Команды PostgreSQL
python db_cli.py postgres-start    # Запуск PostgreSQL
python db_cli.py postgres-stop     # Остановка PostgreSQL
python db_cli.py postgres-status   # Статус PostgreSQL
python db_cli.py postgres-info     # Информация о PostgreSQL
```

### API (db_api.py)
Высокоуровневые функции для интеграции с ботом:
```python
from database.db_api import *

# Управление пользователями
save_user(user_data)               # Сохранение/обновление пользователя
get_user(user_id)                  # Получение пользователя
get_all_users()                    # Все пользователи

# Управление избранным
add_to_favorites(user_id, favorite_id)  # Добавить в избранное
get_favorites(user_id, limit=10)         # Получить избранных
remove_from_favorites(user_id, favorite_id)  # Удалить из избранного
is_in_favorites(user_id, target_id)      # Проверка наличия в избранном

# Управление черным списком
add_to_blacklist(user_id, blacklisted_id)    # Добавить в черный список
get_blacklist(user_id)                       # Получить черный список
remove_from_blacklist(user_id, blacklisted_id)  # Удалить из черного списка
is_user_blacklisted(user_id, target_id)     # Проверка черного списка

# Управление фотографиями
save_photos(user_id, photos_data)   # Сохранение фотографий
get_photos(user_id)                 # Получение фотографий

# Управление настройками
save_user_settings(user_id, settings)  # Сохранение настроек
get_user_settings(user_id)             # Получение настроек

# Административные функции
get_database_stats()                 # Статистика БД
get_table_list()                    # Список таблиц
get_table_info(table_name)          # Информация о таблице
get_all_tables_info()               # Информация о всех таблицах (оптимизированно)
```

## 🤖 Автоматизация процессов

### ✅ Автоматизированные процессы:

#### 1. **Автоматический запуск PostgreSQL**
```python
# При инициализации DatabaseInterface
postgres_manager = PostgreSQLManager()
postgres_manager.ensure_postgresql_running()  # Автоматически запускает PostgreSQL
```

#### 2. **Автоматическое создание базы данных**
```python
# При первом подключении
postgres_manager.create_database_if_not_exists()  # Создает 'vkinder_db' если не существует
```

#### 3. **Автоматическое создание таблиц**
```python
# При инициализации DatabaseInterface
Base.metadata.create_all(engine)  # Создает все таблицы из моделей
```

#### 4. **Автоматическое управление сессиями**
```python
# Все API функции автоматически управляют подключениями
with db.get_session() as session:
    # Автоматическое открытие/закрытие сессии
    pass
```

### 🔧 Ручные процессы:

#### 1. **Создание таблиц через CLI**
```bash
python src/database/db_cli.py create
```

#### 2. **Очистка данных**
```bash
python src/database/db_cli.py clear
```

#### 3. **Управление PostgreSQL**
```bash
python src/database/db_cli.py postgres-start
python src/database/db_cli.py postgres-stop
python src/database/db_cli.py postgres-status
```

#### 4. **Просмотр логов**
```bash
python src/database/db_cli.py logs --limit 20
```

### 🚀 Процесс запуска системы:

1. **Инициализация DatabaseInterface**
   - Проверка статуса PostgreSQL
   - Автоматический запуск PostgreSQL (если не запущен)
   - Создание базы данных (если не существует)
   - Создание таблиц (если не существуют)

2. **Готовность к работе**
   - Все таблицы созданы
   - Подключение к базе данных установлено
   - API готов к использованию

3. **Мониторинг**
   - Автоматическое логирование всех операций
   - Отслеживание ошибок подключения
   - Статистика использования

## 📊 Структура базы данных

### Таблицы:
- **vk_users** - Пользователи
- **photos** - Фотографии пользователей (с поддержкой лайков/дизлайков)
- **favorites** - Избранные пользователи
- **blacklisted** - Черный список
- **search_history** - История поиска (с расширенными критериями)
- **user_settings** - Настройки пользователей (с предпочтениями поиска)
- **bot_logs** - Логи системы
- **bot_messages** - Сообщения

### 🆕 Новые поля:
- **photos**: `updated_at`
- **search_history**: `relationship_status`, `has_photo`, `online`
- **user_settings**: `relationship_status`, `has_photo`, `online`

## 🧪 Тестирование

### Запуск примеров
```bash
python database_examples.py
```

### Симуляция работы системы
```bash
python test_database_simulation.py
```

### CLI команды
```bash
python db_cli.py info
python db_cli.py logs --limit 5
python db_cli.py messages 123456
```

## 📚 Документация

- **`DATABASE_INTERFACE_GUIDE.md`** - полное руководство
- **`DATABASE_COMMANDS_REFERENCE.md`** - справочник команд
- **`DATABASE_QUICKSTART.md`** - быстрый старт
- **`database_examples.py`** - примеры использования

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

## 🔍 Мониторинг

### Просмотр статистики
```bash
python db_cli.py info
```

### Просмотр логов
```bash
python db_cli.py logs --limit 20
python db_cli.py logs --level error
```

### Просмотр сообщений
```bash
python db_cli.py messages 123456
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

## 🆘 Решение проблем

### Ошибка подключения
```bash
# Проверьте PostgreSQL
brew services list | grep postgresql
brew services start postgresql
```

### Ошибки прав доступа
```bash
# Создайте пользователя БД
createdb vkinder_db
createuser vkinder_user
```

### Проблемы с таблицами
```bash
# Пересоздайте таблицы
python db_cli.py drop
python db_cli.py create
```

## 🔧 Интеграция с ботом

### Модуль интеграции с базой данных
- **Файл:** `src/bot/database_integration.py`
- **Функции:** Сохранение всех данных в соответствующие таблицы
- **Обработка ошибок:** Graceful fallback при недоступности БД
- **Новая логика:** Проверка успешности сохранения перед сохранением связанных данных
- **Исправления:** Foreign key constraint errors, правильный порядок сохранения

### Запись данных во все таблицы

#### **📊 Таблица `vk_users`:**
```python
# Сохранение пользователей при получении информации
user_data = {
    'id': user_id,
    'first_name': user['first_name'],
    'last_name': user['last_name'],
    'age': age,
    'sex': user.get('sex', 0),
    'city': city,
    'city_id': city_id,
    'country': user.get('country', ''),
    'bdate': user.get('bdate', ''),
    'photo_url': f"https://vk.com/images/camera_200.png",
    'profile_url': f"https://vk.com/id{user_id}",
    'is_closed': user.get('is_closed', False),
    'can_access_closed': user.get('can_access_closed', False)
}
self.db.save_user(user_data)
```

#### **📸 Таблица `photos`:**
```python
# Сохранение фотографий при поиске
photos_data = []
for photo in top_photos:
    photo_data = {
        'url': max_size['url'],
        'type': 'profile',
        'likes': photo.get('likes', {}).get('count', 0)
    }
    photos_data.append(photo_data)
self.db.save_photos(user_id, photos_data)
```

#### **❤️ Таблица `favorites`:**
```python
# Сохранение избранных пользователей
self.db.add_to_favorites(user_id, person_id)
```

#### **🚫 Таблица `blacklisted`:**
```python
# Сохранение заблокированных пользователей
self.db.add_to_blacklist(user_id, person_id)
```

#### **🔍 Таблица `search_history`:**
```python
# Сохранение истории поиска
search_data = {
    'user_id': user_id,
    'search_params': search_params,
    'results_count': len(results),
    'timestamp': datetime.now()
}
self.db.save_search_history(search_data)
```

#### **⚙️ Таблица `user_settings`:**
```python
# Сохранение настроек пользователя
settings_data = {
    'user_id': user_id,
    'min_age': min_age,
    'max_age': max_age,
    'sex_preference': sex_preference,
    'city_preference': city_preference
}
self.db.save_user_settings(settings_data)
```

#### **📝 Таблица `bot_logs`:**
```python
# Логирование в базу данных
self.db.log_to_database("info", "Пользователь выполнил поиск", user_id)
```

#### **💬 Таблица `bot_messages`:**
```python
# Сохранение сообщений бота
self.db.save_bot_message(user_id, "command", message_text)
self.db.save_bot_message(user_id, "response", response_text)
```

## 🔧 Команды управления базой данных

### Основные команды
```bash
# Информация о базе данных
python BOT_BEGIN.py
# Выберите: 10. 🗄️ Информация о базе данных

# Создание таблиц
python BOT_BEGIN.py
# Выберите: 11. 🏗️ Создать таблицы БД

# Удаление таблиц
python BOT_BEGIN.py
# Выберите: 12. 🗑️ Удалить таблицы БД
```

### Управление PostgreSQL
```bash
# Запуск PostgreSQL
python BOT_BEGIN.py
# Выберите: 13. 🚀 Запустить PostgreSQL

# Остановка PostgreSQL
python BOT_BEGIN.py
# Выберите: 14. 🛑 Остановить PostgreSQL

# Статус PostgreSQL
python BOT_BEGIN.py
# Выберите: 15. 📊 Статус PostgreSQL
```

### Очистка данных
```bash
# Очистка всех данных
python BOT_BEGIN.py
# Выберите: 16. 🧹 Очистить данные БД

# Очистка конкретной таблицы
python BOT_BEGIN.py
# Выберите: 20. 🗑️ Очистить конкретную таблицу
```

### Просмотр данных
```bash
# Просмотр логов БД
python BOT_BEGIN.py
# Выберите: 17. 📋 Просмотр логов БД

# Просмотр пользователей БД
python BOT_BEGIN.py
# Выберите: 18. 👥 Просмотр пользователей БД

# Просмотр сообщений БД
python BOT_BEGIN.py
# Выберите: 19. 💬 Просмотр сообщений БД
```

## 🐛 Решение проблем

### Проблемы с импортами
```bash
# Ошибка: No module named 'database_interface'
# Решение: Убедитесь, что src добавлен в sys.path
```

### Проблемы с PostgreSQL
```bash
# Ошибка: PostgreSQL не запущен
# Решение: brew services start postgresql
```

### Проблемы с таблицами
```bash
# Ошибка: Таблица не существует
# Решение: python db_cli.py create
```

### Проблемы с правами доступа
```bash
# Ошибка: Permission denied
# Решение: Создайте пользователя БД с правильными правами
```

## 📋 Справочник команд базы данных

### CLI команды (db_cli.py)

| Команда | Параметры | Описание |
|---------|-----------|----------|
| `python db_cli.py info` | - | Показать информацию о всех таблицах БД |
| `python db_cli.py create` | - | Создать все таблицы базы данных |
| `python db_cli.py drop` | - | Удалить все таблицы (с подтверждением) |
| `python db_cli.py clear <table>` | `table` - название таблицы | Очистить конкретную таблицу |
| `python db_cli.py clear-all` | - | Очистить все таблицы (с подтверждением) |
| `python db_cli.py test-data` | - | Добавить тестовые данные |
| `python db_cli.py logs` | `--user <id>` `--level <level>` `--limit <n>` | Показать логи |
| `python db_cli.py messages <user_id>` | `--limit <n>` | Показать сообщения пользователя |
| `python db_cli.py favorites <user_id>` | - | Показать избранных пользователя |

### Примеры CLI команд:
```bash
# Информация о БД
python db_cli.py info

# Очистка таблицы логов
python db_cli.py clear bot_logs

# Просмотр логов пользователя
python db_cli.py logs --user 123456 --limit 10

# Просмотр ошибок
python db_cli.py logs --level error --limit 5

# Сообщения пользователя
python db_cli.py messages 123456 --limit 20
```

## 💻 API функции (db_api.py)

### Управление базой данных

| Функция | Параметры | Возвращает | Описание |
|---------|-----------|------------|----------|
| `test_database()` | - | `bool` | Тестирование подключения к БД |
| `create_database()` | - | `bool` | Создание всех таблиц |
| `drop_database()` | - | `bool` | Удаление всех таблиц |
| `clear_table(table_name)` | `table_name: str` | `bool` | Очистка конкретной таблицы |
| `clear_all_tables()` | - | `bool` | Очистка всех таблиц |
| `get_database_info()` | - | `dict` | Информация о таблицах |

### Управление пользователями

| Функция | Параметры | Возвращает | Описание |
|---------|-----------|------------|----------|
| `add_user(vk_user_id, first_name, last_name, age, sex, city, country, photo_url)` | `vk_user_id: int`<br>`first_name: str`<br>`last_name: str`<br>`age: int` (опционально)<br>`sex: int` (опционально)<br>`city: str` (опционально)<br>`country: str` (опционально)<br>`photo_url: str` (опционально) | `bool` | Добавление пользователя |
| `get_user(vk_user_id)` | `vk_user_id: int` | `dict` или `None` | Получение пользователя по ID |
| `update_user(vk_user_id, **kwargs)` | `vk_user_id: int`<br>`**kwargs` - поля для обновления | `bool` | Обновление данных пользователя |
| `delete_user(vk_user_id)` | `vk_user_id: int` | `bool` | Удаление пользователя |

### Логирование

| Функция | Параметры | Возвращает | Описание |
|---------|-----------|------------|----------|
| `log_info(message, user_id)` | `message: str`<br>`user_id: int = 0` | `bool` | Запись информационного лога |
| `log_debug(message, user_id)` | `message: str`<br>`user_id: int = 0` | `bool` | Запись отладочного лога |
| `log_error(message, user_id)` | `message: str`<br>`user_id: int = 0` | `bool` | Запись лога ошибки |
| `log_warning(message, user_id)` | `message: str`<br>`user_id: int = 0` | `bool` | Запись лога предупреждения |
| `get_logs(user_id, level, limit)` | `user_id: int = 0`<br>`level: str = None`<br>`limit: int = 100` | `list` | Получение логов |

### Сообщения

| Функция | Параметры | Возвращает | Описание |
|---------|-----------|------------|----------|
| `add_message(user_id, message_type, message_text)` | `user_id: int`<br>`message_type: str`<br>`message_text: str` | `bool` | Добавление сообщения |
| `get_user_messages(user_id, limit)` | `user_id: int`<br>`limit: int = 50` | `list` | Получение сообщений пользователя |

### Избранное

| Функция | Параметры | Возвращает | Описание |
|---------|-----------|------------|----------|
| `add_favorite(user_id, favorite_id)` | `user_id: int`<br>`favorite_id: int` | `bool` | Добавление в избранное |
| `get_favorites(user_id)` | `user_id: int` | `list` | Получение списка избранных |
| `remove_favorite(user_id, favorite_id)` | `user_id: int`<br>`favorite_id: int` | `bool` | Удаление из избранного |

## 🐍 Примеры использования API

### Базовое использование
```python
from db_api import *

# Тестирование подключения
if test_database():
    print("✅ БД работает")

# Информация о БД
info = get_database_info()
print(f"Таблиц: {info['total_tables']}")
```

### Работа с пользователями
```python
# Добавление пользователя
add_user(123456, "Иван", "Петров", 30, 2, "Москва")

# Получение пользователя
user = get_user(123456)
if user:
    print(f"Найден: {user['first_name']} {user['last_name']}")

# Обновление пользователя
update_user(123456, age=31, city="СПб")
```

### Логирование
```python
# Системные логи
log_info("Система запущена")
log_error("Ошибка подключения")

# Логи пользователей
log_info("Пользователь зашел в бота", 123456)
log_debug("Начало поиска", 123456)

# Получение логов
logs = get_logs(user_id=123456, limit=10)
error_logs = get_logs(level="error", limit=5)
```

### Сообщения
```python
# Добавление сообщений
add_message(123456, "command", "/start")
add_message(123456, "response", "Привет!")

# Получение сообщений
messages = get_user_messages(123456, limit=20)
```

### Избранное
```python
# Добавление в избранное
add_favorite(123456, 789012)

# Получение избранных
favorites = get_favorites(123456)

# Удаление из избранного
remove_favorite(123456, 789012)
```

## 🗄️ Управление таблицами

### Создание таблиц
```python
# Создать все таблицы
create_database()
```

### Очистка данных
```python
# Очистить конкретную таблицу
clear_table("bot_logs")

# Очистить все таблицы
clear_all_tables()
```

### Удаление таблиц
```python
# Удалить все таблицы
drop_database()
```

## 📊 Типы данных

### Параметры пользователя
- `vk_user_id`: `int` - ID пользователя VK
- `first_name`: `str` - Имя
- `last_name`: `str` - Фамилия
- `age`: `int` - Возраст (опционально)
- `sex`: `int` - Пол: 1 - женский, 2 - мужской (опционально)
- `city`: `str` - Город (опционально)
- `country`: `str` - Страна (опционально)
- `photo_url`: `str` - URL фотографии (опционально)

### Типы сообщений
- `"command"` - Команда пользователя
- `"response"` - Ответ бота
- `"error"` - Сообщение об ошибке

### Уровни логирования
- `"info"` - Информация
- `"debug"` - Отладка
- `"error"` - Ошибка
- `"warning"` - Предупреждение

## 🐘 Команды PostgreSQL

### CLI команды PostgreSQL

| Команда           | Параметры | Описание                                                              | Пример использования                                     |
| :---------------- | :-------- | :-------------------------------------------------------------------- | :------------------------------------------------------- |
| `postgres-start`  | `-`       | Запускает PostgreSQL сервер.                                          | `python db_cli.py postgres-start`                        |
| `postgres-stop`   | `-`       | Останавливает PostgreSQL сервер.                                      | `python db_cli.py postgres-stop`                         |
| `postgres-restart`| `-`       | Перезапускает PostgreSQL сервер.                                     | `python db_cli.py postgres-restart`                      |
| `postgres-status` | `-`       | Показывает статус PostgreSQL сервера.                                 | `python db_cli.py postgres-status`                       |
| `postgres-info`  | `-`       | Показывает подробную информацию о PostgreSQL.                         | `python db_cli.py postgres-info`                         |

### API функции PostgreSQL

| Функция           | Параметры | Описание                                                              | Возвращает                               |
| :---------------- | :-------- | :-------------------------------------------------------------------- | :--------------------------------------- |
| `start_postgresql()` | `-`       | Запускает PostgreSQL сервер.                                          | `bool`                                   |
| `stop_postgresql()`  | `-`       | Останавливает PostgreSQL сервер.                                      | `bool`                                   |
| `restart_postgresql()` | `-`      | Перезапускает PostgreSQL сервер.                                     | `bool`                                   |
| `check_postgresql_status()` | `-`   | Проверяет статус PostgreSQL сервера.                                 | `bool`                                   |
| `get_postgresql_info()` | `-`     | Получает подробную информацию о PostgreSQL.                          | `Dict[str, Any]`                         |
| `create_database_if_not_exists()` | `-` | Создает базу данных если она не существует.                         | `bool`                                   |
| `ensure_postgresql_ready()` | `-`  | Гарантирует, что PostgreSQL готов к работе.                         | `bool`                                   |

### Примеры использования PostgreSQL

#### CLI команды
```bash
# Проверка статуса PostgreSQL
python db_cli.py postgres-status

# Запуск PostgreSQL
python db_cli.py postgres-start

# Информация о PostgreSQL
python db_cli.py postgres-info

# Остановка PostgreSQL
python db_cli.py postgres-stop
```

#### API функции
```python
from db_api import *

# Проверка статуса
status = check_postgresql_status()

# Получение информации
info = get_postgresql_info()

# Запуск PostgreSQL
start_postgresql()

# Гарантия готовности
ensure_postgresql_ready()
```

## 🔧 Последние улучшения логирования

### 📝 Подробное логирование черного списка

#### **Добавлено в систему логирования:**
- ✅ **Исключение из результатов поиска** - когда пользователь найден в черном списке
- ✅ **Пропуск при навигации** - логирование пропущенных пользователей при "Далее" и "Назад"
- ✅ **Детальная информация** - ID, имя, фамилия каждого пропущенного пользователя
- ✅ **Счетчики пропущенных** - статистика пропущенных пользователей
- ✅ **Контекстная информация** - различение между поиском и навигацией

#### **Примеры логов в базе данных:**
```sql
-- Логи исключения из поиска
INSERT INTO bot_logs (level, message, user_id, created_at) 
VALUES ('INFO', 'Пользователь 12345 исключен из поиска - в черном списке', 67890, NOW());

-- Логи пропуска при навигации
INSERT INTO bot_logs (level, message, user_id, created_at) 
VALUES ('INFO', 'Пользователь 54321 пропущен из-за черного списка', 67890, NOW());

-- Логи навигации назад
INSERT INTO bot_logs (level, message, user_id, created_at) 
VALUES ('INFO', 'При навигации назад пользователь 98765 пропущен из-за черного списка', 67890, NOW());
```

#### **Технические детали реализации:**
```python
# В методе search_users()
for person in unique_results:
    if person['id'] not in blacklisted_ids:
        filtered_results.append(person)
    else:
        excluded_count += 1
        self.logger.info(f"Пользователь {person['id']} ({person.get('first_name', 'Unknown')} {person.get('last_name', 'Unknown')}) исключен из результатов поиска - находится в черном списке для пользователя {user_id}")
        self.db.log_to_database('INFO', f"Пользователь {person['id']} исключен из поиска - в черном списке", user_id)
```

#### **Преимущества нового логирования:**
- ✅ **Полная прозрачность** - видно кто и почему пропущен
- ✅ **Аналитика эффективности** - насколько хорошо работает фильтрация
- ✅ **Отладка проблем** - легко найти почему не показываются анкеты
- ✅ **Мониторинг использования** - как часто используется черный список
- ✅ **Статистика пропусков** - сколько пользователей пропущено

### 🔧 Улучшения системы логирования

#### **Многоуровневое логирование:**
- **INFO уровень** - основные события пропуска пользователей
- **DEBUG уровень** - детальная отладочная информация
- **База данных** - все события сохраняются в таблицу `bot_logs`
- **Файлы** - детальные логи для анализа

#### **Контекстная информация:**
- **При поиске** - "исключен из результатов поиска"
- **При навигации вперед** - "найден в черном списке и пропущен"
- **При навигации назад** - "При навигации назад пользователь найден в черном списке"

## 🔧 Последние исправления и улучшения

### **Исправление Foreign Key Constraint Errors**

#### **🚨 Проблема:**
- ❌ **Ошибка:** `insert or update on table 'photos' violates foreign key constraint`
- ❌ **Фотографии пытались сохраниться** для пользователя, который не был сохранен в `vk_users`
- ❌ **Нарушение внешнего ключа** `photos_vk_user_id_fkey`

#### **✅ Решение:**
```python
# БЫЛО (неправильно):
self.db.save_user(person_data)  # Может не сохраниться
# Сохраняем фотографии сразу - ОШИБКА!
self.db.save_photos(person['id'], photos_data)  # ❌ Foreign key error

# СТАЛО (правильно):
user_saved = self.db.save_user(person_data)  # Получаем результат
if user_saved:  # ✅ Проверяем успешность
    # Сохраняем фотографии ТОЛЬКО если пользователь сохранен
    self.db.save_photos(person['id'], photos_data)  # ✅ Без ошибок
else:
    self.logger.warning(f"Не удалось сохранить пользователя {person['id']}, пропускаем фотографии")
```

#### **🎯 Результат:**
- ✅ **Нет ошибок** `foreign key constraint`
- ✅ **Фотографии сохраняются** только для существующих пользователей
- ✅ **Корректная последовательность** сохранения в БД
- ✅ **Стабильная работа** без ошибок БД

### **Исправление доступа к методам БД**

#### **🚨 Проблема:**
- ❌ **Ошибка:** `'BotDatabaseIntegration' object has no attribute 'get_user'`
- ❌ **Неправильный доступ** к методу `get_user` в `DatabaseInterface`

#### **✅ Решение:**
```python
# БЫЛО (неправильно):
user_data = self.db.get_user(user_id)  # ❌ Ошибка доступа

# СТАЛО (правильно):
user_data = self.db.db.get_user(user_id)  # ✅ Правильный доступ
```

#### **🎯 Результат:**
- ✅ **Корректный доступ** к методам `DatabaseInterface`
- ✅ **Работа индикаторов** статуса пользователей (🟢/⚪)
- ✅ **Проверка новых пользователей** работает правильно

### **Улучшенная логика сохранения данных**

#### **📊 Новая логика сохранения пользователей:**
```python
# 1. Проверяем статус пользователя ДО сохранения
is_new_user = self.is_new_user(person['id'])  # ✅ Проверка ДО сохранения

# 2. Сохраняем пользователя
user_saved = self.db.save_user(person_data)

# 3. Сохраняем фотографии ТОЛЬКО если пользователь сохранен
if user_saved and photos_data:
    self.db.save_photos(person['id'], photos_data)
```

#### **📸 Новая логика сохранения фотографий:**
```python
# Проверяем существование фотографии перед добавлением
existing_photo = session.query(Photo).filter(
    Photo.vk_user_id == user_id,
    Photo.photo_url == photo_data['url']
).first()

if existing_photo:
    # Обновляем количество лайков
    existing_photo.likes_count = photo_data['likes']
else:
    # Добавляем новую фотографию
    new_photo = Photo(
        vk_user_id=user_id,
        photo_url=photo_data['url'],
        photo_type=photo_data['type'],
        likes_count=photo_data['likes']
    )
    session.add(new_photo)
```

#### **❤️ Новая логика избранного:**
```python
# Проверяем существование в избранном
existing_favorite = session.query(Favorite).filter(
    Favorite.user_id == user_id,
    Favorite.favorite_id == favorite_id
).first()

if existing_favorite:
    # Обновляем дату добавления
    existing_favorite.created_at = datetime.now()
else:
    # Добавляем новое избранное
    new_favorite = Favorite(
        user_id=user_id,
        favorite_id=favorite_id,
        created_at=datetime.now()
    )
    session.add(new_favorite)
```

### **Точная фильтрация по возрасту**

#### **🔍 Дополнительная фильтрация результатов:**
```python
# Дополнительная фильтрация по возрасту (VK API иногда неточен)
age_filtered_results = []
age_excluded_count = 0
no_bdate_count = 0

for person in unique_results:
    person_age = self.calculate_age(person.get('bdate', ''))
    if person_age and age_from <= person_age <= age_to:
        age_filtered_results.append(person)
    else:
        age_excluded_count += 1
        if person_age:
            self.logger.debug(f"Пользователь {person['id']} исключен по возрасту: {person_age} лет")
        else:
            no_bdate_count += 1
            self.logger.debug(f"Пользователь {person['id']} исключен - нет даты рождения")

unique_results = age_filtered_results
```

#### **📊 Расширенные параметры поиска:**
```python
search_params = {
    'q': '',
    'sex': target_sex,
    'age_from': age_from,
    'age_to': age_to,
    'status': 6,  # не в браке
    'has_photo': 1,
    'online': 0,  # не обязательно онлайн
    'sort': 0,  # по популярности
    'count': 50,
    'offset': offset,
    'fields': 'city,sex,bdate,photo_200,is_closed,can_access_closed'  # ✅ Расширенные поля
}
```

### **Система индикаторов статуса**

#### **🎯 Индикаторы пользователей:**
- **❤️** - Пользователь в избранном
- **🟢** - Новый пользователь (не был в `vk_users`)
- **⚪** - Существующий пользователь (уже был в `vk_users`)

#### **🎂 Информация о днях рождения:**
- **"Сегодня День рождения!"** - если день рождения сегодня
- **"Скоро день рождения! [дата]"** - если в течение 5 дней
- **"Вчера был День рождения"** - если был вчера

### **Улучшенная система избранного**

#### **📊 Варианты показа избранного:**
- **ТОП-1** - последний добавленный
- **ТОП-5** - последние 5 добавленных
- **ТОП-10** - последние 10 добавленных

#### **📅 Сортировка по дате:**
```python
# Избранные сортируются по дате добавления (последние первые)
favorites = session.query(Favorite).filter(
    Favorite.user_id == user_id
).order_by(Favorite.created_at.desc()).limit(limit).all()
```

## 🆕 Новые возможности

### 📊 API статистики пользователей
- **get_user_statistics()** - базовая статистика пользователя
- **get_user_profile_stats()** - расширенная статистика профиля
- **get_user_activity_summary()** - сводка активности пользователя

### 📝 Продвинутое логирование
- **Логирование в БД** - структурированные логи в таблице `bot_logs`
- **Многоуровневое логирование** - DEBUG, INFO, WARNING, ERROR
- **Временные метки** - уникальные имена файлов логов
- **Отладочная информация** - детальная трассировка операций

### 🔧 Улучшенное управление
- **Автоматическое создание БД** - инициализация при первом запуске
- **CLI инструменты** - удобные команды для управления
- **Мониторинг** - отслеживание производительности
- **Резервное копирование** - автоматические бэкапы

### 🗄️ Расширенная схема данных
- **Новые таблицы** - `bot_logs`, `bot_messages`
- **Дополнительные поля** - временные метки, статусы
- **Индексы** - оптимизация производительности
- **Связи** - улучшенные связи между таблицами

### 🆕 Последние улучшения
- **Исправлена ошибка с черным списком** - унифицирован атрибут `self.blacklisted`
- **Временные метки в логах** - уникальные имена файлов логов с временными метками
- **Улучшенное логирование** - детальная отладочная информация для диагностики
- **API для статистики** - новые функции для получения расширенной статистики
- **Полное отображение лайков** - показ точного количества лайков вместо сокращений
- **Исправлены ошибки обработки данных** - устранены все потенциальные `KeyError` с полом, городом и возрастом
- **Улучшена стабильность** - безопасная обработка пользователей с неполной информацией

## 📈 Производительность

### Оптимизация запросов
- **Индексы** - ускорение поиска по ключевым полям
- **Кэширование** - кэширование часто используемых данных
- **Батчевые операции** - группировка операций для повышения производительности

### Мониторинг
- **Время выполнения** - отслеживание производительности запросов
- **Использование ресурсов** - мониторинг памяти и CPU
- **Алерты** - уведомления о проблемах

## 🛠️ Инструменты разработки

### CLI команды
```bash
# Создание БД
python src/database/db_cli.py create

# Удаление БД
python src/database/db_cli.py drop

# Тестирование подключения
python src/database/db_cli.py test

# Просмотр таблиц
python src/database/db_cli.py tables

# Очистка данных
python src/database/db_cli.py cleanup
```

### API функции
```python
# Получение статистики
from src.database.db_api import get_user_statistics
stats = get_user_statistics(user_id)

# Работа с пользователями
from src.database.db_api import save_user, get_user
user_data = {'id': 123, 'first_name': 'Иван', 'last_name': 'Петров'}
save_user(user_data)
```

## 📊 API Статистики пользователей

### Обзор
API статистики предоставляет детальную информацию о активности пользователей в VKinder Bot. Все функции работают через единый интерфейс базы данных.

### Доступные функции

#### 1. `get_user_statistics(user_id: int) -> dict`
**Назначение:** Получение базовой статистики пользователя

**Возвращает:**
```python
{
    'viewed_profiles': int,      # Просмотренные анкеты
    'favorites_count': int,       # В избранном
    'blacklisted_count': int,     # В черном списке
    'viewed_photos': int,        # Просмотренные фото
    'search_sessions': int       # Поисковые сессии
}
```

#### 2. `get_user_profile_stats(user_id: int) -> dict`
**Назначение:** Получение расширенной статистики профиля

**Возвращает:**
```python
{
    # Базовая статистика
    'viewed_profiles': int,
    'favorites_count': int,
    'blacklisted_count': int,
    'viewed_photos': int,
    'search_sessions': int,
    
    # Дополнительная информация
    'total_searches': int,           # Общее количество поисков
    'last_search_date': str,         # Дата последнего поиска
    'last_search_results': int,      # Результаты последнего поиска
    'user_settings': {               # Настройки пользователя
        'min_age': int,
        'max_age': int,
        'sex_preference': int,
        'city_preference': str,
        'online_only': bool
    }
}
```

#### 3. `get_user_activity_summary(user_id: int) -> dict`
**Назначение:** Получение сводки активности пользователя

**Возвращает:**
```python
{
    'messages_with_bot': int,        # Сообщения с ботом
    'bot_logs_count': int,           # Логи пользователя
    'last_activity': str,            # Последняя активность
    'searches_last_week': int,       # Поиски за неделю
    'messages_last_week': int         # Сообщения за неделю
}
```

### Пример использования
```python
from src.database.db_api import get_user_statistics

user_id = 123456789
stats = get_user_statistics(user_id)

print(f"📊 Статистика пользователя {user_id}:")
print(f"👀 Просмотрено анкет: {stats.get('viewed_profiles', 0)}")
print(f"❤️ В избранном: {stats.get('favorites_count', 0)}")
print(f"🚫 В черном списке: {stats.get('blacklisted_count', 0)}")
print(f"📸 Просмотрено фото: {stats.get('viewed_photos', 0)}")
print(f"🔍 Поисковых сессий: {stats.get('search_sessions', 0)}")
```

## 📝 Система логирования

### Обзор
VKinder Bot использует многоуровневую систему логирования с поддержкой файлового логирования и записи в базу данных. Система обеспечивает детальную трассировку всех операций для отладки и мониторинга.

### Уровни логирования

#### DEBUG - Подробная отладочная информация
- Детальная трассировка выполнения
- Состояние переменных и объектов
- Параметры функций и API вызовов
- Результаты операций с базой данных

#### INFO - Основные события
- Успешные операции
- Статистика и метрики
- Пользовательские действия
- Системные события

#### WARNING - Предупреждения
- Нестандартные ситуации
- Проблемы с доступностью сервисов
- Частичные сбои

#### ERROR - Критические ошибки
- Сбои в работе системы
- Ошибки подключения к БД
- Проблемы с VK API

### Структура логов

#### Файловое логирование
```
logs/
├── bot_system_YYYYMMDD_HHMM.log    # Системные логи бота
├── database_debug_YYYYMMDD_HHMM.log # Отладочные логи БД
├── bot_info.log                    # INFO логи (устаревший)
├── bot_debug.log                   # DEBUG логи (устаревший)
├── bot_error.log                   # ERROR логи (устаревший)
└── bot_system.log                  # Системные логи (устаревший)
```

#### Логирование в базу данных
Таблица `bot_logs`:
- `id` - уникальный идентификатор
- `vk_user_id` - ID пользователя VK
- `log_level` - уровень логирования
- `log_message` - текст сообщения
- `created_at` - время создания

### Настройка логирования

#### Конфигурация в коде
```python
# В vk_bot.py
def _setup_logging(self):
    """Настройка системы логирования"""
    
    # Генерируем суффикс с временной меткой
    timestamp_suffix = self._get_timestamp_suffix()
    
    # Настройка уровня логирования
    log_level = logging.DEBUG if self.debug_mode else logging.INFO
    
    # Конфигурация логирования
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            # Консольный вывод
            logging.StreamHandler(),
            # Файловое логирование
            logging.FileHandler(f'logs/bot_system{timestamp_suffix}.log', encoding='utf-8')
        ]
    )
```

#### Переменные окружения
```bash
# В .env файле
LOG_LEVEL=INFO                    # Уровень логирования
LOG_TO_DB=true                   # Логирование в БД
DEBUG_MODE=false                 # Режим отладки
```

## 📝 Лицензия

Проект создан для учебных целей.

---
*Система управления базой данных PostgreSQL с полной интеграцией и мониторингом!*
