from django.shortcuts import render
from django.template.response import TemplateResponse
from django.http import Http404, JsonResponse
from quests.models import Quest, QuestAttempt
from django.shortcuts import redirect
from django.db.models import Count
import re
import json

# Create your views here.
def index(request):
    quests = [(ele.is_unlocked_for(request.user), ele.is_beaten(request.user), ele) for ele in Quest.objects.all()]
    leaderboard = QuestAttempt.objects.filter(success=True).order_by('profile').values_list('profile__handle').annotate(amount=Count('quest', distinct=True)).order_by('-amount')
    params = {
        'quests': quests,
        'leaderboard': leaderboard,
        'title': 'Quests on Gitcoin',
        'card_desc': 'Use Gitcoin to learn about the Ethereum ecosystem and level up while you do it!',
    }
    return TemplateResponse(request, 'quests/index.html', params)

def details(request, obj_id, name):

    if not request.user.is_authenticated and request.GET.get('login'):
        return redirect('/login/github?next=' + request.get_full_path())

    """Render the Kudos 'detail' page."""
    if not re.match(r'\d+', obj_id):
        raise ValueError(f'Invalid obj_id found.  ID is not a number:  {obj_id}')

    try:
        quest = Quest.objects.get(pk=obj_id)
        if not quest.is_unlocked_for(request.user):
            raise Http404
    except:
        raise Http404

    params = {
        'quest': quest,
        'title': quest.title,
        'card_desc': quest.description,
        'quest_json': quest.to_json_dict(),
    }
    return TemplateResponse(request, 'quests/quest.html', params)
