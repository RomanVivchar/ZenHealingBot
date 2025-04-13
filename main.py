from app.config.settings import settings


import logging
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.handlers.common import common_router




# --- Функции жизненного цикла вебхука ---
async def on_startup(bot: Bot) -> None:
    """Действия при запуске бота."""
    if settings.webhook_host:
        webhook_url = f"{str(settings.webhook_host).rstrip('/')}{settings.webhook_path}"
        try:
            await bot.set_webhook(
                webhook_url,
                secret_token=settings.webhook_secret.get_secret_value() if settings.webhook_secret else None 
            )
            log.info(f"Вебхук установлен на: {webhook_url}")
        except Exception as e:
            log.error(f"Не удалось установить вебхук на {webhook_url}: {e}")
    else:
        log.warning("WEBHOOK_HOST не указан в настройках. Пропуск установки вебхука.")
        log.warning("Для локальной разработки без HTTPS и домена используйте polling.")
        log.warning("Или используйте ngrok/cloudflared для создания временного HTTPS туннеля.")


async def on_shutdown(bot: Bot) -> None:
    """Действия при остановке бота."""
    log.warning("Бот останавливается...")
    # Удаляем вебхук, чтобы Telegram перестал слать обновления
    # Делаем это с `drop_pending_updates=True`, чтобы не получать старые апдейты при след. запуске
    try:
        # Проверяем, что URL был установлен, прежде чем удалять
        if settings.webhook_host:
             await bot.delete_webhook(drop_pending_updates=True)
             log.info("Вебхук успешно удален.")
    except Exception as e:
        log.error(f"Ошибка при удалении вебхука: {e}")

    # Закрываем сессию бота
    await bot.session.close()
    log.warning("Сессия бота закрыта.")



async def main() -> None:
    bot = Bot(token=settings.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(common_router)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret.get_secret_value()
    )

    webhook_requests_handler.register(app, path=settings.webhook_path)

    setup_application(app, dp, bot=bot)

    # Создаем и запускаем веб-сервер aiohttp
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        host=settings.webapp_host,
        port=settings.webapp_port,
    )
    try:
        await site.start()
        log.info(f"Веб-сервер запущен на http://{settings.webapp_host}:{settings.webapp_port}")

        # Бесконечный цикл для поддержания работы сервера
        # В Docker это будет работать нормально
        # При локальном запуске можно прервать через Ctrl+C
        await asyncio.Event().wait()
    finally:
        await runner.cleanup() # Корректно останавливаем AppRunner
        log.info("Веб-сервер остановлен.")




if __name__ == "__main__":
    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    stream=sys.stdout)
    log = logging.getLogger(__name__)

    try:
        # Запускаем асинхронную функцию main через asyncio.run()
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Обрабатываем прерывание (Ctrl+C) или завершение работы
        log.info("Бот остановлен.")