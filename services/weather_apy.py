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


async def get_weather_now(city, lang, api_key):
    """
    Запрос текущей погоды
    """
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang={lang}&units=metric'
    return await get_response(url)
