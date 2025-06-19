from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config_data.config import BOT_TOKEN, POSTGRES_URL
from loguru import logger
from services.cache import RedisCache
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.models import Base


async def create_db():
    """Создаёт таблицы в БД, если их нет."""
    try:
        engine = create_async_engine(POSTGRES_URL.replace("postgresql://", "postgresql+asyncpg://"))
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.success("Таблицы в БД созданы")
        return engine
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        raise


async def on_startup(dp):
    """Действия при запуске бота."""
    await create_db()


async def on_shutdown(dp):
    """Корректное завершение работы."""
    await dp.storage.close()
    await dp.storage.wait_closed()
    session = await bot.get_session()
    await session.close()
    logger.info("Бот остановлен")


storage = MemoryStorage()
try:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    redis_cache = RedisCache()
    logger.info('Bot и Dispatcher успешно инициализированы.')
except Exception as error:
    logger.error(f"Ошибка при инициализации Bot или Dispatcher: {error}")
    raise error
