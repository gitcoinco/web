from django.conf import settings


def insert_settings(request):
    context = {
        'STATIC_URL': settings.STATIC_URL,
    }
    return context
