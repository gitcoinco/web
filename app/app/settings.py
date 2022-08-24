# -*- coding: utf-8 -*-
"""Define the Gitcoin project settings.

Copyright (C) 2021 Gitcoin Core

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
import json
import os
import socket
import warnings

from django.utils.translation import gettext_noop

import environ
import mimetypes
import raven
import sentry_sdk
from boto3.session import Session
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

warnings.filterwarnings("ignore", category=UserWarning, module='psycopg2')

root = environ.Path(__file__) - 2  # Set the base directory to two levels.
env = environ.Env(DEBUG=(bool, False), )  # set default values and casting
env.read_env(str(root.path('app/.env')))  # reading .env file

DEBUG = env.bool('DEBUG', default=True)
QUESTS_LIVE = True
ENV = env('ENV', default='local')
DEBUG_ENVS = env.list('DEBUG_ENVS', default=['local', 'stage', 'test', 'ci'])
IS_DEBUG_ENV = ENV in DEBUG_ENVS
HOSTNAME = env('HOSTNAME', default=socket.gethostname())
BASE_URL = env('BASE_URL', default='http://localhost:8000/')
OVERRIDE_NETWORK = env('OVERRIDE_NETWORK', default=None)
SECRET_KEY = env('SECRET_KEY', default='YOUR-SupEr-SecRet-KeY')
ADMINS = (env.tuple('ADMINS', default=('TODO', 'todo@todo.net')))
BASE_DIR = root()
#social integrations
GIPHY_KEY = env('GIPHY_KEY', default='LtaY19ToaBSckiLU4QjW0kV9nIP75NFy')
YOUTUBE_API_KEY = env('YOUTUBE_API_KEY', default='YOUR-SupEr-SecRet-YOUTUBE-KeY')
ETHERSCAN_API_KEY = env('ETHERSCAN_API_KEY', default='YOUR-ETHERSCAN-KEY')
POLYGONSCAN_API_KEY = env('POLYGONSCAN_API_KEY', default='YOUR-POLYGONSCAN-KEY')
VIEW_BLOCK_API_KEY = env('VIEW_BLOCK_API_KEY', default='YOUR-VIEW-BLOCK-KEY')
FORTMATIC_LIVE_KEY = env('FORTMATIC_LIVE_KEY', default='YOUR-SupEr-SecRet-LiVe-FoRtMaTiC-KeY')
FORTMATIC_TEST_KEY = env('FORTMATIC_TEST_KEY', default='YOUR-SupEr-SecRet-TeSt-FoRtMaTiC-KeY')
PYPL_CLIENT_ID = env('PYPL_CLIENT_ID', default='')
XINFIN_API_KEY = env('XINFIN_API_KEY', default='')
ALGORAND_API_KEY = env('ALGORAND_API_KEY', default='')

# Ratelimit
MARKETING_QUEUE_RATE_LIMIT = env('MARKETING_QUEUE_RATE_LIMIT', default='32/m')
MARKETING_FLUSH_QUEUE = env.bool('MARKETING_FLUSH_QUEUE', default=False)
FLUSH_QUEUE = env.bool('FLUSH_QUEUE', default=False)
RATELIMIT_ENABLE = env.bool('RATELIMIT_ENABLE', default=True)
RATELIMIT_USE_CACHE = env('RATELIMIT_USE_CACHE', default='default')
RATELIMIT_VIEW = env('RATELIMIT_VIEW', default='tdi.views.ratelimited')
BLOCKNATIVE_API = env('BLOCKNATIVE_API', default='')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['localhost'])

TWILIO_FRIENDLY_NAMES = env.list('TWILIO_FRIENDLY_NAMES', default=['VERIFY'])

# Notifications - Global on / off switch
ENABLE_NOTIFICATIONS_ON_NETWORK = env('ENABLE_NOTIFICATIONS_ON_NETWORK', default='mainnet')

# Set .wasm mime type for dev env
if DEBUG:
    mimetypes.add_type("application/wasm", ".wasm", True)

# Application definition
INSTALLED_APPS = [
    'csp',
    'corsheaders',
    'django.contrib.admin',
    'taskapp.celery.CeleryConfig',
    'django_celery_beat',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'collectfast',  # Collectfast | static file collector
    'django.contrib.staticfiles',
    'livereload',
    'cacheops',
    'storages',
    'social_django',
    'cookielaw',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'autotranslate',
    'django_extensions',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.psutil',
    'health_check.contrib.s3boto3_storage',
    'app',
    'avatar',
    'retail',
    'rest_framework',
    'django_filters',
    'marketing',
    'economy',
    'dashboard',
    'quests',
    'tdi',
    'gas',
    'git',
    'healthcheck.apps.HealthcheckConfig',
    'legacy',
    'chartit',
    'email_obfuscator',
    'linkshortener',
    'credits',
    'gitcoinbot',
    'dataviz',
    'impersonate',
    'grants',
    'kudos',
    'django.contrib.postgres',
    'perftools',
    'revenue',
    'inbox',
    'feeswapper',
    'search',
    'oauth2_provider',
    'townsquare',
    'compliance',
    'django_nyt.apps.DjangoNytConfig',
    'mptt',
    'sekizai',
    'sorl.thumbnail',
    'wiki.apps.WikiConfig',
    'wiki.plugins.attachments.apps.AttachmentsConfig',
    'wiki.plugins.notifications.apps.NotificationsConfig',
    'wiki.plugins.images.apps.ImagesConfig',
    'wiki.plugins.macros.apps.MacrosConfig',
    'adminsortable2',
    'debug_toolbar',
    'passport',
    'quadraticlands',
    'mautic_logging',
]

MIDDLEWARE = [
    'csp.middleware.CSPMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'app.middleware.drop_accept_language',
    'app.middleware.drop_recaptcha_post',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ratelimit.middleware.RatelimitMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ROOT_URLCONF = env('ROOT_URLCONF', default='app.urls')

AUTHENTICATION_BACKENDS = (
    # 'social_core.backends.github.GithubOAuth2',  # for Github authentication
    'app.utils.CustomGithubOAuth2',
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': ['retail/templates/', 'dataviz/templates', 'kudos/templates', 'inbox/templates', 'quests/templates', 'townsquare/templates', 'quadraticlands/templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug', 'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages',
            'app.context.preprocess', 'social_django.context_processors.backends',
            'social_django.context_processors.login_redirect',
            "sekizai.context_processors.sekizai",
        ],
    },
}]

SITE_ID = env.int('SITE_ID', default=1)
WSGI_APPLICATION = env('WSGI_APPLICATION', default='app.wsgi.application')

# Explicity use watchdog for inotify
RUNSERVERPLUS_POLLER_RELOADER_TYPE = 'watchdog'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': env.db()
}
if ENV in ['prod']:
    DATABASES = {
        'default': env.db(),
        'read_replica_1': env.db('READ_REPLICA_1_DATABASE_URL'),
        'read_replica_2': env.db('READ_REPLICA_2_DATABASE_URL'),
        'read_replica_3': env.db('READ_REPLICA_3_DATABASE_URL'),
        'read_replica_4': env.db('READ_REPLICA_4_DATABASE_URL'),
        }
    DATABASE_ROUTERS = ['app.db.PrimaryDBRouter']

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [{
    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
}]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_THROTTLE_CLASSES': ('rest_framework.throttling.AnonRateThrottle',),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',
    },
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

AUTH_USER_MODEL = 'auth.User'

# adds django debug toolbar
SUPRESS_DEBUG_TOOLBAR = env.bool('SUPRESS_DEBUG_TOOLBAR', default=False)
if DEBUG and not SUPRESS_DEBUG_TOOLBAR:
    INTERNAL_IPS = [
        # ...
        '127.0.0.1',
        'localhost',
        # ...
    ]
    def callback(request):
        return True
    SHOW_TOOLBAR_CALLBACK = callback
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK" : callback,
    }
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = env('LANGUAGE_CODE', default='en-us')
USE_I18N = env.bool('USE_I18N', default=True)
USE_L10N = env.bool('USE_L10N', default=True)
USE_TZ = env.bool('USE_TZ', default=True)
TIME_ZONE = env.str('TIME_ZONE', default='UTC')

LOCALE_PATHS = ('locale',)

LANGUAGES = [
    ('en', gettext_noop('English')),
    ('es', gettext_noop('Spanish')),
    ('de', gettext_noop('German')),
    ('hi', gettext_noop('Hindi')),
    ('it', gettext_noop('Italian')),
    ('ko', gettext_noop('Korean')),
    ('pl', gettext_noop('Polish')),
    ('ja', gettext_noop('Japanese')),
    ('zh-hans', gettext_noop('Simplified Chinese')),
    ('zh-hant', gettext_noop('Traditional Chinese')),
]

# Elastic APM
ENABLE_APM = env.bool('ENABLE_APM', default=False)
if ENABLE_APM:
    INSTALLED_APPS += ['elasticapm.contrib.django', ]
    MIDDLEWARE.append('elasticapm.contrib.django.middleware.TracingMiddleware')
    APM_SECRET_TOKEN = env.str('APM_SECRET_TOKEN', default='')
    ELASTIC_APM = {
        'SERVICE_NAME': env.str('APM_SERVICE_NAME', default=f'{ENV}-web'),
        'SERVER_URL': env.str('APM_SERVER_URL', default='http://localhost:8200'),
    }
    if APM_SECRET_TOKEN:
        ELASTIC_APM['SECRET_TOKEN'] = APM_SECRET_TOKEN
    if DEBUG and ENV == 'stage':
        ELASTIC_APM['DEBUG'] = True

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
AWS_DEFAULT_REGION = env('AWS_DEFAULT_REGION', default='us-west-2')
AWS_LOG_GROUP = env('AWS_LOG_GROUP', default='Gitcoin')
AWS_LOG_LEVEL = env('AWS_LOG_LEVEL', default='INFO')
AWS_LOG_STREAM = env('AWS_LOG_STREAM', default=f'{ENV}-web')

# Sentry
SENTRY_DSN = env.str('SENTRY_DSN', default='')
SENTRY_JS_DSN = env.str('SENTRY_JS_DSN', default=SENTRY_DSN)

# In case we are running / deploying from within a git repo, we want to use the git repo SHA
# In case we are not in a github repo, we rely on an environment variable
try:
    RELEASE = raven.fetch_git_sha(os.path.abspath(os.pardir)) if ENV == 'prod' else ''
except:
    RELEASE = env.str('GITHUB_SHA', default=' - dev build - ')

RAVEN_JS_VERSION = env.str('RAVEN_JS_VERSION', default='6.8.0')
if SENTRY_DSN:
    sentry_sdk.init(
        SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0.25
    )
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
    }
    if RELEASE:
        RAVEN_CONFIG['release'] = RELEASE

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'host_filter': {
            '()': 'app.log_filters.HostFilter',
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(name)-12s [%(levelname)-8s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.security.*': {
            'handlers': ['console'],
            'level': DEBUG and 'DEBUG' or 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': DEBUG and 'DEBUG' or 'INFO',
        },
    },
}

# Production logging
if ENV not in ['local', 'test', 'staging', 'preview', 'ci']:
    # add AWS monitoring
    boto3_session = Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )

    LOGGING['formatters']['cloudwatch'] = {
        'format': '%(hostname)s %(name)-12s [%(levelname)-8s] %(message)s',
    }
    LOGGING['handlers']['watchtower'] = {
        'level': AWS_LOG_LEVEL,
        'class': 'watchtower.CloudWatchLogHandler',
        'boto3_session': boto3_session,
        'log_group': AWS_LOG_GROUP,
        'stream_name': AWS_LOG_STREAM,
        'filters': ['host_filter'],
        'formatter': 'cloudwatch',
    }
    LOGGING['loggers']['django.db.backends']['level'] = AWS_LOG_LEVEL

    LOGGING['loggers']['django.request'] = LOGGING['loggers']['django.db.backends']
    LOGGING['loggers']['django.security.*'] = LOGGING['loggers']['django.db.backends']
    for ia in INSTALLED_APPS:
        LOGGING['loggers'][ia] = LOGGING['loggers']['django.db.backends']

    # add elasticsearch monitoring
    if ENABLE_APM:
        LOGGING['handlers']['elasticapm'] = {
            'level': 'WARNING',
            'class': 'elasticapm.contrib.django.handlers.LoggingHandler',
        }
        LOGGING['loggers']['elasticapm.errors'] = {
            'level': 'ERROR',
            'handlers': ['sentry', 'console'],
            'propagate': False,
        }
        LOGGING['root']['handlers'] = ['sentry', 'elasticapm']

GEOIP_PATH = env('GEOIP_PATH', default='/usr/share/GeoIP/')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATICFILES_DIRS = env.tuple('STATICFILES_DIRS', default=('assets/',))
STATICFILES_LOCATION = env.str('STATICFILES_LOCATION', default='static')
MEDIAFILES_LOCATION = env.str('MEDIAFILES_LOCATION', default='media')
STATIC_ROOT = root(STATICFILES_LOCATION)

if ENV in ['prod', 'stage', 'test']:
    DEFAULT_FILE_STORAGE = env('DEFAULT_FILE_STORAGE', default='app.static_storage.MediaFileStorage')
    STATICFILES_STORAGE = env('STATICFILES_STORAGE', default='app.static_storage.SilentFileStorage')
    STATIC_HOST = env('STATIC_HOST', default='https://s.gitcoin.co/')
    STATIC_URL = STATIC_HOST + env('STATIC_URL', default=f'{STATICFILES_LOCATION}{"/" if STATICFILES_LOCATION else ""}')
    MEDIA_URL = env(
        'MEDIA_URL', default=f'https://c.gitcoin.co/{MEDIAFILES_LOCATION}{"/" if MEDIAFILES_LOCATION else ""}'
    )
else:
    # Handle local static file storage
    STATICFILES_STORAGE = env('STATICFILES_STORAGE', default='django.contrib.staticfiles.storage.StaticFilesStorage')
    STATIC_HOST = BASE_URL
    STATIC_URL = env('STATIC_URL', default=f'/{STATICFILES_LOCATION}/')

    # Handle local media file storage
    MEDIA_ROOT = root('media')
    MEDIA_URL = env('MEDIA_URL', default=f'/{MEDIAFILES_LOCATION}/')


# Staticfinder finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
]

CACHEOPS_DEGRADE_ON_FAILURE = env.bool('CACHEOPS_DEGRADE_ON_FAILURE', default=True)
CACHEOPS_REDIS = env.str('CACHEOPS_REDIS', default='redis://redis:6379/0')

CACHEOPS_DEFAULTS = {
    'timeout': 60 * 60 * 5
}

# 'all' is an alias for {'get', 'fetch', 'count', 'aggregate', 'exists'}
CACHEOPS = {
    '*.*': {
        'timeout': 60 * 60 * 5,
    },
    'auth.user': {
        'ops': 'get',
        'timeout': 60 * 15,
    },
    'auth.group': {
        'ops': 'get',
        'timeout': 60 * 15,
    },
    'auth.*': {
        'ops': ('fetch', 'get'),
        'timeout': 60 * 60 * 5,
    },
    'auth.permission': {
        'ops': 'all',
        'timeout': 60 * 15,
    },
    'dashboard.activity': {
        'ops': 'all',
        'timeout': 60 * 5,
    },
    'dashboard.bounty': {
        'ops': ('get', 'fetch', 'aggregate'),
        'timeout': 60 * 5,
    },
    'dashboard.tip': {
        'ops': ('get', 'fetch', 'aggregate'),
        'timeout': 60 * 5,
    },
    'dashboard.profile': {
        'ops': ('get', 'fetch', 'aggregate'),
        'timeout': 60 * 5,
    },
    'dashboard.*': {
        'ops': ('fetch', 'get'),
        'timeout': 60 * 60 * 3,
    },
    'economy.*': {
        'ops': 'all',
        'timeout': 60 * 60 * 5,
    },
    'gas.*': {
        'ops': 'all',
        'timeout': 60 * 10,
    },
    'kudos.token': {
        'ops': ('get', 'fetch', 'aggregate'),
        'timeout': 60 * 5,
    },
    'kudos.kudostransfer': {
        'ops': ('get', 'fetch', 'aggregate'),
        'timeout': 60 * 5,
    },
}


# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=CACHEOPS_REDIS)
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ['json']
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = 'json'
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = 'json'
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=CACHEOPS_REDIS)
# https://docs.celeryproject.org/en/latest/userguide/configuration.html#std-setting-task_routes
CELERY_ROUTES = [
    ('dashboard.tasks.calculate_trust_bonus', {'queue': 'gitcoin_passport'}),
    ('grants.tasks.process_grant_contribution', {'queue': 'high_priority'}),
    ('grants.tasks.batch_process_grant_contributions', {'queue': 'high_priority'}),
    ('kudos.tasks.mint_token_request', {'queue': 'high_priority'}),
    ('dashboard.tasks.increment_view_count', {'queue': 'analytics'}),
    ('dashboard.tasks.record_visit', {'queue': 'analytics'}),
    ('dashboard.tasks.record_join', {'queue': 'analytics'}),
    ('townsquare.tasks.increment_offer_view_counts', {'queue': 'analytics'}),
    ('townsquare.tasks.increment_view_counts', {'queue': 'analytics'}),
    ('townsquare.tasks.send_comment_email', {'queue': 'marketing'}),
    ('marketing.tasks.*', {'queue': 'marketing'}),
    ('grants.tasks.*', {'queue': 'default'}),
    ('dashboard.tasks.*', {'queue': 'default'}),
    ('townsquare.tasks.*', {'queue': 'default'}),
    ('kudos.tasks.*', {'queue': 'default'}),
    ]
if DEBUG:
    CELERY_ROUTES = [
        ('*', {'queue': 'default'}),
        ]


DJANGO_REDIS_IGNORE_EXCEPTIONS = env.bool('REDIS_IGNORE_EXCEPTIONS', default=True)
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = env.bool('REDIS_LOG_IGNORED_EXCEPTIONS', default=True)
COLLECTFAST_CACHE = env('COLLECTFAST_CACHE', default='collectfast')
COLLECTFAST_DEBUG = env.bool('COLLECTFAST_DEBUG', default=False)
REDIS_URL = env('REDIS_URL', default='rediscache://redis:6379/0?client_class=django_redis.client.DefaultClient')
SEMAPHORE_REDIS_URL = env('SEMAPHORE_REDIS_URL', default=REDIS_URL)

CACHES = {
    'default': env.cache(
        'REDIS_URL',
        default='rediscache://redis:6379/0?client_class=django_redis.client.DefaultClient'
    ),
    COLLECTFAST_CACHE: env.cache('COLLECTFAST_CACHE_URL', default='dbcache://collectfast'),
    'legacy': env.cache('CACHE_URL', default='dbcache://my_cache_table'),
}
CACHES[COLLECTFAST_CACHE]['OPTIONS'] = {'MAX_ENTRIES': 1000}
CACHES['default']['TIMEOUT'] = 60 * 60 * 3

# HTTPS Handling
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=True)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=3600)
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)

CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)
CSRF_COOKIE_HTTPONLY = env.bool('CSRF_COOKIE_HTTPONLY', default=True)
CSRF_FAILURE_VIEW = 'retail.views.csrf_failure'
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
SECURE_BROWSER_XSS_FILTER = env.bool('SECURE_BROWSER_XSS_FILTER', default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool('SECURE_CONTENT_TYPE_NOSNIFF', default=True)
X_FRAME_OPTIONS = env('X_FRAME_OPTIONS', default='DENY')

# Email Integrations
CONTACT_EMAIL = env('CONTACT_EMAIL', default='')  # TODO
PERSONAL_CONTACT_EMAIL = env('PERSONAL_CONTACT_EMAIL', default='you@foo.bar')
SENDGRID_API_KEY = env('SENDGRID_API_KEY', default='')  # TODO - Required to send email.
EMAIL_HOST = env('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')  # TODO
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')  # TODO
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
SERVER_EMAIL = env('SERVER_EMAIL', default='server@TODO.co')

MAUTIC_USER = env('MAUTIC_USER', default='')
MAUTIC_PASSWORD = env('MAUTIC_PASSWORD', default='')


# IMAP Settings
IMAP_EMAIL = env('IMAP_EMAIL', default='<email>')
IMAP_PASSWORD = env('IMAP_PASSWORD', default='<password>')

# Mailchimp Integration
MAILCHIMP_USER = env.str('MAILCHIMP_USER', default='')
MAILCHIMP_API_KEY = env.str('MAILCHIMP_API_KEY', default='')
MAILCHIMP_LIST_ID = env.str('MAILCHIMP_LIST_ID', default='')
MAILCHIMP_LIST_ID_HUNTERS = env.str('MAILCHIMP_LIST_ID_HUNTERS', default='')
MAILCHIMP_LIST_ID_FUNDERS = env.str('MAILCHIMP_LIST_ID_FUNDERS', default='')
MAILCHIMP_LIST_ID_HACKERS = env.str('MAILCHIMP_LIST_ID_HACKERS', default='')

# Github
GITHUB_API_BASE_URL = env('GITHUB_API_BASE_URL', default='https://api.github.com')
GITHUB_AUTH_BASE_URL = env('GITHUB_AUTH_BASE_URL', default='https://github.com/login/oauth/authorize')
GITHUB_SCOPE = env('GITHUB_SCOPE', default='read:user,user:email')
GITHUB_CLIENT_ID = env('GITHUB_CLIENT_ID', default='')  # TODO
GITHUB_CLIENT_SECRET = env('GITHUB_CLIENT_SECRET', default='')  # TODO
GITHUB_API_USER = env('GITHUB_API_USER', default='')  # TODO
GITHUB_API_TOKEN = env('GITHUB_API_TOKEN', default='')  # TODO
GITHUB_APP_NAME = env('GITHUB_APP_NAME', default='gitcoin-local')

# Google
GOOGLE_AUTH_BASE_URL = env('GOOGLE_AUTH_BASE_URL', default='https://accounts.google.com/o/oauth2/auth')
GOOGLE_TOKEN_URL = env('GOOGLE_TOKEN_URL', default='https://oauth2.googleapis.com/token')
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET', default='')
GOOGLE_SCOPE = env('GOOGLE_SCOPE', default='https://www.googleapis.com/auth/userinfo.profile')

# OATHLIB
OAUTHLIB_INSECURE_TRANSPORT = env('OAUTHLIB_INSECURE_TRANSPORT', default=1)

# Facebook
FACEBOOK_AUTH_BASE_URL = env('FACEBOOK_AUTH_BASE_URL', default='https://www.facebook.com/v9.0/dialog/oauth')
FACEBOOK_TOKEN_URL = env('FACEBOOK_TOKEN_URL', default='https://graph.facebook.com/v9.0/oauth/access_token')
FACEBOOK_CLIENT_ID = env('FACEBOOK_CLIENT_ID', default='')
FACEBOOK_CLIENT_SECRET = env('FACEBOOK_CLIENT_SECRET', default='')

# Notion
NOTION_API_KEY = env('NOTION_API_KEY', default='')
NOTION_SYBIL_DB = env('NOTION_SYBIL_DB', default='')

# Kudos revenue account
KUDOS_REVENUE_ACCOUNT_ADDRESS = env('KUDOS_REVENUE_ACCOUNT_ADDRESS', default='0xAD278911Ad07534F921eD7D757b6c0e6730FCB16')

# Social Auth
LOGIN_URL = 'gh_login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'index'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'index'
SOCIAL_AUTH_GITHUB_KEY = GITHUB_CLIENT_ID
SOCIAL_AUTH_GITHUB_SECRET = GITHUB_CLIENT_SECRET
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'last_name', 'email']
SOCIAL_AUTH_GITHUB_SCOPE = ['read:user', 'user:email']
SOCIAL_AUTH_SANITIZE_REDIRECTS = True
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True if ENV in ['prod', 'test', 'stage'] else False
SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['state']

# Ignore the default protected fields, because 'username' is among those, and specify a custom set
# of fields to protected which does not include 'username'.
# We want to achieve that the social auth app updates the username in gitcoin if it has been changed in github.
SOCIAL_AUTH_NO_DEFAULT_PROTECTED_USER_FIELDS = True
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['id', 'pk', 'password', 'is_active', 'is_staff', 'is_superuser',]

#custom scopes
SOCIAL_AUTH_GH_CUSTOM_KEY = GITHUB_CLIENT_ID
SOCIAL_AUTH_GH_CUSTOM_SECRET = GITHUB_CLIENT_SECRET
SOCIAL_AUTH_GH_CUSTOM_SCOPE = ['read:org', 'public_repo']

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
# This should be executed after the '...user_details' step, as the user_details step will
# update the username (aka github handle) which is then used in `save_profile`. This
# is relevant when the github username / handle changes.
    'app.pipeline.save_profile',
)

# Gitter
GITTER_TOKEN = env('GITTER_TOKEN', default=False)

# optional: only needed if you run the gitcoinbot app
# Setup instructions: https://github.com/gitcoinco/web/blob/master/app/gitcoinbot/README.md
GITCOINBOT_APP_ID = env('GITCOINBOT_APP_ID', default='')
GITCOIN_BOT_CERT_PATH = env('GITCOIN_BOT_CERT_PATH', default='')
SECRET_KEYSTRING = ''
if GITCOIN_BOT_CERT_PATH:
    with open(str(root.path(GITCOIN_BOT_CERT_PATH))) as f:
        SECRET_KEYSTRING = f.read()

GITCOIN_SLACK_ICON_URL = 'https://s.gitcoin.co/static/v2/images/helmet.png'

# Twitter Integration
TWITTER_CONSUMER_KEY = env('TWITTER_CONSUMER_KEY', default='')  # TODO
TWITTER_CONSUMER_SECRET = env('TWITTER_CONSUMER_SECRET', default='')  # TODO
TWITTER_ACCESS_TOKEN = env('TWITTER_ACCESS_TOKEN', default='')  # TODO
TWITTER_ACCESS_SECRET = env('TWITTER_ACCESS_SECRET', default='')  # TODO
TWITTER_USERNAME = env('TWITTER_USERNAME', default='')  # TODO

DISPUTES_TWITTER_CONSUMER_KEY = env('DISPUTES_TWITTER_CONSUMER_KEY', default='')  # TODO
DISPUTES_TWITTER_CONSUMER_SECRET = env('DISPUTES_TWITTER_CONSUMER_SECRET', default='')  # TODO
DISPUTES_TWITTER_ACCESS_TOKEN = env('DISPUTES_TWITTER_ACCESS_TOKEN', default='')  # TODO
DISPUTES_TWITTER_ACCESS_SECRET = env('DISPUTES_TWITTER_ACCESS_SECRET', default='')  # TODO


# Slack Integration
# optional: only needed if you slack things
SLACK_TOKEN = env('SLACK_TOKEN', default='')  # TODO
SLACK_WELCOMEBOT_TOKEN = env('SLACK_WELCOMEBOT_TOKEN', default='')  # TODO

# OpenSea API
OPENSEA_API_KEY = env('OPENSEA_API_KEY', default='')

# Kudos
KUDOS_OWNER_ACCOUNT = env('KUDOS_OWNER_ACCOUNT', default='0xD386793F1DB5F21609571C0164841E5eA2D33aD8')
KUDOS_PRIVATE_KEY = env('KUDOS_PRIVATE_KEY', default='')
KUDOS_CONTRACT_MAINNET = env('KUDOS_CONTRACT_MAINNET', default='0x2aea4add166ebf38b63d09a75de1a7b94aa24163')
KUDOS_CONTRACT_XDAI = env('KUDOS_CONTRACT_XDAI', default='0x74e596525C63393f42C76987b6A66F4e52733efa')
KUDOS_CONTRACT_RINKEBY = env('KUDOS_CONTRACT_RINKEBY', default='0x4077ae95eec529d924571d00e81ecde104601ae8')
KUDOS_CONTRACT_ROPSTEN = env('KUDOS_CONTRACT_ROPSTEN', default='0xcd520707fc68d153283d518b29ada466f9091ea8')
KUDOS_CONTRACT_TESTRPC = env('KUDOS_CONTRACT_TESTRPC', default='0x38c48d14a5bbc38c17ced9cd5f0695894336f426')
KUDOS_NETWORK = env('KUDOS_NETWORK', default='mainnet')

# Passport
PASSPORT_PK_MAINNET = env('PASSPORT_PK_MAINNET', default='')
PASSPORT_PK_RINKEBY = env('PASSPORT_PK_RINKEBY', default='')

# Grants
GRANTS_OWNER_ACCOUNT = env('GRANTS_OWNER_ACCOUNT', default='0xD386793F1DB5F21609571C0164841E5eA2D33aD8')
GRANTS_PRIVATE_KEY = env('GRANTS_PRIVATE_KEY', default='')
GRANTS_SPLITTER_ROPSTEN = env('GRANTS_SPLITTER_ROPSTEN', default='0xe2fd6dfe7f371e884e782d46f043552421b3a9d9')
GRANTS_SPLITTER_MAINNET = env('GRANTS_SPLITTER_MAINNET', default='0xdf869FAD6dB91f437B59F1EdEFab319493D4C4cE')
GRANTS_NETWORK = env('GRANTS_NETWORK', default='mainnet')
GITCOIN_DONATION_ADDRESS = env('GITCOIN_DONATION_ADDRESS', default='0x00De4B13153673BCAE2616b67bf822500d325Fc3')
SPLITTER_CONTRACT_ADDRESS = ''
if GRANTS_NETWORK == 'mainnet':
    SPLITTER_CONTRACT_ADDRESS = GRANTS_SPLITTER_MAINNET
else:
    SPLITTER_CONTRACT_ADDRESS = GRANTS_SPLITTER_ROPSTEN

METATX_GAS_PRICE_THRESHOLD = float(env('METATX_GAS_PRICE_THRESHOLD', default='10000.0'))

GA_PRIVATE_KEY_PATH = env('GA_PRIVATE_KEY_PATH', default='')
GA_PRIVATE_KEY = ''
if GA_PRIVATE_KEY_PATH:
    with open(str(root.path(GA_PRIVATE_KEY_PATH))) as cert_file:
        GA_PRIVATE_KEY = cert_file.read()

# https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py
GOOGLE_ANALYTICS_AUTH_JSON = {
    'type': env('GA_TYPE', default='service_account'),
    'project_id': env('GA_PROJECT_ID', default=''),
    'private_key_id': env('GA_PRIVATE_KEY_ID', default=''),
    'private_key': GA_PRIVATE_KEY,
    'client_email': env('GA_CLIENT_EMAIL', default=''),
    'client_id': env('GA_CLIENT_ID', default=''),
    'auth_uri': env('GA_AUTH_URI', default='https://accounts.google.com/o/oauth2/auth'),
    'token_uri': env('GA_TOKEN_URI', default='https://accounts.google.com/o/oauth2/token'),
    'auth_provider_x509_cert_url':
        env('GA_AUTH_PROVIDER_X509_CERT_URL', default='https://www.googleapis.com/oauth2/v1/certs'),
    'client_x509_cert_url': env('GA_CLIENT_X509_CERT_URL', default='')
}

# List of github usernames to not count as comments on an issue
IGNORE_COMMENTS_FROM = ['gitcoinbot', ]

# optional: only needed if you run the activity-report management command
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_CACHE_MAX_AGE = env.str('AWS_S3_CACHE_MAX_AGE', default='15552000')
AWS_QUERYSTRING_EXPIRE = env.int('AWS_QUERYSTRING_EXPIRE', default=3600)
AWS_S3_ENCRYPTION = env.bool('AWS_S3_ENCRYPTION', default=False)
AWS_S3_OBJECT_PARAMETERS = env.dict('AWS_S3_OBJECT_PARAMETERS', default=None)
S3_USE_SIGV4 = env.bool('S3_USE_SIGV4', default=True)
AWS_IS_GZIPPED = env.bool('AWS_IS_GZIPPED', default=True)
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-west-2')
AWS_S3_SIGNATURE_VERSION = env('AWS_S3_SIGNATURE_VERSION', default='s3v4')
AWS_QUERYSTRING_AUTH = env.bool('AWS_QUERYSTRING_AUTH', default=False)
AWS_S3_FILE_OVERWRITE = env.bool('AWS_S3_FILE_OVERWRITE', default=True)
AWS_PRELOAD_METADATA = env.bool('AWS_PRELOAD_METADATA', default=True)
AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN', default='s.gitcoin.co')
MEDIA_BUCKET = env.str('MEDIA_BUCKET', default=AWS_STORAGE_BUCKET_NAME)
MEDIA_CUSTOM_DOMAIN = env('MEDIA_CUSTOM_DOMAIN', default='c.gitcoin.co')
AWS_DEFAULT_ACL = env('AWS_DEFAULT_ACL', default='public-read')
if not AWS_S3_OBJECT_PARAMETERS:
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': f'max-age={AWS_S3_CACHE_MAX_AGE}', }

CSP_DEFAULT_SRC = False
CSP_FRAME_ANCESTORS = ("'self'")

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = ('googleads.g.doubleclick.net', 'gitcoin.co', 'github.com',)
CORS_ORIGIN_WHITELIST = CORS_ORIGIN_WHITELIST + (AWS_S3_CUSTOM_DOMAIN, MEDIA_CUSTOM_DOMAIN,)

S3_REPORT_BUCKET = env('S3_REPORT_BUCKET', default='')  # TODO
S3_REPORT_PREFIX = env('S3_REPORT_PREFIX', default='')  # TODO

S3_BSCI_SYBIL_BUCKET = env('S3_BSCI_SYBIL_BUCKET', default='')  # TODO

INSTALLED_APPS += env.list('DEBUG_APPS', default=[])


SENDGRID_EVENT_HOOK_URL = env('SENDGRID_EVENT_HOOK_URL', default='sg_event_process')
GITHUB_EVENT_HOOK_URL = env('GITHUB_EVENT_HOOK_URL', default='github/payload/')

# Web3
WEB3_HTTP_PROVIDER = env('WEB3_HTTP_PROVIDER', default='https://rinkeby.infura.io')
INFURA_USE_V3 = env.bool('INFURA_USE_V3', False)
INFURA_V3_PROJECT_ID = env('INFURA_V3_PROJECT_ID', default='1e0a90928efe4bb78bb1eeceb8aacc27')

# COLO Coin
COLO_ACCOUNT_ADDRESS = env('COLO_ACCOUNT_ADDRESS', default='')  # TODO
COLO_ACCOUNT_PRIVATE_KEY = env('COLO_ACCOUNT_PRIVATE_KEY', default='')  # TODO

IPFS_HOST = env('IPFS_HOST', default='ipfs.infura.io')
JS_IPFS_HOST = IPFS_HOST if IPFS_HOST != 'ipfs' else 'localhost'
IPFS_SWARM_PORT = env.int('IPFS_SWARM_PORT', default=4001)
IPFS_UTP_PORT = env.int('IPFS_UTP_PORT', default=4002)
IPFS_API_PORT = env.int('IPFS_API_PORT', default=5001)
IPFS_GATEWAY_PORT = env.int('IPFS_GATEWAY_PORT', default=8080)
IPFS_SWARM_WS_PORT = env.int('IPFS_SWARM_WS_PORT', default=8081)
IPFS_API_ROOT = env('IPFS_API_ROOT', default='/api/v0')
IPFS_API_SCHEME = env('IPFS_API_SCHEME', default='https')

STABLE_COINS = ['DAI', 'SAI', 'USDT', 'TUSD', 'aDAI', 'USDC']

# Silk Profiling and Performance Monitoring
ENABLE_SILK = env.bool('ENABLE_SILK', default=False)
if ENABLE_SILK:
    INSTALLED_APPS += ['silk']
    MIDDLEWARE.append('silk.middleware.SilkyMiddleware')
    SILKY_PYTHON_PROFILER = env.bool('SILKY_PYTHON_PROFILER', default=True)
    SILKY_PYTHON_PROFILER_BINARY = env.bool('SILKY_PYTHON_PROFILER_BINARY', default=False)
    SILKY_AUTHENTICATION = env.bool('SILKY_AUTHENTICATION', default=False)
    SILKY_AUTHORISATION = env.bool('SILKY_AUTHORISATION', default=False)
    SILKY_META = env.bool('SILKY_META', default=True)
    SILKY_INTERCEPT_PERCENT = env.int('SILKY_INTERCEPT_PERCENT', default=50)
    SILKY_MAX_RECORDED_REQUESTS = env.int('SILKY_MAX_RECORDED_REQUESTS', default=10000)
    SILKY_DYNAMIC_PROFILING = env.list('SILKY_DYNAMIC_PROFILING', default=[])
    if ENV == 'stage':
        SILKY_DYNAMIC_PROFILING += [{
            'module': 'dashboard.views',
            'function': 'profile',
            'name': 'Profile View',
        }, {
            'module': 'retail.views',
            'function': 'index',
            'name': 'Index View',
        }]
    SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = env.int('SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT', default=10)

# Datadog Monitoring
ENABLE_DDTRACE = env.bool('ENABLE_DDTRACE', default=False)
if ENABLE_DDTRACE:
    INSTALLED_APPS += ['ddtrace.contrib.django']

WIKI_ACCOUNT_HANDLING = True
WIKI_ACCOUNT_SIGNUP_ALLOWED = True
WIKI_CACHE_TIMEOUT = True

# Sending an email when a bounty is funded below a threshold
LOWBALL_BOUNTY_THRESHOLD = env.float('LOWBALL_BOUNTY_THRESHOLD', default=10.00)

# Gitcoin Bounty Funding Fee settings
FEE_ADDRESS = env('FEE_ADDRESS', default='')

ALETHIO_KEY = env('ALETHIO_KEY', default='')
FEE_ADDRESS_PRIVATE_KEY = env('FEE_ADDRESS_PRIVATE_KEY', default='')
SLIPPAGE = env.float('SLIPPAGE', default=0.05)
UNISWAP_LIQUIDITY_FEE = env.float('UNISWAP_LIQUDITY_FEE', default=0.003)
UNISWAP_TRADE_DEADLINE = env.int('UNISWAP_TRADE_DEADLINE', default=300)

RE_MARKET_LIMIT = env.int('RE_MARKET_LIMIT', default=2)
MINUTES_BETWEEN_RE_MARKETING = env.int('MINUTES_BETWEEN_RE_MARKETING', default=60)

MINICLR_ADDRESS = env('MINICLR_ADDRESS', default='0x00De4B13153673BCAE2616b67bf822500d325Fc3')
MINICLR_PRIVATE_KEY = env('MINICLR_PRIVATE_KEY', default='0x00De4B13153673BCAE2616b67bf822500d325Fc3')


AVATAR_ADDRESS = env('AVATAR_ADDRESS', default='0x00De4B13153673BCAE2616b67bf822500d325Fc3')
AVATAR_PRIVATE_KEY = env('AVATAR_PRIVATE_KEY', default='0x00De4B13153673BCAE2616b67bf822500d325Fc3')

GRANTS_PAYOUT_ADDRESS = env('GRANTS_PAYOUT_ADDRESS', default='0x00De4B13153673BCAE2616b67bf822500d325Fc3')
GRANTS_PAYOUT_PRIVATE_KEY = env('GRANTS_PAYOUT_PRIVATE_KEY', default='0x00De4B13153673BCAE2616b67bf822500d325Fc3')
GRANTS_PAYOUT_CLR_KYC_THRESHOLD = env('GRANTS_PAYOUT_CLR_KYC_THRESHOLD', default=0)

GRANTS_COUPON_25_OFF = env('GRANTS_COUPON_25_OFF', default='OWOCKIFOREVER')
GRANTS_COUPON_50_OFF = env('GRANTS_COUPON_50_OFF', default='OWOCKIFOREVER')
GRANTS_COUPON_100_OFF = env('GRANTS_COUPON_100_OFF', default='OWOCKIFOREVER')

TIP_PAYOUT_ADDRESS = env('TIP_PAYOUT_ADDRESS', default='0x00De4B13153673BCAE2616b67bf822500d325Fc3')
TIP_PAYOUT_PRIVATE_KEY = env('TIP_PAYOUT_PRIVATE_KEY', default='0x00De4B13153673BCAE2616b67bf822500d325Fc3')


ELASTIC_SEARCH_URL = env('ELASTIC_SEARCH_URL', default='')
ACTIVE_ELASTIC_INDEX = env('ACTIVE_ELASTIC_INDEX', default='search-index-1')

account_sid = env('TWILIO_ACCOUNT_SID', default='')
auth_token = env('TWILIO_AUTH_TOKEN', default='')
verify_service = env('TWILIO_VERIFY_SERVICE', default='')

SMS_MAX_VERIFICATION_ATTEMPTS = env('SMS_MAX_VERIFICATION_ATTEMPTS', default=4)
SMS_COOLDOWN_IN_MINUTES = env('SMS_COOLDOWN_IN_MINUTES', default=1)
EMAIL_ACCOUNT_VALIDATION = env.bool('EMAIL_ACCOUNT_VALIDATION', default=False)
PHONE_SALT = env('PHONE_SALT', default='THIS_IS_INSECURE_CHANGE_THIS_PLEASE')

HYPERCHARGE_BOUNTIES_PROFILE_HANDLE = env('HYPERCHARGE_BOUNTIES_PROFILE', default='gitcoinbot')
ADDEVENT_CLIENT_ID = env('ADDEVENT_CLIENT_ID', default='')
ADDEVENT_API_TOKEN = env('ADDEVENT_API_TOKEN', default='')

BRIGHTID_PRIVATE_KEY = env('BRIGHTID_PRIVATE_KEY', default='wrong-private-key')

# Duniter
BMAS_ENDPOINT = env('BMAS_ENDPOINT', default='BMAS g1.duniter.org 443')
ES_CORE_ENDPOINT = env('ES_CORE_ENDPOINT', default='ES_CORE_API g1.data.duniter.fr 443')
ES_USER_ENDPOINT = env('ES_USER_ENDPOINT', default='ES_USER_API g1.data.duniter.fr 443')

# Idena
IDENA_TOKEN_EXPIRY = 60 * 60 # 1 Hours
IDENA_NONCE_EXPIRY = 60 * 2 # 2 Min

# Match Payouts contract
with open(os.path.join(root, 'grants/match_payouts_abi.json'), 'r') as f:
    MATCH_PAYOUTS_ABI = f.read()
MATCH_PAYOUTS_ADDRESS = '0xAB8d71d59827dcc90fEDc5DDb97f87eFfB1B1A5B'


# Merkle Payouts contract
with open(os.path.join(root, 'grants/abi/merkle_payout.json'), 'r') as f:
    MERKLE_PAYOUTS_ABI = f.read()


# BulkCheckout contract
# BulkCheckout parameters
BULK_CHECKOUT_ADDRESS = "0x7d655c57f71464B6f83811C55D84009Cd9f5221C" # same address on mainnet and rinkeby
BULK_CHECKOUT_ABI = '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":true,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"address","name":"dest","type":"address"},{"indexed":true,"internalType":"address","name":"donor","type":"address"}],"name":"DonationSent","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":true,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":true,"internalType":"address","name":"dest","type":"address"}],"name":"TokenWithdrawn","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address payable","name":"dest","type":"address"}],"internalType":"struct BulkCheckout.Donation[]","name":"_donations","type":"tuple[]"}],"name":"donate","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"_dest","type":"address"}],"name":"withdrawEther","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_tokenAddress","type":"address"},{"internalType":"address","name":"_dest","type":"address"}],"name":"withdrawToken","outputs":[],"stateMutability":"nonpayable","type":"function"}]'


JOBS_NODE = env.bool('JOBS_NODE', default=False)
CELERY_NODE = env.bool('CELERY_NODE', default=False)

# GTC Token Distribution
GTC_DIST_API_URL = env('GTC_DIST_API_URL', default='http://localhost:8000/not-valid-url')
GTC_DIST_KEY = env('GTC_DIST_KEY', default='')

# BUNDLE settings
# Generating a checksun is optional. When egenerating the static files for a container build
# we do not want to add a checksum
BUNDLE_USE_CHECKSUM = env('BUNDLE_USE_CHECKSUM', default=True)

# Datadog token for UI logging
DATADOG_TOKEN = env('DATADOG_TOKEN', default=None)
