from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from config_data import config
import states
import requests
import json
from keyboards.reply.reply_keyboard_1 import rep_keyboard_1


@dp.message_handler(lambda message: message.text == 'Погода сейчас' or message.text == '/now')
async def weather_now_city_command(message: types.Message):
    await states.states.WeatherStates.city.set()
    await message.answer(text='В каком городе вы хотите посмотреть погоду?')


@dp.message_handler(state=states.states.WeatherStates.city)
async def weather_now_command(message: types.Message):
    city = message.text
    api_key = config.RAPID_API_KEY
    req = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric')
    try:
        data = json.loads(req.text)
        now_temp = data["main"]["temp"]
        if now_temp > 0:
            await message.answer(text=f'Сейчас в городе {city}: +{now_temp}')
        else:
            await message.answer(text=f'Сейчас в городе {city}: {now_temp}')
    except Exception:
        await message.answer(text='Город указан не верно!')
