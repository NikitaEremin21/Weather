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
from datetime import datetime
from collections import Counter


def weather_description_function(list_weather, i_day):
    """
        Функция анализирует список погодных условий и возвращает наиболее частое
        погодное условие вместе с информацией о возможности осадков.
    """
    weather_description_dict = {
        'ясно': 'ясно ☀️',
        'дождь': 'дождь 🌧',
        'пасмурно': 'пасмурно ☁️',
        'облачно с прояснениями': 'облачно с прояснениями ⛅️',
        'небольшой дождь': 'небольшой дождь',
        'небольшая облачность': 'небольшая облачность',
        'переменная облачность': 'переменная облачность'
    }
    if 'дождь' in list_weather or 'небольшой дождь' in list_weather or 'гроза' in list_weather:
        precipitation = 'Ожидаются осадки'
    else:
        precipitation = 'Осадков не ожидается'
    counter = Counter(list_weather)
    weather_description = counter.most_common(1)
    return weather_description_dict[weather_description[0][0]], precipitation


@dp.message_handler(lambda message: message.text == 'Погода на 5 дней' or message.text == '/five_days')
async def five_days_city_command(message: types.Message):
    await states.states.WeatherStates.city_five_days.set()
    await message.answer(text='В каком городе вы хотите посмотреть погоду?')


@dp.message_handler(state=states.states.WeatherStates.city_five_days)
async def five_days_command(message: types.Message, state: FSMContext):
    city = message.text
    lang = 'ru'
    date_now = datetime.now().date()
    api_key = config.RAPID_API_KEY
    req = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}'
                       f'&appid={api_key}&lang={lang}&units=metric')

    if req.status_code == 200:
        data = json.loads(req.text)
        daily_forecast = {}
        weather_list = {}
        message_text = f"<b>Прогноз погоды на 5 дней в городе {city}:</b>\n"

        for i_day in data['list']:
            dt_txt = i_day['dt_txt']
            date = dt_txt.split()
            if date[0] not in weather_list:
                weather_list[date[0]] = [i_day['weather'][0]['description']]
            else:
                weather_list[date[0]].append(i_day['weather'][0]['description'])

            if date[0] != str(date_now):
                if date[0] not in daily_forecast:
                    daily_forecast[date[0]] = {
                        'temp_min': i_day['main']['temp_min'],
                        'temp_max': i_day['main']['temp_max']
                    }
                else:
                    daily_forecast[date[0]]['temp_min'] = min(daily_forecast[date[0]]['temp_min'],
                                                              i_day['main']['temp_min'])
                    daily_forecast[date[0]]['temp_max'] = max(daily_forecast[date[0]]['temp_max'],
                                                              i_day['main']['temp_max'])

        for i_date in daily_forecast:
            weather_description = weather_description_function(weather_list[i_date], i_date)

            date = datetime.strptime(i_date, "%Y-%m-%d").strftime("%d.%m.%Y")
            message_text += (f'\n<b>{date}</b>\n'
                             f'Преимущественно {weather_description[0]}\n'
                             f'{weather_description[1]}\n'
                             f'Температура:  '
                             f'<b>{round(daily_forecast[i_date]["temp_min"])} - '
                             f'{round(daily_forecast[i_date]["temp_max"])} °C</b>\n')

        await message.answer(text=message_text,
                             parse_mode=types.ParseMode.HTML,
                             reply_markup=rep_keyboard_1)
    else:
        logger.error(f'Ошибка при запросе погоды для города {city}. Статус код: {req.status_code}')
        await message.answer(text=f'Ошибка! Не правильно указан город!',
                             reply_markup=rep_keyboard_1)

    await state.finish()
