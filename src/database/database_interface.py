#!/usr/bin/env python3
"""
Интерфейс для работы с базой данных VKinder Bot
Предоставляет полный набор функций для управления БД, записи данных и обработки исключений
"""

import sys
import os
import hashlib
import secrets
import base64
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import datetime, timedelta, timezone
from src.utils.centralized_logger import centralized_logger
from cryptography.fernet import Fernet

# Защита от прямого запуска
if __name__ == "__main__":
    print("❌ Этот файл нельзя запускать напрямую!")
    print("⚠️ Модули базы данных работают только как часть основной программы")
    sys.exit(1)
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from contextlib import contextmanager

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Добавляем путь к модулям токенов для импорта
tokens_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tokens')
if tokens_path not in sys.path:
    sys.path.append(tokens_path)

# Исправляем импорты для работы как отдельного скрипта
try:
    from .models import (
        Base, VKUser, Photo, Favorite, Blacklisted, 
        UserSettings
    )
except ImportError:
    # Если относительные импорты не работают, используем абсолютные
    from models import (
        Base, VKUser, Photo, Favorite, Blacklisted, 
        UserSettings
    )
import os
from dotenv import load_dotenv
from loguru import logger
try:
    from .postgres_manager import PostgreSQLManager
except ImportError:
    from postgres_manager import PostgreSQLManager

# Загружаем переменные окружения
load_dotenv()


class DatabaseInterface:
    """
    Полноценный интерфейс для работы с базой данных VKinder Bot
    
    Предоставляет функции для:
    - Создания/удаления/очистки базы данных
    - Управления таблицами
    - CRUD операций с данными
    - Обработки исключений
    - Логирования операций
    """
    
    def __init__(self):
        """Инициализация интерфейса базы данных"""
        self.engine = None
        self.Session = None
        self.is_available = False  # Флаг доступности БД
        self._connection_error = None  # Сохраняем ошибку подключения для отладки
        self._setup_connection()
        self._setup_encryption()
    
    def _setup_connection(self):
        """Настройка подключения к базе данных"""
        try:
            # Проверяем и запускаем PostgreSQL если нужно
            postgres_manager = PostgreSQLManager()
            if not postgres_manager.ensure_postgresql_running():
                error_msg = "PostgreSQL недоступен"
                self._connection_error = error_msg
                self.is_available = False
                # Используем print вместо centralized_logger чтобы избежать рекурсии
                print(f"⚠️ {error_msg} - программа будет работать без БД")
                return
            
            # Создаем БД если не существует
            if not postgres_manager.create_database_if_not_exists():
                error_msg = "База данных недоступна"
                self._connection_error = error_msg
                self.is_available = False
                # Используем print вместо centralized_logger чтобы избежать рекурсии
                print(f"⚠️ {error_msg} - программа будет работать без БД")
                return
            
            # Создаем подключение к PostgreSQL используя параметры из postgres_manager
            # postgres_manager автоматически определяет правильный порт
            db_host = postgres_manager.host
            db_port = postgres_manager.port
            db_name = postgres_manager.database
            db_user = postgres_manager.user
            db_password = postgres_manager.password
            
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            self.engine = create_engine(database_url, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            
            # Проверяем подключение
            try:
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self.is_available = True
                self._connection_error = None
                # Используем print вместо centralized_logger чтобы избежать рекурсии
                print("✅ Интерфейс базы данных инициализирован с автоматическим запуском PostgreSQL")
            except Exception as conn_error:
                error_msg = f"Ошибка проверки подключения: {conn_error}"
                self._connection_error = error_msg
                self.is_available = False
                print(f"⚠️ {error_msg} - программа будет работать без БД")
            
        except Exception as e:
            # Не выбрасываем исключение, просто помечаем БД как недоступную
            error_msg = f"Ошибка инициализации интерфейса БД: {e}"
            self._connection_error = error_msg
            self.is_available = False
            # Используем print вместо centralized_logger чтобы избежать рекурсии
            print(f"⚠️ {error_msg} - программа будет работать без БД")
    
    def _setup_encryption(self):
        """Настройка системы шифрования токенов"""
        try:
            # Получаем ключ шифрования
            self.encryption_key = self._get_encryption_key()
            
            # Создаем объект шифрования
            self.cipher = self._create_cipher()
            
            centralized_logger.info("✅ Система шифрования токенов инициализирована")
            
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка инициализации шифрования: {e}")
            raise
    
    def _get_encryption_key(self) -> str:
        """Получение ключа шифрования из переменных окружения"""
        key = os.getenv('TOKEN_ENCRYPTION_KEY')
        if not key:
            # Генерируем ключ на основе VK_APP_SECRET если нет специального ключа
            app_secret = os.getenv('VK_APP_SECRET', 'default_secret')
            key = hashlib.sha256(app_secret.encode()).hexdigest()
            centralized_logger.warning("⚠️ Используется автоматически сгенерированный ключ шифрования", user_id=0)
        return key
    
    def _create_cipher(self) -> Fernet:
        """Создание объекта шифрования"""
        try:
            # Преобразуем ключ в формат Fernet
            key_bytes = self.encryption_key.encode()
            key_hash = hashlib.sha256(key_bytes).digest()
            fernet_key = base64.urlsafe_b64encode(key_hash)
            return Fernet(fernet_key)
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка создания cipher: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Контекстный менеджер для работы с сессией БД"""
        if not self.is_available or not self.Session:
            # Возвращаем контекстный менеджер-заглушку, который ничего не делает
            class DummySession:
                def __getattr__(self, name):
                    return lambda *args, **kwargs: None
            yield DummySession()
            return
        
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            # Если это ошибка подключения, помечаем БД как недоступную
            if isinstance(e, (OperationalError, SQLAlchemyError)):
                self.is_available = False
                self._connection_error = str(e)
                centralized_logger.warning(f"⚠️ БД стала недоступна: {e}", user_id=0)
            centralized_logger.error(f"Ошибка в сессии БД: {e}", user_id=0)
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """
        Тестирование подключения к базе данных
        
        Returns:
            bool: True если подключение успешно, False иначе
        """
        try:
            with self.get_session() as session:
                # Простой запрос для проверки подключения
                result = session.execute(text("SELECT 1")).fetchone()
                centralized_logger.info("✅ Подключение к базе данных работает")
                return True
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка подключения к БД: {e}")
            return False
    
    def create_database(self) -> bool:
        """
        Создание всех таблиц базы данных
        
        Returns:
            bool: True если создание успешно, False иначе
        """
        try:
            centralized_logger.info("🔨 Создание таблиц базы данных...")
            Base.metadata.create_all(self.engine)
            centralized_logger.info("✅ Все таблицы созданы успешно")
            return True
            
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка создания таблиц: {e}")
            return False
    
    def drop_database(self) -> bool:
        """
        Удаление всех таблиц базы данных
        
        Returns:
            bool: True если удаление успешно, False иначе
        """
        try:
            centralized_logger.info("🗑️ Удаление всех таблиц...")
            Base.metadata.drop_all(self.engine)
            centralized_logger.info("✅ Все таблицы удалены")
            return True
            
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка удаления таблиц: {e}")
            return False
    
    def clear_table(self, table_name: str) -> bool:
        """
        Очистка конкретной таблицы
        
        Args:
            table_name (str): Название таблицы для очистки
            
        Returns:
            bool: True если очистка успешна, False иначе
        """
        try:
            with self.get_session() as session:
                # Получаем модель таблицы
                table_model = self._get_table_model(table_name)
                if not table_model:
                    centralized_logger.error(f"❌ Таблица '{table_name}' не найдена")
                    return False
                
                # Очищаем таблицу
                session.query(table_model).delete()
                centralized_logger.info(f"✅ Таблица '{table_name}' очищена")
                return True
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка очистки таблицы '{table_name}': {e}")
            return False
    
    def clear_all_tables(self) -> bool:
        """
        Очистка всех таблиц (сохранение структуры)
        
        Returns:
            bool: True если очистка успешна, False иначе
        """
        try:
            centralized_logger.info("🧹 Очистка всех таблиц...")
            
            # Список всех моделей в правильном порядке (с учетом внешних ключей)
            models = [Favorite, Blacklisted, 
                     UserSettings, Photo, VKUser]
            
            with self.get_session() as session:
                for model in models:
                    try:
                        session.query(model).delete()
                        centralized_logger.debug(f"Очищена таблица: {model.__tablename__}")
                    except Exception as e:
                        centralized_logger.error(f"Ошибка очистки таблицы {model.__tablename__}: {e}")
            
            centralized_logger.info("✅ Все таблицы очищены")
            return True
            
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка очистки всех таблиц: {e}")
            return False
    
    def get_table_info(self) -> Dict[str, Any]:
        """
        Получение информации о всех таблицах
        
        Returns:
            Dict[str, Any]: Словарь с информацией о таблицах
        """
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            info = {
                "total_tables": len(tables),
                "tables": {}
            }
            
            with self.get_session() as session:
                for table_name in tables:
                    try:
                        # Получаем модель таблицы
                        model = self._get_table_model(table_name)
                        if model:
                            try:
                                count = session.query(model).count()
                                info["tables"][table_name] = {
                                    "count": count,
                                    "model": model.__name__
                                }
                            except Exception as count_error:
                                centralized_logger.warning(f"Ошибка подсчета записей в таблице {table_name}: {count_error}")
                                info["tables"][table_name] = {
                                    "count": "error",
                                    "model": model.__name__
                                }
                        else:
                            info["tables"][table_name] = {
                                "count": "unknown",
                                "model": "unknown"
                            }
                    except Exception as e:
                        centralized_logger.error(f"Ошибка обработки таблицы {table_name}: {e}")
                        info["tables"][table_name] = {
                            "count": f"error: {e}",
                            "model": "unknown"
                        }
            
            return info
            
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка получения информации о таблицах: {e}")
            return {"error": str(e)}
    
    def _get_table_model(self, table_name: str):
        """Получение модели таблицы по названию"""
        table_models = {
            "vk_users": VKUser,
            "photos": Photo,
            "favorites": Favorite,
            "blacklisted": Blacklisted,
            "user_settings": UserSettings
        }
        return table_models.get(table_name)
    
    # === CRUD ОПЕРАЦИИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ===
    
    def add_user(self, vk_user_id: int, first_name: str, last_name: str,
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
            country (Optional[str]): Страна
            photo_url (Optional[str]): URL фотографии
            access (Optional[str]): Access - string
            refresh (Optional[str]): Refresh - string
            time (Optional[int]): Time - integer
            
        Returns:
            bool: True если добавление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                # Проверяем, существует ли пользователь
                existing_user = session.query(VKUser).filter(VKUser.vk_user_id == vk_user_id).first()
                if existing_user:
                    centralized_logger.debug(f"Пользователь {vk_user_id} уже существует")
                    return True
                
                # Создаем нового пользователя
                user = VKUser(
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
                
                session.add(user)
                session.commit()
                centralized_logger.info(f"✅ Пользователь {vk_user_id} ({first_name} {last_name}) добавлен")
                return True
                
        except IntegrityError as e:
            centralized_logger.error(f"❌ Ошибка целостности при добавлении пользователя {vk_user_id}: {e}")
            return False
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка добавления пользователя {vk_user_id}: {e}")
            return False
    
    def get_user(self, vk_user_id: int) -> Optional[VKUser]:
        """
        Получение пользователя по VK ID
        
        Args:
            vk_user_id (int): ID пользователя VK
            
        Returns:
            Optional[VKUser]: Пользователь или None
        """
        try:
            with self.get_session() as session:
                user = session.query(VKUser).filter(VKUser.vk_user_id == vk_user_id).first()
                return user
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка получения пользователя {vk_user_id}: {e}")
            return None
    
    def update_user(self, vk_user_id: int, **kwargs) -> bool:
        """
        Обновление данных пользователя
        
        Args:
            vk_user_id (int): ID пользователя VK
            **kwargs: Поля для обновления
            
        Returns:
            bool: True если обновление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                user = session.query(VKUser).filter(VKUser.vk_user_id == vk_user_id).first()
                if not user:
                    centralized_logger.error(f"❌ Пользователь {vk_user_id} не найден")
                    return False
                
                # Обновляем поля
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                
                centralized_logger.info(f"✅ Пользователь {vk_user_id} обновлен")
                return True
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка обновления пользователя {vk_user_id}: {e}")
            return False
    
    def delete_user(self, vk_user_id: int) -> bool:
        """
        Удаление пользователя
        
        Args:
            vk_user_id (int): ID пользователя VK
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                user = session.query(VKUser).filter(VKUser.vk_user_id == vk_user_id).first()
                if not user:
                    centralized_logger.error(f"❌ Пользователь {vk_user_id} не найден")
                    return False
                
                session.delete(user)
                session.commit()
                centralized_logger.info(f"✅ Пользователь {vk_user_id} удален")
                return True
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка удаления пользователя {vk_user_id}: {e}")
            return False
    # === ОПЕРАЦИИ С ИЗБРАННЫМ ===
    
    def add_favorite(self, user_vk_id: int, favorite_vk_id: int) -> bool:
        """
        Добавление в избранное
        
        Args:
            user_vk_id (int): ID пользователя, который добавляет
            favorite_vk_id (int): ID пользователя, которого добавляют
            
        Returns:
            bool: True если добавление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                # Проверяем, не добавлен ли уже
                existing = (session.query(Favorite)
                          .filter(Favorite.user_vk_id == user_vk_id)
                          .filter(Favorite.favorite_vk_id == favorite_vk_id)
                          .first())
                
                if existing:
                    centralized_logger.debug(f"Пользователь {favorite_vk_id} уже в избранном у {user_vk_id}")
                    return True
                
                favorite = Favorite(
                    user_vk_id=user_vk_id,
                    favorite_vk_id=favorite_vk_id
                )
                session.add(favorite)
                session.commit()
                centralized_logger.info(f"✅ Пользователь {favorite_vk_id} добавлен в избранное к {user_vk_id}")
                return True
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка добавления в избранное: {e}")
            return False
    
    def get_favorites(self, user_vk_id: int) -> List[Favorite]:
        """
        Получение списка избранных пользователя
        
        Args:
            user_vk_id (int): ID пользователя VK
            
        Returns:
            List[Favorite]: Список избранных
        """
        try:
            with self.get_session() as session:
                favorites = (session.query(Favorite)
                           .filter(Favorite.user_vk_id == user_vk_id)
                           .order_by(Favorite.created_at.desc())
                           .limit(10)
                           .all())
                # Преобразуем объекты в словари для избежания проблем с сессией
                result = []
                for fav in favorites:
                    result.append({
                        'id': fav.id,
                        'user_vk_id': fav.user_vk_id,
                        'favorite_vk_id': fav.favorite_vk_id,
                        'created_at': fav.created_at
                    })
                return result
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка получения избранных для {user_vk_id}: {e}")
            return []
    
    def remove_favorite(self, user_vk_id: int, favorite_vk_id: int) -> bool:
        """
        Удаление из избранного
        
        Args:
            user_vk_id (int): ID пользователя
            favorite_vk_id (int): ID пользователя для удаления
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                favorite = (session.query(Favorite)
                          .filter(Favorite.user_vk_id == user_vk_id)
                          .filter(Favorite.favorite_vk_id == favorite_vk_id)
                          .first())
                
                if not favorite:
                    centralized_logger.debug(f"Пользователь {favorite_vk_id} не найден в избранном у {user_vk_id}")
                    return True
                
                session.delete(favorite)
                session.commit()
                centralized_logger.info(f"✅ Пользователь {favorite_vk_id} удален из избранного у {user_vk_id}")
                return True
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка удаления из избранного: {e}")
            return False

    # === УПРАВЛЕНИЕ ЧЕРНЫМ СПИСКОМ ===

    def add_to_blacklist(self, user_id: int, blacklisted_id: int) -> bool:
        """
        Добавление пользователя в черный список
        
        Args:
            user_id: ID пользователя, который добавляет в черный список
            blacklisted_id: ID пользователя, которого добавляют в черный список
            
        Returns:
            bool: True если добавление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                # Проверяем, есть ли уже в черном списке
                existing = session.query(Blacklisted).filter(
                    Blacklisted.user_vk_id == user_id,
                    Blacklisted.blocked_vk_id == blacklisted_id
                ).first()
                
                if existing:
                    centralized_logger.warning(f"Пользователь {blacklisted_id} уже в черном списке пользователя {user_id}", user_id=0)
                    return True
                
                # Добавляем в черный список
                blacklisted = Blacklisted(
                    user_vk_id=user_id,
                    blocked_vk_id=blacklisted_id,
                    created_at=datetime.now()
                )
                session.add(blacklisted)
                session.commit()
                
                centralized_logger.info(f"Пользователь {blacklisted_id} добавлен в черный список пользователя {user_id}", user_id=0)
                return True
                
        except Exception as e:
            centralized_logger.error(f"Ошибка добавления в черный список: {e}", user_id=0)
            return False

    def get_blacklisted(self, user_id: int) -> List[int]:
        """
        Получение списка ID пользователей в черном списке
        
        Args:
            user_id: ID пользователя
            
        Returns:
            List[int]: Список ID пользователей в черном списке
        """
        try:
            with self.get_session() as session:
                blacklisted = session.query(Blacklisted).filter(
                    Blacklisted.user_vk_id == user_id
                ).all()
                
                return [b.blocked_vk_id for b in blacklisted]
                
        except Exception as e:
            centralized_logger.error(f"Ошибка получения черного списка: {e}", user_id=0)
            return []

    def remove_from_blacklist(self, user_id: int, blacklisted_id: int) -> bool:
        """
        Удаление пользователя из черного списка
        
        Args:
            user_id: ID пользователя, который удаляет из черного списка
            blacklisted_id: ID пользователя, которого удаляют из черного списка
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                blacklisted = session.query(Blacklisted).filter(
                    Blacklisted.user_vk_id == user_id,
                    Blacklisted.blocked_vk_id == blacklisted_id
                ).first()
                
                if not blacklisted:
                    centralized_logger.warning(f"Пользователь {blacklisted_id} не найден в черном списке пользователя {user_id}", user_id=0)
                    return False
                
                session.delete(blacklisted)
                session.commit()
                
                centralized_logger.info(f"Пользователь {blacklisted_id} удален из черного списка пользователя {user_id}", user_id=0)
                return True
                
        except Exception as e:
            centralized_logger.error(f"Ошибка удаления из черного списка: {e}", user_id=0)
            return False

    def get_user_statistics(self, user_id: int) -> dict:
        """
        Получение статистики пользователя из базы данных
        
        Args:
            user_id: ID пользователя VK
            
        Returns:
            dict: Словарь со статистикой пользователя
        """
        try:
            stats = {}
            
            with self.get_session() as session:
                # Количество просмотренных анкет (уникальные пользователи в vk_users, найденные этим пользователем)
                try:
                    # Считаем количество уникальных пользователей, которых нашел этот пользователь
                    # через фотографии, которые он нашел
                    viewed_count = session.query(Photo).filter(
                        Photo.found_by_user_id == user_id
                    ).with_entities(Photo.vk_user_id).distinct().count()
                    stats['viewed_profiles'] = viewed_count
                except Exception as e:
                    centralized_logger.error(f"❌ Ошибка получения количества просмотренных анкет: {e}")
                    stats['viewed_profiles'] = 0
                
                # Получаем количество избранных и заблокированных
                try:
                    favorites_count = session.query(Favorite).filter(
                        Favorite.user_vk_id == user_id
                    ).count()
                    stats['favorites_count'] = favorites_count
                except Exception as e:
                    centralized_logger.error(f"❌ Ошибка получения количества избранных: {e}")
                    stats['favorites_count'] = 0
                
                try:
                    blacklisted_count = session.query(Blacklisted).filter(
                        Blacklisted.user_vk_id == user_id
                    ).count()
                    stats['blacklisted_count'] = blacklisted_count
                except Exception as e:
                    centralized_logger.error(f"❌ Ошибка получения количества заблокированных: {e}")
                    stats['blacklisted_count'] = 0
                
                # Количество просмотренных фотографий
                try:
                    viewed_photos = session.query(Photo).filter(
                        Photo.found_by_user_id == user_id
                    ).count()
                    stats['viewed_photos'] = viewed_photos
                except Exception as e:
                    centralized_logger.error(f"❌ Ошибка получения количества просмотренных фото: {e}")
                    stats['viewed_photos'] = 0
                
                # Количество поисковых сессий (таблица search_history удалена)
                stats['search_sessions'] = 0
            
            centralized_logger.info(f"✅ Статистика пользователя {user_id} получена: {len(stats)} показателей")
            return stats
            
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка получения статистики пользователя: {e}")
            return {}
    
    def count_records(
        self,
        model_class,
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
            model_class: Класс модели SQLAlchemy (например, Photo, Favorite, Blacklisted)
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
            # Подсчет всех фото
            count = db.count_records(Photo)
            
            # Подсчет фото пользователя за сегодня
            today = datetime.combine(datetime.now().date(), time.min)
            count = db.count_records(
                Photo,
                date_from=today,
                date_field_primary='updated_at',
                date_field_fallback='created_at',
                user_id=12345,
                user_field='found_by_user_id'
            )
            
            # Подсчет уникальных пользователей по фото
            count = db.count_records(
                Photo,
                distinct_field='vk_user_id',
                user_id=12345,
                user_field='found_by_user_id'
            )
        """
        try:
            with self.get_session() as session:
                from sqlalchemy import func, or_, and_
                from datetime import datetime as dt, time as _time
                
                # Начинаем с базового запроса
                if distinct_field:
                    # Если нужно считать уникальные значения
                    attr = getattr(model_class, distinct_field)
                    query = session.query(func.count(func.distinct(attr)))
                else:
                    # Обычный подсчет
                    query = session.query(func.count(model_class.id))
                
                # Применяем фильтр по user_id если указан
                if user_id is not None and user_field:
                    user_attr = getattr(model_class, user_field)
                    query = query.filter(user_attr == user_id)
                
                # Применяем дополнительные фильтры
                if filters:
                    for field_name, value in filters.items():
                        if hasattr(model_class, field_name):
                            attr = getattr(model_class, field_name)
                            if value is None:
                                query = query.filter(attr.is_(None))
                            elif isinstance(value, dict):
                                # Специальные фильтры (например, {'isnot': None})
                                if 'isnot' in value:
                                    query = query.filter(attr.isnot(value['isnot']))
                                elif 'in' in value:
                                    query = query.filter(attr.in_(value['in']))
                                elif 'not_in' in value:
                                    query = query.filter(~attr.in_(value['not_in']))
                            else:
                                query = query.filter(attr == value)
                
                # Применяем фильтр по дате
                if date_from is not None:
                    if date_field_primary and date_field_fallback:
                        # Используем primary поле, если оно не NULL, иначе fallback
                        primary_attr = getattr(model_class, date_field_primary)
                        fallback_attr = getattr(model_class, date_field_fallback)
                        query = query.filter(
                            or_(
                                primary_attr >= date_from,
                                and_(primary_attr.is_(None), fallback_attr >= date_from)
                            )
                        )
                    elif date_field_primary:
                        # Только primary поле
                        primary_attr = getattr(model_class, date_field_primary)
                        query = query.filter(primary_attr >= date_from)
                    elif date_field_fallback:
                        # Только fallback поле
                        fallback_attr = getattr(model_class, date_field_fallback)
                        query = query.filter(fallback_attr >= date_from)
                
                result = query.scalar()
                return result if result is not None else 0
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка подсчета записей {model_class.__name__}: {e}", user_id=0)
            return 0


    # === МЕТОДЫ ШИФРОВАНИЯ И ДЕШИФРОВАНИЯ ТОКЕНОВ ===
    
    def _mask_token(self, token: str) -> str:
        """
        Маскировка токена для безопасного логирования
        Адаптивная маскировка в зависимости от длины токена:
        - 16+ символов: 8***5
        - 13-15 символов: 6***4
        - 11-12 символов: 4***4
        - 9-10 символов: 3***3
        - 8 символов: 2***3
        - 5-7 символов: 1***1
        - 4 символа: 1***
        - менее 4: ***
        
        Args:
            token: Токен для маскировки
            
        Returns:
            str: Маскированный токен
        """
        if not token:
            return "(пустой)"
        
        length = len(token)
        
        if length >= 16:
            return f"{token[:8]}***{token[-5:]}"
        elif length >= 13:
            return f"{token[:6]}***{token[-4:]}"
        elif length >= 11:
            return f"{token[:4]}***{token[-4:]}"
        elif length >= 9:
            return f"{token[:3]}***{token[-3:]}"
        elif length >= 8:
            return f"{token[:2]}***{token[-3:]}"
        elif length >= 5:
            return f"{token[:1]}***{token[-1:]}"
        elif length >= 4:
            return f"{token[:1]}***"
        else:
            return "***"
    
    def encrypt_access_token(self, access_token: str) -> str:
        """
        Шифрование access токена
        
        Args:
            access_token: Токен для шифрования
            
        Returns:
            str: Зашифрованный токен
        """
        try:
            # ⚠️ WARNING: Логирование открытого токена для отладки (маскированный)
            masked_token = self._mask_token(access_token)
            centralized_logger.warning(f"🔐 [TOKEN_ENCRYPT] ШИФРУЕМ ACCESS ТОКЕН: Открытый токен: {masked_token}", user_id=0)
            
            encrypted_token = self.cipher.encrypt(access_token.encode())
            encrypted_str = encrypted_token.decode()
            
            # ⚠️ WARNING: Логирование зашифрованного токена для отладки (маскированный)
            masked_encrypted = self._mask_token(encrypted_str)
            centralized_logger.warning(f"🔐 [TOKEN_ENCRYPT] РЕЗУЛЬТАТ ШИФРОВАНИЯ: Зашифрованный токен: {masked_encrypted}", user_id=0)
            
            return encrypted_str
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка шифрования access токена: {e}")
            raise
    
    def decrypt_access_token(self, encrypted_token: str, user_id: int = 0) -> str:
        """
        Расшифровка access токена
        
        Args:
            encrypted_token: Зашифрованный токен
            user_id: ID пользователя (для логирования, опционально)
            
        Returns:
            str: Расшифрованный токен
        """
        try:
            # Логирование начала расшифровки
            masked_encrypted = self._mask_token(encrypted_token)
            centralized_logger.debug(f"🔓 [TOKEN_DECRYPT] Начало расшифровки: зашифрованный токен (маскированный): {masked_encrypted}, длина={len(encrypted_token)}", user_id=user_id)
            
            # Выполняем расшифровку через Fernet cipher
            centralized_logger.debug(f"🔓 [TOKEN_DECRYPT] Вызываем cipher.decrypt() для расшифровки токена", user_id=user_id)
            decrypted_token = self.cipher.decrypt(encrypted_token.encode())
            decrypted_str = decrypted_token.decode()
            
            # Логирование результата расшифровки
            masked_decrypted = self._mask_token(decrypted_str)
            centralized_logger.debug(f"✅ [TOKEN_DECRYPT] Расшифровка успешна: расшифрованный токен (маскированный): {masked_decrypted}, длина={len(decrypted_str)}", user_id=user_id)
            
            return decrypted_str
        except Exception as e:
            centralized_logger.error(f"❌ [TOKEN_DECRYPT] Ошибка расшифровки access токена: {e}", user_id=user_id)
            raise
    
    def encrypt_refresh_token(self, refresh_token: str) -> str:
        """
        Шифрование refresh токена
        
        Args:
            refresh_token: Refresh токен для шифрования
            
        Returns:
            str: Зашифрованный refresh токен
        """
        try:
            # ⚠️ WARNING: Логирование открытого refresh токена для отладки (маскированный)
            masked_token = self._mask_token(refresh_token)
            centralized_logger.warning(f"🔐 [TOKEN_ENCRYPT] ШИФРУЕМ REFRESH ТОКЕН: Открытый токен: {masked_token}", user_id=0)
            
            encrypted_token = self.cipher.encrypt(refresh_token.encode())
            encrypted_str = encrypted_token.decode()
            
            # ⚠️ WARNING: Логирование зашифрованного refresh токена для отладки (маскированный)
            masked_encrypted = self._mask_token(encrypted_str)
            centralized_logger.warning(f"🔐 [TOKEN_ENCRYPT] РЕЗУЛЬТАТ ШИФРОВАНИЯ: Зашифрованный refresh токен: {masked_encrypted}", user_id=0)
            
            return encrypted_str
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка шифрования refresh токена: {e}")
            raise
    
    def decrypt_refresh_token(self, encrypted_token: str, user_id: int = 0) -> str:
        """
        Расшифровка refresh токена
        
        Args:
            encrypted_token: Зашифрованный refresh токен
            user_id: ID пользователя (для логирования, опционально)
            
        Returns:
            str: Расшифрованный refresh токен
        """
        try:
            # Логирование начала расшифровки
            masked_encrypted = self._mask_token(encrypted_token)
            centralized_logger.debug(f"🔓 [TOKEN_DECRYPT] Начало расшифровки refresh токена: зашифрованный токен (маскированный): {masked_encrypted}, длина={len(encrypted_token)}", user_id=user_id)
            
            # Выполняем расшифровку через Fernet cipher
            centralized_logger.debug(f"🔓 [TOKEN_DECRYPT] Вызываем cipher.decrypt() для расшифровки refresh токена", user_id=user_id)
            decrypted_token = self.cipher.decrypt(encrypted_token.encode())
            decrypted_str = decrypted_token.decode()
            
            # Логирование результата расшифровки
            masked_decrypted = self._mask_token(decrypted_str)
            centralized_logger.debug(f"✅ [TOKEN_DECRYPT] Расшифровка refresh токена успешна: расшифрованный токен (маскированный): {masked_decrypted}, длина={len(decrypted_str)}", user_id=user_id)
            
            return decrypted_str
        except Exception as e:
            centralized_logger.error(f"❌ [TOKEN_DECRYPT] Ошибка расшифровки refresh токена: {e}", user_id=user_id)
            raise
    
    def hash_refresh_token(self, refresh_token: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Хеширование refresh токена с солью
        
        Args:
            refresh_token: Refresh токен для хеширования
            salt: Соль (если не указана, генерируется новая)
            
        Returns:
            Tuple[str, str]: (хеш_токена, соль)
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
    
    def verify_refresh_token(self, refresh_token: str, token_hash: str, salt: str) -> bool:
        """
        Проверка refresh токена по хешу
        
        Args:
            refresh_token: Токен для проверки
            token_hash: Хранимый хеш
            salt: Соль
            
        Returns:
            bool: True если токен совпадает
        """
        try:
            computed_hash, _ = self.hash_refresh_token(refresh_token, salt)
            return computed_hash == token_hash
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка проверки refresh токена: {e}")
            return False
    
    def generate_token_data(self, access_token: str, refresh_token: str, expires_in: int = 3600) -> Dict[str, Any]:
        """
        Генерация всех данных для хранения токенов
        
        Args:
            access_token: Access токен
            refresh_token: Refresh токен
            expires_in: Время жизни токена в секундах
            
        Returns:
            Dict: Словарь с зашифрованными данными
        """
        try:
            # ⚠️ WARNING: Логирование открытых токенов перед шифрованием (маскированные)
            masked_access = self._mask_token(access_token)
            masked_refresh = self._mask_token(refresh_token)
            centralized_logger.warning(f"📝 [TOKEN_GENERATE] ПОДГОТОВКА К СОХРАНЕНИЮ: Открытый access_token: {masked_access}, Открытый refresh_token: {masked_refresh}", user_id=0)
            
            # Шифруем access токен
            encrypted_access = self.encrypt_access_token(access_token)
            
            # Шифруем refresh токен
            encrypted_refresh = self.encrypt_refresh_token(refresh_token)
            
            # Хешируем refresh токен
            refresh_hash, salt = self.hash_refresh_token(refresh_token)
            
            # Генерируем IV для дополнительной безопасности
            iv = secrets.token_hex(12)
            
            # Вычисляем время истечения
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            
            return {
                'encrypted_access_token': encrypted_access,
                'encrypted_refresh_token': encrypted_refresh,
                'refresh_token_hash': refresh_hash,
                'token_salt': salt,
                'token_iv': iv,
                'token_expires_at': expires_at,
                'token_updated_at': datetime.now(timezone.utc)
            }
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка генерации данных токенов: {e}")
            raise
    
    def is_token_expired(self, expires_at: datetime) -> bool:
        """
        Проверка истечения токена
        
        Args:
            expires_at: Время истечения токена
            
        Returns:
            bool: True если токен истек
        """
        # Убеждаемся, что оба datetime имеют timezone
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        current_time = datetime.now(timezone.utc)
        return current_time >= expires_at
    
    def get_token_expiry_time(self, expires_in: int) -> datetime:
        """
        Получение времени истечения токена
        
        Args:
            expires_in: Время жизни в секундах
            
        Returns:
            datetime: Время истечения
        """
        return datetime.now(timezone.utc) + timedelta(seconds=expires_in)


    # === МЕТОДЫ ДЛЯ РАБОТЫ С ТОКЕНАМИ ПОЛЬЗОВАТЕЛЕЙ ===
    
    def save_user_tokens(self, vk_user_id: int, access_token: str, refresh_token: str, expires_in: int = 3600) -> bool:
        """
        Сохранение зашифрованных токенов пользователя
        
        Args:
            vk_user_id: ID пользователя VK
            access_token: Access токен
            refresh_token: Refresh токен
            expires_in: Время жизни токена в секундах
            
        Returns:
            bool: True если сохранение успешно, False иначе
        """
        try:
            # Логируем полученные токены ДО шифрования
            masked_access_before = self._mask_token(access_token)
            masked_refresh_before = self._mask_token(refresh_token)
            centralized_logger.info(f"💾 [TOKEN_SAVE] ПОЛУЧИЛИ ТОКЕНЫ для пользователя {vk_user_id}: access_token={masked_access_before} (тип: ACCESS_TOKEN), refresh_token={masked_refresh_before} (тип: REFRESH_TOKEN)", user_id=vk_user_id)
            
            # Генерируем зашифрованные данные используя встроенные методы
            token_data = self.generate_token_data(access_token, refresh_token, expires_in)
            
            with self.get_session() as session:
                centralized_logger.debug(f"🔍 Начинаем сохранение токенов для пользователя {vk_user_id}")
                
                # Получаем или создаем настройки пользователя
                user_settings = session.query(UserSettings).filter(
                    UserSettings.vk_user_id == vk_user_id
                ).first()
                
                centralized_logger.debug(f"🔍 Настройки пользователя {vk_user_id}: {'найдены' if user_settings else 'не найдены'}")
                
                if not user_settings:
                    # Проверяем, существует ли пользователь в vk_users
                    existing_user = session.query(VKUser).filter(
                        VKUser.vk_user_id == vk_user_id
                    ).first()
                    
                    centralized_logger.debug(f"🔍 Пользователь {vk_user_id} в vk_users: {'найден' if existing_user else 'не найден'}")
                    
                    if not existing_user:
                        # Создаем пользователя с минимальными данными
                        centralized_logger.debug(f"🔍 Создаем пользователя {vk_user_id}")
                        new_user = VKUser(
                            vk_user_id=vk_user_id,
                            first_name="Пользователь",
                            last_name="VK"
                        )
                        session.add(new_user)
                        session.flush()  # Получаем ID
                        centralized_logger.debug(f"✅ Пользователь {vk_user_id} создан")
                    
                    # Создаем новые настройки
                    centralized_logger.debug(f"🔍 Создаем настройки для пользователя {vk_user_id}")
                    user_settings = UserSettings(
                        vk_user_id=vk_user_id,
                        min_age=18,
                        max_age=35
                    )
                    session.add(user_settings)
                    centralized_logger.debug(f"✅ Настройки для пользователя {vk_user_id} созданы")
                
                # Обновляем поля токенов
                centralized_logger.debug(f"🔍 Обновляем токены для пользователя {vk_user_id}")
                user_settings.encrypted_access_token = token_data['encrypted_access_token']
                user_settings.encrypted_refresh_token = token_data['encrypted_refresh_token']
                user_settings.refresh_token_hash = token_data['refresh_token_hash']
                user_settings.token_salt = token_data['token_salt']
                user_settings.token_iv = token_data['token_iv']
                user_settings.token_expires_at = token_data['token_expires_at']
                user_settings.token_updated_at = token_data['token_updated_at']
                
                # ⚠️ WARNING: Логирование зашифрованных данных, которые записываем в БД (маскированные)
                masked_access_enc = self._mask_token(token_data['encrypted_access_token'])
                masked_refresh_enc = self._mask_token(token_data['encrypted_refresh_token'])
                centralized_logger.warning(f"💾 [TOKEN_SAVE] ЗАПИСЫВАЕМ В БД для пользователя {vk_user_id}: encrypted_access_token={masked_access_enc}, encrypted_refresh_token={masked_refresh_enc}", user_id=vk_user_id)
                
                centralized_logger.debug(f"✅ Токены для пользователя {vk_user_id} обновлены в сессии")
            
            centralized_logger.info(f"✅ Токены пользователя {vk_user_id} сохранены в зашифрованном виде")
            return True
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка сохранения токенов пользователя {vk_user_id}: {e}")
            return False
    
    def get_user_access_token(self, vk_user_id: int) -> Optional[str]:
        """
        Получение расшифрованного access токена пользователя
        
        Args:
            vk_user_id: ID пользователя VK
            
        Returns:
            Optional[str]: Расшифрованный access токен или None
        """
        try:
            centralized_logger.debug(f"🔍 Начинаем получение access токена для пользователя {vk_user_id}", user_id=vk_user_id)
            
            with self.get_session() as session:
                centralized_logger.debug(f"🔍 Ищем настройки пользователя {vk_user_id} в таблице user_settings...", user_id=vk_user_id)
                user_settings = session.query(UserSettings).filter(
                    UserSettings.vk_user_id == vk_user_id
                ).first()
                
                if not user_settings:
                    centralized_logger.debug(f"❌ Настройки пользователя {vk_user_id} не найдены в БД", user_id=vk_user_id)
                    return None
                
                centralized_logger.debug(f"✅ Настройки пользователя {vk_user_id} найдены в БД", user_id=vk_user_id)
                
                if not user_settings.encrypted_access_token:
                    centralized_logger.debug(f"❌ Зашифрованный access токен пользователя {vk_user_id} не найден в БД", user_id=vk_user_id)
                    return None
                
                centralized_logger.debug(f"✅ Зашифрованный access токен пользователя {vk_user_id} найден в БД", user_id=vk_user_id)
                
                # DEBUG: Логирование зашифрованного токена из БД перед расшифровкой (маскированный)
                masked_enc = self._mask_token(user_settings.encrypted_access_token)
                centralized_logger.info(f"📥 [TOKEN_READ] ПОЛУЧИЛИ ИЗ БД для пользователя {vk_user_id}: encrypted_access_token={masked_enc} (тип: ENCRYPTED_ACCESS_TOKEN)", user_id=vk_user_id)
                
                # Расшифровываем токен используя встроенный метод (даже если он истек, чтобы видеть результат)
                centralized_logger.debug(f"🔓 [TOKEN_DECRYPT] Начинаем расшифровку access токена пользователя {vk_user_id}...", user_id=vk_user_id)
                centralized_logger.debug(f"🔓 [TOKEN_DECRYPT] Вызываем decrypt_access_token() с зашифрованным токеном длиной {len(user_settings.encrypted_access_token)} символов", user_id=vk_user_id)
                
                decrypted_token = self.decrypt_access_token(user_settings.encrypted_access_token, user_id=vk_user_id)
                
                # Дополнительное логирование результата (decrypt_access_token уже логирует детали)
                if decrypted_token:
                    masked_dec = self._mask_token(decrypted_token)
                    centralized_logger.info(f"📤 [TOKEN_DECRYPT] РАСШИФРОВАЛИ для пользователя {vk_user_id}: access_token={masked_dec} (тип: ACCESS_TOKEN), длина={len(decrypted_token)}", user_id=vk_user_id)
                else:
                    centralized_logger.error(f"❌ [TOKEN_DECRYPT] РАСШИФРОВКА НЕУДАЧНА для пользователя {vk_user_id}: метод decrypt_access_token вернул None", user_id=vk_user_id)
                
                # Проверяем, не истек ли токен (после расшифровки, чтобы видеть расшифрованный токен в логах)
                if user_settings.token_expires_at:
                    centralized_logger.debug(f"🔍 Проверяем срок действия токена пользователя {vk_user_id}: {user_settings.token_expires_at}", user_id=vk_user_id)
                    if self.is_token_expired(user_settings.token_expires_at):
                        centralized_logger.info(f"⚠️ Токен пользователя {vk_user_id} истек (расшифрованный токен показан выше)", user_id=vk_user_id)
                        return None
                    centralized_logger.debug(f"✅ Токен пользователя {vk_user_id} не истек", user_id=vk_user_id)
                else:
                    centralized_logger.debug(f"⚠️ Время истечения токена пользователя {vk_user_id} не установлено", user_id=vk_user_id)
                
                if decrypted_token:
                    centralized_logger.debug(f"✅ Access токен пользователя {vk_user_id} успешно расшифрован и получен из БД", user_id=vk_user_id)
                    return decrypted_token
                else:
                    centralized_logger.error(f"❌ Не удалось расшифровать access токен пользователя {vk_user_id}", user_id=vk_user_id)
                    return None
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка получения access токена пользователя {vk_user_id}: {e}", user_id=vk_user_id)
            return None
    
    def get_user_refresh_token(self, vk_user_id: int) -> Optional[str]:
        """
        Получение refresh token hash пользователя из БД
        
        Args:
            vk_user_id: ID пользователя VK
            
        Returns:
            Optional[str]: Refresh token hash или None если не найден
        """
        try:
            with self.get_session() as session:
                user_settings = session.query(UserSettings).filter(
                    UserSettings.vk_user_id == vk_user_id
                ).first()
                
                if not user_settings or not user_settings.refresh_token_hash:
                    centralized_logger.debug(f"Refresh токен пользователя {vk_user_id} не найден в БД")
                    return None
                
                centralized_logger.debug(f"Refresh токен пользователя {vk_user_id} найден в БД")
                return user_settings.refresh_token_hash
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка получения refresh токена пользователя {vk_user_id}: {e}")
            return None
    
    def get_user_refresh_token_decrypted(self, vk_user_id: int) -> Optional[str]:
        """
        Получение расшифрованного refresh токена пользователя из БД
        
        Args:
            vk_user_id: ID пользователя VK
            
        Returns:
            Optional[str]: Расшифрованный refresh token или None если не найден
        """
        try:
            with self.get_session() as session:
                user_settings = session.query(UserSettings).filter(
                    UserSettings.vk_user_id == vk_user_id
                ).first()
                
                if not user_settings or not user_settings.encrypted_refresh_token:
                    centralized_logger.debug(f"Refresh токен пользователя {vk_user_id} не найден в БД")
                    return None
                
                # DEBUG: Логирование зашифрованного refresh токена из БД перед расшифровкой (маскированный)
                masked_refresh_enc = self._mask_token(user_settings.encrypted_refresh_token)
                centralized_logger.info(f"📥 [TOKEN_READ] ПОЛУЧИЛИ ИЗ БД для пользователя {vk_user_id}: encrypted_refresh_token={masked_refresh_enc} (тип: ENCRYPTED_REFRESH_TOKEN)", user_id=vk_user_id)
                
                # Расшифровываем токен используя встроенный метод
                centralized_logger.debug(f"🔓 [TOKEN_DECRYPT] Начинаем расшифровку refresh токена пользователя {vk_user_id}...", user_id=vk_user_id)
                centralized_logger.debug(f"🔓 [TOKEN_DECRYPT] Вызываем decrypt_refresh_token() с зашифрованным токеном длиной {len(user_settings.encrypted_refresh_token)} символов", user_id=vk_user_id)
                
                decrypted_token = self.decrypt_refresh_token(user_settings.encrypted_refresh_token, user_id=vk_user_id)
                
                # Дополнительное логирование результата
                if decrypted_token:
                    masked_dec = self._mask_token(decrypted_token)
                    centralized_logger.info(f"📤 [TOKEN_DECRYPT] РАСШИФРОВАЛИ для пользователя {vk_user_id}: refresh_token={masked_dec} (тип: REFRESH_TOKEN), длина={len(decrypted_token)}", user_id=vk_user_id)
                
                centralized_logger.debug(f"✅ Refresh токен пользователя {vk_user_id} успешно получен из БД", user_id=vk_user_id)
                return decrypted_token
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка получения расшифрованного refresh токена пользователя {vk_user_id}: {e}")
            return None
    
    def verify_user_refresh_token(self, vk_user_id: int, refresh_token: str) -> bool:
        """
        Проверка refresh токена пользователя
        
        Args:
            vk_user_id: ID пользователя VK
            refresh_token: Refresh токен для проверки
            
        Returns:
            bool: True если токен валиден, False иначе
        """
        try:
            with self.get_session() as session:
                user_settings = session.query(UserSettings).filter(
                    UserSettings.vk_user_id == vk_user_id
                ).first()
                
                if not user_settings or not user_settings.refresh_token_hash or not user_settings.token_salt:
                    centralized_logger.debug(f"Refresh токен пользователя {vk_user_id} не найден в БД")
                    return False
                
                # Проверяем токен используя встроенный метод
                is_valid = self.verify_refresh_token(
                    refresh_token,
                    user_settings.refresh_token_hash,
                    user_settings.token_salt
                )
                
                if is_valid:
                    centralized_logger.debug(f"Refresh токен пользователя {vk_user_id} валиден")
                else:
                    centralized_logger.debug(f"Refresh токен пользователя {vk_user_id} невалиден")
                
                return is_valid
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка проверки refresh токена пользователя {vk_user_id}: {e}")
            return False
    
    def is_user_token_expired(self, vk_user_id: int) -> bool:
        """
        Проверка истечения токена пользователя
        
        Args:
            vk_user_id: ID пользователя VK
            
        Returns:
            bool: True если токен истек, False иначе
        """
        try:
            centralized_logger.debug(f"🔍 Проверяем истечение токена пользователя {vk_user_id}", user_id=vk_user_id)
            
            with self.get_session() as session:
                centralized_logger.debug(f"🔍 Ищем настройки пользователя {vk_user_id} для проверки истечения токена...", user_id=vk_user_id)
                user_settings = session.query(UserSettings).filter(
                    UserSettings.vk_user_id == vk_user_id
                ).first()
                
                if not user_settings:
                    centralized_logger.debug(f"❌ Настройки пользователя {vk_user_id} не найдены - считаем токен истекшим", user_id=vk_user_id)
                    return True
                
                if not user_settings.token_expires_at:
                    centralized_logger.debug(f"❌ Время истечения токена пользователя {vk_user_id} не установлено - считаем токен истекшим", user_id=vk_user_id)
                    return True
                
                centralized_logger.debug(f"🔍 Время истечения токена пользователя {vk_user_id}: {user_settings.token_expires_at}", user_id=vk_user_id)
                
                # Проверяем истечение используя встроенный метод
                is_expired = self.is_token_expired(user_settings.token_expires_at)
                
                if is_expired:
                    centralized_logger.info(f"⚠️ Токен пользователя {vk_user_id} истек", user_id=vk_user_id)
                else:
                    centralized_logger.debug(f"✅ Токен пользователя {vk_user_id} не истек", user_id=vk_user_id)
                
                return is_expired
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка проверки истечения токена пользователя {vk_user_id}: {e}", user_id=vk_user_id)
            return True
    
    def clear_user_tokens(self, vk_user_id: int) -> bool:
        """
        Очистка токенов пользователя из базы данных
        
        Args:
            vk_user_id: ID пользователя VK
            
        Returns:
            bool: True если очистка успешна, False иначе
        """
        try:
            with self.get_session() as session:
                user_settings = session.query(UserSettings).filter(
                    UserSettings.vk_user_id == vk_user_id
                ).first()
                
                if user_settings:
                    # Очищаем поля токенов
                    user_settings.encrypted_access_token = None
                    user_settings.refresh_token_hash = None
                    user_settings.token_salt = None
                    user_settings.token_iv = None
                    user_settings.token_expires_at = None
                    user_settings.token_updated_at = None
                    
                    centralized_logger.info(f"✅ Токены пользователя {vk_user_id} очищены из БД")
                    return True
                else:
                    centralized_logger.debug(f"Настройки пользователя {vk_user_id} не найдены")
                    return True
                    
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка очистки токенов пользователя {vk_user_id}: {e}")
            return False
    
    def get_user_token_info(self, vk_user_id: int) -> dict:
        """
        Получение информации о токенах пользователя
        
        Args:
            vk_user_id: ID пользователя VK
            
        Returns:
            dict: Информация о токенах
        """
        try:
            with self.get_session() as session:
                user_settings = session.query(UserSettings).filter(
                    UserSettings.vk_user_id == vk_user_id
                ).first()
                
                if not user_settings:
                    return {
                        'has_tokens': False,
                        'is_expired': True,
                        'expires_at': None,
                        'updated_at': None
                    }
                
                has_tokens = bool(user_settings.encrypted_access_token and user_settings.refresh_token_hash)
                is_expired = True
                
                if user_settings.token_expires_at:
                    # Используем встроенный метод проверки истечения
                    is_expired = self.is_token_expired(user_settings.token_expires_at)
                
                return {
                    'has_tokens': has_tokens,
                    'is_expired': is_expired,
                    'expires_at': user_settings.token_expires_at.isoformat() if user_settings.token_expires_at else None,
                    'updated_at': user_settings.token_updated_at.isoformat() if user_settings.token_updated_at else None
                }
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка получения информации о токенах пользователя {vk_user_id}: {e}")
            return {
                'has_tokens': False,
                'is_expired': True,
                'expires_at': None,
                'updated_at': None
            }
    
    def update_user_tokens(self, vk_user_id: int, access_token: Optional[str] = None, 
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
            with self.get_session() as session:
                # Проверяем существование пользователя
                user = session.query(VKUser).filter(
                    VKUser.vk_user_id == vk_user_id
                ).first()
                
                # Если пользователь не существует, создаем его
                # Для администратора группы (ID 900000009) используем специальные данные
                GROUP_ADMIN_USER_ID = 900000009
                if not user:
                    if vk_user_id == GROUP_ADMIN_USER_ID:
                        # Создаем администратора группы с указанными данными
                        centralized_logger.info(f"🔨 Создание администратора группы с ID {vk_user_id}", user_id=0)
                        user = VKUser(
                            vk_user_id=GROUP_ADMIN_USER_ID,
                            first_name="Группа",
                            last_name="Администратор",
                            age=99,
                            sex=0,
                            city="Москва",
                            city_id=1
                        )
                    else:
                        # Для обычных пользователей создаем с минимальными данными
                        centralized_logger.info(f"🔨 Создание пользователя с ID {vk_user_id}", user_id=vk_user_id)
                        user = VKUser(
                            vk_user_id=vk_user_id,
                            first_name="Пользователь",
                            last_name="Неизвестный"
                        )
                    session.add(user)
                    session.flush()  # Получаем ID пользователя
                    centralized_logger.info(f"✅ Пользователь {vk_user_id} создан", user_id=vk_user_id if vk_user_id != GROUP_ADMIN_USER_ID else 0)
                
                # Проверяем существование настроек пользователя
                user_settings = session.query(UserSettings).filter(
                    UserSettings.vk_user_id == vk_user_id
                ).first()
                
                # Если настройки не найдены, создаем их
                if not user_settings:
                    centralized_logger.info(f"🔨 Создание настроек для пользователя {vk_user_id}", user_id=vk_user_id if vk_user_id != GROUP_ADMIN_USER_ID else 0)
                    user_settings = UserSettings(
                        vk_user_id=vk_user_id,
                        min_age=18,
                        max_age=35
                    )
                    session.add(user_settings)
                    session.flush()
                    centralized_logger.info(f"✅ Настройки пользователя {vk_user_id} созданы", user_id=vk_user_id if vk_user_id != GROUP_ADMIN_USER_ID else 0)
                
                # Обновляем access токен если предоставлен (используем встроенное шифрование)
                if access_token:
                    masked_access_before = self._mask_token(access_token)
                    centralized_logger.info(f"💾 [TOKEN_UPDATE] ПОЛУЧИЛИ ACCESS TOKEN для пользователя {vk_user_id}: access_token={masked_access_before} (тип: ACCESS_TOKEN)", user_id=vk_user_id)
                    encrypted_access = self.encrypt_access_token(access_token)
                    user_settings.encrypted_access_token = encrypted_access
                    # ⚠️ WARNING: Логирование обновления access токена (маскированный)
                    masked_access = self._mask_token(encrypted_access)
                    centralized_logger.warning(f"💾 [TOKEN_UPDATE] ЗАПИСЫВАЕМ В БД для пользователя {vk_user_id}: encrypted_access_token={masked_access}", user_id=vk_user_id)
                
                # Обновляем refresh токен если предоставлен (используем встроенное шифрование)
                if refresh_token:
                    masked_refresh_before = self._mask_token(refresh_token)
                    centralized_logger.info(f"💾 [TOKEN_UPDATE] ПОЛУЧИЛИ REFRESH TOKEN для пользователя {vk_user_id}: refresh_token={masked_refresh_before} (тип: REFRESH_TOKEN)", user_id=vk_user_id)
                    encrypted_refresh = self.encrypt_refresh_token(refresh_token)
                    refresh_hash, salt = self.hash_refresh_token(refresh_token)
                    user_settings.encrypted_refresh_token = encrypted_refresh
                    user_settings.refresh_token_hash = refresh_hash
                    user_settings.token_salt = salt
                    # ⚠️ WARNING: Логирование обновления refresh токена (маскированный)
                    masked_refresh = self._mask_token(encrypted_refresh)
                    centralized_logger.warning(f"💾 [TOKEN_UPDATE] ЗАПИСЫВАЕМ В БД для пользователя {vk_user_id}: encrypted_refresh_token={masked_refresh}", user_id=vk_user_id)
                
                # Обновляем время истечения если предоставлено
                if expires_in:
                    expires_at = self.get_token_expiry_time(expires_in)
                    user_settings.token_expires_at = expires_at
                
                # Обновляем время последнего обновления
                user_settings.token_updated_at = datetime.now(timezone.utc)
                
                centralized_logger.info(f"✅ Токены пользователя {vk_user_id} обновлены")
                return True
                
        except Exception as e:
            centralized_logger.error(f"❌ Ошибка обновления токенов пользователя {vk_user_id}: {e}")
            return False


def main():
    """Основная функция для тестирования интерфейса базы данных"""
    print("🔧 Тестирование интерфейса базы данных VKinder Bot")
    print("=" * 60)
    
    # Создаем экземпляр интерфейса
    db_interface = DatabaseInterface()
    
    # Тестируем подключение
    print("\n1. Тестирование подключения...")
    if db_interface.test_connection():
        print("✅ Подключение работает")
    else:
        print("❌ Ошибка подключения")
        return
    
    # Получаем информацию о таблицах
    print("\n2. Информация о таблицах...")
    table_info = db_interface.get_table_info()
    print(f"📊 Всего таблиц: {table_info.get('total_tables', 0)}")
    
    for table_name, info in table_info.get('tables', {}).items():
        print(f"  - {table_name}: {info['count']} записей")
    
    # Тестируем добавление пользователя
    print("\n3. Тестирование добавления пользователя...")
    test_user_id = 123456789
    if db_interface.add_user(
        vk_user_id=test_user_id,
        first_name="Тест",
        last_name="Пользователь",
        age=25,
        sex=2,
        city="Москва"
    ):
        print("✅ Пользователь добавлен")
    else:
        print("❌ Ошибка добавления пользователя")
    
    # Тестирование добавления лога пропущено - логирование в БД отключено
    print("\n4. Тестирование добавления лога...")
    print("⚠️ Логирование в БД отключено, все логи идут только в файлы")
    
    # Таблица bot_messages удалена
    print("\n5. Тестирование добавления сообщения...")
    print("⚠️ Таблица bot_messages удалена, все логи идут только в файлы")
    
    # Получаем обновленную информацию
    print("\n6. Обновленная информация о таблицах...")
    table_info = db_interface.get_table_info()
    for table_name, info in table_info.get('tables', {}).items():
        print(f"  - {table_name}: {info['count']} записей")
    
    print("\n✅ Тестирование завершено!")


if __name__ == "__main__":
    main()
