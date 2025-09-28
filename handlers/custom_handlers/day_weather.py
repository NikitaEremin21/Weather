from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from services.weather_api import get_weather_day, get_coordinates
from services.validators import validation_city_name, validate_date_format, validate_date_range
from services.errors import CityValidationError, CityNotFoundError, DateValidationCity, MessageError, APIError
from config_data import config
import states
import requests
import json
import re
from keyboards.reply.reply_keyboards import get_main_keyboard, get_cancel_keyboard
from datetime import datetime
from loguru import logger


async def get_message_text(date, weather):
    try:
        date = datetime.strptime(date, "%Y-%m-%d")

        message_text = (f'Дата: <b>{datetime.strftime(date, "%d.%m.%Y")}</b> \n'
                        f'Минимальная температура: <b>{round(weather["temperature"]["min"])} °C</b>\n'
                        f'Максимальная температура: <b>{round(weather["temperature"]["max"])} °C</b>')
        return True, message_text
    except Exception as e:
        logger.error(f'Произошла ошибка при формировании сообщения: {e}')
        return False, 'Произошла ошибка при формировании сообщения!'


@dp.message_handler(lambda message: message.text == 'Погода в выбранную дату' or message.text == '/day_weather')
async def day_weather_city(message: types.Message):
    await states.states.WeatherStates.city_day_weather.set()
    await message.answer(text='В каком городе вы хотите посмотреть погоду?',
                         reply_markup=get_cancel_keyboard())


@dp.message_handler(state=states.states.WeatherStates.city_day_weather)
async def day_weather_date(message: types.Message, state: FSMContext):
    try:
        if message.text == "Отмена":
            await cancel_handler(message, state)
            return
        city = message.text
        if not validation_city_name(city):
            raise CityValidationError

        api_key = config.OPENWEATHER_API_KEY

        status, data = await get_coordinates(city, api_key)
        if not status:
            if 'Город не найден' in data:
                raise CityNotFoundError
            raise APIError

        if not data:
            raise CityNotFoundError

        lat, lon = data[0]['lat'], data[0]['lon']
        await states.states.WeatherStates.date_day_weather.set()
        await state.update_data(lat=lat, lon=lon, city=city)
        await message.answer(text='📅 Введите дату в формате <b>ДД.ММ.ГГГГ</b>\n\n'
                                  'Например: <code>06.02.2024</code>\n\n'
                                  '⚠️ Обратите внимание:\n'
                                  '• Данные доступны за период <b>с 02.01.1979 по сегодняшний день</b>.\n'
                                  '• Если ввести неверный формат, бот не сможет обработать запрос.',
                             parse_mode=types.ParseMode.HTML)
    except CityValidationError:
        await message.answer(text='Некорректное название города')
    except CityNotFoundError:
        await message.answer(text='Город не найден')
    except APIError as e:
        await message.answer(text=f'Сервис временно не доступен, попробуйте позже!',
                             reply_markup=get_main_keyboard())
        logger.error(f'Error: {e}')
        await state.finish()
    except Exception as e:
        logger.error(str(e))
        await message.answer(text='Ошибка! Повторите позже!',
                             reply_markup=get_main_keyboard())
        await state.finish()


@dp.message_handler(state=states.states.WeatherStates.date_day_weather)
async def day_weather_command(message: types.Message, state: FSMContext):
    try:
        if message.text == "Отмена":
            await cancel_handler(message, state)
            return
        try:
            validate_date_format(message.text)
            input_date = datetime.strptime(message.text, '%d.%m.%Y')
            validate_date_range(input_date)
        except DateValidationCity as e:
            await message.answer(str(e))
            return
        except ValueError:
            await message.answer("Некорректная дата! Используйте формат ДД.ММ.ГГГГ, например, 06.02.2024.")
            return

        date = datetime.strftime(input_date, '%Y-%m-%d')
        api_key = config.OPENWEATHER_API_KEY
        data = await state.get_data()
        lat = data.get('lat')
        lon = data.get('lon')
        city = data.get('city')

        status, weather = await get_weather_day(lat, lon, city, date, api_key)
        if not status:
            raise APIError

        status, message_text = await get_message_text(date, weather)
        if not status:
            logger.error(f'Не удалось сформировать ответ для города {city}')
            raise MessageError
        await message.answer(text=message_text,
                             parse_mode=types.ParseMode.HTML,
                             reply_markup=get_main_keyboard())

        logger.info(f'Успешно выполнен запрос для города "{data.get("city")}"')
        await state.finish()

    except APIError as e:
        logger.error(f'Error: {e}')
        await message.answer(str(e),
                             reply_markup=get_main_keyboard())
        await state.finish()
    except MessageError as e:
        await message.answer(str(e),
                             reply_markup=get_main_keyboard())
        await state.finish()
    except Exception as e:
        logger.error(str(e))
        await message.answer(text='Ошибка! Повторите позже!',
                             reply_markup=get_main_keyboard())
        await state.finish()


@dp.message_handler(text="Отмена", state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer(
        "Действие отменено",
        reply_markup=get_main_keyboard()
    )
