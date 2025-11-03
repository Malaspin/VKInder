#!/usr/bin/env python3
"""
Менеджер PostgreSQL для автоматической проверки и запуска базы данных
Проверяет статус PostgreSQL и запускает его при необходимости
"""

import os
import sys
import subprocess
import time
import platform
import psycopg2
from typing import Optional, Dict, Any
from loguru import logger
from src.utils.centralized_logger import centralized_logger


class PostgreSQLManager:
    """Менеджер для управления PostgreSQL"""
    
    def _get_local_db_path(self) -> str:
        """
        Получение абсолютного пути к локальной базе данных
        База данных находится в src/database/DB_BASE/vkinder_cluster
        
        Returns:
            str: Абсолютный путь к директории базы данных
        """
        # Определяем путь относительно файла postgres_manager.py
        # Файл находится в src/database/, база в src/database/DB_BASE/vkinder_cluster
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        local_data_path = os.path.join(current_file_dir, 'DB_BASE', 'vkinder_cluster')
        # Преобразуем в абсолютный путь для надежности
        return os.path.abspath(local_data_path)
    
    def __init__(self):
        """Инициализация менеджера PostgreSQL"""
        self.host = os.getenv('DB_HOST', 'localhost')
        # Проверяем, есть ли локальная база в проекте
        # База теперь находится в src/database/DB_BASE/vkinder_cluster
        local_data_path = self._get_local_db_path()
        
        # Берем порт из .env, если не указан - определяем автоматически
        env_port = os.getenv('DB_PORT')
        if env_port:
            self.port = int(env_port)
        elif os.path.exists(local_data_path):
            # Локальная база использует порт 5433
            self.port = 5433
            # Используем print для отладки (только один раз при инициализации)
            print(f"📁 Локальная база данных найдена: {local_data_path}")
        else:
            # Локальная база использует порт 5433
            self.port = 5433
            # Используем print для отладки (только если база не найдена)
            print(f"⚠️ Локальная база данных не найдена по пути: {local_data_path}")
        
        self.database = os.getenv('DB_NAME', 'vkinder_db')
        self.user = os.getenv('DB_USER', 'vkinder_user')
        self.password = os.getenv('DB_PASSWORD', 'vkinder123')
        self.os_type = self._detect_os()
        
        # Кэширование статуса PostgreSQL для оптимизации
        self._status_cache = None
        self._status_cache_time = 0
        self._cache_timeout = 30  # Кэш на 30 секунд
    
    def _detect_os(self) -> str:
        """
        Определение операционной системы
        
        Returns:
            str: 'windows', 'macos', 'linux' или 'unknown'
        """
        system = platform.system().lower()
        if system == 'windows':
            return 'windows'
        elif system == 'darwin':
            return 'macos'
        elif system == 'linux':
            return 'linux'
        else:
            return 'unknown'
    
    def check_postgresql_status(self) -> bool:
        """
        Проверка статуса PostgreSQL
        
        Returns:
            bool: True если PostgreSQL запущен, False иначе
        """
        try:
            # Сначала пробуем подключиться к системной базе 'postgres' для проверки статуса PostgreSQL
            # Это работает даже если целевая база данных еще не создана
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database='postgres',  # Используем системную базу для проверки статуса
                user=self.user,
                password=self.password,
                connect_timeout=5  # Таймаут подключения 5 секунд
            )
            conn.close()
            # Используем print вместо centralized_logger чтобы избежать циклических зависимостей
            # Выводим только при первой успешной проверке или при смене статуса
            if not hasattr(self, '_last_success_time'):
                print("✅ PostgreSQL запущен и доступен")
                self._last_success_time = time.time()
            return True
            
        except psycopg2.OperationalError as e:
            # Используем print вместо centralized_logger чтобы избежать циклических зависимостей
            # Логируем только один раз в секунду, чтобы не засорять логи
            current_time = time.time()
            if not hasattr(self, '_last_warning_time'):
                self._last_warning_time = 0
            if current_time - self._last_warning_time > 10:  # Логируем не чаще раза в 10 секунд
                print(f"⚠️ PostgreSQL недоступен: {e}")
                self._last_warning_time = current_time
            return False
        except Exception as e:
            # Используем print вместо centralized_logger чтобы избежать циклических зависимостей
            current_time = time.time()
            if not hasattr(self, '_last_error_time'):
                self._last_error_time = 0
            if current_time - self._last_error_time > 10:  # Логируем не чаще раза в 10 секунд
                print(f"❌ Ошибка проверки PostgreSQL: {e}")
                self._last_error_time = current_time
            return False
    
    def start_postgresql(self) -> bool:
        """
        Универсальный запуск PostgreSQL для всех ОС
        
        Returns:
            bool: True если запуск успешен, False иначе
        """
        try:
            centralized_logger.info(f"🚀 Запуск PostgreSQL на {self.os_type.upper()}...")
            
            if self.os_type == 'windows':
                return self._start_postgresql_windows()
            elif self.os_type == 'macos':
                # Проверяем сначала локальную БД в src/database/DB_BASE/vkinder_cluster
                local_data_path = self._get_local_db_path()
                if os.path.exists(local_data_path):
                    centralized_logger.info(f"📍 Найдена локальная БД, используем порт {self.port}")
                    return self._start_local_postgres(local_data_path)
                # Иначе используем Homebrew PostgreSQL
                return self._start_homebrew_postgres()
            elif self.os_type == 'linux':
                return self._start_postgresql_linux()
            else:
                centralized_logger.error(f"❌ Неподдерживаемая ОС: {self.os_type}")
                return False
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка запуска PostgreSQL: {e}")
            return False
    
    def _start_postgresql_windows(self) -> bool:
        """
        Запуск PostgreSQL на Windows
        
        Returns:
            bool: True если запуск успешен, False иначе
        """
        try:
            centralized_logger.info("🚀 Запуск PostgreSQL на Windows...")
            
            # Проверяем службу PostgreSQL
            if self._check_windows_service():
                return self._start_windows_service()
            
            # Проверяем установку через установщик
            elif self._check_windows_installation():
                return self._start_windows_postgres()
            
            else:
                centralized_logger.error("❌ PostgreSQL не найден. Установите PostgreSQL с официального сайта")
                return False
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка запуска PostgreSQL на Windows: {e}")
            return False
    
    def _start_postgresql_linux(self) -> bool:
        """
        Запуск PostgreSQL на Linux
        
        Returns:
            bool: True если запуск успешен, False иначе
        """
        try:
            centralized_logger.info("🚀 Запуск PostgreSQL на Linux...")
            
            # Проверяем systemd
            if self._check_systemd():
                return self._start_systemd_postgres()
            
            # Проверяем service
            elif self._check_service_command():
                return self._start_service_postgres()
            
            # Проверяем pg_ctl
            elif self._check_pg_ctl():
                return self._start_pg_ctl()
            
            else:
                centralized_logger.error("❌ PostgreSQL не найден. Установите: sudo apt install postgresql")
                return False
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка запуска PostgreSQL на Linux: {e}")
            return False
    
    def _check_windows_service(self) -> bool:
        """Проверка службы PostgreSQL на Windows"""
        try:
            result = subprocess.run(['sc', 'query', 'postgresql'], 
                                  capture_output=True, text=True, timeout=10)
            return 'postgresql' in result.stdout.lower()
        except:
            return False
    
    def _start_windows_service(self) -> bool:
        """Запуск службы PostgreSQL на Windows"""
        try:
            result = subprocess.run(['sc', 'start', 'postgresql'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                centralized_logger.info("✅ Служба PostgreSQL запущена")
                return True
            else:
                centralized_logger.error(f"❌ Ошибка запуска службы: {result.stderr}")
                return False
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка запуска службы: {e}")
            return False
    
    def _check_windows_installation(self) -> bool:
        """Проверка установки PostgreSQL на Windows"""
        try:
            # Проверяем стандартные пути установки
            common_paths = [
                r"C:\Program Files\PostgreSQL",
                r"C:\Program Files (x86)\PostgreSQL",
                r"C:\PostgreSQL"
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return True
            return False
        except:
            return False
    
    def _start_windows_postgres(self) -> bool:
        """Запуск PostgreSQL через pg_ctl на Windows"""
        try:
            # Ищем pg_ctl в стандартных путях
            pg_ctl_paths = [
                r"C:\Program Files\PostgreSQL\*\bin\pg_ctl.exe",
                r"C:\Program Files (x86)\PostgreSQL\*\bin\pg_ctl.exe"
            ]
            
            for path_pattern in pg_ctl_paths:
                import glob
                matches = glob.glob(path_pattern)
                if matches:
                    pg_ctl = matches[0]
                    result = subprocess.run([pg_ctl, 'start', '-D', 'data'], 
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        centralized_logger.info("✅ PostgreSQL запущен через pg_ctl")
                        return True
            
            centralized_logger.error("❌ Не удалось найти pg_ctl")
            return False
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка запуска PostgreSQL: {e}")
            return False
    
    def _check_systemd(self) -> bool:
        """Проверка systemd на Linux"""
        try:
            result = subprocess.run(['systemctl', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _start_systemd_postgres(self) -> bool:
        """Запуск PostgreSQL через systemd"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                centralized_logger.info("✅ PostgreSQL запущен через systemctl")
                return True
            else:
                centralized_logger.error(f"❌ Ошибка запуска через systemctl: {result.stderr}")
                return False
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка запуска через systemctl: {e}")
            return False
    
    def _check_service_command(self) -> bool:
        """Проверка команды service на Linux"""
        try:
            result = subprocess.run(['service', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _start_service_postgres(self) -> bool:
        """Запуск PostgreSQL через service"""
        try:
            result = subprocess.run(['sudo', 'service', 'postgresql', 'start'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                centralized_logger.info("✅ PostgreSQL запущен через service")
                return True
            else:
                centralized_logger.error(f"❌ Ошибка запуска через service: {result.stderr}")
                return False
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка запуска через service: {e}")
            return False
    
    def _check_pg_ctl(self) -> bool:
        """Проверка pg_ctl на Linux"""
        try:
            result = subprocess.run(['which', 'pg_ctl'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _start_pg_ctl(self) -> bool:
        """Запуск PostgreSQL через pg_ctl на Linux"""
        try:
            # Ищем директорию данных PostgreSQL
            data_dirs = [
                '/var/lib/postgresql/data',
                '/usr/local/var/postgres',
                '/opt/postgresql/data'
            ]
            
            for data_dir in data_dirs:
                if os.path.exists(data_dir):
                    result = subprocess.run(['pg_ctl', 'start', '-D', data_dir], 
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        centralized_logger.info("✅ PostgreSQL запущен через pg_ctl")
                        return True
            
            centralized_logger.error("❌ Не удалось найти директорию данных PostgreSQL")
            return False
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка запуска через pg_ctl: {e}")
            return False
    
    def start_postgresql_macos(self) -> bool:
        """
        Запуск PostgreSQL на macOS
        
        Returns:
            bool: True если запуск успешен, False иначе
        """
        try:
            centralized_logger.info("🚀 Запуск PostgreSQL на macOS...")
            
            # Проверяем, установлен ли PostgreSQL через Homebrew
            if self._check_homebrew_postgres():
                return self._start_homebrew_postgres()
            
            # Проверяем системный PostgreSQL
            elif self._check_system_postgres():
                return self._start_system_postgres()
            
            else:
                centralized_logger.error("❌ PostgreSQL не найден. Установите через Homebrew: brew install postgresql")
                return False
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка запуска PostgreSQL: {e}")
            return False
    
    def _check_homebrew_postgres(self) -> bool:
        """Проверка наличия PostgreSQL через Homebrew"""
        try:
            result = subprocess.run(['brew', 'services', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            return 'postgresql' in result.stdout
        except:
            return False
    
    def _check_system_postgres(self) -> bool:
        """Проверка системного PostgreSQL"""
        try:
            result = subprocess.run(['which', 'postgres'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _start_homebrew_postgres(self) -> bool:
        """Запуск PostgreSQL через Homebrew"""
        try:
            # Сначала проверяем, есть ли локальная база в проекте
            # База находится в src/database/DB_BASE/vkinder_cluster
            local_data_path = self._get_local_db_path()
            
            if os.path.exists(local_data_path):
                centralized_logger.info("📁 Найдена локальная база данных в проекте")
                return self._start_local_postgres(local_data_path)
            else:
                centralized_logger.info("🍺 Запуск PostgreSQL через Homebrew...")
                
                # Запускаем PostgreSQL через brew services
                result = subprocess.run(['brew', 'services', 'start', 'postgresql'], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    centralized_logger.info("✅ PostgreSQL запущен через Homebrew")
                    return True
                else:
                    centralized_logger.error(f"❌ Ошибка запуска через Homebrew: {result.stderr}")
                    return False
                
        except subprocess.TimeoutExpired:
            centralized_logger.error("❌ Таймаут запуска PostgreSQL")
            return False
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка запуска через Homebrew: {e}")
            return False
    
    def _start_local_postgres(self, data_path: str) -> bool:
        """Запуск локального PostgreSQL из папки проекта"""
        try:
            # Преобразуем относительный путь в абсолютный
            abs_data_path = os.path.abspath(data_path)
            centralized_logger.info(f"🚀 Запуск PostgreSQL из папки проекта: {abs_data_path}")
            
            # Проверяем, что директория существует
            if not os.path.exists(abs_data_path):
                centralized_logger.error(f"❌ Директория не найдена: {abs_data_path}")
                return False
            
            # Определяем путь к pg_ctl
            pg_ctl_path = '/opt/homebrew/bin/pg_ctl'
            if not os.path.exists(pg_ctl_path):
                pg_ctl_path = 'pg_ctl'
            
            # Запускаем PostgreSQL с локальным data_directory
            log_file = os.path.join(abs_data_path, 'logfile')
            result = subprocess.run([pg_ctl_path, 'start', '-D', abs_data_path, '-l', log_file],
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                centralized_logger.info(f"✅ PostgreSQL запущен из папки проекта: {abs_data_path}")
                return True
            else:
                centralized_logger.error(f"❌ Ошибка запуска локального PostgreSQL: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            centralized_logger.error("❌ Таймаут запуска PostgreSQL")
            return False
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка запуска локального PostgreSQL: {e}")
            return False
    
    def _start_system_postgres(self) -> bool:
        """Запуск системного PostgreSQL"""
        try:
            centralized_logger.info("🔧 Запуск системного PostgreSQL...")
            
            # Пробуем запустить через pg_ctl
            result = subprocess.run(['pg_ctl', 'start', '-D', '/usr/local/var/postgres'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                centralized_logger.info("✅ Системный PostgreSQL запущен")
                return True
            else:
                centralized_logger.error(f"❌ Ошибка запуска системного PostgreSQL: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            centralized_logger.error("❌ Таймаут запуска PostgreSQL")
            return False
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка запуска системного PostgreSQL: {e}")
            return False
    
    def wait_for_postgresql(self, timeout: int = 60) -> bool:
        """
        Ожидание запуска PostgreSQL
        
        Args:
            timeout (int): Таймаут ожидания в секундах
            
        Returns:
            bool: True если PostgreSQL запустился, False иначе
        """
        # Используем print вместо centralized_logger чтобы избежать циклических зависимостей
        print(f"⏳ Ожидание запуска PostgreSQL (таймаут: {timeout}с)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_postgresql_status():
                print("✅ PostgreSQL успешно запущен!")
                return True
            
            time.sleep(2)  # Ждем 2 секунды между проверками
        
        print(f"❌ Таймаут ожидания PostgreSQL ({timeout}с)")
        return False
    
    def ensure_postgresql_running(self) -> bool:
        """
        Гарантирует, что PostgreSQL запущен (с кэшированием)
        
        Returns:
            bool: True если PostgreSQL запущен, False иначе
        """
        # Проверяем кэш
        current_time = time.time()
        if (self._status_cache is not None and 
            current_time - self._status_cache_time < self._cache_timeout):
            return self._status_cache
        
        # Используем print вместо centralized_logger чтобы избежать циклических зависимостей
        print("🔍 Проверка статуса PostgreSQL...")
        
        # Проверяем текущий статус
        if self.check_postgresql_status():
            # Обновляем кэш
            self._status_cache = True
            self._status_cache_time = current_time
            return True
        
        # Если не запущен, пытаемся запустить
        print("🚀 PostgreSQL не запущен, пытаемся запустить...")
        
        if self.start_postgresql():
            # Ждем запуска
            if self.wait_for_postgresql():
                # Обновляем кэш
                self._status_cache = True
                self._status_cache_time = current_time
                return True
        
        # Обновляем кэш (неудачный результат)
        self._status_cache = False
        self._status_cache_time = current_time
        print("❌ Не удалось запустить PostgreSQL")
        return False
    
    def reset_status_cache(self):
        """Сброс кэша статуса PostgreSQL"""
        self._status_cache = None
        self._status_cache_time = 0
    
    def create_database_if_not_exists(self) -> bool:
        """
        Создание базы данных если она не существует
        
        Returns:
            bool: True если БД создана или существует, False иначе
        """
        try:
            # Подключаемся к системной БД postgres
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database='postgres',
                user=self.user,
                password=self.password
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Проверяем, существует ли БД
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database,))
            if cursor.fetchone():
                # DEBUG: база уже существует - это нормально, не логируем как INFO
                centralized_logger.debug(f"База данных '{self.database}' уже существует (проверка при инициализации)")
                cursor.close()
                conn.close()
                return True
            
            # Создаем БД
            centralized_logger.info(f"🔨 Создание базы данных '{self.database}'...")
            cursor.execute(f'CREATE DATABASE "{self.database}"')
            centralized_logger.info(f"✅ База данных '{self.database}' создана")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка создания базы данных: {e}")
            return False
    
    def get_postgresql_info(self) -> Dict[str, Any]:
        """
        Получение информации о PostgreSQL
        
        Returns:
            Dict[str, Any]: Информация о PostgreSQL
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database='postgres',
                user=self.user,
                password=self.password
            )
            cursor = conn.cursor()
            
            # Получаем версию PostgreSQL
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            
            # Получаем список БД
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
            databases = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return {
                'version': version,
                'host': self.host,
                'port': self.port,
                'user': self.user,
                'databases': databases,
                'target_database': self.database,
                'target_database_exists': self.database in databases
            }
            
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка получения информации о PostgreSQL: {e}")
            return {'error': str(e)}
    
    def stop_postgresql(self) -> bool:
        """
        Универсальная остановка PostgreSQL для всех ОС
        
        Returns:
            bool: True если остановка успешна, False иначе
        """
        try:
            centralized_logger.info(f"🛑 Остановка PostgreSQL на {self.os_type.upper()}...")
            
            if self.os_type == 'windows':
                return self._stop_postgresql_windows()
            elif self.os_type == 'macos':
                return self._stop_postgresql_macos()
            elif self.os_type == 'linux':
                return self._stop_postgresql_linux()
            else:
                centralized_logger.error(f"❌ Неподдерживаемая ОС: {self.os_type}")
                return False
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка остановки PostgreSQL: {e}")
            return False
    
    def _stop_postgresql_windows(self) -> bool:
        """Остановка PostgreSQL на Windows"""
        try:
            # Пытаемся остановить службу
            result = subprocess.run(['sc', 'stop', 'postgresql'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                centralized_logger.info("✅ Служба PostgreSQL остановлена")
                return True
            else:
                centralized_logger.error(f"❌ Ошибка остановки службы: {result.stderr}")
                return False
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка остановки PostgreSQL на Windows: {e}")
            return False
    
    def _stop_postgresql_linux(self) -> bool:
        """Остановка PostgreSQL на Linux"""
        try:
            # Пытаемся остановить через systemctl
            if self._check_systemd():
                result = subprocess.run(['sudo', 'systemctl', 'stop', 'postgresql'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    centralized_logger.info("✅ PostgreSQL остановлен через systemctl")
                    return True
            
            # Пытаемся остановить через service
            if self._check_service_command():
                result = subprocess.run(['sudo', 'service', 'postgresql', 'stop'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    centralized_logger.info("✅ PostgreSQL остановлен через service")
                    return True
            
            centralized_logger.error("❌ Не удалось остановить PostgreSQL")
            return False
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка остановки PostgreSQL на Linux: {e}")
            return False
    
    def _stop_postgresql_macos(self) -> bool:
        """Остановка PostgreSQL на macOS"""
        try:
            # Пытаемся остановить через Homebrew
            if self._check_homebrew_postgres():
                result = subprocess.run(['brew', 'services', 'stop', 'postgresql'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    centralized_logger.info("✅ PostgreSQL остановлен через Homebrew")
                    return True
            
            # Пытаемся остановить через pg_ctl
            if self._check_system_postgres():
                result = subprocess.run(['pg_ctl', 'stop'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    centralized_logger.info("✅ PostgreSQL остановлен через pg_ctl")
                    return True
            
            centralized_logger.error("❌ Не удалось остановить PostgreSQL")
            return False
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка остановки PostgreSQL на macOS: {e}")
            return False
    
    def restart_postgresql(self) -> bool:
        """
        Универсальный перезапуск PostgreSQL для всех ОС
        
        Returns:
            bool: True если перезапуск успешен, False иначе
        """
        try:
            centralized_logger.info(f"🔄 Перезапуск PostgreSQL на {self.os_type.upper()}...")
            
            # Сначала останавливаем
            if self.stop_postgresql():
                time.sleep(2)  # Небольшая пауза
                
                # Затем запускаем
                if self.start_postgresql():
                    # Ждем запуска
                    if self.wait_for_postgresql():
                        centralized_logger.info("✅ PostgreSQL успешно перезапущен")
                        return True
            
            centralized_logger.error("❌ Не удалось перезапустить PostgreSQL")
            return False
            
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка перезапуска PostgreSQL: {e}")
            return False


def main():
    """Основная функция для тестирования менеджера PostgreSQL"""
    print("🐘 МЕНЕДЖЕР POSTGRESQL")
    print("=" * 50)
    
    manager = PostgreSQLManager()
    
    # Проверяем и запускаем PostgreSQL
    if manager.ensure_postgresql_running():
        print("✅ PostgreSQL запущен и доступен")
        
        # Создаем БД если нужно
        if manager.create_database_if_not_exists():
            print("✅ База данных готова")
        
        # Показываем информацию
        info = manager.get_postgresql_info()
        if 'error' not in info:
            print(f"\n📊 Информация о PostgreSQL:")
            print(f"  🐘 Версия: {info['version']}")
            print(f"  🏠 Хост: {info['host']}:{info['port']}")
            print(f"  👤 Пользователь: {info['user']}")
            print(f"  📄 База данных: {info['target_database']}")
            print(f"  ✅ БД существует: {info['target_database_exists']}")
            print(f"  📋 Всего БД: {len(info['databases'])}")
        else:
            print(f"❌ Ошибка получения информации: {info['error']}")
    else:
        print("❌ Не удалось запустить PostgreSQL")
        print("\n🔧 Рекомендации:")
        print("  1. Установите PostgreSQL: brew install postgresql")
        print("  2. Запустите вручную: brew services start postgresql")
        print("  3. Проверьте настройки в .env файле")


if __name__ == "__main__":
    main()
