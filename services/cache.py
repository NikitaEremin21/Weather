import redis
from config_data.config import REDIS_HOST, REDIS_PORT
from loguru import logger
import json


class RedisCache:
    def __init__(self):
        try:
            self.redis = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True
            )
            logger.info('Соединение с Redis установлено!')
        except Exception as e:
            logger.error(f'Ошибка при установке соединения с Redis: {e}')
            raise

    def set(self, key, data):
        """Добавление данных в кэш"""
        try:
            self.redis.set(key, json.dumps(data))
            print('Данные добавлены')
            return True
        except Exception as e:
            logger.error(f'Ошибка при добавлении данных в кэш: {e}')
            return False

    def get(self, key):
        """Получение данных из кэша"""
        try:
            cache_data = self.redis.get(key)
            if cache_data:
                print('Данные получены')
                return json.loads(cache_data)
            return None
        except Exception as e:
            logger.error(f'Ошибка при получении данных из кэша: {e}')
            return False

