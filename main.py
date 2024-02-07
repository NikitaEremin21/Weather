from aiogram import Bot, Dispatcher, executor, types
from loader import dp
import handlers
from loguru import logger

logger.info('Бот запущен (info)')

if __name__ == '__main__':
    executor.start_polling(dp)
