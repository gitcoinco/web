from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse


def lbcheck(request):
    """Handle returning a 200 response if the app is "basically" operational."""
    return HttpResponse(status=200)


@staff_member_required
def spec(request):
    """Handle returning deployment specific specifications and stats."""
    specs = {'release': settings.RELEASE, 'env': settings.ENV, 'hostname': settings.HOSTNAME}
    return JsonResponse(specs, status=200)
