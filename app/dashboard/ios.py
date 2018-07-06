import json
import logging

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Bounty, Interest, Profile
from github.utils import get_github_user_data
from marketing.mails import new_match
from marketing.models import Match
from ratelimit.decorators import ratelimit

logging.basicConfig(level=logging.DEBUG)


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
        access_token = body.get('token') if body.get('token') else request.GET.get('token')
        github_username = body.get('github_username')
        try:
            github_user_data = get_github_user_data(access_token)
        except Exception:
            github_user_data = {}
        access_token_invalid = not access_token or github_user_data.get('login') != github_username
        if access_token_invalid:
            status = 405
            message = f'Not authorized or invalid github token for github user {github_username}'
        else:
            # handle a POST
            bounty_id = body.get('bounty_id')
            email_address = body.get('email_address')
            direction = body.get('direction')

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
                message = f'Validation failed: {validation_failed}'
            else:
                bounty = Bounty.objects.get(pk=bounty_id)
                # save obj
                Match.objects.create(
                    bounty=bounty,
                    email=email_address,
                    direction=direction,
                    github_username=github_username,
                )

                try:
                    if direction == '+':
                        profiles = Profile.objects.filter(handle=github_username)
                        profile = profiles.first() if profiles.exists() else None
                        interest = Interest.objects.create(profile_id=profile.pk)
                        bounty.interested.add(interest)
                        # TODO -- user create_new_interest_helper
                except Exception as e:
                    print(f'could not get profile {e}')
                    logging.exception(e)

                # send match email
                if direction == '+':
                    to_emails = [email_address, bounty.bounty_owner_email]
                    # KO 2018/05/07 -- do not send match emails for ios
                    # since intros happen on the github thread.
                    # new_match(to_emails, bounty, github_username)

                # response
                status = 200
                message = 'Success'
    response = {
        'status': status,
        'message': message,
    }
    return JsonResponse(response, status=status)
