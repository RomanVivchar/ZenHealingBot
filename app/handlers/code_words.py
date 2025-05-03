from aiogram import F, Router
from aiogram.types import Message
from ..config.bot_instance import bot
import logging
from app.keyboards.inline import buy_guide_keyboard

code_words_router = Router(name="code_words_handlers")

logger = logging.getLogger('aiogram')

#! ДОБАВИТЬ ОПЛАТУ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

@code_words_router.message(F.text == "СТРЕСС")
async def stress_word(message: Message):
  try:
    await message.answer("Вот Ваш гайд на Антистресс-протокол" )
    await bot.send_document("../guides/СТРЕССГАЙД.pdf")
    logger.info(f"Успешно отправлен гайд СТРЕСС для user_id={message.from_user.id}")
  except Exception as e:
    logger.error(f"Ошибка при отправке гайда СТРЕСС для user_id={message.from_user.id}: {e}")


@code_words_router.message(F.text == "ЗАВТРАК")
async def breakfast_word(message: Message):
  logger.info(f"Пользователь {message.from_user.id} запросил гайд ЗАВТРАК")
  try:

    keyboard = buy_guide_keyboard(url="#!")

    await message.answer("Хочешь, чтобы утро наконец перестало начинаться с кофе и крошек?\n\n" \
    "Гайд «Полезные завтраки» — это практическое руководство для занятых людей, которые хотят наладить утреннее питание без каши в голове (и на тарелке).\n\n" \
    "Внутри:\n\n" \
    "формулы сбалансированного завтрака,\n\n" \
    "20+ быстрых рецептов,\n\n" \
    "схемы заготовки на неделю,\n\n" \
    "лайфхаки против утреннего голода и переедания вечером.\n\n\n" \
    "Если хочешь перестать хаотично есть по утрам и научиться насыщаться — этот гайд для тебя.", reply_markup=keyboard)
  except Exception as e:
    logger.error(f"Ошибка при отправке гайда ЗАВТРАКИ для user_id={message.from_user.id}: {e}")


@code_words_router.message(F.text == "КУХНЯ")
async def kitchen_word(message: Message):
  logger.info(f"Пользователь {message.from_user.id} запросил гайд КУХНЯ")
  try:
    keyboard = buy_guide_keyboard(url="#!")
    await message.answer("Гайд «Безопасная кухня» — это инструкция для тех, кто хочет готовить вкусно и жить подольше.\n\n" \
    "Разберёмся:\n\n" \
    "какую посуду стоит выкинуть прямо сейчас,\n\n" \
    "как не вырастить цивилизацию в холодильнике,\n\n" \
    "что можно замораживать, а что превратится в болотную слизь,\n\n" \
    "как не отправить гостей в больницу из-за аллергенов или бактерий.\n\n\n" \
    "Внутри — честные факты, инструкции, лайфхаки и немного чёрного юмора. Если хочешь быть не просто кулинаром, а адекватным хозяином своей кухни — это то, с чего стоит начать.", reply_markup=keyboard)
  except Exception as e:
    logger.error(f"Ошибка при отправке гайдв КУХНЯ для user_id={message.from_user.id}: {e}")


@code_words_router.message(F.text == "ПЕРЕЕДАЮ")
async def overeating_word(message: Message):
  logger.info(f"Пользователь {message.from_user.id} запросил гайд ПЕРЕЕДАЮ")
  try:
    keyboard = buy_guide_keyboard(url="#!")
    await message.answer("Этот гайд — для тех, кто днём «держится», а вечером съедает всё, что не прикручено к полу.\n\n" \
    "Мы не будем ругать тебя за слабую силу воли. Вместо этого:\n\n" \
    "разберём психологические и физиологические причины вечерних срывов,\n\n" \
    "покажем 3 сценария переедания и как их распознать,\n\n" \
    "дадим систему выхода без морали и самобичевания.\n\n\n" \
    "Если ты устал(а) начинать «новую жизнь с понедельника» и хочешь простых, но работающих шагов — загляни в гайд.", reply_markup=keyboard)
  except Exception as e:
    logger.error(f"Ошибка при отправке гайдв ПЕРЕЕДАЮ для user_id={message.from_user.id}: {e}")



@code_words_router.message(F.text == "АППЕТИТ")
async def appetite_word(message: Message):
  logger.info(f"Пользователь {message.from_user.id} запросил гайд АППЕТИТ")
  try:
    keyboard = buy_guide_keyboard(url="#!")
    await message.answer("Если еда стала компаньоном, утешением, наградой и поводом для вины — этот гайд для тебя.\n\n" \
    "Мы мягко, но точно:\n\n" \
    "разберёмся, где эмоциональный голод, а где настоящий,\n\n" \
    "посмотрим на гормоны (грейлин, лептин, инсулин),\n\n" \
    "выстроим режим, который регулирует аппетит,\n\n" \
    "научимся выбирать еду без запретов и откатов.\n\n\n" \
    "Гайд поможет тебе перестать жить от срыва до срыва и вернуть себе ощущение, что ты — у руля.", reply_markup=keyboard)
  except Exception as e:
    logger.error(f"Ошибка при отправке гайдв АППЕТИТ для user_id={message.from_user.id}: {e}")



@code_words_router.message(F.text == "ДЕФИЦИТ")
async def deficit_word(message: Message):
  logger.info(f"Пользователь {message.from_user.id} запросил гайд ДЕФИЦИТ")
  try:
    keyboard = buy_guide_keyboard(url="#!")
    await message.answer("Ты вроде бы питаешься нормально, но сил нет, волосы сыпятся, настроение скачет и витаминки из аптеки не помогают?\n\n" \
    "Гайд «Питание при дефицитах» — это чек-лист и навигатор по теме нутриентов. Без рекламы БАДов и бреда.\n\n" \
    "Внутри:\n\n" \
    "на что указывают симптомы (усталость, выпадение волос, тяга к сладкому),\n\n" \
    "с чего начинать — питание или анализы,\n\n" \
    "как не навредить себе «самолечением».\n\n\n" \
    "Если хочешь перестать гадать и начать понимать — этот гайд поможет выстроить уверенность в питании.", reply_markup=keyboard)
  except Exception as e:
    logger.error(f"Ошибка при отправке гайдв АППЕТИТ для user_id={message.from_user.id}: {e}")