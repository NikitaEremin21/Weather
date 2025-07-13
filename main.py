from aiogram import Bot, Dispatcher, executor, types
from loader import dp, bot, on_startup, on_shutdown
import handlers
from loguru import logger


if __name__ == '__main__':
    logger.info("Бот запущен")
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )
