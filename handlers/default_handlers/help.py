from aiogram import types
from config_data.config import DEFAULT_COMMANDS
from loader import dp


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    await message.answer(text='Список доступных команд:\n\n' + '\n'.join(text))
