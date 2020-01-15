from django.db import transaction

from app.redis_service import RedisService
from celery import app
from celery.utils.log import get_task_logger
from django.db import connection

logger = get_task_logger(__name__)

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
        with connection.cursor() as cursor:
            id_as_str = ",".join(str(id) for id in pks)
            query = f"UPDATE dashboard_activity SET view_count = view_count + 1 WHERE id in ({id_as_str});"
            cursor.execute(query)
            cursor.close()
            print('done')

