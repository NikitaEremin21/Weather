import re
from services.errors import CityValidationError


def validation_city_name(city):
    """
    Функция для валидации названия города
    """
    city = city.strip()
    if not re.fullmatch(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', city):
        return False
    return True
