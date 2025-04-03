from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from services.weather_apy import get_weather_day, get_coordinates
from config_data import config
import states
import requests
import json
import re
from keyboards.reply.reply_keyboard_1 import weather_keyboard
from datetime import datetime
from loguru import logger


class WeatherError(Exception):
    pass


# async def get_coordinates(city, api_key):
#     """
#     Получение координат города из OpenWeather API
#     """
#     url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={1}&appid={api_key}&units=metric'
#     try:
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         if not data:
#             return False, 'Город не найден. Попробуйте ввести другой город.'
#         result = data[0]['lat'], data[0]['lon']
#         return True, result
#     except requests.exceptions.HTTPError as e:
#         logger.error(f'Ошибка при запросе координат: {e}')
#         return False, f'Сервис временно недоступен. Попробуйте позже!'
#     except requests.exceptions.Timeout as e:
#         logger.error(f'Ошибка при запросе координат: {e}')
#         return False, f'Сервис временно недоступен. Попробуйте позже!'
#     except requests.RequestException as e:
#         logger.error(f'Ошибка при запросе координат: {e}')
#         return False, f'Сервис временно недоступен. Попробуйте позже!'
#
#
# async def get_weather(lat, lon, date, api_key):
#     """
#     Получает погодные данные из OpenWeather API
#     :param lat:
#     :param lon:
#     :param date:
#     :param api_key:
#     :return:
#     """
#     url = (f'https://api.openweathermap.org/data/3.0/onecall/day_summary?'
#            f'lat={lat}&lon={lon}&date={date}&appid={api_key}&units=metric')
#     try:
#         response = requests.get(url, timeout=10)
#         return True, response.json()
#     except requests.exceptions.HTTPError as e:
#         logger.error(f'Ошибка при запросе координат: {e}')
#         return False, f'Сервис временно недоступен. Попробуйте позже!'
#     except requests.exceptions.Timeout as e:
#         logger.error(f'Ошибка при запросе координат: {e}')
#         return False, f'Сервис временно недоступен. Попробуйте позже!'
#     except requests.RequestException as e:
#         logger.error(f'Ошибка при запросе координат: {e}')
#         return False, f'Сервис временно недоступен. Попробуйте позже!'


async def get_message_text(date, weather):
    try:
        date = datetime.strptime(date, "%Y-%m-%d")

        message_text = (f'Дата: <b>{datetime.strftime(date, "%d.%m.%Y")}</b> \n'
                        f'Минимальная температура: <b>{round(weather["temperature"]["min"])} °C</b>\n'
                        f'Максимальная температура: <b>{round(weather["temperature"]["max"])} °C</b>')
        return True, message_text
    except Exception as e:
        logger.error(f'Произошла ошибка при формировании сообщения: {e}')
        return False, 'Ошибка! Попробуйте еще раз!'


@dp.message_handler(lambda message: message.text == 'Погода в выбранную дату' or message.text == '/day_weather')
async def day_weather_city(message: types.Message):
    await states.states.WeatherStates.city_day_weather.set()
    await message.answer(text='В каком городе вы хотите посмотреть погоду?')


@dp.message_handler(state=states.states.WeatherStates.city_day_weather)
async def day_weather_date(message: types.Message, state: FSMContext):
    api_key = config.RAPID_API_KEY
    city = message.text
    try:
        if not city.replace(" ", "").isalpha():
            raise WeatherError()

        status, result = await get_coordinates(city, api_key)
        if not status:
            raise ValueError()

        lat, lon = result
        await states.states.WeatherStates.date_day_weather.set()
        await state.update_data(lat=lat, lon=lon)
        await message.answer(text='Введите дату! \n\n'
                                  '• Обратите внимание на формат даты <b>(Пример: 06.02.2024)</b> \n'
                                  '• В этом разделе можно получить прогноз погоды на выбранную дату '
                                  'в промежутке со 2 января 1979 года до 2 января 2025 года',
                             parse_mode=types.ParseMode.HTML)
    except WeatherError:
        await message.answer(text="Введите корректное название города (только буквы)!")
    except ValueError:
        await message.answer(text='Город не найдет! Проверьте, правильно ли написано название!')


@dp.message_handler(state=states.states.WeatherStates.date_day_weather)
async def day_weather_command(message: types.Message, state: FSMContext):
    try:
        date_text = message.text
        date_pattern = r'^\d{2}\.\d{2}\.\d{4}$'
        if not re.match(date_pattern, date_text):
            await message.answer("Неверный формат даты! Используйте формат ДД.ММ.ГГГГ.")
            return

        try:
            input_date = datetime.strptime(str(message.text), '%d.%m.%Y')
        except ValueError:
            raise WeatherError("Некорректная дата! Используйте формат ДД.ММ.ГГГГ, например, 06.02.2024.")

        min_date = datetime(1979, 1, 2)
        max_date = datetime(2025, 1, 2)
        if not (min_date <= input_date <= max_date):
            await message.answer(f"Дата должна быть в пределах с {min_date.strftime('%d.%m.%Y')}"
                                 f"по {max_date.strftime('%d.%m.%Y')}.")
            return

        date = datetime.strftime(input_date, '%Y-%m-%d')
        api_key = config.RAPID_API_KEY
        data = await state.get_data()
        lat = data.get('lat')
        lon = data.get('lon')

        status, weather = await get_weather_day(lat, lon, date, api_key)
        if not status:
            raise WeatherError(weather)

        status, message_text = await get_message_text(date, weather)
        if not status:
            raise WeatherError(message_text)
        await message.answer(text=message_text,
                             parse_mode=types.ParseMode.HTML,
                             reply_markup=weather_keyboard)

    except WeatherError as e:
        await message.answer(text=f'{e}')
    except Exception:
        await message.answer(text='Ошибка! Повторите позже!')

    await state.finish()
