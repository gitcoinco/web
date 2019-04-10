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
import hmac
import base64
import hashlib
import datetime
import secrets
import json

import oauth2 as oauth

from django.conf import settings

logger = logging.getLogger(__name__)


def request_oauth_token(callback_url='example.com/callback'):
    """Obtain a request token from Twitter OAth API.

    Args:
        callback_url (str): URL for the Twitter OAuth API to call back.

    Returns:
        Dict: A dict containing received parameters.
    """
    url = 'https://api.twitter.com/oauth/request_token'
    callback_url_percent = percent_encoding(callback_url)
    key = settings.TWITTER_CONSUMER_KEY
    nonce = generate_nonce()
    timestamp = generate_timestamp()
    signature = generate_hmac(1, nonce, timestamp, callback=callback_url_percent)
    signature = str(signature)[2:-1]
    signature = percent_encoding(signature)

    authorization_header = f'OAuth ' \
        f'oauth_nonce="{nonce}",' \
        f'oauth_callback="{callback_url_percent}",' \
        f'oauth_signature_method="HMAC-SHA1",' \
        f'oauth_timestamp="{timestamp}",' \
        f'oauth_consumer_key="{key}",' \
        f'oauth_signature="{signature}",' \
        f'oauth_version="1.0"'

    logger_m('header: ' + authorization_header)

    try:
        response = requests.post(url,
                                 headers={'Accept': '*/*',
                                          'Authorization': authorization_header},
                                 data={'oauth_callback': callback_url})
        # To be formatted....
        logger_m(response.text)
        return response_to_json(response.text)
    except Exception as e:
        logger.error("Could not get OAuth token - Reason: %s - Auth Header: %s",
                     e, authorization_header)
        logger_m(str(e))
        logger_m(authorization_header)
    return {}


def request_oauth_token_with_lib(callback_url='example.com/callback'):
    """Obtain a request token from Twitter OAth API.
        Using oauth2 library.

    Args:
        callback_url (str): URL for the Twitter OAuth API to call back.

    Returns:
        Dict: A dict containing received parameters.
    """
    consumer = oauth.Consumer(key=settings.TWITTER_CONSUMER_KEY,
                              secret=settings.TWITTER_CONSUMER_SECRET)
    signature_method_plaintext = oauth.SignatureMethod_PLAINTEXT()
    signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
    request_url = 'https://api.twitter.com/oauth/request_token'

    token_string=f'oauth_token_secret={settings.TWITTER_ACCESS_SECRET}&' \
        f'oauth_token={settings.TWITTER_ACCESS_TOKEN}'
    token = oauth.Token.from_string(token_string)
    token.set_callback(callback_url)
    oauth_request = oauth.Request.from_consumer_and_token(
        consumer,
        token=token,
        http_method='POST',
        http_url=request_url
    )
    oauth_request.sign_request(signature_method_hmac_sha1,
                               consumer,
                               token)
    request_header=oauth_request.to_header()
    logger_m(request_header)
    response = requests.post(request_url, headers=request_header)
    logger_m(response.text)
    return response_to_json(response.text)


def access_oauth_token(token, verify_str):
    """Convert the request token to an access token.

    Args:
        token (str):
        verify_str (str):

    Returns:
        Dict: A dict containing received parameters.
    """
    url = 'https://api.twitter.com/oauth/access_token'
    key = settings.TWITTER_CONSUMER_KEY
    nonce = generate_nonce()
    timestamp = generate_timestamp()
    signature = generate_hmac(3, nonce, timestamp, token)

    authorization_header = f'OAuth ' \
        f'oauth_consumer_key="{key}",' \
        f'oauth_nonce="{nonce}",' \
        f'oauth_signature="{signature}",' \
        f'oauth_signature_method="HMAC-SHA1",' \
        f'oauth_timestamp="{timestamp}",' \
        f'oauth_token={token}' \
        f'oauth_verifier="{verify_str}"' \
        f'oauth_version="1.0"'

    try:
        response = requests.post(url, headers={'Accept': '*/*',
                                               'Authorization': authorization_header})
        # To be formatted....
        logger_m(response.text)
        return response_to_json(response.text)
    except Exception as e:
        logger.error("Could not get OAuth token - Reason: %s - Auth Header: %s",
                     e, authorization_header)
        logger_m(str(e))
        logger_m(authorization_header)
    return {}


def response_to_json(response_str):
    """Convert response string into json format.

    Args:
        response_str (str): Response string form web, encoded ( a=b&c=d )

    Returns:
        response_dict (json): Json format of data.
    """
    response_dict = {}
    try:
        parameter_part = response_str.split('&')
        for every_parameter in parameter_part:
            key_value_pair = every_parameter.split('=')
            response_dict[key_value_pair[0]] = key_value_pair[1]
        return response_dict
    except Exception as e:
        logger.error("Could not convert the string due to wrong format - Reason: %s", e)
        logger_m(str(e))
    return {}


def generate_timestamp():
    """Generate timestamp for request in the first step.
       The number is the seconds since the Unix epoch.

    Args: None

    Returns:
        time_str (str): Be caution! It is a string.
    """
    return datetime.datetime.now().strftime('%s')


def generate_nonce():
    """Generate a random nonce for the request in first step.
       The nonce is a random string in base64 format with length of 32 bytes .

    Args: None

    Returns:
        nonce (str): 32-byte nonce.
    """
    return secrets.token_hex(16)


def generate_hmac(step, nonce, timestamp, token=None, callback=None):
    """Generate HMAC-SHA1 signature for the request in first step.

    Args:
        callback (str): The callback url,
                    For obtain token only.
        step (int): Obtain token: 1; Access token: 3.
        nonce (str): Random nonce word.
        timestamp (str): Seconds since the Unix epoch
        token (str): Old token to access for a new token.
                    For accessing new token only.

    Return:
        signature (str): Encoded string.
    """
    msg = ''
    if step == 1:
        msg = f'POST&https%3A%2F%2Fapi.twitter.com%2Foauth%2Frequest_token&' \
            f'oauth_callback%3D{callback}' \
            f'%26oauth_consumer_key%3D{settings.TWITTER_CONSUMER_KEY}' \
            f'%26oauth_nonce%3D{nonce}' \
            f'%26oauth_signature_method%3DHMAC-SHA1' \
            f'%26oauth_timestamp%3D{timestamp}' \
            f'%26oauth_token%3D{settings.TWITTER_ACCESS_TOKEN}' \
            f'%26oauth_version%3D1.0'
    elif step == 3:
        msg = f'POST&https%3A%2F%2Fapi.twitter.com%2Foauth%2Faccess_token&' \
            f'oauth_consumer_key%3D{settings.TWITTER_CONSUMER_KEY}' \
            f'%26oauth_nonce%3D{nonce}' \
            f'%26oauth_signature_method%3DHMAC-SHA1' \
            f'%26oauth_timestamp%3D{timestamp}' \
            f'%26oauth_token%3D{token}' \
            f'%26oauth_version%3D1.0'

    logger_m(msg)

    key = settings.TWITTER_CONSUMER_SECRET
    key += '&'
    key += settings.TWITTER_ACCESS_SECRET
    logger_m(key)

    message_bytes = bytes(msg, 'ascii')
    key_bytes = bytes(key, 'ascii')

    signature = base64.b64encode(
        hmac.new(key_bytes, message_bytes, digestmod=hashlib.sha1).digest())

    logger_m(str(signature))

    return signature


def percent_encoding(str_raw):
    """Convert string into Percent Encoding value.

    Args:
        str_raw (str): String to be converted.

    Returns:
        str_raw (str): Encoded str.
    """
    str_raw = str_raw.replace('=', '%3D')
    str_raw = str_raw.replace('+', '%2B')
    str_raw = str_raw.replace('/', '%2F')
    str_raw = str_raw.replace(':', '%3A')
    return str_raw


def logger_m(msg_raw):
    msg = str(msg_raw)
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = time_str + ': ' + msg + '\n'
    print(msg)
    with open('log272503', 'a') as fo:
        fo.write(msg)


if __name__ == "__main__":
    pass
