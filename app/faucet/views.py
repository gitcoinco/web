
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.validators import validate_email, validate_slug
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.html import escape, strip_tags
from django.views.decorators.csrf import csrf_exempt

from faucet.models import FaucetRequest
from github.utils import search_github
from marketing.mails import new_faucet_request, processed_faucet_request


def faucet(request):
    faucet_amount = getattr(settings, "FAUCET_AMOUNT", .003)
    params = {
        'title': 'Faucet',
        'faucet_amount': faucet_amount
    }

    return TemplateResponse(request, 'faucet_form.html', params)


def check_github(profile):
    if settings.ENV == 'local':
        creds = False
    else:
        creds = True
    user = search_github(profile + ' in:login type:user')
    if len(user['items']) == 0 or user['items'][0]['login'].lower() != profile.lower():
       response = {
        'status': 200,
        'user': False
      }
    else:
       response = {
        'status': 200,
        'user': user['items'][0]
      }
    return response


@csrf_exempt
def save_faucet(request):
    try:
        validate_slug(request.POST.get('githubProfile'))
    except Exception as e:
        return JsonResponse({
          'message': e.messages[0]
        }, status=400)

    try:
        validate_email(request.POST.get('emailAddress'))
    except Exception as e:
        return JsonResponse({
          'message': e.messages[0]
        }, status=400)

    try:
        validate_slug(request.POST.get('ethAddress'))
    except Exception as e:
        return JsonResponse({
          'message': e.messages[0]
        }, status=400)
    githubProfile = request.POST.get('githubProfile')
    emailAddress = request.POST.get('emailAddress')
    ethAddress = request.POST.get('ethAddress')
    comment = escape(strip_tags(request.POST.get('comment')))
    checkeduser = check_github(githubProfile)
    if FaucetRequest.objects.user(githubProfile):
        return JsonResponse({
            'message': 'The submitted github profile shows a previous faucet distribution.'
        }, status=403)
    elif checkeduser == False:
        return JsonResponse({
          'message': 'The submitted github profile could not be found on github.'
        }, status=400)
    else:
        githubMeta = checkeduser

    fr = FaucetRequest(
        fulfilled=False,
        github_username=githubProfile,
        github_meta=githubMeta,
        address=ethAddress,
        email=emailAddress,
        comment=comment
    )

    fr.save()

    new_faucet_request(fr)

    return JsonResponse({
      'message': 'Created.'
    }, status=201)


@staff_member_required
def process_faucet_request(request, pk):

    obj = FaucetRequest.objects.get(pk=pk)
    faucet_amount = settings.FAUCET_AMOUNT
    context = {
        'obj': obj,
        'faucet_amount': faucet_amount
    }

    if obj.fulfilled:
        return redirect('/_administrationfaucet/faucetrequest/')

    if request.POST.get('destinationAccount', False):
        obj.fulfilled = True
        obj.fulfill_date = timezone.now()
        obj.save()
        processed_faucet_request(obj)

        return redirect('/_administrationfaucet/faucetrequest/')

    return TemplateResponse(request, 'process_faucet_request.html', context)
