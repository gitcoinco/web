from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import EmailPreferenceLog


@csrf_exempt
@require_POST
def email_preference_log(request):

    if not request.user.is_authenticated:
        return JsonResponse(
            { 'error': _('You must be authenticated') },
            status=401
        )

    user_id = 77
    destination = 'hubspot'
    event_data = {'hello': 'hello'}
    response_data = {'hallo': 'hallo'}

    try:
        log =  EmailPreferenceLog(
            user_id=user_id,
            destination=destination,
            event_data=event_data,
            response_data=response_data
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
