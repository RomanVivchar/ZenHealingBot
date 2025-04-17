import logging
import sys
from logging.handlers import RotatingFileHandler # Используем ротацию файлов
import os
# --- Настройка основного логгера ---

log_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# --- Обработчик для вывода в консоль ---
console_handler = logging.StreamHandler(sys.stdout) 
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)

# --- Обработчик для записи в файл с ротацией ---

log_file = '../logs/bot.log' 

file_handler = RotatingFileHandler(
    log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO) 

# --- Получаем корневой логгер или логгер для aiogram ---
logger = logging.getLogger('aiogram') 
logger.setLevel(logging.INFO) 

# --- Добавляем обработчики к логгеру ---
if logger.hasHandlers():
    logger.handlers.clear()

logger.addHandler(console_handler) 
logger.addHandler(file_handler)    

# --- Настройка логгера для специфичных частей (опционально) ---
# Например, для платежной системы
payment_logger = logging.getLogger('bot.payments')
# Он унаследует настройки от 'bot', но можно и переопределить
# payment_logger.setLevel(logging.DEBUG) # Например, временно включить детальное логирование платежей
# payment_logger.addHandler(specific_payment_handler) # Можно добавить специфичный обработчик

# --- Первый лог ---
logger.info("Настройка логирования завершена. Бот готов к запуску.")
