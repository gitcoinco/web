# -*- coding: utf-8 -*-
"""Define the custom static storage to surpress bad URL references."""
from datetime import datetime

from django.conf import settings

from storages.backends.s3boto3 import S3ManifestStaticStorage, S3StaticStorage


class SilentFileStorage(S3ManifestStaticStorage, S3StaticStorage):
    """Define the static storage using S3 via boto3 with hashing.

    If Django cannot find a referenced url in an asset, it will silently pass.

    """

    location = settings.STATICFILES_LOCATION
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN

    def __init__(self, *args, **kwargs):
        # Init S3StaticStorage and S3ManifestStaticStorage to send assets to S3
        super(SilentFileStorage, self).__init__(*args, **kwargs)

    def exists(self, name):
        """Check if the named file exists in S3 storage"""
        # Check file exists on S3
        exists = super(SilentFileStorage, self).exists(name)
        # This is a hack to get a status report during S3ManifestStaticStorage._postProcess
        print(
            "INFO " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - Checking for matching file hash on S3 - " +
            name + ": " + ("Skipping based on matching file hashes" if exists else "Hashes did not match")
        )
        return exists

    def url(self, name, force=True):
        """Handle catching bad URLs and return the name if route is unavailable."""
        try:
            return super(SilentFileStorage, self).url(name, force=force)
        except Exception:
            return name

    def _url(self, hashed_name_func, name, force=True, hashed_files=None):
        """Handle catching bad URLs and return the name if route is unavailable."""
        try:
            hashed_name = self.stored_name or ''
            return super(SilentFileStorage, self)._url(hashed_name, name, force=force, hashed_files=hashed_files)
        except Exception:
            return name


class MediaFileStorage(S3StaticStorage):
    """Define the media storage backend for user uploaded/stored files."""

    location = settings.MEDIAFILES_LOCATION
    bucket_name = settings.MEDIA_BUCKET
    custom_domain = settings.MEDIA_CUSTOM_DOMAIN

    def __init__(self, *args, **kwargs):
        # Save media to S3 only (we dont need an additional local copy)
        super(MediaFileStorage, self).__init__(*args, **kwargs)
