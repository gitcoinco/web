import json

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Bounty
from marketing.mails import new_match
from marketing.models import Match
from ratelimit.decorators import ratelimit


@ratelimit(key='ip', rate='50/m', method=ratelimit.UNSAFE, block=True)
@csrf_exempt
def save(request):

    status = 422
    message = 'Please use a POST'
    body = {}
    try:
        body = json.loads(request.body)
    except Exception:
        status = 400
        message = 'Bad Request'

    if body.get('bounty_id', False):

        # handle a POST
        bounty_id = body.get('bounty_id')
        email_address = body.get('email_address')
        direction = body.get('direction')
        github_username = body.get('github_username')

        # do validation
        validation_failed = False

        # email
        try:
            validate_email(email_address)
        except ValidationError:
            validation_failed = 'email'

        # bounty
        if not Bounty.objects.filter(pk=bounty_id).exists():
            validation_failed = 'bounty does not exist'

        # direction
        if direction not in ['+', '-']:
            validation_failed = 'direction must be either + or -'

        # github_username
        if not github_username:
            validation_failed = 'no github_username'

        # handle validation failures
        if validation_failed:
            status = 422
            message = 'Validation failed: {}'.format(validation_failed)
        else:
            bounty = Bounty.objects.get(pk=bounty_id)
            # save obj
            Match.objects.create(
                bounty=bounty,
                email=email_address,
                direction=direction,
                github_username=github_username,
            )

            # send match email
            if direction == '+':
                to_emails = [email_address, bounty.bounty_owner_email]
                new_match(to_emails, bounty, github_username)

            # response
            status = 200
            message = 'Success'

    response = {
        'status': status,
        'message': message,
    }
    return JsonResponse(response, status=status)
