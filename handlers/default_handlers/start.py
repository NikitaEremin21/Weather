from aiogram import types
from loader import dp
from keyboards.reply.reply_keyboards import get_main_keyboard


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(text='Привет! 🌦️ Я бот "Weather".\n\n'
                              'Я использую данные открытого источника "OpenWeather", чтобы предоставить '
                              'вам актуальную и достоверную информацию о погоде.\n'
                              'Я могу:\n\n'
                              ' • показать погоду в данный момент\n'
                              ' • показать погоду на 5 дней\n'
                              ' • показать погоду в определенную дату.',
                         reply_markup=get_main_keyboard())
