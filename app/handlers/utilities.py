from aiogram import Bot
from aiogram import types
from aiogram.types import FSInputFile


async def send_pdf_document(chat_id: str, message: types.Message, pdf_file_path: str, bot: Bot):
    try:
        # Используем FSInputFile для работы с локальными файлами
        # aiogram сам откроет файл в бинарном режиме и закроет его после отправки
        pdf_document = FSInputFile(pdf_file_path)

        # Отправляем документ
        # message.chat.id - ID чата, куда отправляем (чат, откуда пришла команда)
        await bot.send_document(
            chat_id=chat_id,
            document=pdf_document, # Передаем объект файла
            caption="Вот ваш PDF-гайд!" # Опционально: добавить подпись к файлу
        )
        print(f"PDF файл {pdf_file_path} успешно отправлен в чат {message.chat.id}")

    except FileNotFoundError:
        await message.answer(f"Ошибка: Файл {pdf_file_path} не найден.")
        print(f"Ошибка: Файл {pdf_file_path} не найден.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при отправке файла: {e}")
        print(f"Ошибка при отправке файла: {e}")

