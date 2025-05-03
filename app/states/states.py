from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.callback_data import CallbackData

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
    "anxiety_pms_irritability": "Тревожность / ПМС / раздражительность",
    "fatigue_bloating": "Усталость после еды / вздутие",
    "sugar_craving_overeating": "Тяга к сладкому / переедание вечером",
    "all_at_once": "Всё сразу",
    "none_of_these": "Ничего из этого"
}

# Уникальные ключи для "исключающих" вариантов
EXCLUSIVE_OPTIONS = {"all_at_once", "none_of_these"}