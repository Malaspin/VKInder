#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Централизованная система логирования
Приоритет: База данных > Файлы > Консоль
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from loguru import logger

# СНАЧАЛА отключаем ВСЕ существующие логгеры
root_logger = logging.getLogger()
root_logger.handlers.clear()
root_logger.setLevel(logging.CRITICAL)

# Отключаем распространение для всех основных логгеров
logger_names = [
    'src.database.database_interface',
    'src.database.postgres_manager', 
    'src.bot.vk_bot',
    'src.database.db_api',
    'src.utils.centralized_logger'
]

for logger_name in logger_names:
    other_logger = logging.getLogger(logger_name)
    other_logger.propagate = False
    other_logger.handlers.clear()
    other_logger.setLevel(logging.CRITICAL)

# Защита от прямого запуска
if __name__ == "__main__":
    print("❌ Этот файл нельзя запускать напрямую!")
    print("⚠️ Модули утилит работают только как часть основной программы")
    sys.exit(1)

class CentralizedLogger:
    """Централизованная система логирования с приоритетом БД"""
    
    def __init__(self):
        """Инициализация централизованного логгера"""
        self.db_available = False
        self.db_interface = None
        self.file_logger = None
        self.console_logger = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Настройка системы логирования"""
        try:
            # СНАЧАЛА отключаем ВСЕ существующие логгеры
            self._disable_all_loggers()
            
            # Инициализация БД будет выполнена лениво при первом обращении
            self.db_interface = None
            self.db_available = False
            self._db_initialized = False
            
        except Exception as e:
            logger.warning(f"⚠️ Централизованное логирование: ошибка инициализации - {e}")
            self.db_available = False
        
        # Настройка файлового логирования как fallback
        self._setup_file_logging()
        
        # Настройка консольного логирования
        self._setup_console_logging()
    
    def _disable_all_loggers(self):
        """Отключить все существующие логгеры от вывода в консоль"""
        try:
            # Получаем root логгер
            root_logger = logging.getLogger()
            
            # Очищаем все обработчики root логгера
            root_logger.handlers.clear()
            
            # Устанавливаем высокий уровень для root логгера
            root_logger.setLevel(logging.CRITICAL)
            
            # Отключаем распространение для всех основных логгеров
            logger_names = [
                'src.database.database_interface',
                'src.database.postgres_manager', 
                'src.bot.vk_bot',
                'src.database.db_api',
                'src.utils.centralized_logger'
            ]
            
            for logger_name in logger_names:
                other_logger = logging.getLogger(logger_name)
                other_logger.propagate = False
                other_logger.handlers.clear()
                other_logger.setLevel(logging.CRITICAL)
                
        except Exception as e:
            print(f"❌ Ошибка отключения логгеров: {e}")
    
    def _setup_file_logging(self):
        """Настройка файлового логирования"""
        try:
            # Создаем директорию для логов
            os.makedirs('logs', exist_ok=True)
            
            # Генерируем суффикс с временной меткой
            timestamp_suffix = datetime.now().strftime("_%Y%m%d_%H")
            
            # Настройка файлового логгера
            log_filename = f'logs/centralized{timestamp_suffix}.log'
            self.file_logger = logging.getLogger('centralized_file')
            self.file_logger.setLevel(logging.DEBUG)
            
            # Очищаем существующие обработчики
            self.file_logger.handlers.clear()
            
            # Добавляем файловый обработчик
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.file_logger.addHandler(file_handler)
            # Отключаем распространение для предотвращения дублирования
            self.file_logger.propagate = False
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки файлового логирования: {e}")
    
    def _setup_console_logging(self):
        """Настройка консольного логирования - только технические реперные точки и ошибки"""
        try:
            # Устанавливаем уровень root логгера, чтобы предотвратить дублирование
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.WARNING)  # Только WARNING и ERROR для root
            
            # Отключаем все другие логгеры от вывода в консоль
            for logger_name in ['src.database.database_interface', 'src.database.postgres_manager', 'src.bot.vk_bot']:
                other_logger = logging.getLogger(logger_name)
                other_logger.propagate = False
                other_logger.handlers.clear()
            
            # Создаем консольный логгер
            self.console_logger = logging.getLogger('centralized_console')
            self.console_logger.setLevel(logging.WARNING)  # Только WARNING и ERROR в консоль
            
            # Очищаем существующие обработчики
            self.console_logger.handlers.clear()
            
            # Добавляем консольный обработчик
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)  # Только WARNING и ERROR
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.console_logger.addHandler(console_handler)
            
            # Отключаем распространение для предотвращения дублирования
            self.console_logger.propagate = False
            
            logger.info("✅ Централизованное логирование: консоль настроена (только WARNING/ERROR)")
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки консольного логирования: {e}")
    
    def _init_db_if_needed(self):
        """Ленивая инициализация БД при первом обращении"""
        if self._db_initialized:
            return
            
        try:
            from src.database.database_interface import DatabaseInterface
            self.db_interface = DatabaseInterface()
            self.db_available = True
            self._db_initialized = True
            logger.info("✅ Централизованное логирование: БД инициализирована")
        except Exception as e:
            logger.warning(f"⚠️ Централизованное логирование: БД недоступна - {e}")
            self.db_available = False
            self._db_interface = None
            self._db_initialized = True  # Помечаем как инициализированную, чтобы не повторять попытки
    
    def log_to_db_direct(self, level: str, message: str, user_id: int = 0) -> bool:
        """Запись лога в базу данных (без использования centralized_logger)"""
        # Инициализируем БД только если еще не инициализирована
        if not self._db_initialized:
            self._init_db_if_needed()
        
        # Если БД недоступна, не пытаемся записывать
        if not self.db_available or not self.db_interface:
            return False
        
        try:
            # Нормализуем уровень логирования (всегда lowercase)
            normalized_level = level.lower()
            
            return self.db_interface.add_bot_log(
                vk_user_id=user_id,
                log_level=normalized_level,
                log_message=message
            )
        except Exception as e:
            # Если произошла ошибка, помечаем БД как недоступную
            self.db_available = False
            # Используем print вместо centralized_logger чтобы избежать рекурсии
            print(f"❌ Ошибка записи лога в БД: {e}")
            return False
    
    def log_to_db(self, level: str, message: str, user_id: int = 0) -> bool:
        """Запись лога в базу данных (устаревший метод)"""
        return self.log_to_db_direct(level, message, user_id)
    
    def log_to_file(self, level: str, message: str, user_id: int = 0):
        """Запись лога в файл"""
        if not self.file_logger:
            return
        
        try:
            # Форматируем сообщение с user_id
            formatted_message = f"[User:{user_id}] {message}" if user_id > 0 else message
            
            # Записываем в файл
            if level.lower() == 'debug':
                self.file_logger.debug(formatted_message)
            elif level.lower() == 'info':
                self.file_logger.info(formatted_message)
            elif level.lower() == 'warning':
                self.file_logger.warning(formatted_message)
            elif level.lower() == 'error':
                self.file_logger.error(formatted_message)
            else:
                self.file_logger.info(formatted_message)
                
        except Exception as e:
            logger.error(f"❌ Ошибка записи лога в файл: {e}")
    
    def log_to_console(self, level: str, message: str, user_id: int = 0):
        """Запись лога в консоль (только INFO, WARNING, ERROR)"""
        if not self.console_logger:
            return
        
        # Нормализуем уровень логирования
        normalized_level = level.lower()
        
        # В консоль выводим все уровни для отладки токенов
        if normalized_level not in ['debug', 'info', 'warning', 'error']:
            return
        
        try:
            # Форматируем сообщение с user_id
            formatted_message = f"[User:{user_id}] {message}" if user_id > 0 else message
            
            # Записываем в консоль БЕЗ использования стандартного логгера
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {normalized_level.upper()} - {formatted_message}")
                
        except Exception as e:
            print(f"❌ Ошибка записи лога в консоль: {e}")
    
    def log(self, level: str, message: str, user_id: int = 0, force_console: bool = False):
        """
        Централизованная запись лога (файл, БД, консоль только для WARNING/ERROR)
        
        Args:
            level: Уровень логирования (debug, info, warning, error)
            message: Текст сообщения
            user_id: ID пользователя (0 для системных логов)
            force_console: Принудительный вывод в консоль
        """
        # Приоритет 1: База данных (если доступна)
        if self.db_available:
            self.log_to_db_direct(level, message, user_id)
        
        # Приоритет 2: Файл (всегда записываем как fallback)
        self.log_to_file(level, message, user_id)
        
        # Приоритет 3: Консоль (только WARNING и ERROR, или принудительно)
        if force_console or level.lower() in ['warning', 'error']:
            self.log_to_console(level, message, user_id)
    
    def debug(self, message: str, user_id: int = 0):
        """Запись DEBUG лога"""
        self.log('debug', message, user_id)
    
    def info(self, message: str, user_id: int = 0):
        """Запись INFO лога"""
        self.log('info', message, user_id)
    
    def warning(self, message: str, user_id: int = 0):
        """Запись WARNING лога"""
        self.log('warning', message, user_id)
    
    def tech_point(self, message: str, user_id: int = 0):
        """Техническая реперная точка - выводится в консоль и БД"""
        # В консоль выводим напрямую
        formatted_message = f"[User:{user_id}] {message}" if user_id > 0 else message
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - 📍 {formatted_message}")
        
        # В БД записываем как INFO
        self.log('info', message, user_id)
    
    def error(self, message: str, user_id: int = 0):
        """Запись ERROR лога"""
        self.log('error', message, user_id)
    
    def get_logs(self, user_id: int = 0, level: str = None, limit: int = 100) -> list:
        """Получение логов из базы данных"""
        if not self.db_available or not self.db_interface:
            return []
        
        try:
            return self.db_interface.get_bot_logs(user_id, level, limit)
        except Exception as e:
            logger.error(f"❌ Ошибка получения логов из БД: {e}")
            return []
    
    def is_db_available(self) -> bool:
        """Проверка доступности базы данных"""
        return self.db_available

# Глобальный экземпляр централизованного логгера
centralized_logger = CentralizedLogger()

# Функции для удобного использования
def log_debug(message: str, user_id: int = 0):
    """Запись DEBUG лога"""
    centralized_logger.debug(message, user_id)

def log_info(message: str, user_id: int = 0):
    """Запись INFO лога"""
    centralized_logger.info(message, user_id)

def log_warning(message: str, user_id: int = 0):
    """Запись WARNING лога"""
    centralized_logger.warning(message, user_id)

def log_error(message: str, user_id: int = 0):
    """Запись ERROR лога"""
    centralized_logger.error(message, user_id)

def get_logs(user_id: int = 0, level: str = None, limit: int = 100) -> list:
    """Получение логов из базы данных"""
    return centralized_logger.get_logs(user_id, level, limit)

def is_db_logging_available() -> bool:
    """Проверка доступности логирования в БД"""
    return centralized_logger.is_db_available()
