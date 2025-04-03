from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
from services.weather_apy import get_weather_now
from config_data import config
from loguru import logger
import os
import states
from keyboards.reply.reply_keyboard_1 import weather_keyboard


async def format_weather_data(city, data):
    """
    Форматирует погодные данные для отправки в виде сообщения.
    """
    try:
        now_temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data['main']["humidity"]
        wind = data["wind"]["speed"]
        description = data["weather"][0]["description"]

        icon_id = data["weather"][0]["icon"][:2]
        path_icon = os.path.abspath(os.path.join(f'images/{icon_id}.png'))
        caption = (
            f'Сейчас в городе {city} {description}\n\n'
            f'🌡️ Температура: {"+" if now_temp > 0 else ""}{round(now_temp)} °C\n'
            f'🤗 Ощущается: {"+" if feels_like > 0 else ""}{round(feels_like)} °C\n'
            f'💧 Влажность: {humidity} %\n'
            f'🌬️ Скорость ветра: {round(wind)} м/с\n'
        )
        with open(path_icon, 'rb') as photo:
            return photo.read(), caption
    except Exception as e:
        logger.error(f'Ошибка при получении информации о погоде для города {city}: {e}')
        return None, None


@dp.message_handler(lambda message: message.text == 'Погода сейчас' or message.text == '/now')
async def weather_now_city_command(message: types.Message):
    await states.states.WeatherStates.city.set()
    await message.answer(text='В каком городе вы хотите посмотреть погоду?')


@dp.message_handler(state=states.states.WeatherStates.city)
async def weather_now_command(message: types.Message, state: FSMContext):
    city = message.text
    lang = 'ru'
    api_key = config.RAPID_API_KEY

    success, data = await get_weather_now(city, lang, api_key)

    if not success:
        await message.answer(text=data, reply_markup=weather_keyboard)
        await state.finish()
        return

    photo, caption = await format_weather_data(city, data)

    if photo and caption:
        await message.answer_photo(photo=photo, caption=caption, reply_markup=weather_keyboard)
    else:
        await message.answer(text=f'Не удалось обработать информацию о погоду для города {city}',
                             reply_markup=weather_keyboard)
    await state.finish()
