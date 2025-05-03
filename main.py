# main.py

import asyncio
import logging
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.config.settings import settings
from app.handlers.common import common_router
from app.handlers.code_words import code_words_router
from app.config.bot_instance import bot
# Убедись, что create_db_and_tables доступна (импортирована или определена)
from app.db.database import create_db_and_tables
# Импортируй движок БД, если нужно его закрывать здесь
# from app.db.database import async_engine # Пример


# --- Определяем логгер на уровне модуля ---
# Теперь этот объект 'log' будет доступен во всех функциях этого файла
log = logging.getLogger(__name__)
# ---------------------------------------


# --- Функции жизненного цикла вебхука ---
# Эти функции уже используют 'log', что хорошо
async def on_startup(bot: Bot) -> None:
    """Действия при запуске бота."""
    log.info("Выполняется on_startup: Запуск приложения и установка вебхука...") # Добавлен лог
    if settings.webhook_host:
        webhook_url = f"{str(settings.webhook_host).rstrip('/')}{settings.webhook_path}"
        try:
            # --- Вызов инициализации БД ---
            log.info("Выполняется on_startup: Инициализация базы данных...") # Добавлен лог
            # Убедись, что create_db_and_tables корректно вызывает Base.metadata.create_all
            await create_db_and_tables()
            log.info("Выполняется on_startup: Инициализация базы данных завершена.") # Добавлен лог
            # ----------------------------

            # --- Установка вебхука ---
            log.info(f"Выполняется on_startup: Попытка установить вебхук на: {webhook_url}") # Добавлен лог
            await bot.set_webhook(
                webhook_url,
                secret_token=settings.webhook_secret.get_secret_value() if settings.webhook_secret else None
            )
            log.info(f"Выполняется on_startup: Вебхук успешно установлен на: {webhook_url}") # Добавлен лог
            # -------------------------

        except Exception as e:
            # Эти print() были для отладки, они уже не нужны, так как логирование настроено
            # print("Сообщение об ошибке (из print):", e)
            # print("Тип исключения:", type(e))
            # print("e.args:", e.args)
            log.error(f"Выполняется on_startup: Не удалось установить вебхук на {webhook_url}: {e}", exc_info=True) # exc_info=True добавит traceback
            # В случае неудачи установки вебхука, возможно, стоит выйти из приложения
            # sys.exit(1) # Опционально, если без вебхука бот не имеет смысла

    else:
        log.warning("Выполняется on_startup: WEBHOOK_HOST не указан в настройках. Пропуск установки вебхука.")
        log.warning("Выполняется on_startup: Для локальной разработки без HTTPS и домена используйте polling.")


async def on_shutdown(bot: Bot) -> None:
    """Действия при остановке бота."""
    log.warning("Выполняется on_shutdown: Бот останавливается...") # Добавлен лог

    # --- Удаление вебхука ---
    try:
        log.info("Выполняется on_shutdown: Попытка удалить вебхук...") # Добавлен лог
        if settings.webhook_host:
            await bot.delete_webhook(drop_pending_updates=True)
            log.info("Выполняется on_shutdown: Вебхук успешно удален.") # Добавлен лог
    except Exception as e:
        log.error(f"Выполняется on_shutdown: Ошибка при удалении вебхука: {e}", exc_info=True) # Добавлен лог

    # --- Закрытие сессии бота ---
    log.info("Выполняется on_shutdown: Закрытие сессии бота...") # Добавлен лог
    await bot.session.close()
    log.info("Выполняется on_shutdown: Сессия бота закрыта.") # Добавлен лог

    # --- Закрытие движка БД ---
    # Если движок async_engine требует закрытия здесь (зависит от его жизненного цикла)
    # from app.db.database import async_engine # Импортировать движок
    # if async_engine: # Проверить, что он существует и не None
    #    log.info("Выполняется on_shutdown: Закрытие движка базы данных...")
    #    await async_engine.dispose()
    #    log.info("Выполняется on_shutdown: Движок базы данных закрыт.")
    # -------------------------


# --- Основная асинхронная функция запуска (теперь использует логгер модуля) ---
async def main() -> None:
    log.info("Вход в функцию main()...") # Добавлен лог

    # --- Инициализация основных компонентов ---
    log.info("Инициализация Bot, Storage, Dispatcher...") # Добавлен лог
    try:
        # Убедись, что settings.bot_token существует и корректно загружен
        
        # Убедись, что MemoryStorage импортирован или используй другое хранилище
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        log.info("Bot, Storage, Dispatcher инициализированы.") # Добавлен лог
    except Exception as e:
        log.critical(f"Критическая ошибка при инициализации Bot/Dispatcher: {e}", exc_info=True) # Добавлен лог с уровнем CRITICAL
        sys.exit(1) # Выходим, если не удалось инициализировать

    # --- Регистрация хендлеров и роутеров ---
    log.info("Регистрация startup/shutdown хендлеров и роутеров...") # Добавлен лог
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    # Убедись, что common_router импортирован и является экземпляром Router
    dp.include_router(common_router)
    dp.include_router(code_words_router)
    log.info("Хендлеры и роутеры зарегистрированы.") # Добавлен лог

    # --- Настройка вебхука Aiohttp ---
    log.info("Настройка вебхук-сервера Aiohttp...") # Добавлен лог
    try:
        app = web.Application()

        # Убедись, что webhook_secret загружен
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=settings.webhook_secret.get_secret_value() if settings.webhook_secret else None
        )

        # Убедись, что webhook_path загружен
        webhook_requests_handler.register(app, path=settings.webhook_path)

        setup_application(app, dp, bot=bot)
        log.info("Настройка Aiohttp приложения завершена.") # Добавлен лог

    except Exception as e:
         log.critical(f"Критическая ошибка при настройке вебхук-сервера Aiohttp: {e}", exc_info=True) # Добавлен лог с уровнем CRITICAL
         sys.exit(1) # Выходим, если не удалось настроить сервер

    # --- Запуск веб-сервера ---
    # Убедись, что webapp_host и webapp_port загружены
    log.info(f"Попытка запуска Aiohttp веб-сервера на http://{settings.webapp_host}:{settings.webapp_port}") # Добавлен лог
    runner = web.AppRunner(app)
    try:
        await runner.setup() # Вызвал и дождался setup
        log.info("Aiohttp Runner настроен.") # Добавлен лог

        # Теперь можно создавать TCPSite, передав ему настроенный раннер
        log.info(f"Попытка запуска Aiohttp веб-сервера на http://{settings.webapp_host}:{settings.webapp_port}") # Добавлен лог
        site = web.TCPSite( # Создал сайт ПОСЛЕ await runner.setup()
            runner,
            host=settings.webapp_host,
            port=settings.webapp_port,
        )
        await site.start() # Запустил сайт
        log.info(f"Aiohttp веб-сервер успешно запущен на http://{settings.webapp_host}:{settings.webapp_port}") # Добавлен лог

        # Бесконечный цикл для поддержания работы сервера
        # В Docker это будет работать нормально
        # При локальном запуске можно прервать через Ctrl+C
        log.info("Веб-сервер работает. Ожидание сигнала остановки (Ctrl+C)...") # Добавлен лог
        await asyncio.Event().wait() # Ждем, пока событие не будет установлено (Ctrl+C вызывает KeyboardInterrupt)

    except (KeyboardInterrupt, SystemExit):
        log.warning("Получен сигнал остановки (Ctrl+C / SystemExit). Завершение работы...") # Добавлен лог
    except Exception as e: # Перехватываем другие возможные ошибки во время работы сервера
        log.critical(f"Критическая ошибка во время работы веб-сервера: {e}", exc_info=True) # Добавлен лог с уровнем CRITICAL

    finally:
        log.info("Выполняется финальная очистка ресурсов...") # Добавлен лог
        # Остановка AppRunner (корректно закрывает соединения и т.д.)
        await runner.cleanup()
        log.info("AppRunner очищен.")

        # --- Финальное закрытие ресурсов (БД) ---
        # Если движок БД не был закрыт в on_shutdown
        # from app.db.database import async_engine
        # if async_engine and not async_engine.closed: # Проверить, что он существует и не закрыт
        #    log.info("Финальное закрытие движка базы данных...")
        #    await async_engine.dispose()
        #    log.info("Движок базы данных закрыт.")
        # ---------------------------------------

    log.info("Функция main() завершила выполнение.") # Добавлен лог


# --- Точка входа при запуске скрипта ---
if __name__ == "__main__":
    # --- Базовая конфигурация логирования ---
    # Эта настройка должна быть выполнена первой
    logging.basicConfig(
        level=logging.INFO, # Уровень логирования
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", # Формат сообщений
        stream=sys.stdout # Вывод в консоль
    )
    # Логгер 'log' уже определен на уровне модуля

    # --- Запуск основной асинхронной функции ---
    log.info("Запуск цикла событий asyncio с функцией main().") # Добавлен лог
    try:
        asyncio.run(main())
    except Exception as e:
         # Перехватываем любые исключения, которые могли не быть пойманы внутри main()
         log.critical(f"Необработанное исключение во время выполнения asyncio.run: {e}", exc_info=True) # Добавлен лог с уровнем CRITICAL

    log.info("Цикл событий asyncio завершен.") # Добавлен лог