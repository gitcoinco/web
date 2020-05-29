from django.conf import settings

from redis import Redis
from twilio.rest import Client

from app.settings import account_sid, auth_token


class RedisService:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        redis_url = settings.CELERY_BROKER_URL
        self.redis = Redis.from_url(redis_url)


class TwilioService:
    _client = None
    _service = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        redis = RedisService().redis
        sid = redis.get(f"validation:twilio:sid")
        if not TwilioService._client and not sid:
            TwilioService._client = Client(account_sid, auth_token)

            TwilioService._service = TwilioService._client.verify.services.create(
                friendly_name='Gitcoin Verify Service'
            )
            redis.set(f"validation:twilio:sid", TwilioService._service.sid)

    @property
    def verify(self):
        redis = RedisService().redis
        sid = redis.get(f"validation:twilio:sid")
        return TwilioService.verify.services(sid.decode('utf-8'))
