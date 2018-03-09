import json

from django.conf import settings
from django.utils import timezone

from dashboard.models import Tip


def insert_settings(request):
    """Handle inserting pertinent data into the current context."""
    from marketing.utils import get_stat
    try:
        num_slack = int(get_stat('slack_users'))
    except Exception:
        num_slack = 0
    if num_slack > 1000:
        num_slack = f'{str(round((num_slack) / 1000, 1))}k'
    context = {
        'mixpanel_token': settings.MIXPANEL_TOKEN,
        'STATIC_URL': settings.STATIC_URL,
        'num_slack': num_slack,
        'github_handle': request.session.get('handle', False),
        'email': request.session.get('email', False),
        'name': request.session.get('name', False),
        'rollbar_client_token': settings.ROLLBAR_CLIENT_TOKEN,
        'env': settings.ENV,
    }
    context['json_context'] = json.dumps(context)

    if context['github_handle']:
        context['unclaimed_tips'] = Tip.objects.filter(
            expires_date__gte=timezone.now(),
            receive_txid='',
            username__iexact=context['github_handle'])
        if not settings.DEBUG:
            context['unclaimed_tips'] = context['unclaimed_tips'].filter(network='mainnet')

    return context
