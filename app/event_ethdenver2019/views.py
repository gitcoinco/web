from django.template.response import TemplateResponse
from app.utils import get_profile
# from dashboard.models import Profile


def ethdenver2019(request):
    """Display the Grant details page."""
    profile = get_profile(request)
    if profile is None:
        return TemplateResponse(request, 'ethdenver2019/notloggedin.html', {})
    return TemplateResponse(request, 'ethdenver2019/notloggedin.html', {})
