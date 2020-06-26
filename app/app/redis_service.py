from django.conf import settings

from redis import Redis


class RedisService:
    __redis = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        if not RedisService.__redis:
            redis_url = settings.CELERY_BROKER_URL
            RedisService.__redis = Redis.from_url(redis_url)

    @property
    def redis(self):
        return RedisService.__redis
