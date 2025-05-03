from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from ..states.states import SymptomCallback, SymptomDoneCallback, SYMPTOM_OPTIONS, EXCLUSIVE_OPTIONS


def buy_guide_keyboard(url: str, button_text: str = "Купить PDF"):
  builder = InlineKeyboardBuilder()
  builder.button(
    text=button_text,
    url=url
  )
  return builder.as_markup()


def build_symptoms_keyboard(selected_keys: list[str]) -> InlineKeyboardBuilder:

  builder = InlineKeyboardBuilder()

  for key, text in SYMPTOM_OPTIONS.items():
    button_text = f"{'✅ ' if key in selected_keys else ' '}{text}"
    builder.button(
      text=button_text,
      callback_data=SymptomCallback(key=key)
    )

    builder.button(text="Готово", callback_data=SymptomDoneCallback())

    builder.adjust(1)
    return builder.as_markup()




start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
  [InlineKeyboardButton(text="Пройти мини-диагностику", callback_data="diagnostics")],
  [InlineKeyboardButton(text="Скачать гайд", callback_data="free_guide")],
  [InlineKeyboardButton(text="О консультации", callback_data="about_consultation")],
  [InlineKeyboardButton(text="Просто почитать", callback_data="just_read")]
])

# TODO: Изменить тг на Оксаны
book_consultation = InlineKeyboardMarkup(inline_keyboard=[
  [InlineKeyboardButton(text="Записаться на консультацию", url="https://t.me/")]
])


energy_morning_kb = InlineKeyboardMarkup(inline_keyboard=[
  [InlineKeyboardButton(text="Почти никогда", callback_data="Никогда")],
  [InlineKeyboardButton(text="Иногда, но быстро уходит", callback_data="Иногда")],
  [InlineKeyboardButton(text="Почти всегда, но к вечеру «сдуваюсь»", callback_data="Иногда")],
  [InlineKeyboardButton(text="Все нормально, просто хочу разобраться", callback_data="Нормально")]
])

breakfast_kb = InlineKeyboardMarkup(inline_keyboard=[
  [InlineKeyboardButton(text="Я не завтракаю", callback_data="Незавтрак")],
  [InlineKeyboardButton(text="Кофе / перекус «на бегу»", callback_data="Перекус")],
  [InlineKeyboardButton(text="Ем «потому что надо», но аппетита нет", callback_data="Надоесть")],
  [InlineKeyboardButton(text="Полноценный завтрак, но не чувствую насыщения", callback_data="Полныйзавтрак")]
])

intention_kb = InlineKeyboardMarkup(inline_keyboard=[
  [InlineKeyboardButton(text="Хочу просто рекомендации", callback_data="Рекомендации")],
  [InlineKeyboardButton(text="Нужна помощь: чувствую, что не справляюсь", callback_data="Помощь")],
  [InlineKeyboardButton(text="Хочу двигаться под сопровождением", callback_data="Сопровождение")],
  [InlineKeyboardButton(text="Пока не знаю - просто хочу посмотреть", callback_data="Незнаю")]
])



def build_scenario_1_keyboard():
  #* Клавиатура для выдачи гайда
  builder = InlineKeyboardBuilder()
  builder.button(text="О консультации", callback_data="about_consultation")
  builder.button(text="Подписаться на каналы", callback_data="just_read")

  builder.adjust(1)
  
  return builder.as_markup()

def build_scenario_2_keyboard():
  #* Клавиатура для консультации
  builder = InlineKeyboardBuilder()
  builder.button(text="Что входит в консультацию", callback_data="about_consultation")
  builder.button(text="Записаться", callback_data="https://t.me/ ") # TODO: добавить тгшку
  builder.button(text="Скачать гайд пока", callback_data="download_free_guide")

  builder.adjust(1)

  return builder.as_markup()

def build_scenario_3_keyboard():
  #* Клавиатура для сопровождения
  builder = InlineKeyboardBuilder()
  builder.button(text="Узнать подробнее", callback_data="about_support")
  builder.button(text="оставить заявку", callback_data="book_support")
  builder.button(text="Начать с консультации", callback_data="about_consultation")

  builder.adjust(1)

  return builder.as_markup()