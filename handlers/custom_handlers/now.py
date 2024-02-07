from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from config_data import config
from loguru import logger
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

    if req.status_code == 200:
        data = json.loads(req.text)
        now_temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        icon_id = data["weather"][0]["icon"]
        get_icon = requests.get(f'https://openweathermap.org/img/wn/{icon_id}@2x.png').content
        try:
            if now_temp > 0:
                await message.answer_photo(photo=get_icon, caption=f'Сейчас в городе {city} \n{description}'
                                                                   f'\nТемпература: +{round(now_temp)} °C',
                                           reply_markup=rep_keyboard_1)
            else:
                await message.answer_photo(photo=get_icon, caption=f'Сейчас в городе {city}: \n{description}'
                                                                   f'\nТемпература: {round(now_temp)} °C',
                                           reply_markup=rep_keyboard_1)
        except Exception as e:
            logger.error(f'Ошибка при получении информации о погоде для города {city}: {e}')
            await message.answer(text=f'Не удалось обработать информацию о погоде для города {city}',
                                 reply_markup=rep_keyboard_1)
    else:
        logger.error(f'Ошибка при запросе погоды для города {city}. Статус код: {req.status_code}')
        await message.answer(text=f'Ошибка! Не правильно указан город!',
                             reply_markup=rep_keyboard_1)

    await state.finish()
