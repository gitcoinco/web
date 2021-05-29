from django.conf import settings
from django.db import connection, transaction

from app.services import RedisService
from cacheops import invalidate_obj
from celery import app
from celery.utils.log import get_task_logger
from dashboard.models import Activity

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
    if settings.FLUSH_QUEUE:
        return

    if len(pks) == 0:
        return
    # update DB directly
    with connection.cursor() as cursor:
        id_as_str = ",".join(str(id) for id in pks)
        query = f"UPDATE dashboard_activity SET view_count = view_count + 1 WHERE id in ({id_as_str});"
        cursor.execute(query)
        cursor.close()

    # invalidate cache
    activities = Activity.objects.filter(pk__in=pks)
    for obj in activities:
        invalidate_obj(obj)

@app.shared_task(bind=True, max_retries=3)
def increment_offer_view_counts(self, pks, retry=False):
    """
    :param self:
    :param pks:
    :return:
    """
    with redis.lock("tasks:increment_offer_view_counts", timeout=LOCK_TIMEOUT):
        if len(pks) == 0:
            return
        # update DB directly
        with connection.cursor() as cursor:
            id_as_str = ",".join(str(id) for id in pks)
            if len(id_as_str):
                query = f"UPDATE townsquare_offer SET view_count = view_count + 1 WHERE id in ({id_as_str});"
                cursor.execute(query)
            cursor.close()


@app.shared_task(bind=True, max_retries=3)
def send_comment_email(self, pk, retry=False):
    """
    :param self:
    :param pk:
    :return:
    """
    with redis.lock("tasks:send_comment_email", timeout=LOCK_TIMEOUT):

        from townsquare.models import Comment
        from marketing.mails import comment_email
        instance = Comment.objects.get(pk=pk)
        comment_email(instance)
        print("SENT EMAIL")



@app.shared_task(bind=True, max_retries=3)
def calculate_clr_match(self, retry=False):
    """
    :param self:
    :return:
    """
    with redis.lock("tasks:calculate_clr_match", timeout=LOCK_TIMEOUT):

        from townsquare.models import MatchRound
        mr = MatchRound.objects.current().first()
        if mr:
            mr.process()
