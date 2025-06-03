from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from services.weather_apy import get_weather_five_days
from config_data import config
from loguru import logger
import states
import requests
import json
from keyboards.reply.reply_keyboards import get_main_keyboard, get_cancel_keyboard
from datetime import datetime
from collections import Counter
from services.errors import CityNotFoundError, CityValidationError, APIError
from services.validators import validation_city_name


async def group_weather_data(data, date_now):
    """
    Группирует прогноз погоды по дням
    """
    try:
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
    except Exception as e:
        logger.error(f'Ошибка при получении информации о погоде для города {city}: {e}')
        return None, None


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
        return None


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
    await message.answer(text='В каком городе вы хотите посмотреть погоду?',
                         reply_markup=get_cancel_keyboard())


@dp.message_handler(state=states.states.WeatherStates.city_five_days)
async def five_days_command(message: types.Message, state: FSMContext):
    """
    Обрабатывает данные и возвращает прогноз погоды на 5 дней
    """
    if message.text == "Отмена":
        await cancel_handler(message, state)
        return
    try:
        city = message.text.strip()
        if not validation_city_name(city):
            raise CityValidationError
        lang = 'ru'
        date_now = datetime.now().date()
        api_key = config.RAPID_API_KEY

        status, data = await get_weather_five_days(city, lang, api_key)
        if not status or 'list' not in data:
            if data == 'Город не найден!':
                raise CityNotFoundError
            raise APIError

        daily_forecast, weather_list = await group_weather_data(data, date_now)
        if daily_forecast is None or weather_list is None:
            raise ValueError()

        message_text = await get_message_text(city, daily_forecast, weather_list)

        if message_text is None:
            logger.error(f'Не удалось сформировать ответ для города {city}')
            raise ValueError(f'Не удалось сформировать ответ для города {city}')

        await message.answer(text=message_text,
                             parse_mode=types.ParseMode.HTML,
                             reply_markup=get_main_keyboard())
        logger.info(f'Успешно выполнен запрос для города "{city}"')
        await state.finish()

    except CityValidationError:
        await message.answer(text='Некорректное название города, попробуйте еще раз!')
    except CityNotFoundError:
        await message.answer(text=f'Город не найден!')
    except APIError as e:
        await message.answer(text=f'Сервис временно не доступен, попробуйте позже!',
                             reply_markup=get_main_keyboard())
        logger.error(f'Error: {e}')
        await state.finish()
    except ValueError:
        await message.answer(text=f'Возникла техническая ошибка, попробуйте позже!',
                             reply_markup=get_main_keyboard())
        await state.finish()
    except Exception as e:
        await message.answer(text=f'Возникла техническая ошибка, попробуйте позже!',
                             reply_markup=get_main_keyboard())
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
        reply_markup=get_main_keyboard()
    )
