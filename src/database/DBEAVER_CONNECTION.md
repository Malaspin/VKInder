# 📋 Подключение DBeaver к базе данных VKinder

## 🔌 Параметры подключения

**ВАЖНО:** Бот использует локальный PostgreSQL на порту **5433** (локальный кластер проекта).

### Для работы с основной базой данных (где хранятся данные бота):

```
Host: localhost
Port: 5433
Database: vkinder_db
Username: vkinder_user
Password: vkinder123
```

## 📊 Проверка токенов в базе данных

### Просмотр зашифрованных токенов:

```sql
SELECT 
    vk_user_id, 
    encrypted_access_token IS NOT NULL as has_token,
    refresh_token_hash IS NOT NULL as has_refresh,
    token_expires_at,
    token_updated_at
FROM user_settings
WHERE encrypted_access_token IS NOT NULL
ORDER BY vk_user_id;
```

### Просмотр пользователей с токенами:

```sql
SELECT 
    u.vk_user_id,
    u.first_name,
    u.last_name,
    us.encrypted_access_token IS NOT NULL as has_token,
    us.token_expires_at
FROM vk_users u
JOIN user_settings us ON u.vk_user_id = us.vk_user_id
WHERE us.encrypted_access_token IS NOT NULL
ORDER BY u.vk_user_id;
```

## ⚠️ Важно

- Токены хранятся в **зашифрованном виде** в таблице `user_settings`
- Расшифровка токенов происходит только через API базы данных
- Напрямую из DBeaver токены расшифровать нельзя (нужен ключ шифрования)
- Для безопасности ключ шифрования не хранится в базе данных

## 🚀 Запуск PostgreSQL

### Основной PostgreSQL (порт 5433):
```bash
./src/database/start_postgres.sh
```

## 🛑 Остановка PostgreSQL

### Основной PostgreSQL (порт 5433):
```bash
./src/database/stop_postgres.sh
```
