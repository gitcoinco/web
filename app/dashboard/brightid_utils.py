import base64
import json
import time

from django.conf import settings

import ed25519
import requests


def get_brightid_status(brightid_uuid):
    brightIDUrl = 'https://app.brightid.org/node/v5/verifications/Gitcoin/' + str(brightid_uuid)

    try:
        response = requests.get(brightIDUrl)
        responseData = response.json()
        isVerified = responseData.get('data', {}).get('unique', False) and responseData.get('data', {}).get('context', '') == 'Gitcoin'

        if isVerified:
            return 'verified'
        # NOT CONNECTED
        elif responseData['errorNum'] == 2:
            return 'not_connected'
        # CONNECTED NOT SPONSORED
        elif responseData['errorNum'] == 4:
            sponsor_success = assign_brightid_sponsorship(brightid_uuid)

            if sponsor_success:
                return 'not_verified'
            else:
                return 'unknown'
        # CONNECTED AND SPONSORED, NOT VERIFIED
        elif responseData['errorNum'] == 3:
            return 'not_verified'
        else:
            return 'unknown'
    except:
        return 'unknown'

def assign_brightid_sponsorship(brightid_uuid):
    brightIDv5OpUrl = 'https://app.brightid.org/node/v5/operations'

    op = {
        'name': 'Sponsor',
        'app': 'Gitcoin',
        'contextId': str(brightid_uuid),
        'timestamp': int(time.time()*1000),
        'v': 5
    }

    signing_key = ed25519.SigningKey(base64.b64decode(settings.BRIGHTID_PRIVATE_KEY))
    message = json.dumps(op, sort_keys=True, separators=(',', ':')).encode('ascii')
    sig = signing_key.sign(message)
    op['sig'] = base64.b64encode(sig).decode('ascii')

    response = requests.post(brightIDv5OpUrl, json.dumps(op))
    return 200 == response.status_code

def get_verified_uuids():
    endpointURL = 'https://app.brightid.org/node/v5/verifications/Gitcoin'

    try:
        response = requests.get(endpointURL)
        responseData = response.json()
        approved_uuids = responseData.get('data', {}).get('contextIds', [])

        return approved_uuids
    except:
        return []
