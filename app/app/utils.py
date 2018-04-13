import email
import imaplib
import logging
import time

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geoip2 import GeoIP2
from django.utils import timezone

import requests
import rollbar
from dashboard.models import Profile
from geoip2.errors import AddressNotFoundError
from github.utils import _AUTH, HEADERS, get_user
from ipware.ip import get_real_ip
from marketing.utils import get_or_save_email_subscriber
from social_django.models import UserSocialAuth

logger = logging.getLogger(__name__)


def ellipses(data, _len=75):
    return (data[:_len] + '..') if len(data) > _len else data


def add_contributors(repo_data):
    """Add contributor data to repository data dictionary.

    Args:
        repo_data (dict): The repository data dictionary to be updated.

    Returns:
        dict: The updated repository data dictionary.

    """
    if repo_data.get('fork', False):
        return repo_data

    params = {}
    url = repo_data['contributors_url']
    response = requests.get(url, auth=_AUTH, headers=HEADERS, params=params)
    if response.status_code == 204:  # no content
        return repo_data

    response_data = response.json()
    rate_limited = (isinstance(response_data, dict) and 'documentation_url' in response_data.keys())
    if rate_limited:
        # retry after rate limit
        time.sleep(60)
        return add_contributors(repo_data)

    # no need for retry
    repo_data['contributors'] = response_data
    return repo_data


def sync_profile(handle, user=None):
    data = get_user(handle)
    email = ''
    is_error = 'name' not in data.keys()
    if is_error:
        print("- error main")
        rollbar.report_message('Failed to fetch github username', 'warning', extra_data=data)
        return None

    repos_data = get_user(handle, '/repos')
    repos_data = sorted(repos_data, key=lambda repo: repo['stargazers_count'], reverse=True)
    repos_data = [add_contributors(repo_data) for repo_data in repos_data]

    defaults = {
        'last_sync_date': timezone.now(),
        'data': data,
        'repos_data': repos_data,
    }

    if user and isinstance(user, User):
        defaults['user'] = user
        try:
            defaults['github_access_token'] = user.social_auth.filter(provider='github').latest('pk').access_token
            if user and user.email:
                defaults['email'] = user.email
        except UserSocialAuth.DoesNotExist:
            pass

    # store the org info in postgres
    try:
        profile, created = Profile.objects.update_or_create(handle=handle, defaults=defaults)
        print("Profile:", profile, "- created" if created else "- updated")
    except Exception as e:
        logger.error(e)
        return None

    if user and user.email:
        email = user.email
    elif profile and profile.email:
        email = profile.email

    if email and profile:
        get_or_save_email_subscriber(email, 'sync_profile', profile=profile)

    return profile


def fetch_last_email_id(email_id, password, host='imap.gmail.com', folder='INBOX'):
    mailbox = imaplib.IMAP4_SSL(host)
    try:
        mailbox.login(email_id, password)
    except imaplib.IMAP4.error:
        return None
    response, last_message_set_id = mailbox.select(folder)
    if response != 'OK':
        return None
    return last_message_set_id[0].decode('utf-8')


def fetch_mails_since_id(email_id, password, since_id=None, host='imap.gmail.com', folder='INBOX'):
    # searching via id becuase imap does not support time based search and has only date based search
    mailbox = imaplib.IMAP4_SSL(host)
    try:
        mailbox.login(email_id, password)
    except imaplib.IMAP4.error:
        return None
    mailbox.select(folder)
    _, all_ids = mailbox.search(None, "ALL")
    all_ids = all_ids[0].decode("utf-8").split()
    print(all_ids)
    if since_id:
        ids = all_ids[all_ids.index(str(since_id))+1:]
    else:
        ids = all_ids
    emails = {}
    for fetched_id in ids:
        _, content = mailbox.fetch(str(fetched_id), '(RFC822)')
        emails[str(id)] = email.message_from_string(content[0][1])
    return emails


def itermerge(gen_a, gen_b, key):
    a = None
    b = None

    # yield items in order until first iterator is emptied
    try:
        while True:
            if a is None:
                a = gen_a.next()

            if b is None:
                b = gen_b.next()

            if key(a) <= key(b):
                yield a
                a = None
            else:
                yield b
                b = None
    except StopIteration:
        # yield last item to be pulled from non-empty iterator
        if a is not None:
            yield a

        if b is not None:
            yield b

    # flush remaining items in non-empty iterator
    try:
        for a in gen_a:
            yield a
    except StopIteration:
        pass

    try:
        for b in gen_b:
            yield b
    except StopIteration:
        pass


def handle_location_request(request):
    """Handle determining location data from request IP."""
    ip_address = '24.210.224.38' if settings.DEBUG else get_real_ip(request)
    geolocation_data = {}
    if ip_address:
        geolocation_data = get_location_from_ip(ip_address)
    return geolocation_data, ip_address


def get_location_from_ip(ip_address):
    """Get the location associated with the provided IP address.

    Args:
        ip_address (str): The IP address to lookup.

    Returns:
        dict: The GeoIP location data dictionary.

    """
    city = {}
    if not ip_address:
        return city

    try:
        geo = GeoIP2()
        try:
            city = geo.city(ip_address)
        except AddressNotFoundError:
            pass
    except Exception as e:
        logger.warning(f'Encountered ({e}) while attempting to retrieve a user\'s geolocation')
    return city
