from django.shortcuts import render
from django.template.response import TemplateResponse
import json
from django.http import Http404
from governance.models import Game

# Create your views here.
def index(request, slug):

    try:
        game = Game.objects.get(slug=slug)
    except Exception as e:
        raise e
        return Http404

    game_config = game.to_game_config(request.user.profile)

    params = {
        "game_config_json": json.dumps(game_config),
        "game_config": game_config,
        'game': game,
    }
    response =  TemplateResponse(request, 'governance/games/diplomacy.html', params)
    return response
