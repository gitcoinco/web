import os

import django

from pydocmd.loader import PythonLoader


class DjangoPythonLoader(PythonLoader):

    def __init__(self, config):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'app.settings')
        django.setup()
        self.config = config
