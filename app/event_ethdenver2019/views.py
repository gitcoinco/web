from django.template.response import TemplateResponse
from app.utils import get_profile
from kudos.models import KudosTransfer
from .models import Event_ETHDenver2019_Customizing_Kudos
# from dashboard.models import Profile

def ethdenver2019_redeem(request):
    profile = get_profile(request)
    if profile is None:
        return TemplateResponse(request, 'ethdenver2019/notloggedin.html', {})

    kudos_select = KudosTransfer.objects.filter(recipient_profile=profile).all()

    all_kudos_collected = True
    kudos_selection = []
    kudos_row = []
    kudos_selected = Event_ETHDenver2019_Customizing_Kudos.objects.filter(active=True).all()

    for kudos in kudos_selected:
        recv = kudos_select.filter(kudos_token_cloned_from=kudos.kudos_required).last()
        if recv is None:
            all_kudos_collected = False

    page_ctx = {
        "profile": profile
        }
    if all_kudos_collected:
        page_ctx['success'] = True
    else:
        page_ctx['success'] = False


    return TemplateResponse(request, 'ethdenver2019/redeem.html', page_ctx)

def ethdenver2019(request):
    profile = get_profile(request)
    if profile is None:
        return TemplateResponse(request, 'ethdenver2019/notloggedin.html', {})

    kudos_select = KudosTransfer.objects.filter(recipient_profile=profile).all()

    i_kudos_item = 0
    kudos_selection = []
    kudos_row = []
    kudos_selected = Event_ETHDenver2019_Customizing_Kudos.objects.filter(active=True).all()

    for kudos in kudos_selected:
        kudos_obj = {
            "kudos": kudos.kudos_required,
            "received": False,
            "customizing": kudos,
            # "expanded_kudos": vars(kudos.kudos_required)
        }
        recv = kudos_select.filter(kudos_token_cloned_from=kudos.kudos_required).last()
        if recv:
            kudos_obj['received'] = True

        kudos_row.append(kudos_obj)
        i_kudos_item = i_kudos_item + 1
        if i_kudos_item >= 5:
            i_kudos_item = 0
            kudos_selection.append(kudos_row)
            kudos_row = []

    if i_kudos_item > 0:
        kudos_selection.append(kudos_row)

    page_ctx = {
        "kudos_selection": kudos_selection,
        "profile": profile
        }

    return TemplateResponse(request, 'ethdenver2019/kudosprogress.html', page_ctx)
