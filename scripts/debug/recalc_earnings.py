# used to make sure the DB state matches business logic
# per https://gitcoincore.slack.com/archives/G01JE138QQH/p1617410401006100
from dashboard.models import Earning
from dashboard.tasks import recalculate_earning

for pk in Earning.objects.values_list('pk', flat=True):
    try:
        print(pk)
        recalculate_earning.delay(pk)
    except Exception as e:
        print(e)
