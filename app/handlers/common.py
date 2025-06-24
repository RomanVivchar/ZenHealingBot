import asyncio
import datetime
import logging
import sys

from aiogram import Dispatcher, F, Router, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, FSInputFile, Message
from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from ..config.bot_instance import bot
from ..db.database import AsyncSessionLocal
from ..db.models import User
from ..handlers.utilities import send_pdf_document
from ..keyboards.inline import (
    breakfast_kb,
    build_book_consultation_keyboard,
    build_scenario_breakfast_keyboard,
    build_scenario_consultation_keyboard,
    build_scenario_deficits_keyboard,
    build_scenario_overeating_keyboard,
    build_symptoms_keyboard,
    energy_morning_kb,
    intention_kb,
    start_keyboard,
)
from ..states.states import (
    EXCLUSIVE_OPTIONS,
    SCENARIO_RATING,
    SYMPTOM_OPTIONS,
    Quiz,
    SymptomCallback,
    SymptomDoneCallback,
)

common_router = Router(name="common-handlers")
log = logging.getLogger(__name__)


@common_router.message(CommandStart())
async def handle_start(message: Message):

    user_id = message.from_user.id
    last_interaction = datetime.datetime.now(datetime.timezone.utc)

    async with AsyncSessionLocal() as session:
        try:
            values = {"user_id": user_id, "last_interaction": last_interaction}

            #   insert_stmt = insert(User).values(user_id=user_id, last_interaction=last_interaction)
            #   on_conflict_stmt=insert_stmt.on_conflict_do_update(index_elements=[User.user_id], set={User.last_interaction: datetime.datetime.now(datetime.timezone.utc)})

            user = User(user_id=user_id, last_interaction=last_interaction)
            #   await session.add(user)
            #   await session.flush()

            await session.execute(
                text(
                    f"INSERT INTO public.users (user_id, last_interaction) VALUES ({user_id}, '{last_interaction}')"
                )
            )

            await session.commit()

            await message.answer(
                "Привет! 👋\nЯ — ZenHealingBot. 🌱 Помогаю тем, кто устал жить на автопилоте 😴, бороться с телом 💪 или просто не понимает, куда утекает энергия. ⚡️\n\n"
                "Здесь ты можешь пройти мини-диагностику 🔍, получить гайд 📚 или записаться на консультацию. 🗓️\n\n"
                "Без диет. Без давления. С уважением к твоему состоянию. ✨\n\n"
                "С чего начнём?👇",
                reply_markup=start_keyboard,
            )

            await message.answer(
                "Кстати, Вы можете писать кодовые слова - и я сразу подскажу, что поможет:\n\n"
                "\n - СТРЕСС → Антистресс-протокол (бесплатно)"
                "\n - ЗАВТРАК → Полезные завтраки"
                "\n - КУХНЯ → Безопасная кухня"
                "\n - ПЕРЕЕДАЮ → Как перестать переедать вечером"
                "\n - АППЕТИТ → Аппетит под контролем"
                "\n - ДЕФИЦИТ → Питание при дефицитах"
            )

            log.info("Пользователь: %s добавлен или обновлен в БД.", user_id)
        except SQLAlchemyError as e:
            log.error(
                f"Ошибка при работе с БД для пользователя {user_id}: {e}", exc_info=True
            )
            await message.answer(
                "Произошла ошибка при обработке вашего запроса. Попробуйте позже"
            )

        except Exception as e:
            log.error(
                f"Неожиданная ошибка при обработке /start для пользователя {user_id}: {e}",
                exc_info=True,
            )
            await message.answer(
                "Произошла ошибка при обработке вашего запроса. Попробуйте позже"
            )


@common_router.callback_query(F.data == "main_menu", Command("menu"))
async def main_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🏠 Главное меню\n\n"
        "Вы можете писать кодовые слова - и я сразу подскажу, что поможет:\n\n"
        "\n - СТРЕСС → Антистресс-протокол (бесплатно)"
        "\n - ЗАВТРАК → Полезные завтраки"
        "\n - КУХНЯ → Безопасная кухня"
        "\n - ПЕРЕЕДАЮ → Как перестать переедать вечером"
        "\n - АППЕТИТ → Аппетит под контролем"
        "\n - ДЕФИЦИТ → Питание при дефицитах",
        reply_markup=start_keyboard,
    )


# ? Добавить справку или нет
@common_router.message(Command("help"))
async def handle_help(message: Message):
    await message.answer("Здесь появится справка о боте")


@common_router.callback_query(F.data == "diagnostics")
async def diagnostics_energy(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Quiz.energy_morning)
    await callback.message.answer(
        "Как часто ты чувствуешь усталость по утрам?", reply_markup=energy_morning_kb
    )


@common_router.callback_query(StateFilter(Quiz.energy_morning))
async def diagnostics_breakfast(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Quiz.breakfast_habit)
    energy_morning_answer = callback.data
    await state.update_data(energy_morning_answer=energy_morning_answer)

    await callback.message.edit_text(
        "Что чаще всего бывает у тебя на завтрак?", reply_markup=breakfast_kb
    )


@common_router.callback_query(StateFilter(Quiz.breakfast_habit))
async def diagnostics_symptoms(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Quiz.symptoms)
    breakfast_habit_answer = callback.data
    await state.update_data(breakfast_habit_answer=breakfast_habit_answer)

    keyboard = build_symptoms_keyboard(selected_keys=[])
    await callback.message.edit_text(
        "Какие из симптомов тебе знакомы?", reply_markup=keyboard
    )


@common_router.callback_query(SymptomCallback.filter(), StateFilter(Quiz.symptoms))
async def process_symptom_selection(
    callback: CallbackQuery, callback_data: SymptomCallback, state: FSMContext
):
    await callback.answer()

    symptom_key = callback_data.key

    # Получаем текущий список выбранных ключей из FSM контекста
    # Если список еще не существует, по умолчанию используем пустой список
    data = await state.get_data()
    selected_symptoms = data.get("selected_symptoms", [])

    # --- Логика добавления/удаления выбора и обработки исключающих вариантов ---
    if symptom_key in selected_symptoms:
        # Если вариант УЖЕ был выбран - снимаем выбор
        selected_symptoms.remove(symptom_key)
    else:
        # Если вариант НЕ был выбран - добавляем его

        # Сначала обрабатываем исключающие варианты ("Всё сразу", "Ничего из этого")
        if symptom_key in EXCLUSIVE_OPTIONS:
            # Если выбран исключающий вариант, то сбрасываем все остальные
            selected_symptoms = [symptom_key]
        elif any(key in selected_symptoms for key in EXCLUSIVE_OPTIONS):
            # Если уже был выбран один из исключающих вариантов,
            # а пользователь выбрал обычный симптом, то сбрасываем исключающий и добавляем этот
            selected_symptoms = [symptom_key]
        else:
            # Иначе просто добавляем новый вариант
            selected_symptoms.append(symptom_key)

    # --- Обновляем данные в FSM контексте ---
    await state.update_data(selected_symptoms=selected_symptoms)
    # ---------------------------------------

    # --- Редактируем сообщение с обновленной клавиатурой ---
    # Пересоздаем клавиатуру с учетом нового списка выбранных вариантов
    updated_keyboard = build_symptoms_keyboard(selected_symptoms)

    # Редактируем сообщение
    # Убедись, что callback.message доступен (для inline кнопок он всегда есть)
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=updated_keyboard)


# --- Хендлер для обработки нажатия на кнопку "Готово" ---
# Этот хендлер сработает только на кнопку с callback_data типа SymptomsDoneCallback
@common_router.callback_query(SymptomDoneCallback.filter(), StateFilter(Quiz.symptoms))
async def process_symptoms_done(callback: types.CallbackQuery, state: FSMContext):
    # Ответь на колбэк кнопки "Готово"
    await callback.answer("Выбор симптомов завершен.")

    # --- Получаем окончательные данные о выбранных симптомах ---
    data = await state.get_data()
    final_selections_keys = data.get("selected_symptoms", [])
    # -------------------------------------------------------

    # --- Твоя логика подсчета и определения флага "всё сразу" ---
    symptom_counter = 0
    is_all_at_once_flag = False

    if "all_at_once" in final_selections_keys:
        is_all_at_once_flag = True
        # Если "Всё сразу" выбрано, счетчик может быть равен общему количеству стандартных симптомов
        # Или просто использовать флаг и не считать, зависит от твоей дальнейшей логики
        # symptom_counter = len(SYMPTOM_OPTIONS) - len(EXCLUSIVE_OPTIONS) # Количество стандартных вариантов
    elif "none_of_these" in final_selections_keys:
        symptom_counter = 0
        is_all_at_once_flag = False
    else:
        # Считаем количество выбранных стандартных симптомов
        standard_symptom_keys = [
            key for key in final_selections_keys if key not in EXCLUSIVE_OPTIONS
        ]
        symptom_counter = len(standard_symptom_keys)
        is_all_at_once_flag = False

    print(f"Окончательный выбор симптомов (ключи): {final_selections_keys}")
    print(f"Подсчет стандартных симптомов: {symptom_counter}")
    print(f"Флаг 'Всё сразу': {is_all_at_once_flag}")

    # --- Сохраняем окончательные обработанные данные в FSM контекст или базу данных ---
    # Например, сохраним в FSM контекст для следующего шага
    await state.update_data(
        symptoms_selected_keys=final_selections_keys,  # Можно сохранить сами ключи
        symptoms_count=symptom_counter,
        symptoms_all_flag=is_all_at_once_flag,
    )
    # Теперь эти данные будут доступны на следующем шаге опроса

    # Или сохраняем в базу данных здесь

    # -------------------------------------------------------------------------------

    # --- Переходим к следующему шагу опроса или завершаем его ---
    await callback.message.edit_text(
        "Чего ты хочешь прямо сейчас?", reply_markup=intention_kb
    )

    # Переходим к следующему состоянию в FSM
    await state.set_state(Quiz.offer)
    # Или завершаем опрос:
    # await state.clear()


@common_router.callback_query(StateFilter(Quiz.offer))
async def offer(callback: CallbackQuery, state: FSMContext, bot=bot):

    await callback.answer()
    intention_answer = callback.data
    await state.update_data(intention_answer=intention_answer)

    quiz_results = await state.get_data()

    await state.clear()

    energy_morning = quiz_results.get("energy_morning_answer")
    breakfast_habit = quiz_results.get("breakfast_habit_answer")
    symptoms_count = quiz_results.get("symptoms_count")
    user_intention = quiz_results.get("intention_answer")
    symptoms_all_flag = quiz_results.get("symptoms_all_flag")
    symptoms_selected_keys = quiz_results.get(
        "symptoms_selected_keys", []
    )  # Получаем и ключи выбранных симптомов

    # --- Логика определения сценария ---
    rating = 0  # Переменная для номера сценария
    final_message_text = ""
    final_keyboard = None  # Переменная для финальной клавиатуры

    list_deficits = ["hair_loss", "skin_problems", "mood_swings", "sleep_disorders"]
    count_deficits = 0

    for el in list_deficits:
        if el in symptoms_selected_keys:
            count_deficits += 1

    # * Сценарий 1. Гайд "Питание при дефицитах"
    if user_intention == "Дефициты":
        rating = max(SCENARIO_RATING["deficits"], rating)
    elif energy_morning == "Всегда":
        rating = max(SCENARIO_RATING["deficits"], rating)
    elif count_deficits >= 2:
        rating = max(SCENARIO_RATING["deficits"], rating)

    list_overeating = ["often_overeating", "sugar_craving"]
    count_overeating = 0
    for el in list_overeating:
        if el in symptoms_selected_keys:
            count_overeating += 1

    # * Сценарий 2. Гайд "Как перестать переедать вечером"
    if user_intention == "Переедание":
        rating = max(SCENARIO_RATING["overeating"], rating)
    elif count_overeating >= 1:
        rating = max(SCENARIO_RATING["overeating"], rating)

    # * Сценарий 3. Гайд "Завтрак без хаоса"
    if user_intention == "Завтрак":
        rating = max(SCENARIO_RATING["breakfast"], rating)
    elif (
        energy_morning in ["Иногда", "Всегда"]
        and breakfast_habit != "Полноценный завтрак"
    ):
        rating = max(SCENARIO_RATING["breakfast"], rating)
    elif breakfast_habit in ["Незавтрак", "Перекус"]:
        rating = max(SCENARIO_RATING["breakfast"], rating)

    # * Сценарий 4. Индивидуальная консультация
    if symptoms_count >= 3:
        rating = max(SCENARIO_RATING["consultation"], rating)
    elif energy_morning == "Всегда":
        rating = max(SCENARIO_RATING["consultation"], rating)
    elif user_intention == "Незнаю":
        rating = max(SCENARIO_RATING["consultation"], rating)

    # * Выбор сообщения после определения сценария
    if rating == 4:  # Консультация
        final_message_text = (
            "Ты указал(а) несколько важных симптомов, и кажется, они связаны между собой."
            "Чтобы не гадать, рекомендую начать с индивидуальной консультации."
            "Мы разберём твою ситуацию, я помогу сориентироваться и подскажу, с чего точно стоит начать."
        )
        final_keyboard = build_scenario_consultation_keyboard
    elif rating == 3:  # Дефициты
        final_message_text = (
            "Похоже, твоё тело даёт сигналы о нехватке ресурсов."
            "Я рекомендую начать с гайда «Питание при дефицитах» "
            "— он поможет мягко восполнить пробелы и вернуть энергию."
        )
        final_keyboard = build_scenario_deficits_keyboard
    elif rating == 2:  # Переедания
        final_message_text = (
            " Похоже, сейчас важно наладить контакт с аппетитом и ритмом питания."
            "Начни с гайда «Как перестать переедать вечером»"
            " — он поможет тебе вернуть ощущение контроля и спокойствия."
        )
        final_keyboard = build_scenario_overeating_keyboard
    elif rating == 1:  # Завтрак
        final_message_text = (
            "Часто путь к энергии начинается с утра."
            "Я рекомендую гайд «Завтрак без хаоса» —"
            " он поможет тебе выстроить спокойный, "
            "сытный старт дня и вернуть ресурс."
        )
        final_keyboard = build_scenario_breakfast_keyboard

    # --- Выполняем действие и отправляем финальное сообщение ---
    # В этом же обработчике нужно отправить результат пользователю
    # Например, отправить PDF или сообщение с кнопками сценария.

    chat_id_to_send = callback.message.chat.id  # ID чата, куда отправлять

    await callback.message.edit_text("Спасибо за прохождение диагностики!")
    await bot.send_message(
        chat_id=chat_id_to_send, text=final_message_text, reply_markup=final_keyboard
    )


# TODO: Добавить инфо о консультации
@common_router.callback_query(F.data == "about_consultation")
async def about_consultation(callback: CallbackQuery):
    await callback.answer()
    try:
        await callback.message.answer(
            "Здесь появится информация о консультации",
            reply_markup=build_book_consultation_keyboard,
        )
    except Exception as e:
        log.error(f"Ошибка {e}")


# TODO: Добавить линк на лендинг
@common_router.callback_query(F.data == "just_read")
async def just_read(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "- Линк на лендинг (каталог гайдов)"
        "\n- Telegram-канал: https://t.me/eatwithoutstress"
        "\n- Instagram: https://www.instagram.com/healthy_oks"
    )
