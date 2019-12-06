import shlex
import subprocess

from django.core.management.base import BaseCommand
from django.utils import autoreload


def restart_celery():
    kill_worker_cmd = 'pkill -9 celery'
    subprocess.call(shlex.split(kill_worker_cmd))
    start_worker_cmd = 'celery -A taskapp worker -l INFO'
    subprocess.call(shlex.split(start_worker_cmd))


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('Starting celery worker with autoreload...')
        autoreload.run_with_reloader(restart_celery)
