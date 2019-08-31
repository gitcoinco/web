import os

from celery import Celery
from celery.signals import setup_logging
from django.apps import AppConfig, apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')


class CeleryConfig(AppConfig):
    name = 'taskapp'
    verbose_name = 'Celery Config'

    # Use Django logging instead of celery logger
    @setup_logging.connect
    def on_celery_setup_logging(**kwargs):
        pass

    def ready(self):
        # Using a string here means the worker will not have to
        # pickle the object when using Windows.
        app.config_from_object('django.conf:settings', namespace='CELERY')
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        print(installed_apps)
        app.autodiscover_tasks(lambda: installed_apps, force=True)
