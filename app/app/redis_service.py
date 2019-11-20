from django.conf import settings
from redis import Redis


class RedisService:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        redis_url = settings.CELERY_BROKER_URL
        self.redis = Redis.from_url(redis_url)
