from django.conf import settings


class AvatarError(Exception):
    """Base class for exceptions in the Avatar module."""

    def __init__(self, *args, **kwargs):
        """Initialize the avatar conversion exception with message and args."""

        default_message = 'Avatar error occurred'

        if not (args or kwargs):
            args = (default_message, )

        if settings.DEBUG:
            print(args[0] or default_message)

        super().__init__(*args, **kwargs)


class AvatarConversionError(AvatarError):
    """Handle avatar conversion failures."""

    pass
