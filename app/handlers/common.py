import asyncio
import sys
from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

common_router = Router(name="common-handlers")



@common_router.message(CommandStart())
async def handle_start(message: Message):
  await message.answer("Добрый день, Вас приветствует ZenHealingBot — я помогу Вам пройти мини-диагностику, получить бесплатный или платный гайд, записаться на консультацию или сопровождение. " \
  "\n Также Вы можете писать кодовые слова:" \
  "\n - СТРЕСС → Антистресс-протокол (бесплатно)"
  "\n - ЗАВТРАК → Полезные завтраки"
  "\n - КУХНЯ → Безопасная кухня"
  "\n - ПЕРЕЕДАЮ → Как перестать переедать вечером"
  "\n - АППЕТИТ → Аппетит под контролем"
  "\n - ДЕФИЦИТ → Питание при дефицитах")


@common_router.message(Command("help"))
async def handle_help(message: Message):
  await message.answer("Здесь появится справка о боте")


