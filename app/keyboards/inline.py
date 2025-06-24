from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from ..states.states import (
    EXCLUSIVE_OPTIONS,
    SYMPTOM_OPTIONS,
    SymptomCallback,
    SymptomDoneCallback,
)


def buy_guide_keyboard(url: str, button_text: str = "Купить PDF"):
    builder = InlineKeyboardBuilder()
    builder.button(text=button_text, url=url)
    return builder.as_markup()


def build_symptoms_keyboard(selected_keys: list[str]) -> InlineKeyboardBuilder:

    builder = InlineKeyboardBuilder()

    for key, text in SYMPTOM_OPTIONS.items():

        button_text = f"{'✅ ' if key in selected_keys else ' '}{text}"
        builder.button(text=button_text, callback_data=SymptomCallback(key=key))

    builder.button(text="Готово", callback_data=SymptomDoneCallback())

    builder.adjust(1)
    return builder.as_markup()


start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Пройти мини-диагностику", callback_data="diagnostics"
            )
        ],
        [InlineKeyboardButton(text="Скачать гайд", callback_data="free_guide")],
        [
            InlineKeyboardButton(
                text="О консультации", callback_data="about_consultation"
            )
        ],
        [InlineKeyboardButton(text="Просто почитать", callback_data="just_read")],
    ]
)


energy_morning_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Почти всегда", callback_data="Всегда")],
        [InlineKeyboardButton(text="Иногда", callback_data="Иногда")],
        [InlineKeyboardButton(text="Почти никогда", callback_data="Никогда")],
    ]
)

breakfast_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Только кофе / ничего", callback_data="Незавтрак")],
        [
            InlineKeyboardButton(
                text="Сладкая выпечка / бутерброды", callback_data="Перекус"
            )
        ],
        [
            InlineKeyboardButton(
                text="Полноценный завтрак", callback_data="Полноценный завтрак"
            )
        ],
    ]
)

intention_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Восстановить энергию", callback_data="Энергия")],
        [InlineKeyboardButton(text="Перестать переедать", callback_data="Переедание")],
        [InlineKeyboardButton(text="Выстроить завтрак", callback_data="Завтрак")],
        [
            InlineKeyboardButton(
                text="Разобраться с дефицитами", callback_data="Дефициты"
            )
        ],
        [
            InlineKeyboardButton(
                text="Просто почитать / пока не знаю", callback_data="Незнаю"
            )
        ],
    ]
)


def build_scenario_deficits_keyboard():
    # * Клавиатура для выдачи гайда "Питание при дефицитах"
    builder = InlineKeyboardBuilder()
    builder.button(text="📥 Получить гайд", callback_data="deficit_guide")
    builder.button(
        text="🗓 Записаться на консультацию", callback_data="about_consultation"
    )
    builder.button(text="🔁 Вернуться в меню", callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()


def build_scenario_consultation_keyboard():
    # * Клавиатура для консультации
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Что входит в консультацию❔", callback_data="about_consultation"
    )
    builder.button(
        text="🗓 Записаться на консультацию", callback_data="https://t.me/sharkova"
    )  # TODO: добавить тгшку
    builder.button(text="🔁 Вернуться в меню", callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()


def build_scenario_overeating_keyboard():
    # * Клавиатура для выдачи гайда "Как перестать переедать вечером"
    builder = InlineKeyboardBuilder()
    builder.button(text="📥 Получить гайд", callback_data="overeating_guide")
    builder.button(
        text="🗓 Записаться на консультацию", callback_data="about_consultation"
    )
    builder.button(text="🔁 Вернуться в меню", callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()


def build_scenario_breakfast_keyboard():
    # * Клавиатура для выдачи гайда "Завтрак без хаоса"
    builder = InlineKeyboardBuilder()
    builder.button(text="📥 Получить гайд", callback_data="breakfast_guide")
    builder.button(
        text="🗓 Записаться на консультацию", callback_data="about_consultation"
    )
    builder.button(text="🔁 Вернуться в меню", callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()


def build_book_consultation_keyboard():
    # * Клавиатура для консультации
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🗓 Записаться на консультацию", callback_data="https://t.me/sharkova"
    )  # TODO: добавить тгшку
    builder.button(text="🔁 Вернуться в меню", callback_data="main_menu")

    builder.adjust(1)

    return builder.as_markup()
