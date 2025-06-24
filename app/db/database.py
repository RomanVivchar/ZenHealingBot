# database.py
import asyncio # Импортируем asyncio
import os # Возможно понадобится, если настройки читают переменные окружения
import sys # Для корректного вывода в случае ошибок
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
# Импортируем Base из models.py
from ..config.settings import settings
from ..db.models import Base, User, Payment # Убедись, что models.py доступен по пути импорта
# Импортируем настройки (предполагаем, что они у тебя есть)
# Если settings.py находится по другому пути, скорректируй импорт

import logging

logger = logging.getLogger(__name__) # Логгер для этого модуля

# --- Настройка подключения ---
# Убедись, что в settings.py определена DATABASE_URL_asyncpg
# вида "postgresql+asyncpg://пользователь:пароль@хост:порт/имя_базы_данных"
# При запуске этого скрипта отдельно, убедись, что переменные окружения,
# которые использует settings для формирования DATABASE_URL_asyncpg, установлены.
DATABASE_URL = settings.DATABASE_URL_asyncpg
# ---------------------------

# --- Создание асинхронного движка ---
# echo=True выводит SQL запросы в консоль (удобно для отладки)
# Для продакшена echo=False
async_engine = create_async_engine(url=DATABASE_URL, echo=True)
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
async def create_db_and_tables_debug_individual():
    """Создает таблицы users и payments по отдельности для отладки."""
    print("DEBUG: create_db_and_tables_debug_individual: НАЧАЛО.") # <-- Добавлено
    logger.info("Запуск отладочного создания таблиц по отдельности...")

    try:
        # --- Попытка создать таблицу users ---
        print("DEBUG: create_db_and_tables_debug_individual: Попытка создать таблицу 'users'...") # <-- Добавлено
        async with async_engine.begin() as conn:
            print("DEBUG: create_db_and_tables_debug_individual: Соединение получено для 'users'.") # <-- Добавлено
            await conn.run_sync(Base.metadata.create_all, tables=[User.__table__])
            print("DEBUG: create_db_and_tables_debug_individual: Команда create_all для 'users' выполнена.") # <-- Добавлено
        print("DEBUG: create_db_and_tables_debug_individual: Транзакция для 'users' завершена (должен быть COMMIT).") # <-- Добавлено
        logger.info("Попытка создания таблицы users завершена.")

        # --- Проверка существования users после COMMIT (опционально, может зависнуть если COMMIT не прошел) ---
        print("DEBUG: create_db_and_tables_debug_individual: Проверка существования 'users' после COMMIT...")
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename = 'users';"))
            if result.scalar_one_or_none():
                print("DEBUG: create_db_and_tables_debug_individual: Таблица 'users' найдена после создания.")
            else:
                 print("DEBUG: create_db_and_tables_debug_individual: Таблица 'users' НЕ найдена после создания!")


        # --- Попытка создать таблицу payments ---
        print("DEBUG: create_db_and_tables_debug_individual: Попытка создать таблицу 'payments'...") # <-- Добавлено
        async with async_engine.begin() as conn:
            print("DEBUG: create_db_and_tables_debug_individual: Соединение получено для 'payments'.") # <-- Добавлено
            await conn.run_sync(Base.metadata.create_all, tables=[Payment.__table__])
            print("DEBUG: create_db_and_tables_debug_individual: Команда create_all для 'payments' выполнена.") # <-- Добавлено
        print("DEBUG: create_db_and_tables_debug_individual: Транзакция для 'payments' завершена (должен быть COMMIT).") # <-- Добавлено
        logger.info("Попытка создания таблицы payments завершена.")

        # --- Проверка существования payments после COMMIT (опционально) ---
        print("DEBUG: create_db_and_tables_debug_individual: Проверка существования 'payments' после COMMIT...")
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename = 'payments';"))
            if result.scalar_one_or_none():
                print("DEBUG: create_db_and_tables_debug_individual: Таблица 'payments' найдена после создания.")
            else:
                 print("DEBUG: create_db_and_tables_debug_individual: Таблица 'payments' НЕ найдена после создания!")


        logger.info("Отладочное создание таблиц по отдельности завершено.")
        print("DEBUG: create_db_and_tables_debug_individual: КОНЕЦ (успех или поймана ошибка).") # <-- Добавлено

    except Exception as e:
        logger.error(f"Ошибка при отладочном создании таблиц по отдельности: {e}", exc_info=True)
        print(f"DEBUG: create_db_and_tables_debug_individual: Перехвачена ошибка: {e}", file=sys.stderr) # <-- Добавлено
        # Не перевыбрасываем, так как on_startup ловит
        # raise



# --- Функция для создания таблиц ---
async def create_db_and_tables():
    """Создает таблицы в базе данных на основе моделей."""
    logger.info("Создание таблиц базы данных...")
    print("DEBUG: create_db_and_tables: Функция вызвана.") # <-- Добавлено для отладки
    try:
        print("DEBUG: create_db_and_tables: Попытка получить соединение и начать транзакцию...") # <-- Добавлено для отладки
        # !!! Используем engine.begin() для транзакционного блока !!!
        async with async_engine.begin() as conn:
            print("DEBUG: create_db_and_tables: Соединение получено, транзакция начата.") # <-- Добавлено для отладки
            # Base.metadata.create_all - синхронная операция,
            # поэтому используем conn.run_sync для ее выполнения в асинхронном контексте
            print("DEBUG: create_db_and_tables: Попытка выполнить Base.metadata.create_all...") # <-- Добавлено для отладки
            await conn.run_sync(Base.metadata.create_all, tables=[User.__table__, Payment.__table__])
            print("DEBUG: create_db_and_tables: Base.metadata.create_all выполнена.") # <-- Добавлено для отладки
        # При выходе из блока 'async with', если нет исключений, выполняется COM    
        logger.info("Таблицы базы данных успешно созданы.")
        print("DEBUG: create_db_and_tables: Таблицы должны быть созданы и зафиксированы.") # <-- Добавлено для отладки
        # sys.exit(0) # Эту строку не нужно вызывать, если скрипт часть б    
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц базы данных: {e}", exc_info=True)
        print(f"DEBUG: create_db_and_tables: Перехвачена ошибка: {e}", file=sys.stderr) # <-- Добавлено для отладки в stderr
        # Не перевыбрасываем исключение здесь, так как оно ловится в on_startup
        # raise # Не раскомментируй, если on_startup ловит оши    
    print("DEBUG: create_db_and_tables: Функция завершила выполнение.") 


# --- Блок для запуска скрипта напрямую ---
# if __name__ == "__main__":
#     # При запуске этого скрипта напрямую, запускаем асинхронную функцию создания таблиц
#     print("Запуск скрипта создания таблиц...")
#     asyncio.run(create_db_and_tables())
#     print("Скрипт создания таблиц завершен.")   