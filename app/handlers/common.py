import asyncio
import sys
from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

common_router = Router(name="common-handlers")



@common_router.message(CommandStart())
async def handle_start(message: Message):
  await message.answer(f"Привет {message.from_user.first_name}")


@common_router.message(Command("help"))
async def handle_help(message: Message):
  await message.answer("Здесь появится справка о боте")


