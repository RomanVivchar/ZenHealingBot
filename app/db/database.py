# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
# Импортируем Base из models.py
from .models import Base # Убедись, что models.py доступен по пути импорта
# Импортируем настройки (предполагаем, что они у тебя есть)
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__) # Логгер для этого модуля

# --- Настройка подключения ---
# Убедись, что в settings.py определена DATABASE_URL_asyncpg
# вида "postgresql+asyncpg://пользователь:пароль@хост:порт/имя_базы_данных"
DATABASE_URL = settings.DATABASE_URL_asyncpg
# ---------------------------

# --- Создание асинхронного движка ---
# echo=True выводит SQL запросы в консоль (удобно для отладки)
async_engine = create_async_engine(DATABASE_URL, echo=True) # echo=False в продакшене
# ----------------------------------

# --- Создание фабрики асинхронных сессий ---
# class_=AsyncSession указывает на использование асинхронных сессий
# expire_on_commit=False часто используется в асинхронном коде
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False # Не инвалидировать объекты после коммита
)
# ------------------------------------------

# --- Функция для создания таблиц ---
async def create_db_and_tables():
    """Создает таблицы в базе данных на основе моделей."""
    logger.info("Создание таблиц базы данных...")
    async with async_engine.begin() as conn:
        # Base.metadata.create_all - синхронная операция,
        # поэтому используем conn.run_sync для ее выполнения в асинхронном контексте
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы базы данных успешно созданы.")


# Этот файл НЕ должен содержать код запуска приложения или asyncio.run()