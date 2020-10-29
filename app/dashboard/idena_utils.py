from datetime import datetime
from pytz import UTC
from uuid import uuid4

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

import requests

from eth_account import Account
from eth_utils import keccak, decode_hex

from app.services import RedisService

IDENA_TOKEN_KEY_PREFIX = 'idena_token'

redis = RedisService().redis

requests.request

def create_idena_token(handle):
    token = str(uuid4())
    redis.set(f'{IDENA_TOKEN_KEY_PREFIX}_{token}', handle, settings.IDENA_TOKEN_EXPIRY)
    return token

def get_handle_by_idena_token(token):
    handle = redis.get(f'{IDENA_TOKEN_KEY_PREFIX}_{token}')

    if handle is None:
        return None
    return handle.decode('utf-8')

def idena_callback_url(request, profile):
    callback_url = request.build_absolute_uri(reverse("profile_by_tab", args=("trust",)))
    nonce_endpoint = request.build_absolute_uri(reverse("start_session_idena", args=(profile.handle,)))
    authentication_endpoint = request.build_absolute_uri(reverse("authenticate_idena", args=(profile.handle,)))

    idena_token = create_idena_token(profile.handle)

    return f'dna://signin/v1?token={idena_token}&'\
           f'callback_url={callback_url}&' \
           f'nonce_endpoint={nonce_endpoint}&' \
           f'authentication_endpoint={authentication_endpoint}&' \
           f'favicon_url={settings.BASE_URL}static/v2/images/helmet.png&'

def gen_idena_nonce():
    return f'signin-{uuid4().hex}'

def signature_address(nonce, signature):
    nonce_hash = keccak(keccak(text=nonce))
    address = Account.recoverHash(nonce_hash, signature=decode_hex(signature))
    return address

def parse_datetime_from_iso(iso):
    return timezone.make_aware(
        timezone.datetime.strptime(
            iso, 
            '%Y-%m-%dT%H:%M:%SZ',
        ),
        UTC
    )

def next_validation_time():
    key = 'idena_validation_time'
    value = (redis.get(key) or b'' ).decode('utf-8')

    if not value:
        url = 'https://api.idena.io/api/Epoch/Last'
        r = requests.get(url).json()
        value = r['result']['validationTime']
        idena_validation_time = parse_datetime_from_iso(value)

        expiry = int(idena_validation_time.timestamp() - datetime.utcnow().timestamp()) # cache until next epoch
        redis.set(key, value, expiry)
    else:
        idena_validation_time = parse_datetime_from_iso(value)

    return idena_validation_time

def get_idena_status(address):
    key = f'idena_status_{address}'
    status = (redis.get(key) or b'' ).decode('utf-8')

    if not status:
        url = f'https://api.idena.io/api/Identity/{address}'
        r = requests.get(url).json()
        if 'error' in r:
            status = 'Not validated'
        else:
            status = r['result']['state']
        
        expiry = int(next_validation_time().timestamp() - datetime.utcnow().timestamp()) # cache until next epoch
        redis.set(key, status, expiry)

    return status
