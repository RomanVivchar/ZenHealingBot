from aiogram.utils.keyboard import InlineKeyboardBuilder



def buy_guide_keyboard(url: str, button_text: str = "Купить PDF"):
  builder = InlineKeyboardBuilder()
  builder.button(
    text=button_text,
    url=url
  )
  return builder.as_markup()