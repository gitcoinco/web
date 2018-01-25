from django.conf import settings


def insert_settings(request):
    from marketing.utils import get_stat
    try:
        num_slack = int(get_stat('slack_users'))
    except:
        num_slack = 0
    if num_slack > 1000:
        num_slack = u'{}k'.format(str(round((num_slack)/1000, 1)))
    context = {
        'mixpanel_token': settings.MIXPANEL_TOKEN,
        'STATIC_URL': settings.STATIC_URL,
        'num_slack': num_slack,
        'rollbar_client_token': settings.ROLLBAR_CLIENT_TOKEN,
        'env': settings.ENV,
    }
    return context
