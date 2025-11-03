#!/usr/bin/env python3
"""
API для интеграции с базой данных VKinder Bot
Предоставляет простые функции для использования в основном коде бота
"""

import sys
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.utils.centralized_logger import centralized_logger

# Защита от прямого запуска
if __name__ == "__main__":
    print("❌ Этот файл нельзя запускать напрямую!")
    print("⚠️ Модули базы данных работают только как часть основной программы")
    sys.exit(1)

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from .database_interface import DatabaseInterface
    from .postgres_manager import PostgreSQLManager
    from .models import VKUser, Photo, Favorite, Blacklisted, UserSettings
except ImportError:
    # Если относительные импорты не работают, используем абсолютные
    from database_interface import DatabaseInterface
    from postgres_manager import PostgreSQLManager
    from models import VKUser, Photo, Favorite, Blacklisted, UserSettings

from loguru import logger

# Глобальный экземпляр интерфейса базы данных
_db_interface = None


def get_db_interface() -> Optional[DatabaseInterface]:
    """
    Получение глобального экземпляра интерфейса базы данных
    
    Returns:
        Optional[DatabaseInterface]: Экземпляр интерфейса БД или None если недоступна
    """
    global _db_interface
    if _db_interface is None:
        try:
            _db_interface = DatabaseInterface()
            # Если БД недоступна, всё равно возвращаем объект, но он будет помечен как недоступный
            if not _db_interface.is_available:
                centralized_logger.warning("⚠️ База данных недоступна, операции с БД будут пропущены", user_id=0)
            return _db_interface
        except Exception as e:
            centralized_logger.warning(f"⚠️ Не удалось создать интерфейс БД: {e}, операции с БД будут пропущены", user_id=0)
            # Создаем заглушку вместо None, чтобы избежать ошибок в коде
            class DummyDB:
                is_available = False
                def get_session(self):
                    from contextlib import contextmanager
                    @contextmanager
                    def dummy_session():
                        yield type('obj', (object,), {})()
                    return dummy_session()
            _db_interface = DummyDB()
            return None
    
    # Проверяем, что это правильный объект
    if isinstance(_db_interface, DatabaseInterface):
        return _db_interface
    elif hasattr(_db_interface, 'is_available'):
        # Это заглушка, возвращаем None чтобы указать что БД недоступна
        return None
    else:
        return None


# === УПРАВЛЕНИЕ БАЗОЙ ДАННЫХ ===

def create_database() -> bool:
    """
    Создание всех таблиц базы данных
    
    Returns:
        bool: True если создание успешно, False иначе
    """
    return get_db_interface().create_database()


def drop_database() -> bool:
    """
    Удаление всех таблиц базы данных
    
    Returns:
        bool: True если удаление успешно, False иначе
    """
    return get_db_interface().drop_database()


def clear_table(table_name: str) -> bool:
    """
    Очистка конкретной таблицы
    
    Args:
        table_name (str): Название таблицы для очистки
        
    Returns:
        bool: True если очистка успешна, False иначе
    """
    return get_db_interface().clear_table(table_name)


def clear_all_tables() -> bool:
    """
    Очистка всех таблиц (сохранение структуры)
    
    Returns:
        bool: True если очистка успешна, False иначе
    """
    return get_db_interface().clear_all_tables()


def get_database_info() -> Dict[str, Any]:
    """
    Получение информации о базе данных
    
    Returns:
        Dict[str, Any]: Словарь с информацией о таблицах
    """
    return get_db_interface().get_table_info()


# === УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ===

def add_user(vk_user_id: int, first_name: str, last_name: str, 
             age: Optional[int] = None, sex: Optional[int] = None,
             city: Optional[str] = None, city_id: Optional[int] = None,
             country: Optional[str] = None, photo_url: Optional[str] = None, 
             access: Optional[str] = None, refresh: Optional[str] = None, 
             time: Optional[int] = None) -> bool:
    """
    Добавление нового пользователя
    
    Args:
        vk_user_id (int): ID пользователя VK
        first_name (str): Имя
        last_name (str): Фамилия
        age (Optional[int]): Возраст
        sex (Optional[int]): Пол (1 - женский, 2 - мужской)
        city (Optional[str]): Город
        city_id (Optional[int]): ID города для VK API
        country (Optional[str]): Страна
        photo_url (Optional[str]): URL фотографии
        access (Optional[str]): Access - string
        refresh (Optional[str]): Refresh - string
        time (Optional[int]): Time - integer
        
    Returns:
        bool: True если добавление успешно, False иначе
    """
    result = get_db_interface().add_user(
        vk_user_id=vk_user_id,
        first_name=first_name,
        last_name=last_name,
        age=age,
        sex=sex,
        city=city,
        city_id=city_id,
        country=country,
        photo_url=photo_url,
        access=access,
        refresh=refresh,
        time=time
    )
    
    # Логируем вызов API функции (только в файлы)
    if result:
        centralized_logger.info(f"API: Пользователь {vk_user_id} ({first_name} {last_name}) добавлен через API", user_id=0)
    else:
        centralized_logger.error(f"API: Ошибка добавления пользователя {vk_user_id} через API", user_id=0)
    
    return result


def get_user(vk_user_id: int) -> Optional[Dict[str, Any]]:
    """
    Получение пользователя по VK ID
    
    Args:
        vk_user_id (int): ID пользователя VK
        
    Returns:
        Optional[Dict[str, Any]]: Данные пользователя или None
    """
    try:
        db_interface = get_db_interface()
        with db_interface.get_session() as session:
            from models import VKUser
            user = session.query(VKUser).filter(VKUser.vk_user_id == vk_user_id).first()
            if user:
                return {
                    'id': user.id,
                    'vk_user_id': user.vk_user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'age': user.age,
                    'sex': user.sex,
                    'city': user.city,
                    'city_id': user.city_id,
                    'country': user.country,
                    'photo_url': user.photo_url,
                    'access': user.access,
                    'refresh': user.refresh,
                    'time': user.time,
                    'created_at': user.created_at,
                    'updated_at': user.updated_at
                }
        return None
    except Exception as e:
        centralized_logger.error(f"Ошибка получения пользователя {vk_user_id}: {e}")
        return None


def update_user_fields(vk_user_id: int, access: Optional[str] = None, 
                      refresh: Optional[str] = None, time: Optional[int] = None,
                      city_id: Optional[int] = None) -> bool:
    """
    Обновление дополнительных полей пользователя
    
    Args:
        vk_user_id (int): ID пользователя VK
        access (Optional[str]): Access - string
        refresh (Optional[str]): Refresh - string
        time (Optional[int]): Time - integer
        city_id (Optional[int]): ID города для VK API
        
    Returns:
        bool: True если обновление успешно, False иначе
    """
    try:
        db_interface = get_db_interface()
        with db_interface.get_session() as session:
            from models import VKUser
            user = session.query(VKUser).filter(VKUser.vk_user_id == vk_user_id).first()
            if not user:
                centralized_logger.error(f"API: Пользователь {vk_user_id} не найден для обновления полей")
                return False
            
            # Обновляем только переданные поля
            if access is not None:
                user.access = access
            if refresh is not None:
                user.refresh = refresh
            if time is not None:
                user.time = time
            if city_id is not None:
                user.city_id = city_id
            
            session.commit()
            centralized_logger.info(f"API: Поля пользователя {vk_user_id} обновлены")
            return True
            
    except Exception as e:
        centralized_logger.error(f"Ошибка обновления полей пользователя {vk_user_id}: {e}")
        return False


def get_user_fields(vk_user_id: int) -> Optional[Dict[str, Any]]:
    """
    Получение дополнительных полей пользователя
    
    Args:
        vk_user_id (int): ID пользователя VK
        
    Returns:
        Optional[Dict[str, Any]]: Поля пользователя или None
    """
    try:
        db_interface = get_db_interface()
        with db_interface.get_session() as session:
            from models import VKUser
            user = session.query(VKUser).filter(VKUser.vk_user_id == vk_user_id).first()
            if user:
                return {
                    'vk_user_id': user.vk_user_id,
                    'access': user.access,
                    'refresh': user.refresh,
                    'time': user.time,
                    'updated_at': user.updated_at
                }
        return None
    except Exception as e:
        centralized_logger.error(f"Ошибка получения полей пользователя {vk_user_id}: {e}")
        return None


def update_user(vk_user_id: int, **kwargs) -> bool:
    """
    Обновление данных пользователя
    
    Args:
        vk_user_id (int): ID пользователя VK
        **kwargs: Поля для обновления
        
    Returns:
        bool: True если обновление успешно, False иначе
    """
    result = get_db_interface().update_user(vk_user_id, **kwargs)
    
    # Логируем вызов API функции
    if result:
        centralized_logger.info(f"API: Пользователь {vk_user_id} обновлен через API")
    else:
        centralized_logger.error(f"API: Ошибка обновления пользователя {vk_user_id} через API")
    
    return result


def delete_user(vk_user_id: int) -> bool:
    """
    Удаление пользователя
    
    Args:
        vk_user_id (int): ID пользователя VK
        
    Returns:
        bool: True если удаление успешно, False иначе
    """
    result = get_db_interface().delete_user(vk_user_id)
    
    # Логируем вызов API функции
    if result:
        centralized_logger.info(f"API: Пользователь {vk_user_id} удален через API")
    else:
        centralized_logger.error(f"API: Ошибка удаления пользователя {vk_user_id} через API")
    
    return result


# === ИЗБРАННОЕ ===

def add_favorite(user_id: int, favorite_id: int) -> bool:
    """
    Добавление в избранное
    
    Args:
        user_id (int): ID пользователя, который добавляет
        favorite_id (int): ID пользователя, которого добавляют
        
    Returns:
        bool: True если добавление успешно, False иначе
    """
    result = get_db_interface().add_favorite(
        user_vk_id=user_id,
        favorite_vk_id=favorite_id
    )
    
    # Логируем вызов API функции
    if result:
        centralized_logger.info(f"API: Пользователь {favorite_id} добавлен в избранное к {user_id} через API")
    else:
        centralized_logger.error(f"API: Ошибка добавления в избранное {favorite_id} к {user_id} через API")
    
    return result


def get_favorites(user_id: int) -> List[Dict[str, Any]]:
    """
    Получение списка избранных пользователя
    
    Args:
        user_id (int): ID пользователя VK
        
    Returns:
        List[Dict[str, Any]]: Список избранных
    """
    return get_db_interface().get_favorites(user_vk_id=user_id)


def remove_favorite(user_id: int, favorite_id: int) -> bool:
    """
    Удаление из избранного
    
    Args:
        user_id (int): ID пользователя
        favorite_id (int): ID пользователя для удаления
        
    Returns:
        bool: True если удаление успешно, False иначе
    """
    result = get_db_interface().remove_favorite(
        user_vk_id=user_id,
        favorite_vk_id=favorite_id
    )
    
    # Логируем вызов API функции
    if result:
        centralized_logger.info(f"API: Пользователь {favorite_id} удален из избранного у {user_id} через API")
    else:
        centralized_logger.error(f"API: Ошибка удаления из избранного {favorite_id} у {user_id} через API")
    
    return result


# === ТЕСТИРОВАНИЕ ===

def test_database() -> bool:
    """
    Тестирование подключения к базе данных
    
    Returns:
        bool: True если подключение работает, False иначе
    """
    return get_db_interface().test_connection()


def add_test_data() -> bool:
    """
    Добавление тестовых данных
    
    Returns:
        bool: True если добавление успешно, False иначе
    """
    try:
        # Добавляем тестового пользователя
        add_user(
            vk_user_id=999999,
            first_name="Тест",
            last_name="Пользователь",
            age=25,
            sex=2,
            city="Москва"
        )
        
        # Добавляем тестовые логи
        centralized_logger.info("Тестовый лог от API", 999999)
        centralized_logger.debug("Отладочный лог от API", 999999)
        
        # Таблица bot_messages удалена, логирование только в файлы
        
        return True
        
    except Exception as e:
        centralized_logger.error(f"Ошибка добавления тестовых данных: {e}")
        return False


# === ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ===

def example_usage():
    """Примеры использования API"""
    
    print("🔧 Примеры использования API базы данных")
    print("=" * 50)
    
    # Тестирование подключения
    print("1. Тестирование подключения...")
    if test_database():
        print("✅ Подключение работает")
    else:
        print("❌ Ошибка подключения")
        return
    
    # Получение информации о БД
    print("\n2. Информация о базе данных...")
    info = get_database_info()
    print(f"📊 Всего таблиц: {info.get('total_tables', 0)}")
    
    # Добавление пользователя
    print("\n3. Добавление пользователя...")
    if add_user(123456, "Иван", "Петров", 30, 2, "СПб"):
        print("✅ Пользователь добавлен")
    else:
        print("❌ Ошибка добавления пользователя")
    
    # Логирование
    print("\n4. Логирование...")
    centralized_logger.info("Пользователь зашел в бота", 123456)
    centralized_logger.debug("Отладочная информация", 123456)
    centralized_logger.error("Тестовая ошибка", 123456)
    print("✅ Логи записаны")
    
    # Таблица bot_messages удалена, логирование только в файлы
    print("\n5. Сообщения...")
    print("⚠️ Таблица bot_messages удалена, все логи идут только в файлы")
    
    # Избранное
    print("\n6. Избранное...")
    # Сначала добавляем пользователя, которого будем добавлять в избранное
    add_user(789012, "Анна", "Смирнова", 28, 1, "Москва")
    add_favorite(123456, 789012)
    print("✅ Добавлено в избранное")
    
    # Получение данных
    print("\n7. Получение данных...")
    user = get_user(123456)
    if user:
        print(f"✅ Пользователь найден: {user['first_name']} {user['last_name']}")
    
    # Логирование в БД отключено, логи только в файлах
    print("✅ Логи только в файлах")
    
    favorites = get_favorites(123456)
    print(f"✅ Найдено избранных: {len(favorites)}")
    
    print("\n✅ Все примеры выполнены успешно!")


# === УПРАВЛЕНИЕ POSTGRESQL ===

def start_postgresql() -> bool:
    """
    Запуск PostgreSQL (универсальный для всех ОС)
    
    Returns:
        bool: True если запуск успешен, False иначе
    """
    try:
        manager = PostgreSQLManager()
        result = manager.start_postgresql()
        
        if result:
            centralized_logger.info("PostgreSQL запущен через API")
        else:
            centralized_logger.error("Ошибка запуска PostgreSQL через API")
        
        return result
    except Exception as e:
        centralized_logger.error(f"Ошибка запуска PostgreSQL: {e}")
        return False


def stop_postgresql() -> bool:
    """
    Остановка PostgreSQL (универсальный для всех ОС)
    
    Returns:
        bool: True если остановка успешна, False иначе
    """
    try:
        manager = PostgreSQLManager()
        result = manager.stop_postgresql()
        
        if result:
            centralized_logger.info("PostgreSQL остановлен через API")
        else:
            centralized_logger.error("Ошибка остановки PostgreSQL через API")
        
        return result
    except Exception as e:
        centralized_logger.error(f"Ошибка остановки PostgreSQL: {e}")
        return False


def restart_postgresql() -> bool:
    """
    Перезапуск PostgreSQL (универсальный для всех ОС)
    
    Returns:
        bool: True если перезапуск успешен, False иначе
    """
    try:
        manager = PostgreSQLManager()
        result = manager.restart_postgresql()
        
        if result:
            centralized_logger.info("PostgreSQL перезапущен через API")
        else:
            centralized_logger.error("Ошибка перезапуска PostgreSQL через API")
        
        return result
    except Exception as e:
        centralized_logger.error(f"Ошибка перезапуска PostgreSQL: {e}")
        return False


def check_postgresql_status() -> bool:
    """
    Проверка статуса PostgreSQL
    
    Returns:
        bool: True если PostgreSQL запущен, False иначе
    """
    try:
        manager = PostgreSQLManager()
        result = manager.check_postgresql_status()
        
        if result:
            centralized_logger.info("PostgreSQL статус: запущен")
        else:
            centralized_logger.warning("PostgreSQL статус: не запущен")
        
        return result
    except Exception as e:
        centralized_logger.error(f"Ошибка проверки статуса PostgreSQL: {e}")
        return False


def get_postgresql_info() -> Dict[str, Any]:
    """
    Получение информации о PostgreSQL
    
    Returns:
        Dict[str, Any]: Информация о PostgreSQL
    """
    try:
        manager = PostgreSQLManager()
        info = manager.get_postgresql_info()
        
        if 'error' not in info:
            centralized_logger.info("Информация о PostgreSQL получена через API")
        else:
            centralized_logger.error(f"Ошибка получения информации о PostgreSQL: {info['error']}")
        
        return info
    except Exception as e:
        centralized_logger.error(f"Ошибка получения информации о PostgreSQL: {e}")
        return {'error': str(e)}


def create_database_if_not_exists() -> bool:
    """
    Создание базы данных если она не существует
    
    Returns:
        bool: True если БД создана или существует, False иначе
    """
    try:
        manager = PostgreSQLManager()
        result = manager.create_database_if_not_exists()
        
        if result:
            # DEBUG: база уже существует или создана - это нормально для API вызовов
            centralized_logger.debug("База данных проверена через API (создана или уже существует)")
        else:
            centralized_logger.error("Ошибка создания базы данных через API")
        
        return result
    except Exception as e:
        centralized_logger.error(f"Ошибка создания базы данных: {e}")
        return False


def ensure_postgresql_ready() -> bool:
    """
    Гарантирует, что PostgreSQL готов к работе
    
    Returns:
        bool: True если PostgreSQL готов, False иначе
    """
    try:
        centralized_logger.info("Проверка готовности PostgreSQL через API")
        
        manager = PostgreSQLManager()
        
        # Проверяем и запускаем PostgreSQL
        if not manager.ensure_postgresql_running():
            centralized_logger.error("Не удалось запустить PostgreSQL через API")
            return False
        
        # Создаем БД если нужно
        if not manager.create_database_if_not_exists():
            centralized_logger.error("Не удалось создать базу данных через API")
            return False
        
        centralized_logger.info("PostgreSQL готов к работе через API")
        return True
        
    except Exception as e:
        centralized_logger.error(f"Ошибка подготовки PostgreSQL: {e}")
        return False


# === ДОПОЛНИТЕЛЬНЫЕ ИМПОРТЫ ===
import subprocess
import time

def get_table_list() -> List[str]:
    """Получить список всех таблиц в базе данных"""
    try:
        from sqlalchemy import inspect
        db = get_db_interface()
        if not db or not db.is_available:
            return []
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        return tables
    except Exception as e:
        centralized_logger.error(f"Ошибка получения списка таблиц: {e}", user_id=0)
        return []

def get_table_count(table_name: str) -> int:
    """Получить количество записей в таблице"""
    try:
        from sqlalchemy import text
        db = get_db_interface()
        if not db or not db.is_available:
            return -1
        with db.get_session() as session:
            # Используем raw SQL для подсчета записей
            result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            return count if count is not None else 0
    except Exception as e:
        centralized_logger.error(f"Ошибка получения количества записей в таблице {table_name}: {e}", user_id=0)
        return -1  # Возвращаем -1 для обозначения ошибки

def get_table_info(table_name: str) -> Dict[str, Any]:
    """Получить детальную информацию о таблице"""
    try:
        from sqlalchemy import inspect, text
        from datetime import datetime
        
        db = get_db_interface()
        if not db or not db.is_available:
            return {}
        inspector = inspect(db.engine)
        
        # Проверяем, существует ли таблица
        if table_name not in inspector.get_table_names():
            return None
        
        # Получаем количество записей
        with db.get_session() as session:
            count_result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = count_result.scalar()
        
        # Получаем размер таблицы
        with db.get_session() as session:
            size_result = session.execute(text(f"""
                SELECT pg_size_pretty(pg_total_relation_size('{table_name}')) as size
            """))
            size = size_result.scalar() or "N/A"
        
        # Получаем время последнего обновления (если есть поля updated_at или created_at)
        last_update = "N/A"
        try:
            with db.get_session() as session:
                # Сначала проверяем, какие поля времени существуют в таблице
                inspector = inspect(db.engine)
                columns = inspector.get_columns(table_name)
                column_names = [col['name'] for col in columns]
                
                # Проверяем наличие поля updated_at
                if 'updated_at' in column_names:
                    updated_result = session.execute(text(f"""
                        SELECT MAX(updated_at) FROM {table_name} 
                        WHERE updated_at IS NOT NULL
                    """))
                    updated_time = updated_result.scalar()
                    
                    if updated_time:
                        last_update = updated_time.strftime("%Y-%m-%d %H:%M:%S")
                elif 'created_at' in column_names:
                    # Если нет updated_at, проверяем created_at
                    created_result = session.execute(text(f"""
                        SELECT MAX(created_at) FROM {table_name} 
                        WHERE created_at IS NOT NULL
                    """))
                    created_time = created_result.scalar()
                    if created_time:
                        last_update = created_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            # Если нет полей времени или ошибка, оставляем N/A
            centralized_logger.debug(f"Не удалось получить время обновления для таблицы {table_name}: {e}")
            pass
        
        return {
            'count': count,
            'size': size,
            'last_update': last_update
        }
        
    except Exception as e:
        centralized_logger.error(f"Ошибка получения информации о таблице {table_name}: {e}")
        return None

def get_all_tables_info() -> Dict[str, Dict[str, Any]]:
    """Получить информацию о всех таблицах за один раз (оптимизированно)"""
    try:
        from sqlalchemy import inspect, text
        from datetime import datetime
        
        db = DatabaseInterface()
        inspector = inspect(db.engine)
        
        # Получаем список всех таблиц
        table_names = inspector.get_table_names()
        if not table_names:
            return {}
        
        # Собираем информацию о всех таблицах в одном подключении
        tables_info = {}
        
        with db.get_session() as session:
            # Получаем количество записей для всех таблиц одним запросом
            for table_name in table_names:
                try:
                    # Количество записей
                    count_result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = count_result.scalar()
                    
                    # Размер таблицы
                    size_result = session.execute(text(f"""
                        SELECT pg_size_pretty(pg_total_relation_size('{table_name}')) as size
                    """))
                    size = size_result.scalar() or "N/A"
                    
                    # Время последнего обновления
                    last_update = "N/A"
                    try:
                        # Проверяем поля времени
                        columns = inspector.get_columns(table_name)
                        column_names = [col['name'] for col in columns]
                        
                        if 'updated_at' in column_names:
                            updated_result = session.execute(text(f"""
                                SELECT MAX(updated_at) FROM {table_name} 
                                WHERE updated_at IS NOT NULL
                            """))
                            updated_time = updated_result.scalar()
                            if updated_time:
                                last_update = updated_time.strftime("%Y-%m-%d %H:%M:%S")
                        elif 'created_at' in column_names:
                            created_result = session.execute(text(f"""
                                SELECT MAX(created_at) FROM {table_name} 
                                WHERE created_at IS NOT NULL
                            """))
                            created_time = created_result.scalar()
                            if created_time:
                                last_update = created_time.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        pass  # Игнорируем ошибки с полями времени
                    
                    tables_info[table_name] = {
                        'count': count,
                        'size': size,
                        'last_update': last_update
                    }
                    
                except Exception as e:
                    centralized_logger.debug(f"Ошибка получения информации о таблице {table_name}: {e}")
                    tables_info[table_name] = {
                        'count': 'ERROR',
                        'size': 'ERROR',
                        'last_update': 'ERROR'
                    }
        
        return tables_info
        
    except Exception as e:
        centralized_logger.error(f"Ошибка получения информации о всех таблицах: {e}")
        return {}

def get_database_stats() -> Dict[str, Any]:
    """Получить статистику базы данных"""
    try:
        from sqlalchemy import inspect
        db = DatabaseInterface()
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        stats = {}
        stats['Таблицы'] = len(tables)
        
        # Подсчитываем записи в каждой таблице
        from sqlalchemy import text
        with db.get_session() as session:
            for table in tables:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    stats[f"Записей в {table}"] = count
                except Exception as e:
                    stats[f"Ошибка в {table}"] = str(e)
        
        return stats
    except Exception as e:
        centralized_logger.error(f"Ошибка получения статистики БД: {e}")
        return {"Ошибка": str(e)}

def create_all_tables() -> bool:
    """Создать все таблицы в базе данных"""
    try:
        db = DatabaseInterface()
        success = db.create_database()
        if success:
            centralized_logger.info("Все таблицы созданы успешно")
        else:
            centralized_logger.error("Ошибка создания таблиц")
        return success
    except Exception as e:
        centralized_logger.error(f"Ошибка создания таблиц: {e}")
        return False

def clear_all_tables() -> bool:
    """Очистить все таблицы в базе данных"""
    centralized_logger.info("🔍 Начинаем очистку всех таблиц...")
    
    try:
        centralized_logger.info("🔍 Создаем экземпляр DatabaseInterface...")
        db = DatabaseInterface()
        centralized_logger.info("✅ DatabaseInterface создан успешно")
        
        centralized_logger.info("🔍 Вызываем db.clear_all_tables()...")
        success = db.clear_all_tables()
        centralized_logger.info(f"📊 Результат db.clear_all_tables(): {success}")
        
        if success:
            centralized_logger.info("✅ Все таблицы очищены успешно")
        else:
            centralized_logger.error("❌ Ошибка очистки таблиц")
        return success
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка очистки таблиц: {e}")
        centralized_logger.error(f"❌ Тип ошибки: {type(e).__name__}")
        centralized_logger.error(f"❌ Детали ошибки: {str(e)}")
        return False


# === УПРАВЛЕНИЕ ЧЕРНЫМ СПИСКОМ ===

def add_to_blacklist(user_id: int, blacklisted_id: int) -> bool:
    """
    Добавление пользователя в черный список
    
    Args:
        user_id: ID пользователя, который добавляет в черный список
        blacklisted_id: ID пользователя, которого добавляют в черный список
        
    Returns:
        bool: True если добавление успешно, False иначе
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            centralized_logger.error("❌ База данных недоступна")
            return False
        
        # Проверяем, есть ли уже в черном списке
        existing = db.get_blacklisted(user_id)
        if blacklisted_id in existing:
            centralized_logger.warning(f"⚠️ Пользователь {blacklisted_id} уже в черном списке пользователя {user_id}")
            return True
        
        # Добавляем в черный список
        success = db.add_to_blacklist(user_id, blacklisted_id)
        if success:
            centralized_logger.info(f"✅ Пользователь {blacklisted_id} добавлен в черный список пользователя {user_id}")
        else:
            centralized_logger.error(f"❌ Ошибка добавления пользователя {blacklisted_id} в черный список")
        return success
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка добавления в черный список: {e}")
        return False


def get_blacklist(user_id: int) -> list:
    """
    Получение черного списка пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        list: Список ID пользователей в черном списке
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            centralized_logger.error("❌ База данных недоступна")
            return []
        
        blacklist = db.get_blacklisted(user_id)
        centralized_logger.info(f"✅ Получен черный список пользователя {user_id}: {len(blacklist)} пользователей")
        return blacklist
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка получения черного списка: {e}")
        return []


def remove_from_blacklist(user_id: int, blacklisted_id: int) -> bool:
    """
    Удаление пользователя из черного списка
    
    Args:
        user_id: ID пользователя, который удаляет из черного списка
        blacklisted_id: ID пользователя, которого удаляют из черного списка
        
    Returns:
        bool: True если удаление успешно, False иначе
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            centralized_logger.error("❌ База данных недоступна")
            return False
        
        # Удаляем из черного списка
        success = db.remove_from_blacklist(user_id, blacklisted_id)
        if success:
            centralized_logger.info(f"✅ Пользователь {blacklisted_id} удален из черного списка пользователя {user_id}")
        else:
            centralized_logger.warning(f"⚠️ Пользователь {blacklisted_id} не найден в черном списке пользователя {user_id}")
        return success
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка удаления из черного списка: {e}")
        return False


def is_user_blacklisted(user_id: int, target_user_id: int) -> bool:
    """
    Проверка, находится ли пользователь в черном списке
    
    Args:
        user_id: ID пользователя, чей черный список проверяется
        target_user_id: ID пользователя, которого проверяем
        
    Returns:
        bool: True если пользователь в черном списке, False иначе
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            centralized_logger.error("❌ База данных недоступна")
            return False
        
        blacklist = db.get_blacklisted(user_id)
        is_blacklisted = target_user_id in blacklist
        centralized_logger.debug(f"🔍 Проверка черного списка: пользователь {target_user_id} {'в' if is_blacklisted else 'не в'} черном списке пользователя {user_id}")
        return is_blacklisted
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка проверки черного списка: {e}")
        return False


# === СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ ===

def get_user_statistics(user_id: int) -> dict:
    """
    Получение статистики пользователя из базы данных
    
    Args:
        user_id: ID пользователя VK
        
    Returns:
        dict: Словарь со статистикой пользователя
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            centralized_logger.error("❌ База данных недоступна")
            return {}
        
        # Получаем статистику пользователя
        stats = db.get_user_statistics(user_id)
        centralized_logger.info(f"✅ Получена статистика пользователя {user_id}: {len(stats)} показателей")
        return stats
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка получения статистики пользователя: {e}")
        return {}


def get_user_profile_stats(user_id: int) -> dict:
    """
    Получение расширенной статистики профиля пользователя
    
    Args:
        user_id: ID пользователя VK
        
    Returns:
        dict: Словарь с расширенной статистикой профиля
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            centralized_logger.error("❌ База данных недоступна")
            return {}
        
        # Получаем базовую статистику
        stats = db.get_user_statistics(user_id)
        
        # Добавляем дополнительную информацию о профиле
        with db.get_session() as session:
            # Количество поисковых запросов (таблица search_history удалена)
            stats['total_searches'] = 0
            stats['last_search_date'] = None
            stats['last_search_results'] = 0
            
            # Настройки пользователя
            user_settings = session.query(UserSettings).filter(
                UserSettings.vk_user_id == user_id
            ).first()
            
            if user_settings:
                stats['user_settings'] = {
                    'min_age': user_settings.min_age,
                    'max_age': user_settings.max_age,
                    'sex_preference': user_settings.sex_preference,
                    'city_preference': user_settings.city_preference,
                    'online_only': user_settings.online,
                    'zodiac_signs': user_settings.zodiac_signs if user_settings.zodiac_signs else [],
                    'relationship_statuses': user_settings.relationship_statuses if user_settings.relationship_statuses else []
                }
            else:
                stats['user_settings'] = None
        
        centralized_logger.info(f"✅ Получена расширенная статистика профиля пользователя {user_id}")
        return stats
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка получения статистики профиля: {e}")
        return {}


def get_user_activity_summary(user_id: int) -> dict:
    """
    Получение сводки активности пользователя
    
    Args:
        user_id: ID пользователя VK
        
    Returns:
        dict: Словарь со сводкой активности
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            centralized_logger.error("❌ База данных недоступна")
            return {}
        
        with db.get_session() as session:
            # Общая статистика активности
            activity = {}
            
            # Логирование в БД отключено, логи только в файлах
            activity['bot_logs_count'] = 0
            activity['messages_with_bot'] = 0  # Таблица bot_messages удалена
            activity['last_activity'] = None  # Таблица bot_messages удалена
            
            # Статистика по дням (последние 7 дней)
            from datetime import datetime, timedelta
            week_ago = datetime.now() - timedelta(days=7)
            
            # Поиски за неделю (таблица search_history удалена)
            activity['searches_last_week'] = 0
            activity['messages_last_week'] = 0  # Таблица bot_messages удалена
        
        centralized_logger.info(f"✅ Получена сводка активности пользователя {user_id}")
        return activity
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка получения сводки активности: {e}")
        return {}


# === СОХРАНЕНИЕ ПАРАМЕТРОВ ПОИСКА ===

def save_search_params(vk_user_id: int, min_age: Optional[int] = None, max_age: Optional[int] = None,
                       sex_preference: Optional[int] = None, zodiac_signs: Optional[List[str]] = None,
                       relationship_statuses: Optional[List[str]] = None, online: Optional[bool] = None) -> bool:
    """
    Сохранение параметров поиска пользователя в базу данных
    
    Args:
        vk_user_id: ID пользователя VK
        min_age: Минимальный возраст (если None - не обновляется)
        max_age: Максимальный возраст (если None - не обновляется)
        sex_preference: Предпочтение по полу (1 - женский, 2 - мужской, 0 - любой, None - не обновляется)
        zodiac_signs: Список знаков зодиака (None - не обновляется)
        relationship_statuses: Список статусов отношений (None - не обновляется)
        online: Только онлайн пользователи (None - не обновляется)
        
    Returns:
        bool: True если сохранение успешно, False иначе
    """
    try:
        db = get_db_interface()
        if not db or not db.is_available:
            centralized_logger.warning(f"⚠️ База данных недоступна, параметры поиска не сохранены для пользователя {vk_user_id}", user_id=vk_user_id)
            return False
        
        with db.get_session() as session:
            # Получаем или создаем настройки пользователя
            from .models import UserSettings, VKUser
            
            user_settings = session.query(UserSettings).filter(
                UserSettings.vk_user_id == vk_user_id
            ).first()
            
            if not user_settings:
                # Проверяем, существует ли пользователь
                vk_user = session.query(VKUser).filter(
                    VKUser.vk_user_id == vk_user_id
                ).first()
                
                if not vk_user:
                    centralized_logger.warning(f"⚠️ Пользователь {vk_user_id} не найден в базе, создаем запись пользователя", user_id=vk_user_id)
                    # Создаем пользователя с базовыми данными
                    vk_user = VKUser(
                        vk_user_id=vk_user_id,
                        first_name="Пользователь",
                        last_name="ВКонтакте",
                        age=None,
                        sex=None,
                        city=None
                    )
                    session.add(vk_user)
                    session.flush()
                
                # Создаем настройки пользователя
                user_settings = UserSettings(
                    vk_user_id=vk_user_id,
                    min_age=min_age if min_age is not None else 18,
                    max_age=max_age if max_age is not None else 35
                )
                session.add(user_settings)
                centralized_logger.info(f"✅ Созданы настройки пользователя {vk_user_id}", user_id=vk_user_id)
            
            # Обновляем только переданные параметры
            if min_age is not None:
                user_settings.min_age = min_age
            if max_age is not None:
                user_settings.max_age = max_age
            if sex_preference is not None:
                user_settings.sex_preference = sex_preference
            if zodiac_signs is not None:
                user_settings.zodiac_signs = zodiac_signs
            if relationship_statuses is not None:
                user_settings.relationship_statuses = relationship_statuses
            if online is not None:
                user_settings.online = online
            
            session.commit()
            
            params_str = []
            if min_age is not None or max_age is not None:
                params_str.append(f"возраст={user_settings.min_age}-{user_settings.max_age}")
            if sex_preference is not None:
                params_str.append(f"пол={user_settings.sex_preference}")
            if zodiac_signs is not None:
                params_str.append(f"зодиак={len(zodiac_signs)} знаков")
            if relationship_statuses is not None:
                params_str.append(f"статусы={len(relationship_statuses)}")
            if online is not None:
                params_str.append(f"онлайн={online}")
            
            centralized_logger.info(f"✅ Сохранены параметры поиска для пользователя {vk_user_id}: {', '.join(params_str)}", user_id=vk_user_id)
            return True
            
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка сохранения параметров поиска для пользователя {vk_user_id}: {e}", user_id=vk_user_id)
        import traceback
        centralized_logger.error(f"📊 TRACEBACK: {traceback.format_exc()}", user_id=0)
        return False


def get_search_params(vk_user_id: int) -> Optional[Dict[str, Any]]:
    """
    Получение параметров поиска пользователя из базы данных
    
    Args:
        vk_user_id: ID пользователя VK
        
    Returns:
        Optional[Dict]: Словарь с параметрами поиска или None если не найдены
        {
            'min_age': int,
            'max_age': int,
            'sex_preference': int,
            'zodiac_signs': List[str],
            'relationship_statuses': List[str],
            'online': bool
        }
    """
    try:
        db = get_db_interface()
        if not db or not db.is_available:
            centralized_logger.warning(f"⚠️ База данных недоступна, параметры поиска не получены для пользователя {vk_user_id}", user_id=vk_user_id)
            return None
        
        with db.get_session() as session:
            from .models import UserSettings
            
            user_settings = session.query(UserSettings).filter(
                UserSettings.vk_user_id == vk_user_id
            ).first()
            
            if not user_settings:
                centralized_logger.debug(f"ℹ️ Параметры поиска для пользователя {vk_user_id} не найдены в базе", user_id=vk_user_id)
                return None
            
            params = {
                'min_age': user_settings.min_age,
                'max_age': user_settings.max_age,
                'sex_preference': user_settings.sex_preference,
                'zodiac_signs': user_settings.zodiac_signs if user_settings.zodiac_signs else [],
                'relationship_statuses': user_settings.relationship_statuses if user_settings.relationship_statuses else [],
                'online': user_settings.online if user_settings.online is not None else False
            }
            
            centralized_logger.debug(f"✅ Получены параметры поиска для пользователя {vk_user_id}: возраст={params['min_age']}-{params['max_age']}, пол={params['sex_preference']}, зодиак={len(params['zodiac_signs'])} знаков, статусы={len(params['relationship_statuses'])}", user_id=vk_user_id)
            return params
            
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка получения параметров поиска для пользователя {vk_user_id}: {e}", user_id=vk_user_id)
        import traceback
        centralized_logger.error(f"📊 TRACEBACK: {traceback.format_exc()}", user_id=0)
        return None


# === ФУНКЦИИ ДЛЯ РАБОТЫ С ЗАШИФРОВАННЫМИ ТОКЕНАМИ ===

def save_user_tokens(vk_user_id: int, access_token: str, refresh_token: str, expires_in: int = 3600) -> bool:
    """
    Сохранение зашифрованных токенов пользователя в базе данных
    
    Args:
        vk_user_id: ID пользователя VK
        access_token: Access токен
        refresh_token: Refresh токен
        expires_in: Время жизни токена в секундах
        
    Returns:
        bool: True если сохранение успешно, False иначе
    """
    try:
        db = DatabaseInterface()
        return db.save_user_tokens(vk_user_id, access_token, refresh_token, expires_in)
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка сохранения токенов пользователя {vk_user_id}: {e}")
        return False


def get_user_access_token(vk_user_id: int) -> Optional[str]:
    """
    Получение расшифрованного access токена пользователя
    
    Args:
        vk_user_id: ID пользователя VK
        
    Returns:
        Optional[str]: Расшифрованный access токен или None
    """
    try:
        db = DatabaseInterface()
        return db.get_user_access_token(vk_user_id)
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка получения access токена пользователя {vk_user_id}: {e}")
        return None


def get_user_refresh_token(vk_user_id: int) -> Optional[str]:
    """
    Получение refresh токена пользователя из БД (не расшифрованный, а хеш)
    
    Args:
        vk_user_id: ID пользователя VK
        
    Returns:
        Optional[str]: Refresh token hash или None если не найден
    """
    try:
        db = DatabaseInterface()
        return db.get_user_refresh_token(vk_user_id)
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка получения refresh токена пользователя {vk_user_id}: {e}")
        return None


def get_user_refresh_token_decrypted(vk_user_id: int) -> Optional[str]:
    """
    Получение расшифрованного refresh токена пользователя из БД
    
    Args:
        vk_user_id: ID пользователя VK
        
    Returns:
        Optional[str]: Расшифрованный refresh token или None если не найден
    """
    try:
        db = DatabaseInterface()
        return db.get_user_refresh_token_decrypted(vk_user_id)
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка получения расшифрованного refresh токена пользователя {vk_user_id}: {e}")
        return None


def verify_user_refresh_token(vk_user_id: int, refresh_token: str) -> bool:
    """
    Проверка refresh токена пользователя
    
    Args:
        vk_user_id: ID пользователя VK
        refresh_token: Refresh токен для проверки
        
    Returns:
        bool: True если токен валиден, False иначе
    """
    try:
        db = DatabaseInterface()
        return db.verify_user_refresh_token(vk_user_id, refresh_token)
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка проверки refresh токена пользователя {vk_user_id}: {e}")
        return False


def is_user_token_expired(vk_user_id: int) -> bool:
    """
    Проверка истечения токена пользователя
    
    Args:
        vk_user_id: ID пользователя VK
        
    Returns:
        bool: True если токен истек, False иначе
    """
    try:
        db = DatabaseInterface()
        return db.is_user_token_expired(vk_user_id)
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка проверки истечения токена пользователя {vk_user_id}: {e}")
        return True


def clear_user_tokens(vk_user_id: int) -> bool:
    """
    Очистка токенов пользователя из базы данных
    
    Args:
        vk_user_id: ID пользователя VK
        
    Returns:
        bool: True если очистка успешна, False иначе
    """
    try:
        db = DatabaseInterface()
        return db.clear_user_tokens(vk_user_id)
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка очистки токенов пользователя {vk_user_id}: {e}")
        return False


def get_user_token_info(vk_user_id: int) -> dict:
    """
    Получение информации о токенах пользователя
    
    Args:
        vk_user_id: ID пользователя VK
        
    Returns:
        dict: Информация о токенах
    """
    try:
        db = DatabaseInterface()
        return db.get_user_token_info(vk_user_id)
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка получения информации о токенах пользователя {vk_user_id}: {e}")
        return {
            'has_tokens': False,
            'is_expired': True,
            'expires_at': None,
            'updated_at': None
        }


def update_user_tokens(vk_user_id: int, access_token: Optional[str] = None, 
                      refresh_token: Optional[str] = None, expires_in: Optional[int] = None) -> bool:
    """
    Обновление токенов пользователя
    
    Args:
        vk_user_id: ID пользователя VK
        access_token: Новый access токен (опционально)
        refresh_token: Новый refresh токен (опционально)
        expires_in: Время жизни токена в секундах (опционально)
        
    Returns:
        bool: True если обновление успешно, False иначе
    """
    try:
        db = DatabaseInterface()
        return db.update_user_tokens(vk_user_id, access_token, refresh_token, expires_in)
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка обновления токенов пользователя {vk_user_id}: {e}")
        return False


# === УПРАВЛЕНИЕ ТОКЕНОМ ГРУППЫ ===

# ID специального пользователя для хранения токена группы
GROUP_ADMIN_USER_ID = 900000009


def get_group_token() -> Optional[str]:
    """
    Получение расшифрованного токена группы из базы данных
    
    Returns:
        Optional[str]: Токен группы или None если не найден/недоступен
    """
    try:
        db = DatabaseInterface()
        return db.get_user_access_token(GROUP_ADMIN_USER_ID)
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка получения токена группы: {e}", user_id=0)
        return None


def update_group_token(group_token: str) -> bool:
    """
    Обновление токена группы в базе данных (зашифрованным)
    
    Args:
        group_token: Новый токен группы
        
    Returns:
        bool: True если обновление успешно, False иначе
    """
    try:
        db = DatabaseInterface()
        # Используем expires_in=None для токена группы (не истекает)
        return db.update_user_tokens(GROUP_ADMIN_USER_ID, access_token=group_token, refresh_token=None, expires_in=None)
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка обновления токена группы: {e}", user_id=0)
        return False


def migrate_group_token_from_env() -> bool:
    """
    Миграция токена группы из переменной окружения .env в базу данных
    
    Создает пользователя с ID 900000009 если его нет, и сохраняет токен зашифрованным
    
    Returns:
        bool: True если миграция успешна, False иначе
    """
    try:
        import os
        from dotenv import load_dotenv
        
        # Загружаем переменные окружения
        load_dotenv()
        
        # Получаем токен из .env
        env_token = os.getenv('VK_GROUP_TOKEN')
        if not env_token or env_token == 'your_group_token_here':
            centralized_logger.warning("⚠️ Токен группы не найден в .env или содержит значение по умолчанию", user_id=0)
            return False
        
        # Получаем ID группы
        group_id_str = os.getenv('VK_GROUP_ID', '0')
        try:
            group_id = int(group_id_str)
        except ValueError:
            centralized_logger.error(f"❌ Неверный формат VK_GROUP_ID: {group_id_str}", user_id=0)
            return False
        
        # Проверяем, есть ли уже токен в базе
        existing_token = get_group_token()
        if existing_token:
            centralized_logger.info("ℹ️ Токен группы уже существует в базе данных, пропускаем миграцию", user_id=0)
            return True
        
        # Создаем или обновляем пользователя-администратора
        db = DatabaseInterface()
        if not db.is_available:
            centralized_logger.error("❌ База данных недоступна для миграции токена", user_id=0)
            return False
        
        # Создаем пользователя-администратора если его нет
        try:
            with db.get_session() as session:
                from sqlalchemy import text
                # Проверяем существование пользователя
                user_exists = session.execute(
                    text("SELECT COUNT(*) FROM vk_users WHERE vk_user_id = :user_id"),
                    {"user_id": GROUP_ADMIN_USER_ID}
                ).scalar() > 0
                
                if not user_exists:
                    # Создаем пользователя-администратора
                    session.execute(
                        text("""
                            INSERT INTO vk_users (vk_user_id, first_name, last_name, created_at, updated_at)
                            VALUES (:user_id, 'Group', 'Admin', NOW(), NOW())
                            ON CONFLICT (vk_user_id) DO NOTHING
                        """),
                        {"user_id": GROUP_ADMIN_USER_ID}
                    )
                    session.commit()
                    centralized_logger.info(f"✅ Создан пользователь-администратор с ID {GROUP_ADMIN_USER_ID}", user_id=0)
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка создания пользователя-администратора: {e}", user_id=0)
            return False
        
        # Сохраняем токен в базу
        if update_group_token(env_token):
            centralized_logger.info("✅ Токен группы успешно мигрирован из .env в базу данных", user_id=0)
            return True
        else:
            centralized_logger.error("❌ Ошибка сохранения токена группы в базу данных", user_id=0)
            return False
            
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка миграции токена группы: {e}", user_id=0)
        return False


def read_group_token_console() -> Optional[str]:
    """
    Чтение токена группы из базы данных и вывод в консоль (для администратора)
    
    Returns:
        Optional[str]: Токен группы или None если не найден
    """
    try:
        token = get_group_token()
        if token:
            # Адаптивная маскировка в зависимости от длины токена
            length = len(token) if token else 0
            if length >= 16:
                masked_token = token[:8] + "***" + token[-5:]
            elif length >= 13:
                masked_token = token[:6] + "***" + token[-4:]
            elif length >= 11:
                masked_token = token[:4] + "***" + token[-4:]
            elif length >= 9:
                masked_token = token[:3] + "***" + token[-3:]
            elif length >= 8:
                masked_token = token[:2] + "***" + token[-3:]
            elif length >= 5:
                masked_token = token[:1] + "***" + token[-1:]
            elif length >= 4:
                masked_token = token[:1] + "***"
            else:
                masked_token = "***"
            print(f"🔐 Токен группы найден в базе данных: {masked_token}")
            return token
        else:
            print("❌ Токен группы не найден в базе данных")
            return None
    except Exception as e:
        print(f"❌ Ошибка чтения токена группы: {e}")
        return None


def count_records(
    model_name: str,
    filters: Optional[Dict[str, Any]] = None,
    date_from: Optional[datetime] = None,
    date_field_primary: Optional[str] = None,
    date_field_fallback: Optional[str] = None,
    distinct_field: Optional[str] = None,
    user_id: Optional[int] = None,
    user_field: Optional[str] = None
) -> int:
    """
    Универсальная функция для подсчета записей в базе данных с поддержкой фильтров
    
    Args:
        model_name: Название модели ('Photo', 'Favorite', 'Blacklisted', 'VKUser', 'UserSettings')
        filters: Словарь с дополнительными фильтрами {поле: значение}
        date_from: Дата начала периода для фильтрации по дате
        date_field_primary: Основное поле даты (например, 'updated_at', 'token_updated_at')
        date_field_fallback: Резервное поле даты (например, 'created_at')
        distinct_field: Поле для подсчета уникальных значений (например, 'vk_user_id')
        user_id: ID пользователя для фильтрации по полю user_field
        user_field: Название поля для фильтрации по user_id (например, 'user_vk_id', 'found_by_user_id')
    
    Returns:
        int: Количество записей, соответствующих фильтрам
    
    Примеры использования:
        from datetime import datetime, time
        
        # Подсчет всех фото
        count = count_records('Photo')
        
        # Подсчет фото пользователя за сегодня
        today = datetime.combine(datetime.now().date(), time.min)
        count = count_records(
            'Photo',
            date_from=today,
            date_field_primary='updated_at',
            date_field_fallback='created_at',
            user_id=12345,
            user_field='found_by_user_id'
        )
        
        # Подсчет уникальных пользователей по фото
        count = count_records(
            'Photo',
            distinct_field='vk_user_id',
            user_id=12345,
            user_field='found_by_user_id'
        )
    """
    try:
        from src.database.models import Photo, Favorite, Blacklisted, VKUser, UserSettings
        
        # Маппинг названий моделей на классы
        model_map = {
            'Photo': Photo,
            'Favorite': Favorite,
            'Blacklisted': Blacklisted,
            'VKUser': VKUser,
            'UserSettings': UserSettings
        }
        
        if model_name not in model_map:
            centralized_logger.error(f"❌ Неизвестная модель: {model_name}", user_id=0)
            return 0
        
        model_class = model_map[model_name]
        db = get_db_interface()
        
        if not db or not db.is_available:
            centralized_logger.error("❌ База данных недоступна", user_id=0)
            return 0
        
        return db.count_records(
            model_class=model_class,
            filters=filters,
            date_from=date_from,
            date_field_primary=date_field_primary,
            date_field_fallback=date_field_fallback,
            distinct_field=distinct_field,
            user_id=user_id,
            user_field=user_field
        )
        
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка подсчета записей {model_name}: {e}", user_id=0)
        return 0


def check_group_token_validity(group_token: Optional[str] = None) -> bool:
    """
    Проверка валидности токена группы через VK API
    
    Args:
        group_token: Токен для проверки (если None, берется из базы)
        
    Returns:
        bool: True если токен валиден, False иначе
    """
    try:
        # Получаем токен если не указан
        if group_token is None:
            group_token = get_group_token()
        
        if not group_token:
            centralized_logger.warning("⚠️ Токен группы отсутствует для проверки", user_id=0)
            return False
        
        # Используем простой запрос к VK API для проверки
        import requests
        response = requests.get(
            'https://api.vk.com/method/groups.getById',
            params={
                'access_token': group_token,
                'v': '5.131'
            },
            timeout=5
        )
        
        result = response.json()
        
        if 'error' in result:
            error_code = result.get('error', {}).get('error_code', 0)
            error_msg = result.get('error', {}).get('error_msg', 'Unknown error')
            centralized_logger.error(f"❌ Токен группы невалиден: {error_code} - {error_msg}", user_id=0)
            return False
        
        if 'response' in result:
            centralized_logger.info("✅ Токен группы валиден", user_id=0)
            return True
        
        return False
        
    except Exception as e:
        centralized_logger.error(f"❌ Ошибка проверки валидности токена группы: {e}", user_id=0)
        return False
