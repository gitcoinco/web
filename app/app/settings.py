# -*- coding: utf-8 -*-
"""Define the Gitcoin project settings.

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
import socket

from django.http import Http404

import rollbar

import environ

root = environ.Path(__file__) - 2  # Set the base directory to two levels.
env = environ.Env(DEBUG=(bool, False), )  # set default values and casting
env.read_env(str(root.path('app/.env')))  # reading .env file

DEBUG = env.bool('DEBUG', default=True)
ENV = env('ENV', default='local')
DEBUG_ENVS = env.list('DEBUG_ENVS', default=['local', 'stage', 'test'])
IS_DEBUG_ENV = ENV in DEBUG_ENVS
HOSTNAME = env('HOSTNAME', default=socket.gethostname())
BASE_URL = env('BASE_URL', default='http://localhost:8000/')
SECRET_KEY = env('SECRET_KEY', default='YOUR-SupEr-SecRet-KeY')
ADMINS = (env.tuple('ADMINS', default=('TODO', 'todo@todo.net')))
BASE_DIR = root()

# Ratelimit
RATELIMIT_ENABLE = env.bool('RATELIMIT_ENABLE', default=True)
RATELIMIT_USE_CACHE = env('RATELIMIT_USE_CACHE', default='default')
RATELIMIT_VIEW = env('RATELIMIT_VIEW', default='tdi.views.ratelimited')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['localhost'])

# Notifications - Global on / off switch
ENABLE_NOTIFICATIONS_ON_NETWORK = env(
    'ENABLE_NOTIFICATIONS_ON_NETWORK', default='mainnet')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'app',
    'retail',
    'rest_framework',
    'bootstrap3',
    'marketing',
    'economy',
    'dashboard',
    'faucet',
    'tdi',
    'gas',
    'github',
    'legacy',
    'chartit',
    'email_obfuscator',
    'linkshortener',
    'credits',
    'gitcoinbot',
    'external_bounties',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ratelimit.middleware.RatelimitMiddleware',
    'github.middleware.GithubAuthMiddleware',
]

ROOT_URLCONF = env('ROOT_URLCONF', default='app.urls')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['retail/templates/', 'external_bounties/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context.insert_settings',
            ],
        },
    },
]

SITE_ID = env.int('SITE_ID', default=1)
WSGI_APPLICATION = env('WSGI_APPLICATION', default='app.wsgi.application')

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {'default': env.db()}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend', ),
    'DEFAULT_THROTTLE_CLASSES': ('rest_framework.throttling.AnonRateThrottle', ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',
    },
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': []
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = env('LANGUAGE_CODE', default='en-us')
USE_I18N = env.bool('USE_I18N', default=True)
USE_L10N = env.bool('USE_L10N', default=True)
USE_TZ = env.bool('USE_TZ', default=True)
TIME_ZONE = env.str('TIME_ZONE', default='MST')

if not ENV in ['local', 'test']:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_is_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            },
        },
        'handlers': {
            'rotatingfilehandler': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': '/var/log/django/debug.log',
                'maxBytes': 1024 * 1024 * 10,  # 10 MB
                'backupCount': 100,  # max 100 logs
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'include_html': True,
            }
        },
        'loggers': {
            'django': {
                'handlers': ['rotatingfilehandler', 'mail_admins'],
                'propagate': True,
                'filters': ['require_debug_is_false'],
            },
        },
    }
    LOGGING['loggers']['django.request'] = LOGGING['loggers']['django']
    for ia in INSTALLED_APPS:
        LOGGING['loggers'][ia] = LOGGING['loggers']['django']
else:
    LOGGING = {}

GEOIP_PATH = env('GEOIP_PATH', default='/usr/share/GeoIP/')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATICFILES_STORAGE = env('STATICFILES_STORAGE', default='app.static_storage.SilentFileStorage')
STATICFILES_DIRS = env.tuple('STATICFILES_DIRS', default=('assets/', ))
STATIC_ROOT = root('static')

STATIC_HOST = env('STATIC_HOST', default='')
STATIC_URL = STATIC_HOST + env('STATIC_URL', default='/static/')

CACHES = {'default': env.cache()}

# HTTPS Handling
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=True)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=3600)
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)

CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)
CSRF_COOKIE_HTTPONLY = env.bool('CSRF_COOKIE_HTTPONLY', default=True)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
SECURE_BROWSER_XSS_FILTER = env.bool('SECURE_BROWSER_XSS_FILTER', default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool('SECURE_CONTENT_TYPE_NOSNIFF', default=True)
X_FRAME_OPTIONS = env('X_FRAME_OPTIONS', default='DENY')

# Email Integrations
CONTACT_EMAIL = env('CONTACT_EMAIL', default='TODO')
BCC_EMAIL = env('BCC_EMAIL', default='TODO')
PERSONAL_CONTACT_EMAIL = env('PERSONAL_CONTACT_EMAIL', default='you@foo.bar')
SENDGRID_API_KEY = env('SENDGRID_API_KEY', default='TODO')  # Required to send email.
EMAIL_HOST = env('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='TODO')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='TODO')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
SERVER_EMAIL = env('SERVER_EMAIL', default='server@TODO.co')

# IMAP Settings
IMAP_EMAIL = env('IMAP_EMAIL', default='<email>')
IMAP_PASSWORD = env('IMAP_PASSWORD', default='<password>')

# Mailchimp Integration
MAILCHIMP_USER = env('MAILCHIMP_USER', default='')
MAILCHIMP_API_KEY = env('MAILCHIMP_API_KEY', default='')
MAILCHIMP_LIST_ID = env('MAILCHIMP_LIST_ID', default='')

# Github
GITHUB_API_BASE_URL = env('GITHUB_API_BASE_URL', default='https://api.github.com')
GITHUB_AUTH_BASE_URL = env('GITHUB_AUTH_BASE_URL', default='https://github.com/login/oauth/authorize')
GITHUB_TOKEN_URL = env('GITHUB_TOKEN_URL', default='https://github.com/login/oauth/access_token')
GITHUB_SCOPE = env('GITHUB_SCOPE', default='read:user,user:email,read:org')
GITHUB_CLIENT_ID = env('GITHUB_CLIENT_ID', default='TODO')
GITHUB_CLIENT_SECRET = env('GITHUB_CLIENT_SECRET', default='TODO')
GITHUB_API_USER = env('GITHUB_API_USER', default='TODO')
GITHUB_API_TOKEN = env('GITHUB_API_TOKEN', default='TODO')
GITHUB_APP_NAME = env('GITHUB_APP_NAME', default='gitcoin-local')

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

# Twitter Integration
TWITTER_CONSUMER_KEY = env('TWITTER_CONSUMER_KEY', default='TODO')
TWITTER_CONSUMER_SECRET = env('TWITTER_CONSUMER_SECRET', default='TODO')
TWITTER_ACCESS_TOKEN = env('TWITTER_ACCESS_TOKEN', default='TODO')
TWITTER_ACCESS_SECRET = env('TWITTER_ACCESS_SECRET', default='TODO')
TWITTER_USERNAME = env('TWITTER_USERNAME', default='TODO')

# Slack Integration
# optional: only needed if you slack things
SLACK_TOKEN = env('SLACK_TOKEN', default='TODO')

# Reporting Integrations
MIXPANEL_TOKEN = env('MIXPANEL_TOKEN', default='')

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
    'auth_provider_x509_cert_url': env('GA_AUTH_PROVIDER_X509_CERT_URL',
                                       default='https://www.googleapis.com/oauth2/v1/certs'),
    'client_x509_cert_url': env('GA_CLIENT_X509_CERT_URL', default='')
}

# Rollbar - https://rollbar.com/docs/notifier/pyrollbar/#django
ROLLBAR_CLIENT_TOKEN = env('ROLLBAR_CLIENT_TOKEN', default='')  # post_client_item
ROLLBAR_SERVER_TOKEN = env('ROLLBAR_SERVER_TOKEN', default='')  # post_server_item
if ROLLBAR_SERVER_TOKEN:
    # Handle rollbar initialization.
    ROLLBAR = {
        'access_token': ROLLBAR_SERVER_TOKEN,
        'environment': ENV,
        'root': BASE_DIR,
        'patch_debugview': False,  # Disable debug view patching.
        'branch': 'master',
        'exception_level_filters': [(Http404, 'info')]
    }
    MIDDLEWARE.append('rollbar.contrib.django.middleware.RollbarNotifierMiddleware')
    rollbar.init(**ROLLBAR)

# List of github usernames to not count as comments on an issue
IGNORE_COMMENTS_FROM = ['gitcoinbot', ]

# optional: only needed if you run the activity-report management command
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
S3_REPORT_BUCKET = env('S3_REPORT_BUCKET', default='TODO')
S3_REPORT_PREFIX = env('S3_REPORT_PREFIX', default='TODO')

INSTALLED_APPS += env.list('DEBUG_APPS', default=[])

# Faucet App config
FAUCET_AMOUNT = env.float('FAUCET_AMOUNT', default=.0005)

SENDGRID_EVENT_HOOK_URL = env('SENDGRID_EVENT_HOOK_URL', default='sg_event_process')
GITHUB_EVENT_HOOK_URL = env('GITHUB_EVENT_HOOK_URL', default='github/payload/')

# Web3
WEB3_HTTP_PROVIDER = env('WEB3_HTTP_PROVIDER', default='https://rinkeby.infura.io')

# COLO Coin
COLO_ACCOUNT_ADDRESS = env('COLO_ACCOUNT_ADDRESS', default='')
COLO_ACCOUNT_PRIVATE_KEY = env('COLO_ACCOUNT_PRIVATE_KEY', default='')
