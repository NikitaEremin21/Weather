from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config_data import config
from loguru import logger


storage = MemoryStorage()
try:
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    logger.info('Bot и Dispatcher успешно инициализированы.')
except Exception as error:
    logger.error(f"Ошибка при инициализации Bot или Dispatcher: {error}")
    raise error
