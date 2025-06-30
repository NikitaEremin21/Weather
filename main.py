from aiogram import Bot, Dispatcher, executor, types
from loader import dp, bot, on_startup, on_shutdown
import handlers
from loguru import logger


def main():
    try:
        logger.success('Бот запущен (info)')
        executor.start_polling(dp)
    except Exception as error:
        logger.error(f'Произошла ошибка: {error}')


if __name__ == '__main__':
    logger.info("Бот запущен")
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )
