from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Создаём клавиатуру для выбора типа прогноза погоды

weather_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button_now = KeyboardButton(text='Погода сейчас')
button_five_days = KeyboardButton(text='Погода на 5 дней')
button_specific_date = KeyboardButton(text='Погода в выбранную дату')
weather_keyboard.add(button_now, button_five_days).add(button_specific_date)


cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
button_cancel = KeyboardButton(text='Отмена')
cancel_keyboard.add(button_cancel)
