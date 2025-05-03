# bot_instance.py
from aiogram import Bot
from app.config.settings import settings

bot = Bot(token=settings.bot_token.get_secret_value())