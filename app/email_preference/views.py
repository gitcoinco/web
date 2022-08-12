from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST

from .models import EmailPreferenceLog


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
    except Exception:
        pass


# @csrf_exempt
# def mautic_api(request, endpoint=''):
#
#     if request.user.is_authenticated:
#         response = mautic_proxy(request, endpoint)
#         return response
#     else:
#         return JsonResponse(
#             { 'error': _('You must be authenticated') },
#             status=401
#         )
#
#
# def mautic_proxy(request, endpoint=''):
#     params = request.GET
#     if request.method == 'GET':
#         response = mautic_proxy_backend(request.method, endpoint, None, params)
#     elif request.method in ['POST','PUT','PATCH','DELETE']:
#         response = mautic_proxy_backend(request.method, endpoint, request.body, params)
#
#     return JsonResponse(response)
#
#
# def mautic_proxy_backend(method="GET", endpoint='', payload=None, params=None):
#     # print(method, endpoint, payload, params)
#     credential = f"{settings.MAUTIC_USER}:{settings.MAUTIC_PASSWORD}"
#     token = base64.b64encode(credential.encode("utf-8")).decode("utf-8")
#     headers = {"Authorization": f"Basic {token}"}
#     url = f"https://gitcoin-5fd8db9bd56c8.mautic.net/api/{endpoint}"
#
#     if payload:
#         body_unicode = payload.decode('utf-8')
#         payload = json.loads(body_unicode)
#         http_response = getattr(requests, method.lower())(url=url, headers=headers, params=params, data=json.dumps(payload))
#     else:
#         http_response = getattr(requests, method.lower())(url=url, headers=headers, params=params)
#
#     response = http_response.json()
#
#
#     # Temporary logging of Mautic interaction in order to prepare for a move over from Mautic to Hubspot.
#     try:
#         log = MauticLog(method=method, endpoint=endpoint, payload=payload, params=params, status_code=http_response.status_code)
#         log.save()
#     except Exception:
#         pass
#
#     return response
#
#
# @csrf_exempt
# @require_POST
# def mautic_profile_save(request):
#
#     if request.user.is_authenticated:
#         profile = request.user.profile if hasattr(request.user, 'profile') else None
#         if not profile:
#             return JsonResponse(
#                 { 'error': _('You must be authenticated') },
#                 status=401
#             )
#         mautic_id = request.POST.get('mtcId')
#         profile.mautic_id = mautic_id
#         profile.save()
#
#     else:
#         return JsonResponse(
#             { 'error': _('You must be authenticated') },
#             status=401
#         )
#
#     return JsonResponse(
#         {
#             'success': True,
#             'msg': 'Data saved'
#         },
#         status=200
#     )
