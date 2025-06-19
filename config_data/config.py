import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("now", "Погода сейчас"),
    ("five_days", "Погода на 5 дней"),
    ("day_weather", 'Погода в выбранную дату')
)

OPENWEATHER_NOW_API = 'https://api.openweathermap.org/data/2.5/weather?'
OPENWEATHER_FIVE_DAY_API = 'https://api.openweathermap.org/data/2.5/forecast?'
OPENWEATHER_DAY_WEATHER_API = 'https://api.openweathermap.org/data/3.0/onecall/day_summary?'
OPENWEATHER_COORDINATION = 'http://api.openweathermap.org/geo/1.0/direct?'

POSTGRES_HOST = 'localhost'
POSTGRES_PORT = 5432
POSTGRES_DB = 'weather_bot_db'
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
CACHE_TTL_NOW = 900
CACHE_TTL_FIVE_DAYS = 10800
CACHE_TTL_DAY_WEATHER = 86400
CACHE_TTL_COORDINATE = 1296000
