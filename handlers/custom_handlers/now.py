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
async def weather_now_command(message: types.Message, state: FSMContext):
    city = message.text
    lang = 'ru'
    api_key = config.RAPID_API_KEY
    req = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}'
                       f'&appid={api_key}&lang={lang}&units=metric')

    data = json.loads(req.text)
    now_temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    icon_id = data["weather"][0]["icon"]
    get_icon = requests.get(f'https://openweathermap.org/img/wn/{icon_id}@2x.png').content
    try:
        if now_temp > 0:
            await message.answer_photo(photo=get_icon, caption=f'Сейчас в городе {city} \n{description}'
                                                               f'\nТемпература: +{round(now_temp)}',
                                       reply_markup=rep_keyboard_1)
        else:
            await message.answer_photo(photo=get_icon, caption=f'Сейчас в городе {city}: \n{description}'
                                                               f'\nТемпература: {round(now_temp)}',
                                       reply_markup=rep_keyboard_1)
    except Exception:
        await message.answer(text=f'Не удалось получить информацию о погоде для города {city}')

    await state.finish()
