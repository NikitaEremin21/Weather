from aiogram import Bot, Dispatcher, executor, types
from loader import dp


if __name__ == '__main__':
    executor.start_polling(dp)
