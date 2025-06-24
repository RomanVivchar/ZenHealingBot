from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup


class Quiz(StatesGroup):
    energy_morning = State()
    breakfast_habit = State()
    symptoms = State()
    intention = State()
    offer = State()


class SymptomCallback(CallbackData, prefix="sym_opt"):
    key: str


class SymptomDoneCallback(CallbackData, prefix="sym_done"):
    pass


# Словарь, связывающий ключи с текстом вариантов для кнопок
SYMPTOM_OPTIONS = {
    "sugar_craving": "Тяга к сладкому ",
    "hair_loss": "Выпадение волос / ломкие ногти",
    "skin_problems": "Проблемы с кожей",
    "mood_swings": "Перепады настроения",
    "sleep_disorders": "Нарушения сна",
    "often_overeating": "Частые переедания",
    "all_at_once": "Всё сразу",
    "none_of_these": "Ничего из этого",
}

# Уникальные ключи для "исключающих" вариантов
EXCLUSIVE_OPTIONS = {"all_at_once", "none_of_these"}


SCENARIO_RATING = {"consultation": 4, "deficits": 3, "overeating": 2, "breakfast": 1}
