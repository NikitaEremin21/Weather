from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


rep_keyboard_1 = ReplyKeyboardMarkup(resize_keyboard=True,
                                     one_time_keyboard=True)
Button_1 = KeyboardButton(text='Погода сейчас')
Button_2 = KeyboardButton(text='Погода на 5 дней')
rep_keyboard_1.add(Button_1).add(Button_2)
