import re
from services.errors import DateValidationCity
from datetime import datetime, date


def validation_city_name(city):
    """
    Функция для валидации названия города
    """
    city = city.strip()
    if not re.fullmatch(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', city):
        return False
    return True


def validate_date_format(date_text: str) -> None:
    """Проверяет формат даты ДД.ММ.ГГГГ"""
    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', date_text):
        raise DateValidationCity("Неверный формат даты! Используйте формат ДД.ММ.ГГГГ.")


def validate_date_range(input_date: datetime) -> None:
    """Проверяет, что дата в допустимом диапазоне"""
    year, month, day = str(date.today()).split('-')
    min_date = datetime(1979, 1, 2)
    max_date = datetime(int(year), int(month), int(day))
    if not (min_date <= input_date <= max_date):
        raise DateValidationCity(
            f"Дата должна быть в пределах с {min_date.strftime('%d.%m.%Y')} "
            f"по {max_date.strftime('%d.%m.%Y')}."
        )
