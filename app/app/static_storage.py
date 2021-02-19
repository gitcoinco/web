# -*- coding: utf-8 -*-
"""Define the custom static storage to surpress bad URL references."""
import os
from os.path import basename
from secrets import token_hex

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.contrib.staticfiles.storage import ManifestFilesMixin, HashedFilesMixin

from storages.backends.s3boto3 import S3Boto3Storage, SpooledTemporaryFile


class SilentFileStorage(ManifestFilesMixin, S3Boto3Storage):
    """Define the static storage using S3 via boto3 with hashing.

    If Django cannot find a referenced url in an asset, it will silently pass.

    """

    location = settings.STATICFILES_LOCATION

    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.AWS_STORAGE_BUCKET_NAME
        kwargs['custom_domain'] = settings.AWS_S3_CUSTOM_DOMAIN
        # Init S3Boto3Storage and ManifestFilesMixin to send assets to S3
        super(SilentFileStorage, self).__init__(*args, **kwargs)
        # Init CompressorFileStorage to save local copies for compressor
        self.local_storage = get_storage_class("compressor.storage.CompressorFileStorage")()
        # Init HashedFilesMixin to get filenames with hashes present
        self.local_hashes = HashedFilesMixin()

    def _save_content(self, obj, content, parameters):
        """Create a clone of the content file to avoid premature closure.

        When this is passed to boto3 it wrongly closes the file upon upload
        where as the storage backend expects it to still be open.

        """
        # Seek our content back to the start
        content.seek(0, os.SEEK_SET)

        # Create a temporary file that will write to disk after a specified size
        content_autoclose = SpooledTemporaryFile()

        # Write our original content into our copy that will be closed by boto3
        content_autoclose.write(content.read())

        # Upload the object which will auto close the content_autoclose instance
        super(SilentFileStorage, self)._save_content(obj, content_autoclose, parameters)

        # Cleanup if this is fixed upstream our duplicate should always close
        if not content_autoclose.closed:
            content_autoclose.close()

    def save(self, name, content):
        # record the clean file content (pre gzip)
        file_content = content.file
        # Save remote copy to S3
        super(SilentFileStorage, self).save(name, content)
        # Only save .scss and .js files locally
        if ".scss" in name or ".js" in name:
            # restore the clean file_content
            content.file = file_content
            # Save a local copy for compressor
            self.local_storage._save(name, content)
            # Save a local copy with hash present
            self.local_storage._save(self.local_hashes.hashed_name(name, content), content)
        return name

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


class MediaFileStorage(S3Boto3Storage):
    """Define the media storage backend for user uploaded/stored files."""

    location = settings.MEDIAFILES_LOCATION

    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.MEDIA_BUCKET
        kwargs['custom_domain'] = settings.MEDIA_CUSTOM_DOMAIN
        # Save media to S3 only (we dont need an additional local copy)
        super(MediaFileStorage, self).__init__(*args, **kwargs)


def get_salted_path(instance, filename):
    return f'assets/{token_hex(16)[:15]}/{basename(filename)}'
