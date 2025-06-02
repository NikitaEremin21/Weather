from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
from services.weather_apy import get_weather_now
from config_data import config
from loguru import logger
import os
import states
from keyboards.reply.reply_keyboard_1 import weather_keyboard, cancel_keyboard
from services.errors import CityNotFoundError, CityValidationError, APIError
from services.validators import validation_city_name


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
        path_icon = f'images/{icon_id}.png'
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
    await message.answer(text='В каком городе вы хотите посмотреть погоду?',
                         reply_markup=cancel_keyboard)


@dp.message_handler(state=states.states.WeatherStates.city)
async def weather_now_command(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await cancel_handler(message, state)
        return
    try:
        city = message.text
        if not validation_city_name(city):
            raise CityValidationError
        lang = 'ru'
        api_key = config.RAPID_API_KEY

        status, data = await get_weather_now(city, lang, api_key)

        if not status or 'main' not in data or 'wind' not in data or 'weather' not in data:
            if data == 'Город не найден!':
                raise CityNotFoundError
            raise APIError

        photo, caption = await format_weather_data(city, data)

        if photo and caption:
            await message.answer_photo(photo=photo,
                                       caption=caption,
                                       reply_markup=weather_keyboard)
        else:
            await message.answer(text=f'Не удалось обработать информацию о погоду для города {city}',
                                 reply_markup=weather_keyboard)

        await state.finish()

    except CityValidationError:
        await message.answer(text='Некорректное название города, попробуйте еще раз!',
                             reply_markup=cancel_keyboard)
    except CityNotFoundError:
        await message.answer(text=f'Город не найден, попробуйте еще раз!',
                             reply_markup=cancel_keyboard)
    except APIError as e:
        await message.answer(text=f'Сервис временно не доступен, попробуйте позже!',
                             reply_markup=weather_keyboard)
        logger.error(f'Error: {e}')
        await state.finish()
    except Exception as e:
        await message.answer(text=f'Возникла техническая ошибка, попробуйте позже!',
                             reply_markup=weather_keyboard)
        logger.error(f'Error: {e}')
        await state.finish()


@dp.message_handler(text="Отмена", state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer(
        "Действие отменено",
        reply_markup=weather_keyboard
    )
