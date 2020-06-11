from django.conf import settings

from app.settings import account_sid, auth_token
from redis import Redis
from twilio.rest import Client


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


class TwilioService:
    _client = None
    _service = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __create_connection(self):
        redis = RedisService().redis

        if not TwilioService._client:
            TwilioService._client = Client(account_sid, auth_token)

            TwilioService._service = TwilioService._client.verify.services.create(
                friendly_name='Gitcoin Verify Service'
            )
            redis.set(f"validation:twilio:sid", TwilioService._service.sid)

    def __init__(self):
        self.__create_connection()

    @property
    def lookups(self):
        return TwilioService._client.lookups

    @property
    def verify(self):
        redis = RedisService().redis
        sid = redis.get(f"validation:twilio:sid")
        return TwilioService._client.verify.services(sid.decode('utf-8'))
