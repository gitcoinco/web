from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .models import EmailPreferenceLog


@csrf_exempt
@require_POST
def email_preference_log(request):

    if not request.user.is_authenticated:
        return JsonResponse(
            { 'error': _('You must be authenticated') },
            status=401
        )

    event_data = request.body.decode('utf-8')
    if event_data:
        event_data = json.loads(event_data)

    try:
        log = EmailPreferenceLog(
            destination='hubspot',
            event_data=event_data
        )
        log.save()
        return JsonResponse(
            {
                'success': True,
                'msg': 'Data saved'
            },
            status=200
        )
    except Exception:
        return JsonResponse(
            {'error': _('Something went wrong with saving the request')},
            status=401
        )
