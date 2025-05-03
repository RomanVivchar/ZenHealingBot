import asyncio
import sys
import logging
from aiogram import Dispatcher, F, types, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from ..keyboards.inline import (start_keyboard, book_consultation, energy_morning_kb, breakfast_kb, build_symptoms_keyboard, intention_kb, build_scenario_1_keyboard, build_scenario_2_keyboard, build_scenario_3_keyboard)
from ..handlers.utilities import send_pdf_document
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from ..states.states import Quiz, SymptomCallback, SymptomDoneCallback, SYMPTOM_OPTIONS, EXCLUSIVE_OPTIONS
from ..config.bot_instance import bot


common_router = Router(name="common-handlers")
log = logging.getLogger(__name__)



@common_router.message(CommandStart())
async def handle_start(message: Message):
  await message.answer("Привет!\nЯ — ZenHealingBot. Помогаю тем, кто устал жить на автопилоте, бороться с телом или просто не понимает, куда утекает энергия.\n\n" \
  "Здесь ты можешь пройти мини-диагностику, получить гайд или записаться на консультацию.\n\n" \
  "Без диет. Без давления. С уважением к твоему состоянию.\n\n" \
  "С чего начнём?", reply_markup=start_keyboard)


  await message.answer("Кстати, Вы можете писать кодовые слова - и я сразу подскажу, что поможет:\n\n" \
  "\n - СТРЕСС → Антистресс-протокол (бесплатно)" \
  "\n - ЗАВТРАК → Полезные завтраки" \
  "\n - КУХНЯ → Безопасная кухня" \
  "\n - ПЕРЕЕДАЮ → Как перестать переедать вечером" \
  "\n - АППЕТИТ → Аппетит под контролем" \
  "\n - ДЕФИЦИТ → Питание при дефицитах")


#? Добавить справку или нет
@common_router.message(Command("help"))
async def handle_help(message: Message):
  await message.answer("Здесь появится справка о боте")


@common_router.callback_query(F.data == "diagnostics")
async def diagnostics_energy(callback: CallbackQuery, state: FSMContext):
   await callback.answer()
   await state.set_state(Quiz.energy_morning)
   await callback.message.answer("Как часто ты просыпаешься с ощущением бодрости?", reply_markup=energy_morning_kb)
  

@common_router.callback_query(StateFilter(Quiz.energy_morning))
async def diagnostics_breakfast(callback: CallbackQuery, state: FSMContext):
   await callback.answer()
   await state.set_state(Quiz.breakfast_habit)
   energy_morning_answer = callback.data
   await state.update_data(energy_morning_answer=energy_morning_answer)

   await callback.message.edit_text("Что у тебя обычно на завтрак?", reply_markup=breakfast_kb)
   
   

@common_router.callback_query(StateFilter(Quiz.breakfast_habit))
async def diagnostics_symptoms(callback: CallbackQuery, state: FSMContext):
   await callback.answer()
   await state.set_state(Quiz.symptoms)
   breakfast_habit_answer = callback.data
   await state.update_data(breakfast_habit_answer=breakfast_habit_answer)

   keyboard = build_symptoms_keyboard(selected_keys=[])
   await callback.message.edit_text("Какие состояния тебе знакомы?", reply_markup=keyboard)

@common_router.callback_query(SymptomCallback.filter(), StateFilter(Quiz.symptoms))
async def process_symptom_selection(
   callback: CallbackQuery,
   callback_data: SymptomCallback,
   state: FSMContext
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
        standard_symptom_keys = [key for key in final_selections_keys if key not in EXCLUSIVE_OPTIONS]
        symptom_counter = len(standard_symptom_keys)
        is_all_at_once_flag = False

    print(f"Окончательный выбор симптомов (ключи): {final_selections_keys}")
    print(f"Подсчет стандартных симптомов: {symptom_counter}")
    print(f"Флаг 'Всё сразу': {is_all_at_once_flag}")

    # --- Сохраняем окончательные обработанные данные в FSM контекст или базу данных ---
    # Например, сохраним в FSM контекст для следующего шага
    await state.update_data(
        symptoms_selected_keys=final_selections_keys, # Можно сохранить сами ключи
        symptoms_count=symptom_counter,
        symptoms_all_flag=is_all_at_once_flag
    )
    # Теперь эти данные будут доступны на следующем шаге опроса

    # Или сохраняем в базу данных здесь

    # -------------------------------------------------------------------------------

    # --- Переходим к следующему шагу опроса или завершаем его ---
    await callback.message.edit_text("Какой подход тебе ближе прямо сейчас?", reply_markup=intention_kb)

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
   symptoms_count = quiz_results.get("symptoms_count_answer")
   user_intention = quiz_results.get("intention_answer")
   symptoms_all_flag = quiz_results.get("symptoms_all_flag")
   symptoms_selected_keys = quiz_results.get("symptoms_selected_keys", []) # Получаем и ключи выбранных симптомов


    # --- Логика определения сценария ---
   scenario = None # Переменная для номера сценария
   final_message_text = ""
   final_keyboard = None # Переменная для финальной клавиатуры


   # Пример упорядоченной логики:
   if "none_of_these" in symptoms_selected_keys: # Если выбрано "Ничего из этого"
        scenario = 1 # Сценарий 1: PDF гайд
        final_message_text = "Начни с гайда “Завтрак без хаоса”.\nЭто лёгкий старт, чтобы восстановить утреннюю энергию без сахара и кофе на голодный желудок.\n\n" \
        "Или просто напиши в чат, что тебя волнует — СТРЕСС, ПЕРЕЕДАЮ, ДЕФИЦИТ, КУХНЯ — и я покажу нужный гайд."
        # Клавиатура для этого сценария может быть простой (например, кнопка "В главное меню") или пустой, если файл отправляется сразу.
        final_keyboard = build_scenario_1_keyboard() # Функция, которую мы обсуждали ранее

   elif user_intention == "Рекомендации": # Если явно выбрано намерение "Рекомендации" (перекрывает другие условия, если нужно)
        scenario = 1 # Сценарий 1: PDF гайд
        final_message_text = "Начни с гайда “Завтрак без хаоса”.\nЭто лёгкий старт, чтобы восстановить утреннюю энергию без сахара и кофе на голодный желудок.\n\n" \
        "Или просто напиши в чат, что тебя волнует — СТРЕСС, ПЕРЕЕДАЮ, ДЕФИЦИТ, КУХНЯ — и я покажу нужный гайд."
        final_keyboard = build_scenario_1_keyboard()

   elif "all_at_once" in symptoms_selected_keys: # Если выбрано "Всё сразу"
       scenario = 3 # Сценарий 3: Персональное сопровождение
       final_message_text = "Твоё тело давно сигналит.\nМесячное сопровождение — это 4 сессии, поддержка и корректировки.\nЧтобы не метаться, а идти шаг за шагом."
       final_keyboard = build_scenario_3_keyboard() # Функция, которую мы обсуждали

   elif user_intention == "Сопровождение": # Если явно выбрано намерение "Сопровождение"
       scenario = 3 # Сценарий 3: Персональное сопровождение
       final_message_text = "Твоё тело давно сигналит.\nМесячное сопровождение — это 4 сессии, поддержка и корректировки.\nЧтобы не метаться, а идти шаг за шагом."
       final_keyboard = build_scenario_3_keyboard()

   elif user_intention == "Помощь": # Если явно выбрано намерение "Помощь"
       scenario = 2 # Сценарий 2: Консультация
       final_message_text = "Похоже, дело не только в питании.\nКонсультация — это разбор питания, симптомов, режима и образа жизни. Без шаблонов, под твою ситуацию.\n\n" \
       "Или напиши в чат — СТРЕСС, ПЕРЕЕДАЮ, АППЕТИТ — и я помогу с выбором подхода."
       final_keyboard = build_scenario_2_keyboard() # Функция, которую мы обсуждали

   elif symptoms_count >= 2: # Если симптомов 2 или 3 (и не попали в предыдущие более специфичные условия)
       scenario = 2 # Сценарий 2: Консультация
       final_message_text = "Похоже, дело не только в питании.\nКонсультация — это разбор питания, симптомов, режима и образа жизни. Без шаблонов, под твою ситуацию.\n\n" \
       "Или напиши в чат — СТРЕСС, ПЕРЕЕДАЮ, АППЕТИТ — и я помогу с выбором подхода."
       final_keyboard = build_scenario_2_keyboard()

   else: # Остальные случаи (например, симптомов 0 или 1, намерение не указано или не попало в условия выше)
        scenario = 1 # Сценарий 1: PDF гайд (fallback)
        final_message_text = "Начни с гайда “Завтрак без хаоса”.\nЭто лёгкий старт, чтобы восстановить утреннюю энергию без сахара и кофе на голодный желудок.\n\n" \
        "Или просто напиши в чат, что тебя волнует — СТРЕСС, ПЕРЕЕДАЮ, ДЕФИЦИТ, КУХНЯ — и я покажу нужный гайд."
        final_keyboard = build_scenario_1_keyboard()


   # --- Выполняем действие и отправляем финальное сообщение ---
   # В этом же обработчике нужно отправить результат пользователю
   # Например, отправить PDF или сообщение с кнопками сценария.

   chat_id_to_send = callback.message.chat.id # ID чата, куда отправлять

   if scenario == 1:
       # Сценарий 1: Отправка PDF гайда.
       # Отправь сначала текстовое сообщение, а потом файл.
       await callback.message.edit_text("Спасибо за прохождение диагностики!")
       await bot.send_message(chat_id_to_send, final_message_text, reply_markup=final_keyboard) # Или bot.send_message
       # Здесь вызови функцию, которая отправляет PDF файл (как мы разбирали ранее)
       await send_pdf_document(chat_id=chat_id_to_send, pdf_file_path="../guides/ЗАВТРАКГАЙД.pdf", bot=bot)


   elif scenario in [2, 3]:
       await callback.message.answer( # Или bot.send_message
           text=final_message_text,
           reply_markup=final_keyboard # Отправляем соответствующую клавиатуру
       )


   



@common_router.callback_query(F.data == "free_guide")
async def free_guide(callback: CallbackQuery, bot=bot): # Добавляем bot: Bot, если он не глобальный
    
    pdf_file_path = "./guides/СТРЕССГАЙД.pdf" 

    
    await callback.answer("Отправляю гайд...")

    try:
        pdf_document = FSInputFile(pdf_file_path)

        await callback.message.answer("Забирай бесплатный гайд на антистресс-протокол:")

        await bot.send_document(
            chat_id=callback.message.chat.id, # Берем chat_id из сообщения, связанного с колбэком
            document=pdf_document,
            caption="Надеюсь, он будет полезен!" # Опционально: добавить подпись
        )
        print(f"PDF файл {pdf_file_path} успешно отправлен в чат {callback.message.chat.id} по колбэку free_quide")


    except FileNotFoundError:
        # Отправляем сообщение об ошибке в чат
        await callback.message.answer("Ошибка: Файл гайда не найден на сервере.")
        print(f"Ошибка: Файл {pdf_file_path} не найден.")

    except Exception as e:
        # Отправляем сообщение об ошибке в чат
        await callback.message.answer(f"Произошла ошибка при отправке гайда: {e}")
        print(f"Ошибка при отправке гайда: {e}")



# TODO: Добавить инфо о консультации
@common_router.callback_query(F.data == "about_consultation")
async def about_consultation(callback: CallbackQuery):
  await callback.answer()
  try:
    await callback.message.answer("Здесь появится информация о консультации", reply_markup=book_consultation)
  except Exception as e:
     log.error(f"Ошибка {e}")
     

# TODO: Добавить линк на лендинг
@common_router.callback_query(F.data == "just_read")
async def just_read(callback: CallbackQuery):
  await callback.answer()
  await callback.message.answer("- Линк на лендинг (каталог гайдов)" \
  "\n- Telegram-канал: https://t.me/eatwithoutstress" \
  "\n- Instagram: https://www.instagram.com/healthy_oks")
