"""
Модели базы данных для системы управления PostgreSQL
Определяет структуру всех таблиц для работы с пользователями, поиском и избранным
"""

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List

# Базовый класс для всех моделей
Base = declarative_base()


class VKUser(Base):
    """
    Модель пользователя VK
    
    Хранит основную информацию о пользователях ВКонтакте:
    - ID пользователя, имя, фамилия
    - Возраст, пол, город
    - URL фотографии профиля
    - Статус активности
    """
    __tablename__ = "vk_users"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_user_id = Column(BigInteger, unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(Integer, nullable=True)  # 1 - женский, 2 - мужской
    city = Column(String(100), nullable=True)
    city_id = Column(Integer, nullable=True)  # ID города для VK API
    country = Column(String(100), nullable=True)
    bdate = Column(String(20), nullable=True)
    photo_url = Column(String(500), nullable=True)
    profile_url = Column(String(200), nullable=True)
    is_closed = Column(Boolean, default=False, nullable=True)
    can_access_closed = Column(Boolean, default=False, nullable=True)
    
    # Дополнительные поля пользователя
    access = Column(String(500), nullable=True)  # Access - string
    refresh = Column(String(500), nullable=True)  # Refresh - string
    time = Column(Integer, nullable=True)  # Time - integer
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи с другими таблицами
    photos = relationship("Photo", foreign_keys="Photo.vk_user_id", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", foreign_keys="Favorite.user_vk_id", back_populates="user")
    blacklisted_by = relationship("Blacklisted", foreign_keys="Blacklisted.user_vk_id", back_populates="user")
    user_settings = relationship("UserSettings", back_populates="user", uselist=False)
    
    @property
    def full_name(self) -> str:
        """Полное имя пользователя"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self) -> str:
        """Строковое представление пользователя"""
        return f"<VKUser(id={self.vk_user_id}, name='{self.full_name}')>"


class Photo(Base):
    """
    Модель фотографии пользователя
    
    Хранит информацию о фотографиях пользователей:
    - Ссылка на фотографию
    - Тип фотографии (profile, album, etc.)
    - Количество лайков и дизлайков
    - Кто нашел эту фотографию в поиске
    """
    __tablename__ = "photos"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_user_id = Column(BigInteger, ForeignKey("vk_users.vk_user_id"), nullable=False)
    photo_url = Column(Text, nullable=False)
    photo_type = Column(String(50), nullable=True)  # profile, album, etc.
    likes_count = Column(Integer, default=0, nullable=False)
    
    # Поле для отслеживания того, кто нашел эту фотографию
    found_by_user_id = Column(BigInteger, ForeignKey("vk_users.vk_user_id"), nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user = relationship("VKUser", foreign_keys=[vk_user_id], back_populates="photos")
    found_by_user = relationship("VKUser", foreign_keys=[found_by_user_id])
    
    def __repr__(self) -> str:
        """Строковое представление фотографии"""
        return f"<Photo(id={self.id}, user_id={self.vk_user_id}, type='{self.photo_type}')>"


class Favorite(Base):
    """
    Модель избранных пользователей
    
    Связывает пользователей с их избранными:
    - Кто добавил в избранное
    - Кого добавили в избранное
    """
    __tablename__ = "favorites"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_vk_id = Column(BigInteger, ForeignKey("vk_users.vk_user_id"), nullable=False)
    favorite_vk_id = Column(BigInteger, ForeignKey("vk_users.vk_user_id"), nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("VKUser", foreign_keys=[user_vk_id], back_populates="favorites")
    favorite = relationship("VKUser", foreign_keys=[favorite_vk_id])
    
    def __repr__(self) -> str:
        """Строковое представление избранного"""
        return f"<Favorite(user_id={self.user_vk_id}, favorite_id={self.favorite_vk_id})>"


class Blacklisted(Base):
    """
    Модель черного списка
    
    Связывает пользователей с заблокированными:
    - Кто заблокировал
    - Кого заблокировали
    """
    __tablename__ = "blacklisted"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_vk_id = Column(BigInteger, ForeignKey("vk_users.vk_user_id"), nullable=False)
    blocked_vk_id = Column(BigInteger, ForeignKey("vk_users.vk_user_id"), nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("VKUser", foreign_keys=[user_vk_id], back_populates="blacklisted_by")
    blocked = relationship("VKUser", foreign_keys=[blocked_vk_id])
    
    def __repr__(self) -> str:
        """Строковое представление черного списка"""
        return f"<Blacklisted(user_id={self.user_vk_id}, blocked_id={self.blocked_vk_id})>"




class UserSettings(Base):
    """
    Модель настроек пользователя
    
    Хранит персональные настройки поиска:
    - Возрастной диапазон
    - Предпочтения по полу
    - Предпочтения по городу
    - Статусы отношений
    """
    __tablename__ = "user_settings"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_user_id = Column(BigInteger, ForeignKey("vk_users.vk_user_id"), nullable=False, unique=True)
    min_age = Column(Integer, default=18, nullable=False)
    max_age = Column(Integer, default=35, nullable=False)
    sex_preference = Column(Integer, nullable=True)  # 1 - женский, 2 - мужской, 0 - любой
    city_preference = Column(String(100), nullable=True)
    
    # Новые поля для статусов (JSON для хранения массива)
    relationship_statuses = Column(JSON, nullable=True)  # JSON массив: ["single", "married", ...]
    online = Column(Boolean, default=False, nullable=True)  # Только онлайн
    
    # Поле для знаков зодиака (JSON для хранения массива)
    zodiac_signs = Column(JSON, nullable=True)  # JSON массив: ["aries", "taurus", ...]
    
    # Поля для зашифрованных токенов пользователя
    encrypted_access_token = Column(Text, nullable=True)  # Зашифрованный access token
    encrypted_refresh_token = Column(Text, nullable=True)  # Зашифрованный refresh token
    refresh_token_hash = Column(String(128), nullable=True)  # Хеш refresh token (для проверки)
    token_salt = Column(String(32), nullable=True)  # Соль для refresh token
    token_iv = Column(String(24), nullable=True)  # IV для AES шифрования
    token_expires_at = Column(DateTime(timezone=True), nullable=True)  # Время истечения токена
    token_updated_at = Column(DateTime(timezone=True), nullable=True)  # Время последнего обновления
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user = relationship("VKUser", back_populates="user_settings")
    
    def __repr__(self) -> str:
        """Строковое представление настроек пользователя"""
        return f"<UserSettings(user_id={self.vk_user_id}, age={self.min_age}-{self.max_age})>"
