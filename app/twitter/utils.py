# -*- coding: utf-8 -*-
"""Handle miscellaneous logic and utilities.

Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

import requests
import logging
import json

import oauth2 as oauth

from django.conf import settings

logger = logging.getLogger(__name__)


def get_user(user_name=None, user_id=None):
    """Get user email using twitter's GET/account/verify_credentials API
       Including user's email. Please use this API instead.
    Args:
         user_name:
         user_id:

    Returns:
        json:
    """
    if user_name[0:8] == 'twitter_':
        user_name = user_name[8:]
    consumer = oauth.Consumer(key=settings.TWITTER_CONSUMER_KEY,
                              secret=settings.TWITTER_CONSUMER_SECRET)
    signature_method_plaintext = oauth.SignatureMethod_PLAINTEXT()
    signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
    if user_id:
        request_url = f'https://api.twitter.com/1.1/account/verify_credentials.json?' \
            f'screen_id={user_id}&include_email=true'
    elif user_name:
        request_url = f'https://api.twitter.com/1.1/account/verify_credentials.json?' \
            f'screen_name={user_name}&include_email=true'
    else:
        return {}
    token_string = f'oauth_token_secret={settings.TWITTER_ACCESS_SECRET}&' \
        f'oauth_token={settings.TWITTER_ACCESS_TOKEN}'
    token = oauth.Token.from_string(token_string)
    oauth_request = oauth.Request.from_consumer_and_token(
        consumer,
        token=token,
        http_url=request_url
    )
    oauth_request.sign_request(signature_method_hmac_sha1,
                               consumer,
                               token)
    request_header = oauth_request.to_header()
    response = requests.get(request_url,
                            headers=request_header)
    raw_reply = json.loads(response.text)
    actual_reply = {'name': 'twitter_' + raw_reply['screen_name'],
                    'email': raw_reply['email'],
                    'avatar_url': raw_reply['profile_image_url_https']}
    return actual_reply


if __name__ == "__main__":
    pass
