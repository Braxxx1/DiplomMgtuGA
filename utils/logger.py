import logging
import os

# Создаём папку для логов
if not os.path.exists("logs"):
    os.makedirs("logs")

# Настройка логгера
logging.basicConfig(
    filename="logs/processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)

def log(message):
    """Логирование сообщений"""
    print(message)  # Для отображения в консоли
    logging.info(message)
