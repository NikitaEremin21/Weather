from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Основное меню
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Погода сейчас'),
                KeyboardButton(text='Погода на 5 дней')
            ],
            [
                KeyboardButton(text='Погода в выбранную дату')
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


# Кнопка "отмена"
def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Отмена')
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )



