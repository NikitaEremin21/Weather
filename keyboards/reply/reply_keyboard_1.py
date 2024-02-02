from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


rep_keyboard_1 = ReplyKeyboardMarkup(resize_keyboard=True,
                                     one_time_keyboard=True)
Button_1 = KeyboardButton(text='Погода сейчас')
rep_keyboard_1.add(Button_1)
