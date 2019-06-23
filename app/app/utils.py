import email
import imaplib
import logging
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
from avatar.utils import get_svg_templates, get_user_github_avatar_image
from geoip2.errors import AddressNotFoundError
from git.utils import _AUTH, HEADERS, get_user
from ipware.ip import get_real_ip
from marketing.utils import get_or_save_email_subscriber
from pyshorteners import Shortener
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


def get_query_cache_key(compiler):
    """Generate a cache key from a SQLCompiler.

    This cache key is specific to the SQL query and its context
    (which database is used).  The same query in the same context
    (= the same database) must generate the same cache key.

    Args:
        compiler (django.db.models.sql.compiler.SQLCompiler): A SQLCompiler
            that will generate the SQL query.

    Returns:
        int: The cache key.

    """
    sql, params = compiler.as_sql()
    cache_key = f'{compiler.using}:{sql}:{[str(p) for p in params]}'
    return sha1(cache_key.encode('utf-8')).hexdigest()


def get_table_cache_key(db_alias, table):
    """Generates a cache key from a SQL table.

    Args:
        db_alias (str): The alias of the used database.
        table (str): The name of the SQL table.

    Returns:
        int: The cache key.

    """
    cache_key = f'{db_alias}:{table}'
    return sha1(cache_key.encode('utf-8')).hexdigest()


def get_raw_cache_client(backend='default'):
    """Get a raw Redis cache client connection.

    Args:
        backend (str): The backend to attempt connection against.

    Raises:
        Exception: The exception is raised/caught if any generic exception
            is encountered during the connection attempt.

    Returns:
        redis.client.StrictRedis: The raw Redis client connection.
            If an exception is encountered, return None.

    """
    from django_redis import get_redis_connection
    try:
        return get_redis_connection(backend)
    except Exception as e:
        logger.error(e)
        return None


def get_short_url(url):
    is_short = False
    for shortener in ['Tinyurl', 'Adfly', 'Isgd', 'QrCx']:
        try:
            if not is_short:
                shortener = Shortener(shortener)
                response = shortener.short(url)
                if response != 'Error' and 'http' in response:
                    url = response
                is_short = True
        except Exception:
            pass
    return url


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


def sync_profile(handle, user=None, hide_profile=True):
    from dashboard.models import Profile
    handle = handle.strip().replace('@', '').lower()
    data = get_user(handle)
    email = ''
    is_error = 'name' not in data.keys()
    if is_error:
        print("- error main")
        logger.warning('Failed to fetch github username', exc_info=True, extra={'handle': handle})
        return None

    defaults = {'last_sync_date': timezone.now(), 'data': data, 'hide_profile': hide_profile, }

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
        orgs = get_user(handle, '/orgs')
        profile.organizations = [ele['login'] for ele in orgs]
        keywords = []
        for repo in profile.repos_data_lite:
            language = repo.get('language') if repo.get('language') else ''
            _keywords = language.split(',')
            for key in _keywords:
                if key != '' and key not in keywords:
                    keywords.append(key)

        profile.keywords = keywords
        profile.save()

    except Exception as e:
        logger.error(e)
        return None

    if user and user.email:
        email = user.email
    elif profile and profile.email:
        email = profile.email

    if email and profile:
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


def get_country_from_ip(ip_address, db=None):
    """Get the user's country information from the provided IP address."""
    country = {}
    if db is None:
        db = f'{settings.GEOIP_PATH}GeoLite2-Country.mmdb'

    if not ip_address:
        return country

    try:
        reader = geoip2.database.Reader(db)
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
