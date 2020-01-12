import time

from app.redis_service import RedisService
from celery import app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

redis = RedisService().redis

# Lock timeout of 2 minutes (just in the case that the application hangs to avoid a redis deadlock)
LOCK_TIMEOUT = 60 * 2

