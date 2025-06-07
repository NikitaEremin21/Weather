import requests
import re
from loguru import logger
from config_data.config import (OPENWEATHER_NOW_API, OPENWEATHER_FIVE_DAY_API,
                                OPENWEATHER_DAY_WEATHER_API, OPENWEATHER_COORDINATION)
from services.errors import APIError


def generation_key(name_function, city):
    try:
        city = re.sub(r'[^a-zа-яё0-9]', '', city.lower())
        cache_key = f'{name_function}_{city}'
        return cache_key
    except Exception as e:
        print(f'Ошибка: {e}')


async def get_response(url, cache_key):
    """
    Функция для запросов к API
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return False, 'Город не найден!'
        else:
            logger.error(f'HTTPError: {e}')
            return False, 'Ошибка сервера!'
    except requests.exceptions.Timeout as e:
        logger.error(f'TimeoutError: {e}')
        return False, f'Сервис временно недоступен. Попробуйте позже!'
    except requests.RequestException as e:
        logger.error(f'RequestException: {e}')
        return False, f'Проблему с интернет соединением. Попробуйте позже!'


async def get_coordinates(city, api_key):
    """
    Получение координат города из OpenWeather API
    """
    cache_key = generation_key('coordinate', city)
    url = f'{OPENWEATHER_COORDINATION}q={city}&limit={1}&appid={api_key}&units=metric'
    return await get_response(url, cache_key)


async def get_weather_now(city, lang, api_key):
    """
    Запрос текущей погоды
    """
    cache_key = generation_key('now', city)
    url = f'{OPENWEATHER_NOW_API}q={city}&appid={api_key}&lang={lang}&units=metric'
    return await get_response(url, cache_key)


async def get_weather_five_days(city, lang, api_key):
    """
    Запрос погоды на 5 дней
    """
    cache_key = generation_key('five_days', city)
    url = f'{OPENWEATHER_FIVE_DAY_API}q={city}&appid={api_key}&lang={lang}&units=metric'
    return await get_response(url, cache_key)


async def get_weather_day(lat, lon, city, date, api_key):
    """
    Получает погодные данные из OpenWeather API
    """
    cache_key = generation_key('weather_day', city)
    url = f'{OPENWEATHER_DAY_WEATHER_API}lat={lat}&lon={lon}&date={date}&appid={api_key}&units=metric'
    return await get_response(url, cache_key)
