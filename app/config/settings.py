# src/config/settings.py
import logging
import sys
from pathlib import Path

# Убедимся, что корневая папка проекта в sys.path для корректных импортов
# Это может быть полезно при запуске из разных мест
# Рассчитываем путь к корневой папке (на два уровня выше текущего файла)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# Импорты Pydantic Settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, AnyHttpUrl, Field, validator

log = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Конфигурация Pydantic Settings:
    # - Читать переменные из файла .env
    # - Кодировка файла .env
    # - Игнорировать лишние переменные в окружении
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env', # Ищем .env в корне проекта
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # --- Основные настройки бота ---
    # Токен бота из @BotFather. SecretStr скрывает значение при логировании/выводе.
    bot_token: SecretStr = Field(..., alias='BOT_TOKEN')

    # --- Настройки Вебхука ---
    # URL, который будет слушать Telegram (должен быть HTTPS!)
    # e.g., https://yourdomain.com
    # Может быть None, если вебхук устанавливается вручную или используется polling
    webhook_host: AnyHttpUrl | None = Field(None, alias='WEBHOOK_HOST')
    # Путь для вебхука на твоем сервере, должен начинаться с /
    # Рекомендуется делать его секретным, например, добавляя токен: /webhook/ВАШ_ТОКЕН
    webhook_path: str = Field("/webhook", alias='WEBHOOK_PATH')

    # --- Настройки Веб-приложения (внутреннего) ---
    # Хост, на котором будет слушать встроенный веб-сервер aiohttp
    # '0.0.0.0' означает слушать на всех доступных сетевых интерфейсах
    webapp_host: str = Field("0.0.0.0", alias='WEBAPP_HOST')
    # Порт для встроенного веб-сервера aiohttp
    webapp_port: int = Field(8080, alias='WEBAPP_PORT')

    # --- Опционально: Секретный токен вебхука ---
    # Дополнительная проверка, что запросы приходят именно от Telegram
    webhook_secret: SecretStr | None = Field(None, alias='WEBHOOK_SECRET')

    # --- Опционально: Настройки базы данных ---
    # db_url: str | None = Field(None, alias='DATABASE_URL')

    # --- Валидация ---
    @validator('webhook_path')
    def check_webhook_path(cls, v):
        if not v.startswith('/'):
            raise ValueError("webhook_path должен начинаться с '/'")
        return v

# Создаем экземпляр настроек
try:
    settings = Settings()
    log.info("Настройки успешно загружены.")
    # Выведем некоторые (не секретные!) настройки для проверки
    log.info(f"Webhook Path: {settings.webhook_path}")
    log.info(f"WebApp Host: {settings.webapp_host}")
    log.info(f"WebApp Port: {settings.webapp_port}")
    if settings.webhook_host:
        log.info(f"Webhook Host: {settings.webhook_host}")
    else:
        log.warning("WEBHOOK_HOST не установлен. Установка вебхука будет пропущена.")

except Exception as e:
    log.exception("Ошибка при загрузке настроек!")
    sys.exit(f"Ошибка конфигурации: {e}")

# Теперь можно импортировать settings из других модулей:
# from app.config.settings import settings