#!/usr/bin/env python3
"""
Примеры использования интерфейса базы данных VKinder Bot
Демонстрирует все доступные функции для работы с PostgreSQL
"""

import sys
import os
from typing import Optional, List, Dict, Any

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем API для работы с базой данных
from db_api import *


def example_basic_usage():
    """Базовые примеры использования API"""
    print("🔧 БАЗОВЫЕ ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
    print("=" * 50)
    
    # 1. Тестирование подключения
    print("\n1. Тестирование подключения к БД...")
    if test_database():
        print("✅ Подключение работает")
    else:
        print("❌ Ошибка подключения")
        return
    
    # 2. Получение информации о БД
    print("\n2. Информация о базе данных...")
    info = get_database_info()
    print(f"📊 Всего таблиц: {info.get('total_tables', 0)}")
    for table_name, table_info in info.get('tables', {}).items():
        print(f"  - {table_name}: {table_info['count']} записей")


def example_user_management():
    """Примеры работы с пользователями"""
    print("\n\n👥 УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ")
    print("=" * 50)
    
    # Добавление пользователя
    print("\n1. Добавление пользователя...")
    user_id = 100001
    success = add_user(
        vk_user_id=user_id,
        first_name="Алексей",
        last_name="Петров",
        age=28,
        sex=2,  # 1 - женский, 2 - мужской
        city="Москва",
        country="Россия",
        photo_url="https://example.com/photo.jpg"
    )
    
    if success:
        print("✅ Пользователь добавлен")
    else:
        print("❌ Ошибка добавления пользователя")
    
    # Получение пользователя
    print("\n2. Получение данных пользователя...")
    user = get_user(user_id)
    if user:
        print(f"✅ Найден: {user['first_name']} {user['last_name']}")
        print(f"   Возраст: {user['age']}, Город: {user['city']}")
    else:
        print("❌ Пользователь не найден")
    
    # Обновление пользователя
    print("\n3. Обновление данных пользователя...")
    update_success = update_user(user_id, age=29, city="Санкт-Петербург")
    if update_success:
        print("✅ Данные обновлены")
        
        # Проверяем обновление
        updated_user = get_user(user_id)
        if updated_user:
            print(f"   Новый возраст: {updated_user['age']}")
            print(f"   Новый город: {updated_user['city']}")


def example_logging():
    """Примеры логирования"""
    print("\n\n📝 СИСТЕМА ЛОГИРОВАНИЯ")
    print("=" * 50)
    
    user_id = 100001
    
    # Различные типы логов
    print("\n1. Запись различных типов логов...")
    
    # Системные логи (user_id = 0)
    log_info("Система запущена")
    log_debug("Инициализация модулей")
    log_warning("Предупреждение о низком уровне памяти")
    log_error("Критическая ошибка подключения")
    
    # Логи пользователей
    log_info("Пользователь зашел в бота", user_id)
    log_debug("Начало поиска пользователей", user_id)
    log_info("Поиск завершен успешно", user_id)
    log_error("Ошибка при загрузке фотографий", user_id)
    
    print("✅ Логи записаны")
    
    # Получение логов
    print("\n2. Получение логов...")
    
    # Все логи пользователя
    user_logs = get_logs(user_id=user_id, limit=5)
    print(f"📋 Логов пользователя {user_id}: {len(user_logs)}")
    for log in user_logs:
        print(f"  [{log['log_level'].upper()}] {log['log_message']}")
    
    # Системные логи
    system_logs = get_logs(user_id=0, limit=3)
    print(f"\n📋 Системных логов: {len(system_logs)}")
    for log in system_logs:
        print(f"  [{log['log_level'].upper()}] {log['log_message']}")
    
    # Логи определенного уровня
    error_logs = get_logs(level="error", limit=3)
    print(f"\n📋 Логов ошибок: {len(error_logs)}")
    for log in error_logs:
        print(f"  [{log['log_level'].upper()}] {log['log_message']}")


def example_messages():
    """Примеры работы с сообщениями"""
    print("\n\n💬 СИСТЕМА СООБЩЕНИЙ")
    print("=" * 50)
    
    user_id = 100001
    
    # Добавление сообщений
    print("\n1. Добавление сообщений...")
    
    # Команды пользователя
    add_message(user_id, "command", "/start")
    add_message(user_id, "command", "/help")
    add_message(user_id, "command", "/search")
    
    # Ответы бота
    add_message(user_id, "response", "Привет! Добро пожаловать в VKinder Bot!")
    add_message(user_id, "response", "Вот список доступных команд:")
    add_message(user_id, "response", "Начинаю поиск подходящих пользователей...")
    
    # Ошибки
    add_message(user_id, "error", "Ошибка: не удалось загрузить фотографии")
    
    print("✅ Сообщения добавлены")
    
    # Получение сообщений
    print("\n2. Получение сообщений пользователя...")
    messages = get_user_messages(user_id, limit=10)
    print(f"📋 Найдено сообщений: {len(messages)}")
    
    for msg in messages:
        print(f"  [{msg['message_type'].upper()}] {msg['message_text']}")
        print(f"    Время: {msg['sent_at']}")


def example_favorites():
    """Примеры работы с избранным"""
    print("\n\n❤️ СИСТЕМА ИЗБРАННОГО")
    print("=" * 50)
    
    user_id = 100001
    
    # Добавляем пользователей для избранного
    print("\n1. Добавление пользователей для избранного...")
    favorite_users = [
        {"vk_user_id": 200001, "first_name": "Анна", "last_name": "Иванова", "age": 25, "sex": 1, "city": "Москва"},
        {"vk_user_id": 200002, "first_name": "Мария", "last_name": "Сидорова", "age": 27, "sex": 1, "city": "СПб"},
        {"vk_user_id": 200003, "first_name": "Елена", "last_name": "Козлова", "age": 26, "sex": 1, "city": "Казань"}
    ]
    
    for fav_user in favorite_users:
        add_user(**fav_user)
        print(f"✅ Добавлен пользователь: {fav_user['first_name']} {fav_user['last_name']}")
    
    # Добавление в избранное
    print("\n2. Добавление в избранное...")
    for fav_user in favorite_users:
        success = add_favorite(user_id, fav_user['vk_user_id'])
        if success:
            print(f"✅ {fav_user['first_name']} добавлена в избранное")
        else:
            print(f"❌ Ошибка добавления {fav_user['first_name']} в избранное")
    
    # Получение избранных
    print("\n3. Получение списка избранных...")
    favorites = get_favorites(user_id)
    print(f"📋 Избранных пользователей: {len(favorites)}")
    
    for fav in favorites:
        print(f"  ID: {fav['favorite_vk_id']}")
        print(f"    Добавлен: {fav['created_at']}")
    
    # Удаление из избранного
    print("\n4. Удаление из избранного...")
    if favorites:
        first_favorite = favorites[0]['favorite_vk_id']
        success = remove_favorite(user_id, first_favorite)
        if success:
            print(f"✅ Пользователь {first_favorite} удален из избранного")
        else:
            print(f"❌ Ошибка удаления пользователя {first_favorite}")


def example_database_management():
    """Примеры управления базой данных"""
    print("\n\n🗄️ УПРАВЛЕНИЕ БАЗОЙ ДАННЫХ")
    print("=" * 50)
    
    # Информация о БД
    print("\n1. Информация о базе данных...")
    info = get_database_info()
    print(f"📊 Всего таблиц: {info.get('total_tables', 0)}")
    
    for table_name, table_info in info.get('tables', {}).items():
        print(f"  📄 {table_name}: {table_info['count']} записей")
    
    # Очистка конкретной таблицы (осторожно!)
    print("\n2. Очистка таблицы (пример)...")
    print("⚠️  Внимание: это удалит все данные из таблицы!")
    # clear_table("bot_logs")  # Раскомментируйте для тестирования
    print("ℹ️  Очистка пропущена для безопасности")
    
    # Создание таблиц (если нужно)
    print("\n3. Создание таблиц...")
    print("ℹ️  Таблицы уже существуют")


def example_error_handling():
    """Примеры обработки ошибок"""
    print("\n\n⚠️ ОБРАБОТКА ОШИБОК")
    print("=" * 50)
    
    # Попытка получить несуществующего пользователя
    print("\n1. Получение несуществующего пользователя...")
    user = get_user(999999)
    if user is None:
        print("✅ Корректно обработано: пользователь не найден")
    else:
        print("❌ Неожиданный результат")
    
    # Попытка добавить пользователя с некорректными данными
    print("\n2. Добавление пользователя с некорректными данными...")
    success = add_user(
        vk_user_id=100002,
        first_name="",  # Пустое имя
        last_name="Тест"
    )
    if not success:
        print("✅ Корректно обработано: ошибка валидации")
    else:
        print("❌ Неожиданный результат")
    
    # Попытка добавить в избранное несуществующего пользователя
    print("\n3. Добавление в избранное несуществующего пользователя...")
    success = add_favorite(100001, 999999)
    if not success:
        print("✅ Корректно обработано: нарушение внешнего ключа")
    else:
        print("❌ Неожиданный результат")


def example_integration_patterns():
    """Примеры паттернов интеграции с основным кодом"""
    print("\n\n🔗 ПАТТЕРНЫ ИНТЕГРАЦИИ")
    print("=" * 50)
    
    # Паттерн: Обработка команды пользователя
    print("\n1. Обработка команды пользователя...")
    
    def handle_user_command(user_id: int, command: str):
        """Пример функции обработки команды"""
        # Логируем команду
        log_info(f"Пользователь {user_id} выполнил команду: {command}", user_id)
        
        # Сохраняем команду
        add_message(user_id, "command", command)
        
        # Обрабатываем команду
        if command == "/start":
            response = "Привет! Добро пожаловать в VKinder Bot!"
        elif command == "/help":
            response = "Доступные команды: /start, /search, /favorites"
        elif command == "/search":
            response = "Начинаю поиск подходящих пользователей..."
        else:
            response = "Неизвестная команда. Используйте /help для справки"
        
        # Сохраняем ответ
        add_message(user_id, "response", response)
        
        # Логируем результат
        log_info(f"Отправлен ответ пользователю {user_id}", user_id)
        
        return response
    
    # Тестируем паттерн
    test_user_id = 100003
    add_user(test_user_id, "Тест", "Пользователь", 30, 2, "Москва")
    
    response = handle_user_command(test_user_id, "/start")
    print(f"✅ Обработана команда: {response}")
    
    response = handle_user_command(test_user_id, "/help")
    print(f"✅ Обработана команда: {response}")
    
    # Паттерн: Поиск и добавление в избранное
    print("\n2. Поиск и добавление в избранное...")
    
    def search_and_add_favorite(user_id: int, search_criteria: dict):
        """Пример функции поиска и добавления в избранное"""
        log_info(f"Начало поиска для пользователя {user_id}", user_id)
        
        # Имитируем поиск (в реальности здесь будет VK API)
        found_users = [
            {"vk_user_id": 300001, "first_name": "Наталья", "last_name": "Петрова", "age": 24, "sex": 1, "city": "Москва"},
            {"vk_user_id": 300002, "first_name": "Ольга", "last_name": "Смирнова", "age": 26, "sex": 1, "city": "СПб"}
        ]
        
        log_info(f"Найдено пользователей: {len(found_users)}", user_id)
        
        # Добавляем найденных пользователей
        for user_data in found_users:
            add_user(**user_data)
            add_favorite(user_id, user_data['vk_user_id'])
            log_info(f"Добавлен в избранное: {user_data['first_name']} {user_data['last_name']}", user_id)
        
        return len(found_users)
    
    # Тестируем паттерн
    found_count = search_and_add_favorite(test_user_id, {"age_from": 20, "age_to": 30, "sex": 1})
    print(f"✅ Найдено и добавлено в избранное: {found_count} пользователей")


def main():
    """Основная функция с примерами"""
    print("🚀 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ИНТЕРФЕЙСА БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    try:
        # Запускаем все примеры
        example_basic_usage()
        example_user_management()
        example_logging()
        example_messages()
        example_favorites()
        example_database_management()
        example_error_handling()
        example_integration_patterns()
        
        print("\n\n✅ ВСЕ ПРИМЕРЫ ВЫПОЛНЕНЫ УСПЕШНО!")
        print("=" * 60)
        print("📖 Дополнительная документация: DATABASE_INTERFACE_GUIDE.md")
        print("🔧 CLI команды: python db_cli.py --help")
        print("📊 API функции: from db_api import *")
        
    except Exception as e:
        print(f"\n❌ Ошибка выполнения примеров: {e}")
        log_error(f"Ошибка в примерах: {e}")


if __name__ == "__main__":
    main()
