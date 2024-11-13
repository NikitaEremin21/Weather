from aiogram import Bot
from aiogram.types import BotCommand
from config_data.config import DEFAULT_COMMANDS


async def set_command(bot: Bot):
    """
    Устанавливает команды бота, доступные для пользователя в интерфейсе Telegram.
    :param bot:
    :return:
    """
    await bot.set_my_commands(
            [BotCommand(*i) for i in DEFAULT_COMMANDS]
    )
