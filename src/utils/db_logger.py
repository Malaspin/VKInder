"""
Отдельный модуль для логирования в базу данных
Избегает циклических зависимостей с centralized_logger
"""

import sys
import os
from datetime import datetime

# Добавляем путь к src для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Глобальная переменная для ленивой инициализации
_db_interface = None
_db_available = False
_db_initialized = False

def _init_db_if_needed():
    """Ленивая инициализация БД при первом обращении"""
    global _db_interface, _db_available, _db_initialized
    if _db_initialized:
        return
        
    try:
        from src.database.database_interface import DatabaseInterface
        _db_interface = DatabaseInterface()
        _db_available = True
        _db_initialized = True
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - ✅ db_logger: БД инициализирована")
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - WARNING - ⚠️ db_logger: БД недоступна - {e}")
        _db_available = False
        _db_initialized = True  # Помечаем как инициализированную, чтобы не повторять попытки

def log_to_db(level: str, message: str, user_id: int = 0) -> bool:
    """
    Запись лога в базу данных (без использования centralized_logger)
    
    Args:
        level: Уровень логирования (debug, info, warning, error)
        message: Текст сообщения
        user_id: ID пользователя (0 для системных логов)
    
    Returns:
        bool: True если успешно записано, False если ошибка
    """
    _init_db_if_needed()
    
    if not _db_available or not _db_interface:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - WARNING - ⚠️ db_logger: БД недоступна для записи лога: {message}")
        return False
    
    try:
        # Нормализуем уровень логирования (всегда UPPERCASE)
        normalized_level = level.upper()
        
        # Записываем лог в БД
        success = _db_interface.add_bot_log(
            vk_user_id=user_id,
            log_level=normalized_level,
            log_message=message
        )
        
        return success
        
    except Exception as e:
        # Используем print вместо centralized_logger чтобы избежать рекурсии
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR - ❌ db_logger: Ошибка записи лога в БД: {e}")
        return False

def debug(message: str, user_id: int = 0) -> bool:
    """Запись DEBUG лога в БД"""
    return log_to_db('debug', message, user_id)

def info(message: str, user_id: int = 0) -> bool:
    """Запись INFO лога в БД"""
    return log_to_db('info', message, user_id)

def warning(message: str, user_id: int = 0) -> bool:
    """Запись WARNING лога в БД"""
    return log_to_db('warning', message, user_id)

def error(message: str, user_id: int = 0) -> bool:
    """Запись ERROR лога в БД"""
    return log_to_db('error', message, user_id)

if __name__ == "__main__":
    print("❌ Этот модуль не предназначен для прямого запуска")
    print("Используйте функции log_to_db, debug, info, warning, error")
