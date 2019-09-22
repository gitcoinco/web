from django.shortcuts import render
from django.template.response import TemplateResponse
from django.http import Http404, JsonResponse
from quests.models import Quest
import re
import json

# Create your views here.
def index(request):
    params = {
        'quests': Quest.objects.all(),
        'title': 'Quests on Gitcoin',
        'card_desc': 'Use Gitcoin to learn about the Ethereum ecosystem and level up while you do it!',
    }
    return TemplateResponse(request, 'quests/index.html', params)

def details(request, obj_id, name):

    if not request.user.is_authenticated or request.user.is_authenticated and not getattr(request.user, 'profile', None):
        return redirect('/login/github?next=' + request.get_full_path())

    """Render the Kudos 'detail' page."""
    if not re.match(r'\d+', obj_id):
        raise ValueError(f'Invalid obj_id found.  ID is not a number:  {obj_id}')

    try:
        quest = Quest.objects.get(pk=obj_id)
    except:
        raise Http404

    params = {
        'quest': quest,
        'title': quest.title,
        'card_desc': quest.description,
        'quest_json': quest.to_json_dict(),
    }
    return TemplateResponse(request, 'quests/quest.html', params)
