from aiogram import Bot, Dispatcher, executor, types
from loader import dp
import handlers
from loguru import logger


def main():
    try:
        logger.info('Бот запущен (info)')
        executor.start_polling(dp)
    except Exception as error:
        logger.error(f'Произошла ошибка: {error}')


if __name__ == '__main__':
    main()
