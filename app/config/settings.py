# src/config/settings.py
import logging
import sys
from pathlib import Path
# Импорты Pydantic Settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, AnyHttpUrl, Field, validator

# Убедимся, что корневая папка проекта в sys.path для корректных импортов
# Это может быть полезно при запуске из разных мест
# Рассчитываем путь к корневой папке (на два уровня выше текущего файла)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))



log = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Конфигурация Pydantic Settings:
    # - Читать переменные из файла .env
    # - Кодировка файла .env
    # - Игнорировать лишние переменные в окружении
    
    POSTGRESQL_HOST:str
    POSTGRESQL_PORT:str
    POSTGRESQL_USER:str
    POSTGRESQL_PASSWORD:str
    POSTGRESQL_DBNAME:str

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.POSTGRESQL_USER}:{self.POSTGRESQL_PASSWORD}@{self.POSTGRESQL_HOST}:{self.POSTGRESQL_PORT}/{self.POSTGRESQL_DBNAME}"

    
    # --- Основные настройки бота ---
    
    bot_token: SecretStr = Field(..., alias='BOT_TOKEN')

    # --- Настройки Вебхука ---
    
    webhook_host: AnyHttpUrl | None = Field(None, alias='WEBHOOK_HOST')
    
    webhook_path: str = Field("/webhook", alias='WEBHOOK_PATH')

    # --- Настройки Веб-приложения (внутреннего) ---
    
    webapp_host: str = Field("0.0.0.0", alias='WEBAPP_HOST')
    
    webapp_port: int = Field(8080, alias='WEBAPP_PORT')

    # --- Опционально: Секретный токен вебхука ---
    
    webhook_secret: SecretStr | None = Field(None, alias='WEBHOOK_SECRET')


    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env', # Ищем .env в корне проекта
        env_file_encoding='utf-8',
        extra='ignore'
    )

    

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

