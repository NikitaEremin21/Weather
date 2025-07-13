from aiogram.dispatcher.filters.state import State, StatesGroup


class WeatherStates(StatesGroup):
    city = State()
    city_five_days = State()
    city_day_weather = State()
    date_day_weather = State()


class RegistrationStates(StatesGroup):
    waiting_for_city = State()
