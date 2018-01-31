# -*- coding: utf-8 -*-
"""Define the custom static storage to surpress bad URL references."""
from whitenoise.storage import CompressedManifestStaticFilesStorage


class SilentFileStorage(CompressedManifestStaticFilesStorage):
    """Define the static storage using whitenoise with hashing.

    If Django cannot find a referenced url in an asset, it will silently pass.

    """

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
