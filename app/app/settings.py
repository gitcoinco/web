'''
    Copyright (C) 2017 Gitcoin Core

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

'''
import socket

import environ


root = environ.Path(__file__) - 2 # Set the base directory to two levels.
env = environ.Env(DEBUG=(bool, False), )  # set default values and casting
env.read_env(str(root.path('app/.env')))  # reading .env file
DEBUG = env.bool('DEBUG', default=True)
ENV = env('ENV', default='local')
HOSTNAME = env('HOSTNAME', default=socket.gethostname())

BASE_URL = env('BASE_URL', default='http://localhost:8000/')
SECRET_KEY = env('SECRET_KEY', default='YOUR-SupEr-SecRet-KeY')
ADMINS = (env.tuple('ADMINS', default=('TODO', 'todo@todo.net')))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = root()

RATELIMIT_ENABLE = env.bool('RATELIMIT_ENABLE', default=True)
RATELIMIT_USE_CACHE = env('RATELIMIT_USE_CACHE', default='default')
RATELIMIT_VIEW = env('RATELIMIT_VIEW', default='tdi.views.ratelimited')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['localhost'])

# Notifications - Global on / off switch
ENABLE_NOTIFICATIONS_ON_NETWORK = env.bool(
    'ENABLE_NOTIFICATIONS_ON_NETWORK', default=False)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
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
    'tdi',
    'gas',
    'chartit',
    'email_obfuscator',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ratelimit.middleware.RatelimitMiddleware',
]

ROOT_URLCONF = env('ROOT_URLCONF', default='app.urls')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['retail/templates/'],
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
DATABASES = {
    'default': env.db(),
}


# Password validation
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
    'DEFAULT_FILTER_BACKENDS':
    ('django_filters.rest_framework.DjangoFilterBackend', ),
    'DEFAULT_THROTTLE_CLASSES':
    ('rest_framework.throttling.AnonRateThrottle', ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',
    },
    'DEFAULT_PERMISSION_CLASSES':
    ['rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'],
    'DEFAULT_AUTHENTICATION_CLASSES': []
}

# Internationalization
LANGUAGE_CODE = env('LANGUAGE_CODE', default='en-us')
USE_I18N = env.bool('USE_I18N', default=True)
USE_L10N = env.bool('USE_L10N', default=True)
USE_TZ = env.bool('USE_TZ', default=True)
TIME_ZONE = env('TIME_ZONE', default='MST')

# Logging
if not ENV == 'local':
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_is_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            },
        },
        'disable_existing_loggers': False,
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

# Handle static assets
STATICFILES_DIRS = env.tuple('STATICFILES_DIRS', default=('assets/', ))
STATIC_ROOT = root('static')
STATIC_URL = env('STATIC_URL', default='/static/')

# Cache
CACHES = {
    'default': env.cache(),
}

# HTTPS Handling
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    'SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=True)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=3600)

# Email Integrations
CONTACT_EMAIL = env('CONTACT_EMAIL', default='TODO')
BCC_EMAIL = env('BCC_EMAIL', default='TODO')
PERSONAL_CONTACT_EMAIL = env('PERSONAL_CONTACT_EMAIL', default='you@foo.bar')
SENDGRID_API_KEY = env(
    'SENDGRID_API_KEY', default='TODO')  # Required to send email.
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

# GETH Integration
# optional:  only if you're syncing web3 (mostly used for bounty flow)
CUSTOM_MAINNET_GETH_HOST = env('CUSTOM_MAINNET_GETH_HOST', default='TODO')
CUSTOM_MAINNET_GETH_PORT = env('CUSTOM_MAINNET_GETH_PORT', default='8545')
CUSTOM_RINKEBY_GETH_HOST = env('CUSTOM_RINKEBY_GETH_HOST', default='TODO')
CUSTOM_RINKEBY_GETH_PORT = env('CUSTOM_RINKEBY_GETH_PORT', default='8545')
CUSTOM_TESTRPC_GETH_HOST = env('CUSTOM_TESTRPC_GETH_HOST', default='localhost')
CUSTOM_TESTRPC_GETH_PORT = env('CUSTOM_TESTRPC_GETH_PORT', default='8545')
# Run `scripts/testrpc.bash` and `scripts/prepTestRPC.bash` from https://github.com/gitcoinco/smart_contracts
TESRPC_CONTRACT_ADDRESS = env('TESRPC_CONTRACT_ADDRESS', default='0x0ed0c2a859e9e576cdff840c51d29b6f8a405bdd')
DEFAULT_NETWORK = env('DEFAULT_NETWORK', default='testrpc')
INFURA_KEY = env('INFURA_KEY', default='TODO')  # Requied only needed if you use infura

# Github Specific
GITHUB_API_BASE_URL = env('GITHUB_API_BASE_URL', default='https://github.com/login/oauth/authorize')
GITHUB_TOKEN_URL = env('GITHUB_TOKEN_URL', default='https://github.com/login/oauth/access_token')
GITHUB_SCOPE = env('GITHUB_SCOPE', default='user')
GITHUB_CLIENT_ID = env('GITHUB_CLIENT_ID', default='TODO')
GITHUB_CLIENT_SECRET = env('GITHUB_CLIENT_SECRET', default='TODO')
GITHUB_API_USER = env('GITHUB_API_USER', default='TODO')
GITHUB_API_TOKEN = env('GITHUB_API_TOKEN', default='TODO')
GITHUB_APP_NAME = env('GITHUB_APP_NAME', default='gitcoin')

# Twitter Integration
TWITTER_CONSUMER_KEY = env('TWITTER_CONSUMER_KEY', default='TODO')
TWITTER_CONSUMER_SECRET = env('TWITTER_CONSUMER_SECRET', default='TODO')
TWITTER_ACCESS_TOKEN = env('TWITTER_ACCESS_TOKEN', default='TODO')
TWITTER_ACCESS_SECRET = env('TWITTER_ACCESS_SECRET', default='TODO')
TWITTER_USERNAME = env('TWITTER_USERNAME', default='TODO')

# Slack Integration
# optional: only needed if you slack things
SLACK_TOKEN = env('SLACK_TOKEN', default='TODO')

# Tracking and Reporting Integrations
TRACKJS_TOKEN = env('TRACKJS_TOKEN', default='')
MIXPANEL_TOKEN = env('MIXPANEL_TOKEN', default='')

# Include additional application settings
INSTALLED_APPS += env.list('DEBUG_APPS', default=[])
