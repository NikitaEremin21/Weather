import requests
from loguru import logger


async def get_response(url):
    """
    Функция для запроса к API
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return True, response.json()
    except requests.RequestException as e:
        logger.error(f'API requests failed: {e}')
        return False, 'Сервис временно недоступен. Попробуйте позже!'


async def get_coordinates(city, api_key):
    """
    Получение координат города из OpenWeather API
    """
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={1}&appid={api_key}&units=metric'
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if not data:
            return False, 'Город не найден. Попробуйте ввести другой город.'
        result = data[0]['lat'], data[0]['lon']
        return True, result
    except requests.exceptions.HTTPError as e:
        logger.error(f'Ошибка при запросе координат: {e}')
        return False, f'Сервис временно недоступен. Попробуйте позже!'
    except requests.exceptions.Timeout as e:
        logger.error(f'Ошибка при запросе координат: {e}')
        return False, f'Сервис временно недоступен. Попробуйте позже!'
    except requests.RequestException as e:
        logger.error(f'Ошибка при запросе координат: {e}')
        return False, f'Сервис временно недоступен. Попробуйте позже!'


async def get_weather_now(city, lang, api_key):
    """
    Запрос текущей погоды
    """
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang={lang}&units=metric'
    return await get_response(url)


async def get_weather_five_days(city, lang, api_key):
    """
    Запрос погоды на 5 дней
    """
    url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&lang={lang}&units=metric'
    return await get_response(url)


async def get_weather_day(lat, lon, date, api_key):
    """
    Получает погодные данные из OpenWeather API
    """
    url = (f'https://api.openweathermap.org/data/3.0/onecall/day_summary?'
           f'lat={lat}&lon={lon}&date={date}&appid={api_key}&units=metric')
    try:
        response = requests.get(url, timeout=10)
        return True, response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f'Ошибка при запросе координат: {e}')
        return False, f'Сервис временно недоступен. Попробуйте позже!'
    except requests.exceptions.Timeout as e:
        logger.error(f'Ошибка при запросе координат: {e}')
        return False, f'Сервис временно недоступен. Попробуйте позже!'
    except requests.RequestException as e:
        logger.error(f'Ошибка при запросе координат: {e}')
        return False, f'Сервис временно недоступен. Попробуйте позже!'