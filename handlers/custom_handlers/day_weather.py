from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from config_data import config
import states
import requests
import json
from keyboards.reply.reply_keyboard_1 import weather_keyboard
from datetime import datetime
from loguru import logger


async def get_coordinates(city, api_key):
    """
    Получение координат города из OpenWeather API
    """
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={1}&appid={api_key}&units=metric'
    try:
        response = requests.get(url)
        data = response.json()
        result = data[0]['lat'], data[0]['lon']
        return True, result
    except IndexError:
        logger.error(f'Город "{city}" не найден')
        return False, f'Город "{city}" не найден'
    except requests.RequestException as e:
        logger.error(f'Ошибка при запросе API: {e}')
        return False, f'Ошибка при запросе API: {e}'


@dp.message_handler(lambda message: message.text == 'Погода в выбранную дату' or message.text == '/day_weather')
async def day_weather_city(message: types.Message):
    await states.states.WeatherStates.city_day_weather.set()
    await message.answer(text='В каком городе вы хотите посмотреть погоду?')


@dp.message_handler(state=states.states.WeatherStates.city_day_weather)
async def day_weather_date(message: types.Message, state: FSMContext):
    await states.states.WeatherStates.date_day_weather.set()
    await state.update_data(city=message.text)
    await message.answer(text='Введите дату! \n\n'
                              '• Обратите внимание на формат даты <b>(Пример: 06.02.2024)</b> \n'
                              '• В этом разделе можно получить прогноз погоды на выбранную дату '
                              'в промежутке со 2 января 1979 года до 2 января 2025 года',
                         parse_mode=types.ParseMode.HTML)


@dp.message_handler(state=states.states.WeatherStates.date_day_weather)
async def day_weather_command(message: types.Message, state: FSMContext):
    first_date = datetime.strptime(str(message.text), '%d.%m.%Y')
    date = datetime.strftime(first_date, '%Y-%m-%d')
    api_key = config.RAPID_API_KEY
    data = await state.get_data()
    city = data.get('city')

    status, result = await get_coordinates(city, api_key)
    if not status:
        await message.answer(text=f'Ошибка! {result}')
    lat, lon = result[0], result[1]

    get_weather = requests.get(f'https://api.openweathermap.org/data/3.0/onecall/day_summary?'
                               f'lat={lat}&lon={lon}&date={date}&appid={api_key}&units=metric')

    if get_weather.status_code == 200:
        weather = json.loads(get_weather.text)
        date = datetime.strptime(date, "%Y-%m-%d")

        await message.answer(text=f'Дата: <b>{datetime.strftime(date, "%d.%m.%Y")}</b> \n'
                                  f'Минимальная температура: <b>{round(weather["temperature"]["min"])} °C</b>\n'
                                  f'Максимальная температура: <b>{round(weather["temperature"]["max"])} °C</b>',
                             parse_mode=types.ParseMode.HTML,
                             reply_markup=weather_keyboard)
    else:
        logger.error(f'Ошибка при запросе погоды. Статус код: {get_weather.status_code}')
        await message.answer(text=f'Ошибка! Не правильно указана дата!',
                             reply_markup=weather_keyboard)

    await state.finish()
