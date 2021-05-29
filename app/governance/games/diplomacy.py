from django.shortcuts import render
from django.template.response import TemplateResponse
import json
from django.http import Http404
from governance.models import Game
from django.shortcuts import redirect
import uuid

# Create your views here.
def diplomacy_idx(request):
    games = Game.objects.all()
    params = {
        'games': games,
    }
    response =  TemplateResponse(request, 'governance/games/diplomacy_idx.html', params)
    return response

# Create your views here.
def create(request):
    title = str(uuid.uuid4())
    game = Game.objects.create(title=title)
    return redirect('/governance/diplomacy/' + game.slug)


def index(request, slug):
    if slug == 'create':
        return create(request)

    try:
        game = Game.objects.get(slug=slug)
    except Exception as e:
        return Http404

    game_config = game.to_game_config(request.user.profile)

    params = {
        "game_config_json": json.dumps(game_config),
        "game_config": game_config,
        'game': game,
    }
    response =  TemplateResponse(request, 'governance/games/diplomacy.html', params)
    return response
