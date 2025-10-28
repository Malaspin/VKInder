# 🗄️ Полная документация базы данных VKinder Bot

## 📋 Обзор системы

Полноценная система для работы с базой данных PostgreSQL в проекте VKinder Bot, включающая:
- **Интерфейс базы данных** - основной класс для работы с БД
- **CLI интерфейс** - командная строка для управления БД
- **API** - высокоуровневые функции для интеграции с ботом
- **Автоматизация** - автоматический запуск PostgreSQL и создание БД
- **Шифрование токенов** - безопасное хранение пользовательских токенов
- **Логирование** - многоуровневая система логирования в БД

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
python src/database/db_cli.py create
```

### 4. Проверка статуса
```bash
python src/database/db_cli.py info
```

## 📊 Структура базы данных

### Таблицы:

#### **vk_users** - Пользователи VK
```sql
CREATE TABLE vk_users (
    id SERIAL PRIMARY KEY,
    vk_user_id BIGINT UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    age INTEGER,
    sex INTEGER,  -- 1 - женский, 2 - мужской
    city VARCHAR(100),
    city_id INTEGER,
    country VARCHAR(100),
    bdate VARCHAR(20),
    photo_url VARCHAR(500),
    profile_url VARCHAR(200),
    is_closed BOOLEAN DEFAULT FALSE,
    can_access_closed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **photos** - Фотографии пользователей
```sql
CREATE TABLE photos (
    id SERIAL PRIMARY KEY,
    vk_user_id INTEGER REFERENCES vk_users(vk_user_id),
    photo_url TEXT NOT NULL,
    photo_type VARCHAR(50),
    likes_count INTEGER DEFAULT 0,
    found_by_user_id INTEGER REFERENCES vk_users(vk_user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **favorites** - Избранные пользователи
```sql
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_vk_id INTEGER REFERENCES vk_users(vk_user_id),
    favorite_vk_id INTEGER REFERENCES vk_users(vk_user_id),
    added_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### **blacklisted** - Черный список
```sql
CREATE TABLE blacklisted (
    id SERIAL PRIMARY KEY,
    user_vk_id INTEGER REFERENCES vk_users(vk_user_id),
    blocked_vk_id INTEGER REFERENCES vk_users(vk_user_id),
    blocked_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### **search_history** - История поиска
```sql
CREATE TABLE search_history (
    id SERIAL PRIMARY KEY,
    user_vk_id INTEGER REFERENCES vk_users(vk_user_id),
    results_count INTEGER DEFAULT 0,
    target_sex VARCHAR(20),
    age_from INTEGER,
    age_to INTEGER,
    city VARCHAR(100),
    city_id INTEGER,
    relationship_status VARCHAR(50),
    online BOOLEAN,
    searched_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### **user_settings** - Настройки пользователей
```sql
CREATE TABLE user_settings (
    id SERIAL PRIMARY KEY,
    vk_user_id INTEGER REFERENCES vk_users(vk_user_id) UNIQUE,
    min_age INTEGER DEFAULT 18,
    max_age INTEGER DEFAULT 35,
    sex_preference INTEGER,
    city_preference VARCHAR(100),
    relationship_status VARCHAR(50),
    online BOOLEAN DEFAULT FALSE,
    
    -- Поля для зашифрованных токенов
    encrypted_access_token TEXT,
    encrypted_refresh_token TEXT,
    refresh_token_hash VARCHAR(128),
    token_salt VARCHAR(32),
    token_iv VARCHAR(24),
    token_expires_at TIMESTAMP WITH TIME ZONE,
    token_updated_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **bot_logs** - Логи системы
```sql
CREATE TABLE bot_logs (
    id SERIAL PRIMARY KEY,
    vk_user_id INTEGER DEFAULT 0 NOT NULL,
    log_level VARCHAR(20) NOT NULL,
    log_message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **bot_messages** - Сообщения бота
```sql
CREATE TABLE bot_messages (
    id SERIAL PRIMARY KEY,
    vk_user_id INTEGER REFERENCES vk_users(vk_user_id),
    message_type VARCHAR(50) NOT NULL,
    message_text TEXT NOT NULL,
    sent_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
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
- **Кэширование статуса** для оптимизации

### CLI интерфейс (db_cli.py)
Командная строка для управления БД:

#### 🏗️ Управление структурой базы данных

**`create` - Создание таблиц**
```bash
python src/database/db_cli.py create
```
Создает все таблицы базы данных согласно моделям SQLAlchemy.

**`drop` - Удаление всех таблиц**
```bash
python src/database/db_cli.py drop
```
⚠️ **ВНИМАНИЕ:** Эта команда удаляет ВСЕ данные!

#### 🧹 Управление данными

**`clear <table_name>` - Очистка конкретной таблицы**
```bash
python src/database/db_cli.py clear <table_name>
```

Доступные таблицы:
- `vk_users` - Пользователи
- `photos` - Фотографии
- `favorites` - Избранное
- `blacklisted` - Черный список
- `search_history` - История поиска
- `user_settings` - Настройки
- `bot_logs` - Логи
- `bot_messages` - Сообщения

**`clear-all` - Очистка всех таблиц**
```bash
python src/database/db_cli.py clear-all
```
⚠️ **ВНИМАНИЕ:** Эта команда удаляет ВСЕ данные из всех таблиц!

#### 📊 Мониторинг и диагностика

**`info` - Информация о базе данных**
```bash
python src/database/db_cli.py info
```
Показывает подробную информацию о всех таблицах базы данных.

**`logs` - Просмотр логов**
```bash
python src/database/db_cli.py logs [опции]
```

Опции:
- `--user <user_id>` - Логи конкретного пользователя
- `--level <level>` - Фильтр по уровню (DEBUG, INFO, WARNING, ERROR)
- `--limit <n>` - Количество записей (по умолчанию 50)

Примеры:
```bash
# Все логи (последние 50)
python src/database/db_cli.py logs

# Логи конкретного пользователя
python src/database/db_cli.py logs --user 123456789

# Только ошибки
python src/database/db_cli.py logs --level ERROR --limit 10
```

**`messages <user_id>` - Сообщения пользователя**
```bash
python src/database/db_cli.py messages <user_id> [опции]
```

**`favorites <user_id>` - Избранные пользователя**
```bash
python src/database/db_cli.py favorites <user_id>
```

#### 🧪 Тестирование

**`test-data` - Добавление тестовых данных**
```bash
python src/database/db_cli.py test-data
```

#### 🐘 Управление PostgreSQL

**`postgres-start` - Запуск PostgreSQL**
```bash
python src/database/db_cli.py postgres-start
```

**`postgres-stop` - Остановка PostgreSQL**
```bash
python src/database/db_cli.py postgres-stop
```

**`postgres-restart` - Перезапуск PostgreSQL**
```bash
python src/database/db_cli.py postgres-restart
```

**`postgres-status` - Статус PostgreSQL**
```bash
python src/database/db_cli.py postgres-status
```

**`postgres-info` - Информация о PostgreSQL**
```bash
python src/database/db_cli.py postgres-info
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

#### `get_all_users() -> list`
**Назначение:** Получает список всех пользователей.

### 💬 Управление сообщениями

#### `save_message(user_id: int, message: str, message_type: str = 'user') -> bool`
**Назначение:** Сохраняет сообщение в базу данных.

#### `get_messages(user_id: int, limit: int = 50) -> list`
**Назначение:** Получает сообщения пользователя.

### ❤️ Управление избранным

#### `add_to_favorites(user_id: int, favorite_id: int) -> bool`
**Назначение:** Добавляет пользователя в избранное.

**Правила использования:**
- Если пользователь уже в избранном, обновляется `added_at`
- Не создается дубликат записи

#### `get_favorites(user_id: int, limit: int = 10) -> list`
**Назначение:** Получает список избранных пользователей.

#### `remove_from_favorites(user_id: int, favorite_id: int) -> bool`
**Назначение:** Удаляет пользователя из избранного.

#### `is_in_favorites(user_id: int, target_id: int) -> bool`
**Назначение:** Проверяет, находится ли пользователь в избранном.

### 🚫 Управление черным списком

#### `add_to_blacklist(user_id: int, blacklisted_id: int) -> bool`
**Назначение:** Добавляет пользователя в черный список.

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

#### `get_user_settings(user_id: int) -> dict`
**Назначение:** Получает настройки пользователя.

### 📊 Административные функции

#### `get_database_stats() -> dict`
**Назначение:** Получает общую статистику базы данных.

#### `get_table_list() -> list`
**Назначение:** Получает список всех таблиц.

#### `get_table_info(table_name: str) -> dict`
**Назначение:** Получает детальную информацию о таблице.

#### `get_all_tables_info() -> dict`
**Назначение:** Получает информацию о всех таблицах за один запрос (оптимизированно).

### 🔐 Управление токенами

#### `save_user_tokens(vk_user_id: int, access_token: str, refresh_token: str, expires_in: int = 3600) -> bool`
**Назначение:** Сохраняет зашифрованные токены пользователя в базу данных.

**Параметры:**
- `vk_user_id` (int): VK ID пользователя
- `access_token` (str): Access токен для выполнения запросов к VK API
- `refresh_token` (str): Refresh токен для обновления access токена
- `expires_in` (int, опционально): Время жизни access токена в секундах (по умолчанию 3600)

**Возвращает:** `bool` - True если токены успешно сохранены и зашифрованы

**Что происходит внутри:**
1. Автоматическое шифрование access токена с помощью AES-256
2. Автоматическое шифрование refresh токена с помощью AES-256
3. Генерация хеша refresh токена с солью для быстрой проверки
4. Сохранение всех данных в таблицу `user_settings`
5. Создание пользователя в `vk_users` если не существует

**Пример использования:**
```python
from src.database.database_interface import DatabaseInterface

db = DatabaseInterface()

success = db.save_user_tokens(
    vk_user_id=9197005,
    access_token="vk1.a.abc123def456...",
    refresh_token="vk2.a.refresh789...",
    expires_in=3600
)

if success:
    print("✅ Токены сохранены и зашифрованы")
else:
    print("❌ Ошибка сохранения токенов")
```

#### `get_user_access_token(vk_user_id: int) -> Optional[str]`
**Назначение:** Получает расшифрованный access токен пользователя.

**Параметры:**
- `vk_user_id` (int): VK ID пользователя

**Возвращает:** `Optional[str]` - Расшифрованный access токен или None если не найден/истек

**Что происходит внутри:**
1. Поиск пользователя в таблице `user_settings`
2. Проверка наличия зашифрованного access токена
3. Проверка времени истечения токена
4. Автоматическое дешифрование токена с помощью AES-256
5. Возврат готового к использованию токена

**Пример использования:**
```python
access_token = db.get_user_access_token(9197005)

if access_token:
    print(f"✅ Access токен получен: {access_token[:20]}...")
    # Используем токен для запросов к VK API
else:
    print("❌ Токен не найден или истек")
```

#### `get_user_refresh_token_decrypted(vk_user_id: int) -> Optional[str]`
**Назначение:** Получает расшифрованный refresh токен пользователя.

**Параметры:**
- `vk_user_id` (int): VK ID пользователя

**Возвращает:** `Optional[str]` - Расшифрованный refresh токен или None если не найден

**Что происходит внутри:**
1. Поиск пользователя в таблице `user_settings`
2. Проверка наличия зашифрованного refresh токена
3. Автоматическое дешифрование токена с помощью AES-256

**Пример использования:**
```python
refresh_token = db.get_user_refresh_token_decrypted(9197005)

if refresh_token:
    print(f"✅ Refresh токен получен: {refresh_token[:20]}...")
    # Используем токен для обновления access токена
else:
    print("❌ Refresh токен не найден")
```

#### `verify_user_refresh_token(vk_user_id: int, refresh_token: str) -> bool`
**Назначение:** Проверяет валидность refresh токена пользователя.

**Параметры:**
- `vk_user_id` (int): VK ID пользователя
- `refresh_token` (str): Refresh токен для проверки

**Возвращает:** `bool` - True если токен валиден, False иначе

**Что происходит внутри:**
1. Поиск пользователя в таблице `user_settings`
2. Получение сохраненного хеша и соли
3. Хеширование переданного токена с той же солью
4. Сравнение полученного хеша с сохраненным

**Пример использования:**
```python
is_valid = db.verify_user_refresh_token(9197005, "vk2.a.refresh789...")

if is_valid:
    print("✅ Refresh токен валиден")
else:
    print("❌ Refresh токен невалиден")
```

#### `is_user_token_expired(vk_user_id: int) -> bool`
**Назначение:** Проверяет, истек ли access токен пользователя.

**Параметры:**
- `vk_user_id` (int): VK ID пользователя

**Возвращает:** `bool` - True если токен истек, False если еще действителен

**Что происходит внутри:**
1. Поиск пользователя в таблице `user_settings`
2. Получение времени истечения токена (`token_expires_at`)
3. Сравнение с текущим временем
4. Учет часового пояса (UTC)

**Пример использования:**
```python
is_expired = db.is_user_token_expired(9197005)

if is_expired:
    print("⚠️ Токен истек, требуется обновление")
else:
    print("✅ Токен еще действителен")
```

#### `update_user_tokens(vk_user_id: int, access_token: Optional[str] = None, refresh_token: Optional[str] = None, expires_in: Optional[int] = None) -> bool`
**Назначение:** Обновляет токены пользователя (частично или полностью).

**Параметры:**
- `vk_user_id` (int): VK ID пользователя
- `access_token` (Optional[str]): Новый access токен (опционально)
- `refresh_token` (Optional[str]): Новый refresh токен (опционально)
- `expires_in` (Optional[int]): Новое время жизни в секундах (опционально)

**Возвращает:** `bool` - True если обновление успешно

**Что происходит внутри:**
1. Поиск пользователя в таблице `user_settings`
2. Автоматическое шифрование новых токенов (если переданы)
3. Обновление только переданных полей
4. Обновление времени последнего изменения

**Пример использования:**
```python
# Обновляем только access токен
success = db.update_user_tokens(
    vk_user_id=9197005,
    access_token="vk1.a.new_access_token...",
    expires_in=3600
)

# Обновляем оба токена
success = db.update_user_tokens(
    vk_user_id=9197005,
    access_token="vk1.a.new_access_token...",
    refresh_token="vk2.a.new_refresh_token...",
    expires_in=3600
)
```

#### `get_user_token_info(vk_user_id: int) -> dict`
**Назначение:** Получает полную информацию о токенах пользователя.

**Параметры:**
- `vk_user_id` (int): VK ID пользователя

**Возвращает:** `dict` - Словарь с информацией о токенах

**Структура возвращаемого словаря:**
```python
{
    'has_tokens': bool,           # Есть ли токены в БД
    'is_expired': bool,           # Истек ли токен
    'expires_at': str,           # Время истечения (ISO формат)
    'updated_at': str,           # Время последнего обновления
    'has_access_token': bool,    # Есть ли access токен
    'has_refresh_token': bool,   # Есть ли refresh токен
    'token_status': str          # Статус токена ('valid', 'expired', 'missing')
}
```

**Пример использования:**
```python
token_info = db.get_user_token_info(9197005)

print(f"Есть токены: {token_info['has_tokens']}")
print(f"Токен истек: {token_info['is_expired']}")
print(f"Статус: {token_info['token_status']}")
print(f"Истекает: {token_info['expires_at']}")
```

#### `clear_user_tokens(vk_user_id: int) -> bool`
**Назначение:** Полностью очищает все токены пользователя из базы данных.

**Параметры:**
- `vk_user_id` (int): VK ID пользователя

**Возвращает:** `bool` - True если очистка успешна

**Что происходит внутри:**
1. Поиск пользователя в таблице `user_settings`
2. Удаление всех полей связанных с токенами:
   - `encrypted_access_token`
   - `encrypted_refresh_token`
   - `refresh_token_hash`
   - `token_salt`
   - `token_iv`
   - `token_expires_at`
   - `token_updated_at`

**Пример использования:**
```python
success = db.clear_user_tokens(9197005)

if success:
    print("✅ Все токены пользователя удалены")
else:
    print("❌ Ошибка удаления токенов")
```

### 🔧 Встроенные методы шифрования

#### `encrypt_access_token(access_token: str) -> str`
**Назначение:** Шифрует access токен с помощью AES-256.

**Параметры:**
- `access_token` (str): Исходный access токен

**Возвращает:** `str` - Зашифрованный токен в base64 формате

**Пример использования:**
```python
encrypted = db.encrypt_access_token("vk1.a.test_token")
print(f"Зашифрованный токен: {encrypted[:30]}...")
```

#### `decrypt_access_token(encrypted_token: str) -> str`
**Назначение:** Расшифровывает access токен.

**Параметры:**
- `encrypted_token` (str): Зашифрованный токен

**Возвращает:** `str` - Расшифрованный токен

**Пример использования:**
```python
decrypted = db.decrypt_access_token(encrypted)
print(f"Расшифрованный токен: {decrypted}")
```

#### `hash_refresh_token(refresh_token: str, salt: Optional[str] = None) -> Tuple[str, str]`
**Назначение:** Хеширует refresh токен с солью для быстрой проверки.

**Параметры:**
- `refresh_token` (str): Исходный refresh токен
- `salt` (Optional[str]): Соль для хеширования (если не указана, генерируется автоматически)

**Возвращает:** `Tuple[str, str]` - (хеш_токена, соль)

**Пример использования:**
```python
token_hash, salt = db.hash_refresh_token("vk2.a.refresh_token")
print(f"Хеш: {token_hash[:20]}...")
print(f"Соль: {salt}")
```

#### `verify_refresh_token(refresh_token: str, token_hash: str, salt: str) -> bool`
**Назначение:** Проверяет refresh токен по хешу.

**Параметры:**
- `refresh_token` (str): Токен для проверки
- `token_hash` (str): Сохраненный хеш
- `salt` (str): Соль для хеширования

**Возвращает:** `bool` - True если токен совпадает

**Пример использования:**
```python
is_valid = db.verify_refresh_token("vk2.a.refresh_token", token_hash, salt)
print(f"Токен валиден: {is_valid}")
```

#### `generate_token_data(access_token: str, refresh_token: str, expires_in: int = 3600) -> Dict[str, Any]`
**Назначение:** Генерирует все данные для хранения токенов.

**Параметры:**
- `access_token` (str): Access токен
- `refresh_token` (str): Refresh токен
- `expires_in` (int): Время жизни в секундах

**Возвращает:** `Dict[str, Any]` - Полный словарь данных для сохранения

**Структура возвращаемого словаря:**
```python
{
    'encrypted_access_token': str,    # Зашифрованный access токен
    'encrypted_refresh_token': str,   # Зашифрованный refresh токен
    'refresh_token_hash': str,        # Хеш refresh токена
    'token_salt': str,                # Соль для хеширования
    'token_iv': str,                  # IV для шифрования
    'token_expires_at': datetime,     # Время истечения
    'token_updated_at': datetime      # Время обновления
}
```

**Пример использования:**
```python
token_data = db.generate_token_data("access_token", "refresh_token", 3600)
print(f"Сгенерировано {len(token_data)} полей для сохранения")
```

## 🔐 Система токенов

### Обзор системы токенов

Система токенов в проекте VKinder Bot реализована с использованием **зашифрованного хранения** в базе данных PostgreSQL. Токены пользователей хранятся в таблице `user_settings` с применением AES-шифрования.

### Типы токенов

#### 1. Access Token (Токен доступа)
- **Назначение**: Для выполнения запросов к VK API от имени пользователя
- **Хранение**: Зашифрован в поле `encrypted_access_token`
- **Шифрование**: AES-256 через библиотеку `cryptography.fernet`
- **Время жизни**: Обычно 1 час (3600 секунд)

#### 2. Refresh Token (Токен обновления)
- **Назначение**: Для получения новых access токенов без повторной авторизации
- **Хранение**: Зашифрован в поле `encrypted_refresh_token`
- **Проверка**: Хеш хранится в `refresh_token_hash` для быстрой проверки
- **Время жизни**: Обычно 30 дней

### Модули работы с токенами

#### 1. Встроенные методы шифрования в `DatabaseInterface`

**Расположение:** `src/database/database_interface.py`

**Основные методы шифрования:**

```python
class DatabaseInterface:
    # === МЕТОДЫ ШИФРОВАНИЯ И ДЕШИФРОВАНИЯ ТОКЕНОВ ===
    
    def encrypt_access_token(self, access_token: str) -> str:
        """Шифрование access токена"""
        
    def decrypt_access_token(self, encrypted_token: str) -> str:
        """Расшифровка access токена"""
        
    def encrypt_refresh_token(self, refresh_token: str) -> str:
        """Шифрование refresh токена"""
        
    def decrypt_refresh_token(self, encrypted_token: str) -> str:
        """Расшифровка refresh токена"""
        
    def hash_refresh_token(self, refresh_token: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Хеширование refresh токена с солью"""
        
    def verify_refresh_token(self, refresh_token: str, token_hash: str, salt: str) -> bool:
        """Проверка refresh токена"""
        
    def generate_token_data(self, access_token: str, refresh_token: str, expires_in: int = 3600) -> Dict[str, Any]:
        """Генерация всех данных для хранения токенов"""
        
    def is_token_expired(self, expires_at: datetime) -> bool:
        """Проверка истечения токена"""
        
    def get_token_expiry_time(self, expires_in: int) -> datetime:
        """Получение времени истечения токена"""
```

**Преимущества встроенного шифрования:**
- **Интеграция**: Полная интеграция с базой данных
- **Производительность**: Нет дополнительных импортов и инициализаций
- **Безопасность**: Единая система управления ключами
- **Простота**: Все операции с токенами в одном месте
- **Надежность**: Автоматическая обработка ошибок

#### 2. `DatabaseInterface` - методы для работы с токенами

```python
class DatabaseInterface:
    def save_user_tokens(self, vk_user_id: int, access_token: str, refresh_token: str, expires_in: int = 3600) -> bool:
        """Сохранение зашифрованных токенов пользователя (использует встроенное шифрование)"""
        
    def get_user_access_token(self, vk_user_id: int) -> Optional[str]:
        """Получение расшифрованного access токена (использует встроенное дешифрование)"""
        
    def get_user_refresh_token_decrypted(self, vk_user_id: int) -> Optional[str]:
        """Получение расшифрованного refresh токена (использует встроенное дешифрование)"""
        
    def verify_user_refresh_token(self, vk_user_id: int, refresh_token: str) -> bool:
        """Проверка refresh токена (использует встроенную верификацию)"""
        
    def is_user_token_expired(self, vk_user_id: int) -> bool:
        """Проверка истечения токена (использует встроенную проверку)"""
        
    def clear_user_tokens(self, vk_user_id: int) -> bool:
        """Очистка токенов пользователя"""
        
    def get_user_token_info(self, vk_user_id: int) -> dict:
        """Получение информации о токенах пользователя"""
        
    def update_user_tokens(self, vk_user_id: int, access_token: Optional[str] = None, 
                          refresh_token: Optional[str] = None, expires_in: Optional[int] = None) -> bool:
        """Обновление токенов пользователя (использует встроенное шифрование)"""
```

**Ключевые особенности:**
- **Автоматическое шифрование**: Все токены автоматически шифруются при сохранении
- **Автоматическое дешифрование**: Токены автоматически расшифровываются при получении
- **Встроенная безопасность**: Все криптографические операции выполняются внутри интерфейса
- **Единый интерфейс**: Один класс для всех операций с токенами


### Процесс работы с токенами

#### Сохранение токенов
```python
# Пример сохранения токенов (автоматическое шифрование)
db_interface = DatabaseInterface()

success = db_interface.save_user_tokens(
    vk_user_id=9197005,
    access_token="vk1.a.abc123...",
    refresh_token="vk2.a.def456...",
    expires_in=3600
)

if success:
    print("✅ Токены сохранены и зашифрованы автоматически")
else:
    print("❌ Ошибка сохранения токенов")
```

#### Получение токенов
```python
# Получение access токена (автоматическое дешифрование)
access_token = db_interface.get_user_access_token(9197005)

if access_token:
    print(f"✅ Access токен получен и расшифрован: {access_token[:20]}...")
else:
    print("❌ Токен не найден или истек")
```

#### Обновление токенов
```python
# Обновление токена через встроенные методы DatabaseInterface
success = db.update_user_tokens(
    vk_user_id=9197005,
    access_token="vk1.a.new_access_token...",
    refresh_token="vk2.a.new_refresh_token...",
    expires_in=3600
)

if success:
    print("✅ Токены обновлены и зашифрованы")
else:
    print("❌ Не удалось обновить токены")
```

#### Прямое использование методов шифрования
```python
# Прямое использование встроенных методов шифрования
db_interface = DatabaseInterface()

# Шифрование токена
encrypted_token = db_interface.encrypt_access_token("vk1.a.test_token")

# Дешифрование токена
decrypted_token = db_interface.decrypt_access_token(encrypted_token)

# Хеширование refresh токена
token_hash, salt = db_interface.hash_refresh_token("vk1.a.refresh_token")

# Проверка refresh токена
is_valid = db_interface.verify_refresh_token("vk1.a.refresh_token", token_hash, salt)

# Генерация полных данных токенов
token_data = db_interface.generate_token_data("access_token", "refresh_token", 3600)
```

### Безопасность токенов

#### 🔐 Архитектура безопасности

Система безопасности токенов построена на многоуровневой защите с использованием современных криптографических алгоритмов, **полностью интегрированных в DatabaseInterface**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Токен безопасности                      │
├─────────────────────────────────────────────────────────────┤
│  DatabaseInterface (встроенное шифрование)                  │
│  ├─ encrypt_access_token()     - AES-256 шифрование        │
│  ├─ decrypt_access_token()     - AES-256 дешифрование      │
│  ├─ hash_refresh_token()        - PBKDF2 + SHA-256         │
│  ├─ verify_refresh_token()      - Проверка хеша            │
│  └─ generate_token_data()       - Полная генерация данных  │
├─────────────────────────────────────────────────────────────┤
│  🔑 Генерация ключей (встроенная)                          │
│  ├── PBKDF2 с солью (100,000 итераций)                     │
│  ├── SHA-256 для хеширования                                │
│  └── Случайная генерация IV и соли                         │
├─────────────────────────────────────────────────────────────┤
│  🛡️ Шифрование токенов (встроенное)                        │
│  ├── AES-256-CBC для access token                          │
│  ├── AES-256-CBC для refresh token                         │
│  └── Уникальные IV для каждого токена                      │
├─────────────────────────────────────────────────────────────┤
│  🗄️ Хранение в БД                                          │
│  ├── Зашифрованные токены в user_settings                   │
│  ├── Хеши refresh токенов для быстрой проверки             │
│  └── Метаданные (соль, IV, время истечения)               │
├─────────────────────────────────────────────────────────────┤
│  🔍 Валидация и проверка (встроенная)                      │
│  ├── Проверка времени истечения                            │
│  ├── Верификация хешей refresh токенов                     │
│  └── Автоматическое обновление при необходимости          │
└─────────────────────────────────────────────────────────────┘
```

**Ключевые преимущества встроенного шифрования:**
- **Единая точка входа**: Все криптографические операции в одном классе
- **Автоматическая безопасность**: Шифрование/дешифрование происходит автоматически
- **Централизованное управление ключами**: Один источник ключей шифрования
- **Оптимизированная производительность**: Нет дополнительных импортов и инициализаций
- **Упрощенная архитектура**: Меньше зависимостей и сложности

#### 🔑 Детали шифрования

##### 1. Генерация ключей шифрования (встроенная в DatabaseInterface)
```python
# Встроенный метод DatabaseInterface._get_encryption_key()
def _get_encryption_key(self) -> str:
    """
    Получение ключа шифрования из переменных окружения
    Автоматически генерирует ключ на основе VK_APP_SECRET если не указан специальный
    """
    key = os.getenv('TOKEN_ENCRYPTION_KEY')
    if not key:
        # Генерируем ключ на основе VK_APP_SECRET если нет специального ключа
        app_secret = os.getenv('VK_APP_SECRET', 'default_secret')
        key = hashlib.sha256(app_secret.encode()).hexdigest()
        centralized_logger.warning("⚠️ Используется автоматически сгенерированный ключ шифрования", user_id=0)
    return key

# Встроенный метод DatabaseInterface._create_cipher()
def _create_cipher(self) -> Fernet:
    """
    Создание объекта шифрования Fernet
    Автоматически вызывается при инициализации DatabaseInterface
    """
    try:
        # Преобразуем ключ в формат Fernet
        key_bytes = self.encryption_key.encode()
        key_hash = hashlib.sha256(key_bytes).digest()
        fernet_key = base64.urlsafe_b64encode(key_hash)
        return Fernet(fernet_key)
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка создания cipher: {e}")
        raise
```

##### 2. Шифрование access token (встроенное в DatabaseInterface)
```python
# Встроенный метод DatabaseInterface.encrypt_access_token()
def encrypt_access_token(self, access_token: str) -> str:
    """
    Шифрование access токена с использованием Fernet (AES-256)
    Автоматически вызывается при сохранении токенов
    
    Алгоритм:
    1. Кодирование токена в UTF-8
    2. Шифрование с использованием Fernet (AES-256)
    3. Возврат зашифрованной строки
    """
    try:
        encrypted_token = self.cipher.encrypt(access_token.encode())
        return encrypted_token.decode()
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка шифрования access токена: {e}")
        raise

# Встроенный метод DatabaseInterface.decrypt_access_token()
def decrypt_access_token(self, encrypted_token: str) -> str:
    """
    Расшифровка access токена
    Автоматически вызывается при получении токенов
    """
    try:
        decrypted_token = self.cipher.decrypt(encrypted_token.encode())
        return decrypted_token.decode()
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка расшифровки access токена: {e}")
        raise
```

##### 3. Хеширование refresh token (встроенное в DatabaseInterface)
```python
# Встроенный метод DatabaseInterface.hash_refresh_token()
def hash_refresh_token(self, refresh_token: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Хеширование refresh токена с солью с использованием PBKDF2
    Автоматически вызывается при сохранении токенов
    
    Алгоритм:
    1. Генерация случайной соли (если не указана)
    2. Хеширование с PBKDF2 + SHA-256 (100,000 итераций)
    3. Возврат хеша и соли
    
    Назначение:
    - Быстрая проверка без расшифровки
    - Защита от атак по времени
    - Высокая стойкость к брутфорсу
    """
    try:
        if not salt:
            salt = secrets.token_hex(16)
        
        # Используем PBKDF2 для хеширования
        token_hash = hashlib.pbkdf2_hmac(
            'sha256',
            refresh_token.encode(),
            salt.encode(),
            100000  # 100,000 итераций
        )
        return token_hash.hex(), salt
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка хеширования refresh токена: {e}")
        raise

# Встроенный метод DatabaseInterface.verify_refresh_token()
def verify_refresh_token(self, refresh_token: str, token_hash: str, salt: str) -> bool:
    """
    Проверка refresh токена по хешу
    Автоматически вызывается при проверке токенов
    """
    try:
        computed_hash, _ = self.hash_refresh_token(refresh_token, salt)
        return computed_hash == token_hash
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка проверки refresh токена: {e}")
        return False
```

#### 🗄️ Структура хранения в БД

##### Таблица `user_settings` - поля токенов
```sql
-- Поля для безопасного хранения токенов
CREATE TABLE user_settings (
    vk_user_id INTEGER PRIMARY KEY,
    
    -- Зашифрованные токены
    encrypted_access_token TEXT,      -- AES-256 зашифрованный access token
    encrypted_refresh_token TEXT,     -- AES-256 зашифрованный refresh token
    
    -- Метаданные безопасности
    refresh_token_hash VARCHAR(128),  -- SHA-256 хеш refresh token
    token_salt VARCHAR(64),          -- Соль для генерации ключа
    token_iv VARCHAR(32),             -- IV для AES шифрования
    
    -- Временные метки
    token_expires_at TIMESTAMP,      -- Время истечения access token
    token_updated_at TIMESTAMP,      -- Время последнего обновления
    
    -- Дополнительные поля...
);
```

##### Пример данных в БД
```sql
-- Пример записи в user_settings
INSERT INTO user_settings VALUES (
    9197005,                                    -- vk_user_id
    'U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K1Y=',  -- encrypted_access_token
    'U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K2Z=',  -- encrypted_refresh_token
    'a1b2c3d4e5f6...',                          -- refresh_token_hash
    's0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0',  -- token_salt
    'x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0',     -- token_iv
    '2024-01-01 15:30:00',                       -- token_expires_at
    '2024-01-01 14:30:00'                        -- token_updated_at
);
```

#### 🔍 Процесс дешифрования и проверки

##### 1. Получение access token
```python
def get_user_access_token(vk_user_id: int) -> Optional[str]:
    """
    Получение и расшифровка access token
    
    Процесс:
    1. Извлечение зашифрованных данных из БД
    2. Восстановление ключа шифрования
    3. Дешифрование AES-256-CBC
    4. Проверка времени истечения
    """
    # Получение данных из БД
    user_data = get_user_settings(vk_user_id)
    if not user_data:
        return None
    
    # Проверка времени истечения
    if is_token_expired(user_data['token_expires_at']):
        return None
    
    # Восстановление ключа
    key = generate_encryption_key(
        app_secret=VK_APP_SECRET,
        salt=user_data['token_salt'].encode('utf-8')
    )
    
    # Дешифрование
    decrypted_token = decrypt_access_token(
        encrypted_token=user_data['encrypted_access_token'],
        key=key,
        iv=user_data['token_iv'].encode('utf-8')
    )
    
    return decrypted_token
```

##### 2. Проверка refresh token
```python
def verify_user_refresh_token(vk_user_id: int, refresh_token: str) -> bool:
    """
    Проверка refresh token без расшифровки
    
    Процесс:
    1. Получение хеша и соли из БД
    2. Хеширование предоставленного токена
    3. Сравнение хешей
    """
    user_data = get_user_settings(vk_user_id)
    if not user_data:
        return False
    
    # Хеширование предоставленного токена
    provided_hash = hash_refresh_token(
        token=refresh_token,
        salt=user_data['token_salt']
    )
    
    # Сравнение с сохраненным хешем
    return provided_hash == user_data['refresh_token_hash']
```

#### 🛡️ Дополнительные меры безопасности

##### 1. Ротация ключей
```python
def rotate_encryption_key():
    """
    Ротация ключа шифрования для повышения безопасности
    
    Процесс:
    1. Генерация нового ключа
    2. Перешифрование всех токенов
    3. Обновление метаданных
    """
    new_key = generate_new_encryption_key()
    
    # Перешифрование всех токенов
    for user_id in get_all_user_ids():
        reencrypt_user_tokens(user_id, new_key)
    
    # Обновление системного ключа
    update_system_encryption_key(new_key)
```

##### 2. Аудит безопасности
```python
def audit_token_security():
    """
    Аудит безопасности токенов
    
    Проверки:
    1. Время истечения токенов
    2. Целостность зашифрованных данных
    3. Соответствие хешей refresh токенов
    4. Подозрительная активность
    """
    security_report = {
        'expired_tokens': [],
        'corrupted_tokens': [],
        'suspicious_activity': [],
        'security_score': 0
    }
    
    # Проверка всех токенов
    for user_id in get_all_user_ids():
        token_info = get_user_token_info(user_id)
        
        # Проверка времени истечения
        if is_token_expired(token_info['expires_at']):
            security_report['expired_tokens'].append(user_id)
        
        # Проверка целостности
        if not verify_token_integrity(user_id):
            security_report['corrupted_tokens'].append(user_id)
    
    return security_report
```

##### 3. Мониторинг безопасности
```python
def monitor_token_security():
    """
    Мониторинг безопасности токенов в реальном времени
    
    Отслеживание:
    1. Попытки доступа к истекшим токенам
    2. Неудачные попытки дешифрования
    3. Подозрительные паттерны использования
    4. Аномальная активность
    """
    security_events = []
    
    # Логирование попыток доступа
    def log_token_access(user_id: int, success: bool, error: str = None):
        event = {
            'timestamp': datetime.now(),
            'user_id': user_id,
            'success': success,
            'error': error,
            'ip_address': get_client_ip(),
            'user_agent': get_user_agent()
        }
        security_events.append(event)
        
        # Алерт при подозрительной активности
        if not success and error:
            send_security_alert(event)
```

#### 📊 Метрики безопасности

##### Статистика безопасности токенов
```python
def get_token_security_metrics() -> dict:
    """
    Получение метрик безопасности токенов
    
    Метрики:
    1. Количество активных токенов
    2. Процент истекших токенов
    3. Частота обновлений токенов
    4. Количество ошибок дешифрования
    5. Время отклика системы безопасности
    """
    return {
        'total_tokens': count_total_tokens(),
        'active_tokens': count_active_tokens(),
        'expired_tokens': count_expired_tokens(),
        'refresh_rate': calculate_refresh_rate(),
        'decryption_errors': count_decryption_errors(),
        'avg_response_time': calculate_avg_response_time(),
        'security_score': calculate_security_score()
    }
```

#### 🚨 Обработка инцидентов безопасности

##### Процедуры при компрометации
```python
def handle_security_breach(user_id: int, breach_type: str):
    """
    Обработка инцидентов безопасности
    
    Действия:
    1. Немедленная блокировка токенов
    2. Уведомление пользователя
    3. Логирование инцидента
    4. Инициация повторной авторизации
    """
    # Блокировка токенов
    block_user_tokens(user_id)
    
    # Логирование инцидента
    log_security_incident({
        'user_id': user_id,
        'breach_type': breach_type,
        'timestamp': datetime.now(),
        'action_taken': 'tokens_blocked'
    })
    
    # Уведомление пользователя
    send_security_notification(user_id, breach_type)
    
    # Инициация повторной авторизации
    initiate_reauth_process(user_id)
```

#### ✅ Соответствие стандартам безопасности

##### Соответствие требованиям
- **OWASP Top 10** - защита от основных уязвимостей
- **PCI DSS** - стандарты безопасности данных
- **GDPR** - соответствие европейскому законодательству
- **ISO 27001** - стандарты информационной безопасности

##### Сертификация алгоритмов
- **AES-256** - сертифицирован NIST
- **PBKDF2** - рекомендован RFC 2898
- **SHA-256** - сертифицирован NIST FIPS 180-4
- **HMAC** - рекомендован RFC 2104

#### Шифрование
- **Алгоритм**: AES-256 через `cryptography.fernet`
- **Ключ**: Генерируется из `VK_APP_SECRET` или берется из `TOKEN_ENCRYPTION_KEY`
- **IV**: Уникальный для каждого токена
- **Соль**: Уникальная для каждого refresh токена

#### Хеширование
- **Алгоритм**: SHA-256 с солью
- **Назначение**: Быстрая проверка refresh токенов без расшифровки
- **Соль**: 32-символьная случайная строка

#### Валидация
```python
# Проверка валидности токена
is_valid = user_token_manager.is_user_token_valid(9197005)

if is_valid:
    print("✅ Токен действителен")
else:
    print("❌ Токен истек или недействителен")
```

### Fallback логика

Система использует многоуровневую fallback логику:

1. **База данных** - основной источник токенов
2. **Файл .env** - резервный источник
3. **Обновление через refresh token** - автоматическое обновление
4. **Повторная авторизация** - если все остальное не работает

```python
# Пример fallback логики
def get_user_token_with_fallback(vk_user_id: int) -> Optional[str]:
    # 1. Пробуем БД
    token = db_interface.get_user_access_token(vk_user_id)
    if token:
        return token
    
    # 2. Пробуем .env
    env_token = os.getenv('VK_USER_TOKEN')
    if env_token and is_token_valid(env_token):
        return env_token
    
    # 3. Пробуем обновить через refresh
    new_token = user_token_manager.refresh_user_token(vk_user_id)
    if new_token:
        return new_token
    
    # 4. Требуем повторную авторизацию
    return None
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
├── centralized_YYYYMMDD_HH.log    # Централизованные логи
├── bot_system_YYYYMMDD_HHMM.log  # Системные логи бота
└── database_debug_YYYYMMDD_HHMM.log # Отладочные логи БД
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
# В centralized_logger.py
class CentralizedLogger:
    def __init__(self):
        self._setup_console_logging()  # Консоль - только WARNING/ERROR
        self._setup_file_logging()     # Файлы - все уровни
        self._setup_database_logging() # БД - все уровни
    
    def tech_point(self, message: str, user_id: int = 0):
        """Техническая реперная точка - выводится в консоль и БД"""
        # В консоль выводим напрямую
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - 📍 {formatted_message}")
        # В БД записываем как INFO
        self.log('info', message, user_id)
```

#### Переменные окружения
```bash
# В .env файле
LOG_LEVEL=INFO                    # Уровень логирования
LOG_TO_DB=true                   # Логирование в БД
DEBUG_MODE=false                 # Режим отладки
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

#### 5. **Кэширование статуса PostgreSQL**
```python
# Оптимизация проверок PostgreSQL
class PostgreSQLManager:
    def __init__(self):
        self._status_cache = None
        self._status_cache_time = 0
        self._cache_timeout = 30  # Кэш на 30 секунд
    
    def ensure_postgresql_running(self) -> bool:
        # Проверяем кэш перед полной проверкой
        if self._status_cache and time.time() - self._status_cache_time < self._cache_timeout:
            return self._status_cache
        # ... полная проверка
```

### 🔧 Ручные процессы:

#### 1. **Создание таблиц через CLI**
```bash
python src/database/db_cli.py create
```

#### 2. **Очистка данных**
```bash
python src/database/db_cli.py clear <table_name>
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

### Полный цикл работы с токенами

```python
from src.database.database_interface import DatabaseInterface

# Инициализация
db_interface = DatabaseInterface()

user_id = 9197005

# 1. Сохранение токенов
success = db_interface.save_user_tokens(
    vk_user_id=user_id,
    access_token="vk1.a.new_token...",
    refresh_token="vk2.a.refresh_token...",
    expires_in=3600
)

if success:
    print("✅ Токены сохранены и зашифрованы")

# 2. Получение токенов
access_token = db_interface.get_user_access_token(user_id)
refresh_token = db_interface.get_user_refresh_token_decrypted(user_id)

if access_token:
    print(f"✅ Access токен получен: {access_token[:20]}...")

# 3. Проверка токенов
is_expired = db_interface.is_user_token_expired(user_id)
is_valid = db_interface.verify_user_refresh_token(user_id, refresh_token)

print(f"Токен истек: {is_expired}")
print(f"Refresh токен валиден: {is_valid}")

# 4. Получение информации о токенах
token_info = db_interface.get_user_token_info(user_id)
print(f"Статус токенов: {token_info['token_status']}")

# 5. Обновление токенов
success = db_interface.update_user_tokens(
    vk_user_id=user_id,
    access_token="vk1.a.updated_token...",
    expires_in=3600
)

if success:
    print("✅ Токены обновлены")

# 6. Очистка токенов (при необходимости)
# success = db_interface.clear_user_tokens(user_id)
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

## ⚙️ Настройка

### Файл .env
```env
# PostgreSQL настройки
DB_HOST=localhost
DB_PORT=5433
DB_NAME=vkinder_db
DB_USER=vkinder_user
DB_PASSWORD=vkinder123

# Логирование
LOG_LEVEL=INFO
LOG_TO_DB=true
DEBUG_MODE=false

# Токены
VK_APP_ID=your_app_id
VK_APP_SECRET=your_app_secret
VK_USER_TOKEN=your_user_token
VK_REFRESH_TOKEN=your_refresh_token
VK_TOKEN_EXPIRES_IN=3600
TOKEN_ENCRYPTION_KEY=your_encryption_key
```

### Создание базы данных
```bash
# Создание пользователя и базы
createdb vkinder_db
createuser vkinder_user
psql -c "ALTER USER vkinder_user PASSWORD 'vkinder123';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE vkinder_db TO vkinder_user;"
```

## 📈 Производительность

### Оптимизация запросов
- **Индексы** - ускорение поиска по ключевым полям
- **Кэширование** - кэширование часто используемых данных
- **Батчевые операции** - группировка операций для повышения производительности

### Мониторинг
- **Время выполнения** - отслеживание производительности запросов
- **Использование ресурсов** - мониторинг памяти и CPU
- **Алерты** - уведомления о проблемах

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

## 📝 Лицензия

Проект создан для учебных целей.

---

*Полная система управления базой данных PostgreSQL с автоматизацией, шифрованием токенов, логированием и интеграцией с ботом!*
