import json
import logging

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Bounty, Interest, Profile
from git.utils import get_github_user_data
from marketing.mails import new_match
from marketing.models import Match
from ratelimit.decorators import ratelimit

logging.basicConfig(level=logging.DEBUG)


@ratelimit(key='ip', rate='50/m', method=ratelimit.UNSAFE, block=True)
@csrf_exempt
def save(request):
    status = 422
    message = 'The IOS app is disabled'
    response = {
        'status': status,
        'message': message,
    }
    return JsonResponse(response, status=status)
