from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config_data import config
from loguru import logger
import states
import requests
import json
import os
from keyboards.reply.reply_keyboard_1 import weather_keyboard


async def get_weather_data(city, lang, api_key):
    """
    Получает данные о погоде с OpenWeather API.
    :param city:
    :param lang:
    :param api_key:
    :return:
    """
    try:
        response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}'
                                f'&appid={api_key}&lang={lang}&units=metric')
        return json.loads(response.text)
    except requests.RequestException as e:
        logger.error(f'Ошибка при запросе погоды для города {city}. Статус код: {e}')
        return None


@dp.message_handler(lambda message: message.text == 'Погода сейчас' or message.text == '/now')
async def weather_now_city_command(message: types.Message):
    await states.states.WeatherStates.city.set()
    await message.answer(text='В каком городе вы хотите посмотреть погоду?')


@dp.message_handler(state=states.states.WeatherStates.city)
async def weather_now_command(message: types.Message, state: FSMContext):
    city = message.text
    lang = 'ru'
    api_key = config.RAPID_API_KEY
    data = await get_weather_data(city, lang, api_key)
    if data:
        try:
            now_temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data['main']["humidity"]
            wind = data["wind"]["speed"]
            description = data["weather"][0]["description"]

            icon_id = data["weather"][0]["icon"][:2]
            path_icon = os.path.abspath(os.path.join(f'images/{icon_id}.png'))

            with open(path_icon, 'rb') as photo:
                caption = (
                    f'Сейчас в городе {city} {description}\n'
                    f'-------------------------------------------------\n'
                    f'Температура: {"+" if now_temp > 0 else ""}{round(now_temp)} °C\n'
                    f'Ощущается: {"+" if feels_like > 0 else ""}{round(feels_like)} °C\n'
                    f'Влажность: {humidity} %\n'
                    f'Скорость ветра: {round(wind)} м/с\n'
                )
                await message.answer_photo(photo=photo, caption=caption, reply_markup=weather_keyboard)
        except Exception as e:
            logger.error(f'Ошибка при получении информации о погоде для города {city}: {e}')
            await message.answer(text=f'Не удалось обработать информацию о погоде для города {city}',
                                 reply_markup=weather_keyboard)

    await message.answer(text=f'Ошибка! Не правильно указан город!',
                         reply_markup=weather_keyboard)

    await state.finish()
