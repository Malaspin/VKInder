-- Инициализация базы данных для VKinder Bot
-- Этот файл выполняется при первом запуске PostgreSQL контейнера

-- Создаем расширения если нужно
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создаем схему если нужно
-- CREATE SCHEMA IF NOT EXISTS vkinder;

-- Устанавливаем права для пользователя
GRANT ALL PRIVILEGES ON DATABASE vkinder_db TO vkinder_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vkinder_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vkinder_user;

-- Настраиваем поиск по тексту (опционально)
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
