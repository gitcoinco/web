from django.template.response import TemplateResponse
from app.utils import get_profile
from kudos.models import KudosTransfer, Token
from .models import Event_ETHDenver2019_Customizing_Kudos
# from dashboard.models import Profile


def ethdenver2019(request):
    """Display the Grant details page."""
    profile = get_profile(request)
    if profile is None:
        return TemplateResponse(request, 'ethdenver2019/notloggedin.html', {})

    i_kudos_item = 0
    kudos_selection = []
    kudos_row = []

    #kudos_select = KudosTransfer.objects.filter(recipient_profile=profile).all()

    kudos_selected = Event_ETHDenver2019_Customizing_Kudos.objects.all()
    for kudos in kudos_selected:
        kudos_obj = { "kudos": kudos.kudos_required, "received": False, "customizing": kudos, "expanded_kudos": vars(kudos.kudos_required)}
        kudos_row.append(kudos_obj)
        i_kudos_item = i_kudos_item + 1
        if i_kudos_item >= 5:
            i_kudos_item = 0
            kudos_selection.append(kudos_row)
            kudos_row = []

    if i_kudos_item > 0:
        kudos_selection.append(kudos_row)

    return TemplateResponse(request, 'ethdenver2019/kudosprogress.html', {"kudos_selection": kudos_selection, "profile": profile})
