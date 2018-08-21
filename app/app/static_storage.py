# -*- coding: utf-8 -*-
"""Define the custom static storage to surpress bad URL references."""
from os.path import basename
from secrets import token_hex

from django.conf import settings
from django.contrib.staticfiles.storage import ManifestFilesMixin

from storages.backends.s3boto3 import S3Boto3Storage


class SilentFileStorage(ManifestFilesMixin, S3Boto3Storage):
    """Define the static storage using S3 via boto3 with hashing.

    If Django cannot find a referenced url in an asset, it will silently pass.

    """

    location = settings.STATICFILES_LOCATION

    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = settings.AWS_S3_CUSTOM_DOMAIN
        super(SilentFileStorage, self).__init__(*args, **kwargs)

    def url(self, name, **kwargs):
        """Handle catching bad URLs and return the name if route is unavailable."""
        try:
            return super(SilentFileStorage, self).url(name, **kwargs)
        except Exception:
            return name

    def _url(self, hashed_name_func, name, force=False, hashed_files=None):
        """Handle catching bad URLs and return the name if route is unavailable."""
        try:
            hashed_name = self.stored_name or ''
            return super(SilentFileStorage, self)._url(hashed_name, name, force)
        except Exception:
            return name


class MediaFileStorage(S3Boto3Storage):
    """Define the media storage backend for user uploaded/stored files."""

    location = settings.MEDIAFILES_LOCATION

    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = settings.MEDIA_CUSTOM_DOMAIN
        super(MediaFileStorage, self).__init__(*args, **kwargs)


def get_salted_path(instance, filename):
    return f'assets/{token_hex(16)[:15]}/{basename(filename)}'
