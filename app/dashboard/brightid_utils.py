import json
import time
import requests
import base64
import ed25519
from django.conf import settings

def get_brightid_status(brightid_uuid):
    brightIDUrl = 'http://node.brightid.org/brightid/v4/verifications/Gitcoin/' + str(brightid_uuid)

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
    brightIDv5OpUrl = 'http://node.brightid.org/brightid/v5/operations'

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

    if 200 == response.status_code:
        # {'data': {'hash': 'LVleLJw0siU7C47-MhpVXZTfhpJl2AXvNr-Vx2N11sI'}}
        return True
    else:
        return False

def get_verified_uuids():
    endpointURL = 'https://app.brightid.org/node/v5/verifications/Gitcoin'

    try:
        response = requests.get(endpointURL)
        responseData = response.json()
        approved_uuids = responseData.get('data', {}).get('contextIds', [])

        return approved_uuids
    except:
        return []

