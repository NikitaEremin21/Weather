from aiogram import types
from loader import dp
from keyboards.reply.reply_keyboards import get_main_keyboard
from aiogram.dispatcher import FSMContext
from states.states import RegistrationStates
from services.user_service import get_user_by_telegram_id, register_user
from sqlalchemy.ext.asyncio import AsyncSession
from loader import bot
from loader import storage
from config_data.config import POSTGRES_URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


engine = create_async_engine(POSTGRES_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(text='Привет! 🌦️ Я бот "Weather".\n\n'
                              'Я использую данные открытого источника "OpenWeather", чтобы предоставить '
                              'вам актуальную и достоверную информацию о погоде.\n'
                              'Я могу:\n\n'
                              ' • показать погоду в данный момент\n'
                              ' • показать погоду на 5 дней\n'
                              ' • показать погоду в определенную дату.\n\n'
                              'Для начала, введите ваш город по умолчанию',
                         )
    await RegistrationStates.waiting_for_city.set()


@dp.message_handler(state=RegistrationStates.waiting_for_city)
async def process_city(message, state):
    city = message.text.strip()

    async with AsyncSessionLocal() as db:
        result = await register_user(message.from_user, city, db)
        if not result:
            await message.answer('Произошла ошибка при регистрации. Попробуйте позже.')
            await state.finish()
            return

    await message.answer(
        'Вы успешно зарегистрированы! ✅',
        reply_markup=get_main_keyboard()
    )
    await state.finish()

