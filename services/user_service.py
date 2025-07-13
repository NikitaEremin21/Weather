from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import User
from loguru import logger


async def get_user_by_telegram_id(telegram_id, db):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalars().first()


async def register_user(telegram_user, city, db):
    try:
        new_user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name or '',
            last_name=telegram_user.last_name,
            city=city,
            language=telegram_user.language_code,
            notifications_enabled=False,
        )
        db.add(new_user)
        await db.commit()
        logger.info(f'Пользователь {telegram_user.id} зарегистрирован')
        return True
    except Exception as e:
        logger.error(f'Ошибка при регистрации пользователя: {e}')
        return False
