import email
import functools
import imaplib
import json
import logging
import multiprocessing.pool
import os
import re
import time
from hashlib import sha1
from secrets import token_hex

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geoip2 import GeoIP2
from django.db.models import Lookup
from django.db.models.fields import Field
from django.utils import timezone
from django.utils.translation import LANGUAGE_SESSION_KEY

import geoip2.database
import requests
from avatar.models import SocialAvatar
from avatar.utils import get_user_github_avatar_image
from geoip2.errors import AddressNotFoundError
from git.utils import get_user
from ipware.ip import get_real_ip
from marketing.utils import get_or_save_email_subscriber
from social_core.backends.github import GithubOAuth2
from social_django.models import UserSocialAuth

logger = logging.getLogger(__name__)


@Field.register_lookup
class NotEqual(Lookup):
    """Allow lookup and exclusion using not equal."""

    lookup_name = 'ne'

    def as_sql(self, compiler, connection):
        """Handle as SQL method for not equal lookup."""
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f'{lhs} <> {rhs}', params


def ellipses(data, _len=75):
    return (data[:_len] + '..') if len(data) > _len else data


def setup_lang(request, user):
    """Handle setting the user's language preferences and store in the session.

    Args:
        request (Request): The Django request object.
        user (User): The Django user object.

    Raises:
        DoesNotExist: The exception is raised if no profile is found for the specified handle.

    """
    from dashboard.models import Profile
    profile = None
    if user.is_authenticated and hasattr(user, 'profile'):
        profile = user.profile
    else:
        try:
            profile = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            pass
    if profile:
        request.session[LANGUAGE_SESSION_KEY] = profile.get_profile_preferred_language()
        request.session.modified = True


def get_upload_filename(instance, filename):
    salt = token_hex(16)
    file_path = os.path.basename(filename)
    return f"docs/{getattr(instance, '_path', '')}/{salt}/{file_path}"


def sync_profile(handle, user=None, hide_profile=True, delay_okay=False):
    from dashboard.models import Profile
    handle = handle.strip().replace('@', '').lower()
    profile = Profile.objects.filter(handle=handle).exists()
    # cant sync_profile if profile not existing, especially if profile is needed for login
    delay = delay_okay and profile
    if delay:
        from dashboard.tasks import sync_profile as sync_profile_task
        user_pk = user.pk if user else None
        sync_profile_task.delay(handle, user_pk, hide_profile)
    else:
        actually_sync_profile(handle, user=user, hide_profile=hide_profile)


def actually_sync_profile(handle, user=None, hide_profile=True):
    from dashboard.models import Profile
    handle = handle.strip().replace('@', '').lower()
    if user and hasattr(user, 'profile'):
        try:
            access_token = user.social_auth.filter(provider='github').latest('pk').access_token
            data = get_user(handle, token=access_token)

            user = User.objects.get(username__iexact=handle)
            if data and data.login:
                profile = user.profile
                user.username = data.login
                user.save()
                profile.handle = data.login
                profile.email = user.email
                profile.save()

        except Exception as e:
            logger.error(e)
            return None
    else:
        data = get_user(handle)

    email = ''
    is_error = not hasattr(data, 'name')
    if is_error:
        print("- error main")
        logger.warning(f'Failed to fetch github username {handle}', exc_info=True, extra={'handle': handle})
        return None

    defaults = {'last_sync_date': timezone.now(), 'data': data.raw_data}

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
        profile_exists = Profile.objects.filter(handle=handle).count()
        if not profile_exists:
            defaults['hide_profile'] = hide_profile
        profile, created = Profile.objects.update_or_create(handle=handle, defaults=defaults)
        latest_obj = profile.user.social_auth.filter(provider='github').latest('pk') if profile.user else None
        access_token = latest_obj.access_token if latest_obj else None
        orgs = get_user(handle, token=access_token).get_orgs()
        profile.organizations = [ele.login for ele in orgs if ele] if orgs else []
        print("Profile:", profile, "- created" if created else "- updated")
        keywords = []
        if get_user(handle):
            for repo in get_user(handle).get_repos():
                language = repo.language or ''
                _keywords = language.split(',')
                for key in _keywords:
                    if key != '' and key not in keywords:
                        keywords.append(key)

            profile.keywords = keywords
        profile.save()
    except UserSocialAuth.DoesNotExist:
        pass
    except Exception as e:
        logger.exception(e)
        return None

    if user and user.email:
        email = user.email
    elif profile and profile.email:
        email = profile.email

    if email and profile:
        profile.email = email
        profile.save()
        get_or_save_email_subscriber(email, 'sync_profile', profile=profile)

    if profile and not profile.github_access_token:
        token = profile.get_access_token(save=False)
        profile.github_access_token = token
        profile.save()

    if profile and not profile.avatar_baseavatar_related.last():
        github_avatar_img = get_user_github_avatar_image(profile.handle)
        if github_avatar_img:
            try:
                github_avatar = SocialAvatar.github_avatar(profile, github_avatar_img)
                github_avatar.save()
                profile.activate_avatar(github_avatar.pk)
                profile.save()
            except Exception as e:
                logger.warning(f'Encountered ({e}) while attempting to save a user\'s github avatar')

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
        ids = all_ids[all_ids.index(str(since_id)) + 1:]
    else:
        ids = all_ids
    emails = {}
    for fetched_id in ids:
        _, content = mailbox.fetch(str(fetched_id), '(RFC822)')
        emails[str(id)] = email.message_from_string(content[0][1])
    return emails


def handle_location_request(request):
    """Handle determining location data from request IP."""
    ip_address = '24.210.224.38' if settings.DEBUG else get_real_ip(request)
    geolocation_data = {}
    if ip_address:
        geolocation_data = get_location_from_ip(ip_address)
    return geolocation_data, ip_address


geoIPobject = None
geoIPCountryobject = None


def get_geoIP_singleton():
    global geoIPobject
    if not geoIPobject:
        geoIPobject = GeoIP2()
    return geoIPobject


def get_geoIP_country_singleton():
    global geoIPCountryobject
    db = f'{settings.GEOIP_PATH}GeoLite2-Country.mmdb'
    if not geoIPCountryobject:
        geoIPCountryobject = geoip2.database.Reader(db)
    return geoIPCountryobject


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
        geo = get_geoIP_singleton()
        try:
            city = geo.city(ip_address)
        except AddressNotFoundError:
            pass
    except Exception as e:
        logger.warning(f'Encountered ({e}) while attempting to retrieve a user\'s geolocation')
    return city


def get_country_from_ip(ip_address):
    """Get the user's country information from the provided IP address."""
    country = {}

    if not ip_address:
        return country

    try:
        reader = get_geoIP_country_singleton()
        country = reader.country(ip_address)
    except AddressNotFoundError:
        pass
    except Exception as e:
        logger.warning(f'Encountered ({e}) while attempting to retrieve a user\'s geolocation')

    return country


def clean_str(string):
    """Clean the provided string of all non-alpha numeric characters."""
    return re.sub(r'\W+', '', string)


def get_default_network():
    if settings.DEBUG:
        return 'rinkeby'
    return 'mainnet'


def get_semaphore(namespace, count=1, db=None, blocking=False, stale_client_timeout=60):
    from redis import Redis
    from redis_semaphore import Semaphore
    from urllib.parse import urlparse
    redis = urlparse(settings.SEMAPHORE_REDIS_URL)

    if db is None:
        db = int(redis.path.lstrip('/'))

    semaphore = Semaphore(
        Redis(host=redis.hostname, port=redis.port, db=db),
        count=count,
        namespace=namespace,
        blocking=blocking,
        stale_client_timeout=stale_client_timeout,
    )
    return semaphore


def release_semaphore(namespace, semaphore=None):
    if not semaphore:
        semaphore = get_semaphore(namespace)

    token = semaphore.get_namespaced_key(namespace)
    semaphore.signal(token)


def get_profile(request):
    """Get the current profile from the provided request.

    Returns:
        dashboard.models.Profile: The current user's Profile.

    """
    is_authed = request.user.is_authenticated
    profile = getattr(request.user, 'profile', None) if is_authed else None

    if is_authed and not profile:
        profile = sync_profile(request.user.username, request.user, hide_profile=False)

    return profile


class CustomGithubOAuth2(GithubOAuth2):
    EXTRA_DATA = [('scope', 'scope'), ]

    def get_scope(self):
        scope = super(CustomGithubOAuth2, self).get_scope()
        if self.data.get('extrascope'):
            scope += ['public_repo', 'read:org']
            from dashboard.management.commands.sync_orgs_repos import Command
            Command().handle()
        return scope


def get_profiles_from_text(text):
    from dashboard.models import Profile

    username_pattern = re.compile(r'@(\S+)')
    mentioned_usernames = re.findall(username_pattern, text)
    return Profile.objects.filter(handle__in=mentioned_usernames).distinct()


def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""

    def timeout_decorator(item):
        """Wrap the original function."""

        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)

        return func_wrapper

    return timeout_decorator


def notion_write(database_id='', payload=None):
    # write to the pages api (https://developers.notion.com/reference/post-page)
    url = "https://api.notion.com/v1/pages"
    # define the parent (database) that we're writing to and set the properties (row content)
    body = {"parent": {"type": "database_id", "database_id": database_id}, "properties": payload}

    # return success as dict
    return notion_api_call(url, body)


def notion_read(database_id, payload=None):
    # read from the database query api (https://developers.notion.com/docs/working-with-databases)
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    # return success as dict
    return notion_api_call(url, payload)


def notion_api_call(url='', payload=None):
    # retrieve auth from headers
    headers = {
        "Authorization": f"Bearer {settings.NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2021-05-13"
    }
    # default the body to empty dict
    body = payload if isinstance(payload, dict) else {}
    # print({'url':url, 'headers':json.dumps(headers), 'data':json.dumps(body)})
    response = requests.post(url=url, headers=headers, data=json.dumps(body))

    # throw exception if we dont get a 200 response
    if response.status_code != 200:
        raise Exception("Failed to set to/get from notion")

    # return success as dict
    return response


def allow_all_origins(response):
    """Pass in a response and add header to allow all CORs requests"""

    response["Access-Control-Allow-Origin"] = "*"

    return response
