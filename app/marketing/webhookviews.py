import json
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

import pytz
from marketing.models import EmailEvent


# https://sendgrid.com/docs/API_Reference/Webhooks/event.html 
example = """
[
  {
    "email":"john.doe@sendgrid.com",
    "timestamp": 1337197600,
    "smtp-id":"<4FB4041F.6080505@sendgrid.com>",
    "sg_event_id":"sendgrid_internal_event_id",
    "sg_message_id":"sendgrid_internal_message_id",
    "event": "processed"
  },
  {
    "email":"john.doe@sendgrid.com",
    "timestamp": 1337966815,
    "ip":"X.XX.XXX.XX",
    "sg_event_id":"sendgrid_internal_event_id",
    "url":"https://sendgrid.com",
    "sg_message_id":"sendgrid_internal_message_id",
    "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "event":"click"
  },
  {
    "ip": "X.XX.XXX.XX",
    "sg_user_id": 123,
    "sg_event_id":"sendgrid_internal_event_id",
    "sg_message_id":"sendgrid_internal_message_id",
    "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "event": "group_unsubscribe",
    "email": "john.doe@sendgrid.com",
    "timestamp": 1337969592,
    "asm_group_id": 42
  }
]

"""


@csrf_exempt
def process(request):
    response = json.loads(request.body)
    for event in response:
        created_on = datetime.utcfromtimestamp(event['timestamp']).replace(tzinfo=pytz.utc)

        EmailEvent.objects.create(
            email=event['email'],
            event=event['event'],
            created_on=created_on,
            payload=event,
            )

    return HttpResponse('Thanks!')
