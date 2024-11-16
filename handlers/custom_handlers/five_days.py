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
from keyboards.reply.reply_keyboard_1 import weather_keyboard
from datetime import datetime
from collections import Counter


async def get_weather_data(city, lang, api_key):
    """
    Получает данные о погоде из OpenWeather API.
    """
    url = (f'https://api.openweathermap.org/data/2.5/forecast?q={city}'
           f'&appid={api_key}&lang={lang}&units=metric')
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f'Ошибка при запросе погоды для города {city}. Статус код: {e}')
        return None


async def group_weather_data(data, date_now):
    """
    Группирует прогноз погоды по дням
    """
    daily_forecast = {}
    weather_list = {}

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
    return daily_forecast, weather_list


async def get_message_text(city, daily_forecast, weather_list):
    """
    Формирование текста сообщения
    """
    try:
        message_text = f"<b>Прогноз погоды на 5 дней в городе {city}:</b>\n"

        for i_date in daily_forecast:
            weather_description = weather_description_function(weather_list[i_date])

            date = datetime.strptime(i_date, "%Y-%m-%d").strftime("%d.%m.%Y")
            message_text += (f'\n<b>{date}</b>\n'
                             f'Преимущественно {weather_description[0]}\n'
                             f'{weather_description[1]}\n'
                             f'Температура:  '
                             f'<b>{round(daily_forecast[i_date]["temp_min"])} - '
                             f'{round(daily_forecast[i_date]["temp_max"])} °C</b>\n')
        return message_text
    except Exception as e:
        logger.error(f'Ошибка в обработке данных: {e}')


def weather_description_function(list_weather):
    """
    Функция анализирует список погодных условий и возвращает наиболее частое
    погодное условие вместе с информацией о возможности осадков.
    """
    weather_description_dict = {
        'ясно': 'ясно ☀️',
        'дождь': 'дождь 🌧️',
        'пасмурно': 'пасмурно ☁️',
        'облачно с прояснениями': 'облачно с прояснениями ⛅',
        'небольшой дождь': '\nнебольшой дождь 🌧️',
        'небольшая облачность': 'небольшая облачность ☁️',
        'переменная облачность': 'переменная облачность ⛅',
        'небольшой снег': 'небольшой снег ❄️',
        'снег': 'снег ❄️'
    }
    precipitation = 'Ожидаются осадки' if any(word in list_weather for word in ['дождь', 'гроза', 'небольшой дождь'])\
        else 'Осадков не ожидается'
    counter = Counter(list_weather)
    weather_description = counter.most_common(1)
    return weather_description_dict[weather_description[0][0]], precipitation


@dp.message_handler(lambda message: message.text == 'Погода на 5 дней' or message.text == '/five_days')
async def five_days_city_command(message: types.Message):
    """
    Начинает диалог для получения прогноза погоды
    """
    await states.states.WeatherStates.city_five_days.set()
    await message.answer(text='В каком городе вы хотите посмотреть погоду?')


@dp.message_handler(state=states.states.WeatherStates.city_five_days)
async def five_days_command(message: types.Message, state: FSMContext):
    """
    Обрабатывает данные и возвращает прогноз погоды на 5 дней
    """
    city = message.text.strip()
    lang = 'ru'
    date_now = datetime.now().date()
    api_key = config.RAPID_API_KEY

    if not city.replace(" ", "").isalpha():
        await message.answer("Введите корректное название города (только буквы)!")
        return

    await message.answer("Ищу данные...")
    try:
        data = await get_weather_data(city, lang, api_key)
        if not data:
            raise ValueError('Не удалось получить данные о погоде.')

        daily_forecast, weather_list = await group_weather_data(data, date_now)
        message_text = await get_message_text(city, daily_forecast, weather_list)
        if not message_text:
            raise ValueError('Не удалось сформировать ответ.')

        await message.answer(text=message_text,
                             parse_mode=types.ParseMode.HTML,
                             reply_markup=weather_keyboard)
    except ValueError as e:
        logger.error(e)
        await message.answer(text='Ошибка в обработке данных',
                             reply_markup=weather_keyboard)
    except Exception as e:
        logger.error(f'Непредвиденная ошибка: {e}')
        await message.answer(text=f'Ошибка! Не правильно указан город!',
                             reply_markup=weather_keyboard)
    await state.finish()
