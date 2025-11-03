# 🗄️ Полное руководство по API базы данных и CLI

## 📋 Оглавление

1. [Обзор](#обзор)
2. [Архитектура API](#архитектура-api)
3. [Высокоуровневое API (db_api.py)](#высокоуровневое-api-db_apipy)
4. [Низкоуровневое API (database_interface.py)](#низкоуровневое-api-database_interfacepy)
5. [CLI интерфейс (db_cli.py)](#cli-интерфейс-db_clipy)
6. [Модели данных](#модели-данных)
7. [Примеры использования](#примеры-использования)
8. [Обработка ошибок](#обработка-ошибок)

---

## 🎯 Обзор

Система работы с базой данных VKinder Bot состоит из трех основных уровней:

1. **Высокоуровневое API** (`db_api.py`) - простые функции для использования в коде бота
2. **Низкоуровневое API** (`database_interface.py`) - класс с полным контролем операций
3. **CLI интерфейс** (`db_cli.py`) - командная строка для управления БД

---

## 🏗️ Архитектура API

```
┌─────────────────────────────────────────────────────────────┐
│              Application Code (Bot, Tests)                 │
├─────────────────────────────────────────────────────────────┤
│  📊 High-Level API (db_api.py)                             │
│  ├── Простые функции                                        │
│  ├── Автоматическое управление сессиями                     │
│  └── Обработка ошибок                                       │
├─────────────────────────────────────────────────────────────┤
│  🔧 Low-Level API (database_interface.py)                 │
│  ├── DatabaseInterface класс                               │
│  ├── Прямая работа с сессиями                              │
│  ├── Шифрование токенов                                    │
│  └── Управление подключением                                │
├─────────────────────────────────────────────────────────────┤
│  🗄️ SQLAlchemy ORM (models.py)                             │
│  └── Модели данных                                          │
├─────────────────────────────────────────────────────────────┤
│  🐘 PostgreSQL Database                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Высокоуровневое API (db_api.py)

### Инициализация

```python
from src.database.db_api import get_db_interface

# Получение интерфейса БД (создается автоматически при первом вызове)
db = get_db_interface()
```

### Управление базой данных

#### `create_database() -> bool`
Создание всех таблиц базы данных.

```python
from src.database.db_api import create_database

if create_database():
    print("✅ Таблицы созданы")
else:
    print("❌ Ошибка создания таблиц")
```

#### `drop_database() -> bool`
Удаление всех таблиц базы данных.

```python
from src.database.db_api import drop_database

if drop_database():
    print("✅ Таблицы удалены")
```

#### `clear_table(table_name: str) -> bool`
Очистка конкретной таблицы.

```python
from src.database.db_api import clear_table

clear_table("vk_users")
```

#### `clear_all_tables() -> bool`
Очистка всех таблиц (сохранение структуры).

```python
from src.database.db_api import clear_all_tables

clear_all_tables()
```

#### `get_database_info() -> Dict[str, Any]`
Получение информации о базе данных.

```python
from src.database.db_api import get_database_info

info = get_database_info()
print(f"Всего таблиц: {info.get('total_tables', 0)}")
for table_name, table_info in info.get('tables', {}).items():
    print(f"{table_name}: {table_info['count']} записей")
```

### Управление пользователями

#### `add_user(vk_user_id, first_name, last_name, ...) -> bool`
Добавление нового пользователя.

```python
from src.database.db_api import add_user

add_user(
    vk_user_id=123456789,
    first_name="Иван",
    last_name="Иванов",
    age=25,
    sex=2,  # 1 - женский, 2 - мужской
    city="Москва",
    city_id=1
)
```

#### `get_user(vk_user_id) -> Optional[Dict[str, Any]]`
Получение пользователя по VK ID.

```python
from src.database.db_api import get_user

user = get_user(123456789)
if user:
    print(f"{user['first_name']} {user['last_name']}")
```

#### `update_user(vk_user_id, **kwargs) -> bool`
Обновление данных пользователя.

```python
from src.database.db_api import update_user

update_user(123456789, age=26, city="Санкт-Петербург")
```

#### `delete_user(vk_user_id) -> bool`
Удаление пользователя.

```python
from src.database.db_api import delete_user

delete_user(123456789)
```

### Избранное

#### `add_favorite(user_id, favorite_id) -> bool`
Добавление в избранное.

```python
from src.database.db_api import add_favorite

add_favorite(user_id=123456789, favorite_id=987654321)
```

#### `get_favorites(user_id) -> List[Dict[str, Any]]`
Получение списка избранного.

```python
from src.database.db_api import get_favorites

favorites = get_favorites(123456789)
for fav in favorites:
    print(f"Избранный: {fav['favorite_vk_id']}")
```

#### `remove_favorite(user_id, favorite_id) -> bool`
Удаление из избранного.

```python
from src.database.db_api import remove_favorite

remove_favorite(user_id=123456789, favorite_id=987654321)
```

### Черный список

#### `add_to_blacklist(user_id, blacklisted_id) -> bool`
Добавление в черный список.

```python
from src.database.db_api import add_to_blacklist

add_to_blacklist(user_id=123456789, blacklisted_id=987654321)
```

#### `get_blacklist(user_id) -> List[int]`
Получение списка заблокированных пользователей.

```python
from src.database.db_api import get_blacklist

blacklist = get_blacklist(123456789)
print(f"Заблокировано: {len(blacklist)} пользователей")
```

#### `remove_from_blacklist(user_id, blacklisted_id) -> bool`
Удаление из черного списка.

```python
from src.database.db_api import remove_from_blacklist

remove_from_blacklist(user_id=123456789, blacklisted_id=987654321)
```

#### `is_user_blacklisted(user_id, target_user_id) -> bool`
Проверка, находится ли пользователь в черном списке.

```python
from src.database.db_api import is_user_blacklisted

if is_user_blacklisted(123456789, 987654321):
    print("Пользователь заблокирован")
```

### Управление токенами

#### `get_user_access_token(user_id) -> Optional[str]`
Получение расшифрованного access токена пользователя.

```python
from src.database.db_api import get_user_access_token

token = get_user_access_token(123456789)
if token:
    print("Токен получен")
```

#### `get_user_refresh_token_decrypted(user_id) -> Optional[str]`
Получение расшифрованного refresh токена.

```python
from src.database.db_api import get_user_refresh_token_decrypted

refresh_token = get_user_refresh_token_decrypted(123456789)
```

#### `update_user_tokens(user_id, access_token, refresh_token, expires_in) -> bool`
Обновление токенов пользователя.

```python
from src.database.db_api import update_user_tokens

update_user_tokens(
    vk_user_id=123456789,
    access_token="new_access_token",
    refresh_token="new_refresh_token",
    expires_in=3600
)
```

#### `is_user_token_expired(user_id) -> bool`
Проверка истечения токена.

```python
from src.database.db_api import is_user_token_expired

if is_user_token_expired(123456789):
    print("Токен истек")
```

#### `verify_user_refresh_token(user_id, refresh_token) -> bool`
Проверка валидности refresh токена.

```python
from src.database.db_api import verify_user_refresh_token

if verify_user_refresh_token(123456789, "refresh_token"):
    print("Refresh токен валиден")
```

### Параметры поиска

#### `save_search_params(user_id, min_age, max_age, sex_preference, ...) -> bool`
Сохранение параметров поиска.

```python
from src.database.db_api import save_search_params

save_search_params(
    vk_user_id=123456789,
    min_age=18,
    max_age=35,
    sex_preference=1,  # 1 - женский, 2 - мужской
    zodiac_signs=["leo", "virgo"],
    relationship_statuses=["actively_looking", "single"],
    online=True
)
```

#### `get_search_params(user_id) -> Optional[Dict[str, Any]]`
Получение сохраненных параметров поиска.

```python
from src.database.db_api import get_search_params

params = get_search_params(123456789)
if params:
    print(f"Возраст: {params['min_age']}-{params['max_age']}")
    print(f"Пол: {params['sex_preference']}")
```

### Статистика

#### `get_user_statistics(user_id) -> dict`
Получение базовой статистики пользователя.

```python
from src.database.db_api import get_user_statistics

stats = get_user_statistics(123456789)
print(f"Просмотрено анкет: {stats.get('viewed_profiles', 0)}")
print(f"В избранном: {stats.get('favorites_count', 0)}")
```

#### `get_user_profile_stats(user_id) -> dict`
Получение расширенной статистики профиля.

```python
from src.database.db_api import get_user_profile_stats

profile_stats = get_user_profile_stats(123456789)
print(f"Настройки: {profile_stats.get('user_settings')}")
```

#### `get_user_activity_summary(user_id) -> dict`
Получение сводки активности пользователя.

```python
from src.database.db_api import get_user_activity_summary

summary = get_user_activity_summary(123456789)
print(f"Сегодня: {summary.get('today', {})}")
```

#### `count_records(model_name, ...) -> int`

**Новое!** Универсальная функция для подсчета записей в базе данных с поддержкой фильтров и фильтрации по датам.

**Параметры:**
- `model_name` (str): Название модели ('Photo', 'Favorite', 'Blacklisted', 'VKUser', 'UserSettings')
- `filters` (Optional[Dict[str, Any]]): Словарь с дополнительными фильтрами {поле: значение}
- `date_from` (Optional[datetime]): Дата начала периода для фильтрации по дате
- `date_field_primary` (Optional[str]): Основное поле даты (например, 'updated_at', 'token_updated_at')
- `date_field_fallback` (Optional[str]): Резервное поле даты (например, 'created_at')
- `distinct_field` (Optional[str]): Поле для подсчета уникальных значений (например, 'vk_user_id')
- `user_id` (Optional[int]): ID пользователя для фильтрации по полю user_field
- `user_field` (Optional[str]): Название поля для фильтрации по user_id (например, 'user_vk_id', 'found_by_user_id')

**Возвращает:** `int` - Количество записей, соответствующих фильтрам

**Особенности:**
- Автоматическое использование `updated_at` если есть, иначе `created_at` (при указании обоих полей)
- Поддержка подсчета уникальных значений через `distinct_field`
- Гибкая фильтрация по пользователю и дополнительным полям
- Специальные фильтры: `{'isnot': None}`, `{'in': [values]}`, `{'not_in': [values]}`

**Примеры использования:**

```python
from src.database.db_api import count_records
from datetime import datetime, time

# Подсчет всех фото
count = count_records('Photo')
print(f"Всего фото: {count}")

# Подсчет фото пользователя
count = count_records(
    'Photo',
    user_id=123456789,
    user_field='found_by_user_id'
)
print(f"Фото пользователя: {count}")

# Подсчет фото за сегодня (с использованием updated_at, если есть, иначе created_at)
today = datetime.combine(datetime.now().date(), time.min)
count = count_records(
    'Photo',
    date_from=today,
    date_field_primary='updated_at',
    date_field_fallback='created_at',
    user_id=123456789,
    user_field='found_by_user_id'
)
print(f"Фото за сегодня: {count}")

# Подсчет уникальных профилей (анкет) по фотографиям
count = count_records(
    'Photo',
    distinct_field='vk_user_id',
    user_id=123456789,
    user_field='found_by_user_id'
)
print(f"Уникальных профилей: {count}")

# Подсчет избранного пользователя за сегодня
count = count_records(
    'Favorite',
    date_from=today,
    date_field_fallback='created_at',
    user_id=123456789,
    user_field='user_vk_id'
)
print(f"Избранное за сегодня: {count}")

# Подсчет пользователей, обновивших токены сегодня
count = count_records(
    'UserSettings',
    date_from=today,
    date_field_primary='token_updated_at',
    date_field_fallback='created_at',
    distinct_field='vk_user_id'
)
print(f"Пользователей обновили токены: {count}")

# Подсчет с дополнительными фильтрами
count = count_records(
    'Photo',
    filters={'vk_user_id': 123456789, 'found_by_user_id': None}
)
print(f"Фото без found_by_user_id: {count}")

# Подсчет пользователей с токенами (token_updated_at не NULL)
count = count_records(
    'UserSettings',
    filters={'token_updated_at': {'isnot': None}},
    distinct_field='vk_user_id'
)
print(f"Пользователей с токенами: {count}")
```

**Использование в коде бота:**

Эта функция используется в `handle_statistics_async` для подсчета всех статистических данных, вместо прямых SQL-запросов. Все подсчеты идут через единую точку доступа API базы данных, что исключает прямую работу с SQLAlchemy из кода бота.

**Логика фильтрации по датам:**
- Для `favorites`: используется `created_at` (эквивалент `added_at`)
- Для `blacklisted`: используется `created_at` (эквивалент `blocked_at`)
- Для `photo`: `updated_at` -> `created_at`
- Для `vk_users`: `updated_at` -> `created_at`
- Для `user_settings` (работа с ботом): `updated_at` -> `created_at`
- Для `user_settings` (обновление токенов): `token_updated_at` -> `created_at`

### Токен группы

#### `get_group_token() -> Optional[str]`
Получение расшифрованного токена группы.

```python
from src.database.db_api import get_group_token

token = get_group_token()
```

#### `update_group_token(group_token: str) -> bool`
Обновление токена группы.

```python
from src.database.db_api import update_group_token

update_group_token("new_group_token")
```

#### `check_group_token_validity(group_token: Optional[str] = None) -> bool`
Проверка валидности токена группы через VK API.

```python
from src.database.db_api import check_group_token_validity

if check_group_token_validity():
    print("Токен группы валиден")
```

### Управление PostgreSQL

#### `start_postgresql() -> bool`
Запуск PostgreSQL (для локальной БД).

```python
from src.database.db_api import start_postgresql

start_postgresql()
```

#### `stop_postgresql() -> bool`
Остановка PostgreSQL.

```python
from src.database.db_api import stop_postgresql

stop_postgresql()
```

#### `check_postgresql_status() -> bool`
Проверка статуса PostgreSQL.

```python
from src.database.db_api import check_postgresql_status

if check_postgresql_status():
    print("PostgreSQL работает")
```

---

## 🔧 Низкоуровневое API (database_interface.py)

### Класс DatabaseInterface

#### Инициализация

```python
from src.database.database_interface import DatabaseInterface

db = DatabaseInterface()
if db.is_available:
    print("БД доступна")
```

#### Работа с сессиями

```python
with db.get_session() as session:
    from src.database.models import VKUser
    user = session.query(VKUser).filter(VKUser.vk_user_id == 123456789).first()
    if user:
        user.age = 26
        session.commit()
```

#### Шифрование токенов

```python
# Шифрование access токена
encrypted = db.encrypt_access_token("access_token")
decrypted = db.decrypt_access_token(encrypted)

# Шифрование refresh токена
encrypted = db.encrypt_refresh_token("refresh_token")
decrypted = db.decrypt_refresh_token(encrypted)

# Хеширование refresh токена (для проверки)
token_hash, salt = db.hash_refresh_token("refresh_token")
is_valid = db.verify_refresh_token("refresh_token", token_hash, salt)
```

#### Методы работы с данными

Все методы из высокоуровневого API доступны здесь напрямую:

```python
# Пользователи
db.add_user(vk_user_id=123456789, first_name="Иван", last_name="Иванов")
user = db.get_user(123456789)
db.update_user(123456789, age=26)
db.delete_user(123456789)

# Избранное
db.add_favorite(user_vk_id=123456789, favorite_vk_id=987654321)
favorites = db.get_favorites(123456789)
db.remove_favorite(user_vk_id=123456789, favorite_vk_id=987654321)

# Черный список
db.add_to_blacklist(user_id=123456789, blacklisted_id=987654321)
blacklist = db.get_blacklisted(123456789)
db.remove_from_blacklist(user_id=123456789, blacklisted_id=987654321)

# Токены
db.save_user_tokens(vk_user_id=123456789, access_token="...", refresh_token="...", expires_in=3600)
access_token = db.get_user_access_token(123456789)
refresh_token = db.get_user_refresh_token_decrypted(123456789)
is_expired = db.is_user_token_expired(123456789)
```

---

## 💻 CLI интерфейс (db_cli.py)

### Использование через BOT_BEGIN.py

Через главное меню управления (`python BOT_BEGIN.py`):

```
1. Создать таблицы базы данных
2. Удалить все таблицы
3. Очистить таблицу
4. Очистить все таблицы
5. Информация о базе данных
6. Добавить тестовые данные
...
```

### Прямое использование

**Примечание:** `db_cli.py` защищен от прямого запуска. Используйте через `BOT_BEGIN.py` или импортируйте класс `DatabaseCLI`.

```python
from src.database.db_cli import DatabaseCLI

cli = DatabaseCLI()

# Создание таблиц
cli.create_database()

# Информация о БД
cli.show_info()

# Добавление тестовых данных
cli.add_test_data()
```

---

## 📊 Модели данных

### VKUser

Пользователи VK.

```python
from src.database.models import VKUser

# Поля:
# - id (SERIAL PRIMARY KEY)
# - vk_user_id (BIGINT UNIQUE)
# - first_name, last_name
# - age, sex, city, city_id
# - bdate, photo_url, profile_url
# - created_at, updated_at
```

### Photo

Фотографии пользователей.

```python
from src.database.models import Photo

# Поля:
# - id (SERIAL PRIMARY KEY)
# - vk_user_id (INTEGER)
# - photo_url (TEXT)
# - photo_type (VARCHAR) - 'profile' или 'tagged'
# - likes_count (INTEGER)
# - found_by_user_id (INTEGER)
# - created_at, updated_at
```

### Favorite

Избранное.

```python
from src.database.models import Favorite

# Поля:
# - id (SERIAL PRIMARY KEY)
# - user_vk_id (INTEGER)
# - favorite_vk_id (INTEGER)
# - created_at
```

### Blacklisted

Черный список.

```python
from src.database.models import Blacklisted

# Поля:
# - id (SERIAL PRIMARY KEY)
# - user_vk_id (INTEGER)
# - blocked_vk_id (INTEGER)
# - created_at
```

### UserSettings

Настройки пользователей.

```python
from src.database.models import UserSettings

# Поля:
# - id (SERIAL PRIMARY KEY)
# - vk_user_id (INTEGER UNIQUE)
# - encrypted_access_token (TEXT)
# - encrypted_refresh_token (TEXT)
# - refresh_token_hash (TEXT)
# - token_salt (TEXT)
# - token_iv (TEXT)
# - token_expires_at (TIMESTAMP)
# - token_updated_at (TIMESTAMP)
# - min_age, max_age (INTEGER)
# - sex_preference (INTEGER)
# - city_preference (VARCHAR)
# - relationship_statuses (JSON)
# - online (BOOLEAN)
# - zodiac_signs (JSON)
```

---

## 📝 Примеры использования

### Полный пример работы с пользователем

```python
from src.database.db_api import *

# Добавление пользователя
add_user(
    vk_user_id=123456789,
    first_name="Иван",
    last_name="Иванов",
    age=25,
    sex=2,
    city="Москва"
)

# Получение пользователя
user = get_user(123456789)
print(f"{user['first_name']} {user['last_name']}")

# Обновление токенов
update_user_tokens(
    vk_user_id=123456789,
    access_token="new_token",
    refresh_token="new_refresh",
    expires_in=3600
)

# Сохранение параметров поиска
save_search_params(
    vk_user_id=123456789,
    min_age=18,
    max_age=35,
    sex_preference=1,
    zodiac_signs=["leo", "virgo"],
    online=True
)

# Получение параметров
params = get_search_params(123456789)
print(f"Возраст: {params['min_age']}-{params['max_age']}")

# Работа с избранным
add_favorite(user_id=123456789, favorite_id=987654321)
favorites = get_favorites(123456789)
print(f"Избранных: {len(favorites)}")

# Статистика
stats = get_user_statistics(123456789)
print(f"Просмотрено: {stats['viewed_profiles']}")

# Подсчет записей с фильтрами (новая функция)
from src.database.db_api import count_records
from datetime import datetime, time

# Подсчет фото пользователя за сегодня
today = datetime.combine(datetime.now().date(), time.min)
photos_today = count_records(
    'Photo',
    date_from=today,
    date_field_primary='updated_at',
    date_field_fallback='created_at',
    user_id=123456789,
    user_field='found_by_user_id'
)
print(f"Фото за сегодня: {photos_today}")

# Подсчет уникальных профилей
profiles_count = count_records(
    'Photo',
    distinct_field='vk_user_id',
    user_id=123456789,
    user_field='found_by_user_id'
)
print(f"Уникальных профилей: {profiles_count}")
```

### Пример работы с низкоуровневым API

```python
from src.database.database_interface import DatabaseInterface
from src.database.models import VKUser, Favorite

db = DatabaseInterface()

if db.is_available:
    with db.get_session() as session:
        # Создание пользователя
        user = VKUser(
            vk_user_id=123456789,
            first_name="Иван",
            last_name="Иванов",
            age=25,
            sex=2
        )
        session.add(user)
        session.commit()
        
        # Добавление в избранное
        favorite = Favorite(
            user_vk_id=123456789,
            favorite_vk_id=987654321
        )
        session.add(favorite)
        session.commit()
```

---

## ⚠️ Обработка ошибок

### Проверка доступности БД

```python
from src.database.db_api import get_db_interface

db = get_db_interface()
if db is None or not db.is_available:
    print("База данных недоступна")
    # Fallback логика
```

### Обработка исключений

```python
from src.database.db_api import add_user

try:
    success = add_user(vk_user_id=123456789, first_name="Иван", last_name="Иванов")
    if not success:
        print("Ошибка добавления пользователя")
except Exception as e:
    print(f"Критическая ошибка: {e}")
```

### Логирование

Все операции автоматически логируются через `centralized_logger`. Ошибки логируются на уровне ERROR, успешные операции - на уровне INFO.

---

## 🔍 Дополнительные функции

### Информация о таблицах

```python
from src.database.db_api import get_table_list, get_table_count, get_table_info

# Список всех таблиц
tables = get_table_list()

# Количество записей в таблице
count = get_table_count("vk_users")

# Полная информация о таблице
info = get_table_info("vk_users")
```

### Статистика БД

```python
from src.database.db_api import get_database_stats

stats = get_database_stats()
print(f"Всего пользователей: {stats['total_users']}")
print(f"Всего фотографий: {stats['total_photos']}")
```

---

## 💻 CLI интерфейс (BOT_BEGIN.py)

### Главное меню управления

При запуске `python BOT_BEGIN.py` отображается интерактивное меню:

```
╔═══════════════════════════════════════════════════════════╗
║              🤖 VKinder Bot - Управление                 ║
╚═══════════════════════════════════════════════════════════╝

0. ❌ Выход
1. 🔨 Создать таблицы базы данных
2. 🗑️  Удалить все таблицы
3. 🧹 Очистить таблицу
4. 🧹 Очистить все таблицы
5. 📊 Информация о базе данных
6. 🧪 Добавить тестовые данные
...
18. 🔐 Прочитать токен группы
19. 🔄 Обновить токен группы
```

### Операции с базой данных

**Создание таблиц (пункт 1):**
- Создает все таблицы через `db_api.create_database()`
- Показывает результат операции

**Удаление таблиц (пункт 2):**
- Запрашивает подтверждение
- Удаляет все таблицы через `db_api.drop_database()`

**Очистка таблицы (пункт 3):**
- Запрашивает название таблицы
- Очищает данные таблицы (структура сохраняется)

**Информация о БД (пункт 5):**
- Показывает количество таблиц
- Показывает количество записей в каждой таблице

**Тестовые данные (пункт 6):**
- Добавляет тестовых пользователей
- Добавляет тестовые фотографии
- Добавляет тестовые связи (избранное, черный список)

### Управление токенами через CLI

**Чтение токена группы (пункт 18):**
```python
from src.database.db_api import read_group_token_console

token = read_group_token_console()
if token:
    print(f"Токен группы: {token[:20]}...{token[-10:]}")
```

**Обновление токена группы (пункт 19):**
```python
from src.database.db_api import update_group_token, check_group_token_validity

token = input("Введите новый токен группы: ")
if check_group_token_validity(token):
    if update_group_token(token):
        print("✅ Токен успешно обновлен")
else:
    print("❌ Токен невалиден")
```

---

**См. также:**
- [README.md](../README.md) - общая документация проекта
- [BOT_API_GUIDE.md](BOT_API_GUIDE.md) - документация Bot API

