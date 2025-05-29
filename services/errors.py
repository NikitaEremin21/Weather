class WeatherBotError(Exception):
    """Базовый класс для всех ошибок"""
    def __init__(self, message='Ошибка при получении данных о погоде'):
        self.message = message
        super().__init__(self.message)


class CityNotFoundError(WeatherBotError):
    """Город не найден"""

    def __init__(self, message='Некорректное название города.'):
        self.message = message
        super().__init__(self.message)


class CityValidationError(WeatherBotError):
    """Ошибка валидации города"""
    def __init__(self, message='Некорректное название города.'):
        self.message = message
        super().__init__(self.message)


class DateValidationCity(WeatherBotError):
    """Ошибка валидации даты"""
    def __init__(self, message='Некорректный формат даты'):
        self.message = message
        super().__init__(self.message)


class APIError(WeatherBotError):
    """Ошибка API"""
    def __init__(self, message='Сервис погоды временно недоступен. Попробуйте позже!'):
        self.message = message
        super().__init__(self.message)
