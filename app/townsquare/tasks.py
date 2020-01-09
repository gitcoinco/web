from app.redis_service import RedisService
from celery import app
from celery.utils.log import get_task_logger
from dashboard.models import Activity
logger = get_task_logger(__name__)
from django.db import transaction

redis = RedisService().redis

# Lock timeout of 2 minutes (just in the case that the application hangs to avoid a redis deadlock)
LOCK_TIMEOUT = 60 * 2

@app.shared_task(bind=True, max_retries=3)
def increment_view_counts(self, pks, retry=False):
    """
    :param self:
    :param pks:
    :return:
    """
    with redis.lock("tasks:increment_view_counts", timeout=LOCK_TIMEOUT):
        activities = Activity.objects.filter(pk__in=pks)
        with transaction.atomic():
            for activity in activities:
                activity.view_count += 1
                activity.save()


