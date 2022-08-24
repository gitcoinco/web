import os

from django.apps import AppConfig, apps
from django.conf import settings

import environ
import sentry_sdk
from celery import Celery
from celery.signals import setup_logging
from sentry_sdk.integrations.celery import CeleryIntegration

env = environ.Env(DEBUG=(bool, False), )  # set default values and casting
# Sentry
SENTRY_DSN = env.str('SENTRY_DSN', default='')
SENTRY_JS_DSN = env.str('SENTRY_JS_DSN', default=SENTRY_DSN)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_JS_DSN,
        integrations=[CeleryIntegration()]
    )

class CeleryConfig(AppConfig):
    name = 'taskapp'
    verbose_name = 'Celery Config'

    # Use Django logging instead of celery logger
    @setup_logging.connect
    def on_celery_setup_logging(**kwargs):
        pass

    def ready(self):
        # Using a string here means the worker will not have to
        app.config_from_object('django.conf:settings', namespace='CELERY')
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)
        app.conf.task_routes = {ele[0]: ele[1] for ele in settings.CELERY_ROUTES}
        app.conf.task_default_queue = 'default'
