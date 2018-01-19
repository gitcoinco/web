from app.github import search
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.validators import validate_slug, validate_email
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.html import strip_tags, escape
from marketing.mails import send_mail
from models import FaucetRequest
from sendgrid.helpers.mail import Content, Email, Mail, Personalization

import sendgrid
import json

def faucet(request):
    faucet_amount = getattr(settings, "FAUCET_AMOUNT", .003)
    params = {
        'title': 'Faucet',
        'faucet_amount': faucet_amount
    }

    return TemplateResponse(request, 'faucet_form.html', params)

def github_profile(request, profile):
    if FaucetRequest.objects.user(profile):
      response = {
          'status': 200,
          'name': profile
      }
      return JsonResponse(response)
    else:
      response = check_github(profile)
      return JsonResponse(response)

def check_github(profile):
  if settings.ENV == 'local':
    creds = False
  else:
    creds = True
  user = search(profile + ' in:login type:user', creds)
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
    print checkeduser
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
        github_username = githubProfile,
        github_meta = githubMeta,
        address = ethAddress,
        email = emailAddress,
        comment = comment
    )

    fr.save()
    from_email = settings.PERSONAL_CONTACT_EMAIL
    to_email = settings.SERVER_EMAIL
    subject = "New Faucet Request"
    body = "A new faucet request was completed. You may fund the request here : https://gitcoin.co/_administration/process_faucet_request/[pk]"
    send_mail(from_email, to_email, subject, body.replace('[pk]', str(fr.pk)), from_name="No Reply from Gitcoin.co")
    return JsonResponse({
      'message': 'Created.'
    }, status=201)

@staff_member_required
def process_faucet_request(request, pk):

    obj = FaucetRequest.objects.get(pk=pk)
    faucet_amount = getattr(settings, "FAUCET_AMOUNT", .003)
    context = {
        'obj': obj,
        'faucet_amount': faucet_amount
    }

    print request.POST.get('destinationAccount')
    print request.POST
    if obj.fulfilled:
        return redirect('/_administrationfaucet/faucetrequest/')

    if request.POST.get('destinationAccount', False):
        obj.fulfilled = True
        obj.save()

        return redirect('/_administrationfaucet/faucetrequest/')

    return TemplateResponse(request, 'process_faucet_request.html', context)
