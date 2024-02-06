from aiogram.dispatcher.filters.state import State, StatesGroup


class WeatherStates(StatesGroup):
    city = State()
    city_five_days = State()
