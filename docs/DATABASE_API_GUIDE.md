# 📊 Руководство по API базы данных VKinder Bot

## 🎯 Обзор

Данное руководство описывает полный API для работы с базой данных PostgreSQL в проекте VKinder Bot. API предоставляет высокоуровневые функции для управления пользователями, сообщениями, избранным, черным списком и другими данными.

## 🏗️ Архитектура системы

### Компоненты системы:

```
┌─────────────────────────────────────────────────────────────┐
│                    VKinder Bot Application                 │
├─────────────────────────────────────────────────────────────┤
│  src/bot/database_integration.py  (BotDatabaseIntegration) │
│  └── Промежуточный слой между ботом и API                  │
├─────────────────────────────────────────────────────────────┤
│  src/database/db_api.py  (High-Level API)                  │
│  └── Высокоуровневые функции для бизнес-логики             │
├─────────────────────────────────────────────────────────────┤
│  src/database/database_interface.py  (DatabaseInterface)    │
│  └── Низкоуровневые операции с базой данных                │
├─────────────────────────────────────────────────────────────┤
│  src/database/postgres_manager.py  (PostgreSQLManager)      │
│  └── Управление PostgreSQL сервером                        │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL Database Server                                │
│  └── Хранение всех данных приложения                       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Процесс подключения и запуска

### Автоматизированные процессы:

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

### Ручные процессы:

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

## 📋 API Функции

### 🔐 Управление пользователями

#### `save_user(user_data: dict) -> bool`
**Назначение:** Сохраняет или обновляет пользователя в базе данных.

**Параметры:**
- `user_data` (dict): Словарь с данными пользователя
  - `id` (int): VK ID пользователя
  - `first_name` (str): Имя
  - `last_name` (str): Фамилия
  - `sex` (int): Пол (1-женский, 2-мужской)
  - `bdate` (str): Дата рождения
  - `city` (dict): Город `{'id': int, 'title': str}`
  - `photo_url` (str): URL главного фото

**Возвращает:** `bool` - True если успешно сохранено

**Пример использования:**
```python
from database.db_api import save_user

user_data = {
    'id': 123456789,
    'first_name': 'Анна',
    'last_name': 'Петрова',
    'sex': 1,
    'bdate': '15.05.1990',
    'city': {'id': 1, 'title': 'Москва'},
    'photo_url': 'https://vk.com/photo123'
}

success = save_user(user_data)
if success:
    print("Пользователь сохранен успешно")
```

#### `get_user(user_id: int) -> dict`
**Назначение:** Получает данные пользователя по VK ID.

**Параметры:**
- `user_id` (int): VK ID пользователя

**Возвращает:** `dict` - Данные пользователя или None

**Пример использования:**
```python
from database.db_api import get_user

user = get_user(123456789)
if user:
    print(f"Найден пользователь: {user['first_name']} {user['last_name']}")
```

#### `get_all_users() -> list`
**Назначение:** Получает список всех пользователей.

**Возвращает:** `list` - Список всех пользователей

### 💬 Управление сообщениями

#### `save_message(user_id: int, message: str, message_type: str = 'user') -> bool`
**Назначение:** Сохраняет сообщение в базу данных.

**Параметры:**
- `user_id` (int): VK ID пользователя
- `message` (str): Текст сообщения
- `message_type` (str): Тип сообщения ('user' или 'bot')

**Возвращает:** `bool` - True если успешно сохранено

#### `get_messages(user_id: int, limit: int = 50) -> list`
**Назначение:** Получает сообщения пользователя.

**Параметры:**
- `user_id` (int): VK ID пользователя
- `limit` (int): Максимальное количество сообщений

**Возвращает:** `list` - Список сообщений

### ❤️ Управление избранным

#### `add_to_favorites(user_id: int, favorite_id: int) -> bool`
**Назначение:** Добавляет пользователя в избранное.

**Параметры:**
- `user_id` (int): VK ID пользователя, который добавляет
- `favorite_id` (int): VK ID пользователя, которого добавляют

**Возвращает:** `bool` - True если успешно добавлено

**Правила использования:**
- Если пользователь уже в избранном, обновляется `added_at`
- Не создается дубликат записи

#### `get_favorites(user_id: int, limit: int = 10) -> list`
**Назначение:** Получает список избранных пользователей.

**Параметры:**
- `user_id` (int): VK ID пользователя
- `limit` (int): Максимальное количество записей

**Возвращает:** `list` - Список избранных пользователей, отсортированный по `added_at DESC`

#### `remove_from_favorites(user_id: int, favorite_id: int) -> bool`
**Назначение:** Удаляет пользователя из избранного.

#### `is_in_favorites(user_id: int, target_id: int) -> bool`
**Назначение:** Проверяет, находится ли пользователь в избранном.

### 🚫 Управление черным списком

#### `add_to_blacklist(user_id: int, blacklisted_id: int) -> bool`
**Назначение:** Добавляет пользователя в черный список.

**Параметры:**
- `user_id` (int): VK ID пользователя, который блокирует
- `blacklisted_id` (int): VK ID пользователя, которого блокируют

#### `get_blacklist(user_id: int) -> list`
**Назначение:** Получает список заблокированных пользователей.

#### `remove_from_blacklist(user_id: int, blacklisted_id: int) -> bool`
**Назначение:** Удаляет пользователя из черного списка.

#### `is_user_blacklisted(user_id: int, target_user_id: int) -> bool`
**Назначение:** Проверяет, находится ли пользователь в черном списке.

### 📸 Управление фотографиями

#### `save_photos(user_id: int, photos_data: list) -> bool`
**Назначение:** Сохраняет фотографии пользователя.

**Параметры:**
- `user_id` (int): VK ID пользователя
- `photos_data` (list): Список словарей с данными фотографий
  - `url` (str): URL фотографии
  - `likes_count` (int): Количество лайков
  - `photo_type` (str): Тип фотографии ('profile' или 'tagged')

**Правила использования:**
- Если фотография уже существует, обновляется `likes_count`
- Не создается дубликат записи

#### `get_photos(user_id: int) -> list`
**Назначение:** Получает фотографии пользователя.

### ⚙️ Управление настройками

#### `save_user_settings(user_id: int, settings: dict) -> bool`
**Назначение:** Сохраняет настройки пользователя.

**Параметры:**
- `user_id` (int): VK ID пользователя
- `settings` (dict): Словарь настроек
  - `age_from` (int): Минимальный возраст
  - `age_to` (int): Максимальный возраст
  - `sex_preference` (int): Предпочтение по полу
  - `city_preference` (dict): Предпочтение по городу

#### `get_user_settings(user_id: int) -> dict`
**Назначение:** Получает настройки пользователя.

### 📊 Административные функции

#### `get_database_stats() -> dict`
**Назначение:** Получает общую статистику базы данных.

**Возвращает:** `dict` - Статистика по всем таблицам

#### `get_table_list() -> list`
**Назначение:** Получает список всех таблиц.

#### `get_table_info(table_name: str) -> dict`
**Назначение:** Получает детальную информацию о таблице.

**Параметры:**
- `table_name` (str): Название таблицы

**Возвращает:** `dict` - Информация о таблице (количество записей, размер, время обновления)

#### `get_all_tables_info() -> dict`
**Назначение:** Получает информацию о всех таблицах за один запрос (оптимизированно).

**Возвращает:** `dict` - Словарь с информацией о всех таблицах

## 🔧 Правила использования API

### 1. **Инициализация подключения**

```python
# Автоматическая инициализация при импорте
from database.db_api import save_user, get_user

# Ручная инициализация (если нужно)
from database.database_interface import DatabaseInterface
db = DatabaseInterface()
```

### 2. **Обработка ошибок**

```python
try:
    success = save_user(user_data)
    if success:
        print("Операция выполнена успешно")
    else:
        print("Ошибка выполнения операции")
except Exception as e:
    print(f"Критическая ошибка: {e}")
```

### 3. **Проверка существования данных**

```python
# Всегда проверяйте результат перед использованием
user = get_user(user_id)
if user:
    # Пользователь найден
    print(f"Пользователь: {user['first_name']}")
else:
    # Пользователь не найден
    print("Пользователь не найден")
```

### 4. **Использование транзакций**

```python
# API автоматически управляет транзакциями
# Каждая функция выполняется в своей транзакции
# При ошибке транзакция откатывается автоматически
```

## 🚨 Важные ограничения

### 1. **Типы данных**
- `user_id` всегда должен быть `int`
- `city` должен быть словарем с ключами `id` и `title`
- `sex` должен быть `1` (женский) или `2` (мужской)

### 2. **Ограничения базы данных**
- Максимальная длина сообщения: 1000 символов
- Максимальная длина URL фотографии: 500 символов
- Максимальная длина имени/фамилии: 100 символов

### 3. **Производительность**
- Используйте `get_all_tables_info()` вместо множественных вызовов `get_table_info()`
- Для больших выборок используйте параметр `limit`
- Избегайте частых вызовов `get_database_stats()`

## 🔍 Отладка и мониторинг

### Логирование
```python
import logging
logger = logging.getLogger('database')

# API автоматически логирует все операции
# Уровни логирования: DEBUG, INFO, WARNING, ERROR
```

### Проверка состояния
```python
from database.db_api import get_database_stats

stats = get_database_stats()
print(f"Всего пользователей: {stats.get('vk_users', 0)}")
print(f"Всего сообщений: {stats.get('bot_messages', 0)}")
```

## 📝 Примеры использования

### Полный цикл работы с пользователем

```python
from database.db_api import *

# 1. Сохранение пользователя
user_data = {
    'id': 123456789,
    'first_name': 'Анна',
    'last_name': 'Петрова',
    'sex': 1,
    'bdate': '15.05.1990',
    'city': {'id': 1, 'title': 'Москва'},
    'photo_url': 'https://vk.com/photo123'
}

if save_user(user_data):
    print("Пользователь сохранен")

# 2. Сохранение фотографий
photos_data = [
    {
        'url': 'https://vk.com/photo123',
        'likes_count': 15,
        'photo_type': 'profile'
    },
    {
        'url': 'https://vk.com/photo124',
        'likes_count': 8,
        'photo_type': 'tagged'
    }
]

if save_photos(123456789, photos_data):
    print("Фотографии сохранены")

# 3. Добавление в избранное
if add_to_favorites(987654321, 123456789):
    print("Пользователь добавлен в избранное")

# 4. Сохранение настроек
settings = {
    'age_from': 25,
    'age_to': 35,
    'sex_preference': 2,
    'city_preference': {'id': 1, 'title': 'Москва'}
}

if save_user_settings(987654321, settings):
    print("Настройки сохранены")

# 5. Получение данных
user = get_user(123456789)
favorites = get_favorites(987654321, limit=5)
photos = get_photos(123456789)
```

### Работа с избранным и черным списком

```python
# Проверка перед добавлением
if not is_in_favorites(user_id, target_id):
    add_to_favorites(user_id, target_id)
    print("Добавлено в избранное")
else:
    print("Уже в избранном")

# Проверка черного списка перед показом
if not is_user_blacklisted(user_id, target_id):
    # Показать пользователя
    pass
else:
    # Пропустить пользователя
    pass
```

## 🛠️ Устранение неполадок

### Частые проблемы:

1. **Ошибка подключения к базе данных**
   - Проверьте, запущен ли PostgreSQL
   - Проверьте настройки в `.env` файле

2. **Ошибка "table does not exist"**
   - Выполните `python src/database/db_cli.py create`

3. **Ошибка "foreign key constraint"**
   - Убедитесь, что пользователь существует перед сохранением связанных данных

4. **Медленная работа**
   - Используйте `get_all_tables_info()` вместо множественных вызовов
   - Проверьте индексы в базе данных

### Команды для диагностики:

```bash
# Проверка статуса PostgreSQL
python src/database/db_cli.py postgres-status

# Просмотр логов
python src/database/db_cli.py logs

# Очистка данных (ОСТОРОЖНО!)
python src/database/db_cli.py clear
```

## 📚 Дополнительные ресурсы

- [README_BD.md](README_BD.md) - Общее описание базы данных
- [DATABASE_CLI_GUIDE.md](DATABASE_CLI_GUIDE.md) - Руководство по CLI базы данных
- [src/database/models.py](src/database/models.py) - Модели данных
- [src/database/database_interface.py](src/database/database_interface.py) - Низкоуровневый API
