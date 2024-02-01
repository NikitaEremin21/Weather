from aiogram import types
from loader import dp
from keyboards.reply.reply_keyboard_1 import rep_keyboard_1


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(text='Добро пожаловать в  бот!',
                         reply_markup=rep_keyboard_1)
