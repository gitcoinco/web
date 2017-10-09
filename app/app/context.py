from django.conf import settings


def insert_settings(request):
    from marketing.utils import get_stat
    num_slack = int(get_stat('slack_users'))
    if num_slack > 1000:
        num_slack = u'{}k'.format(str(round((num_slack)/1000, 1)))
    context = {
        'STATIC_URL': settings.STATIC_URL,
        'num_slack': num_slack,
    }
    return context
