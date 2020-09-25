from django.shortcuts import render
from django.template.response import TemplateResponse
import json

# Create your views here.
def index(request):

    game_config = {
      'room_name': 'testroom',
      'allocation': 100,
      'this_player': request.user.profile.handle,
      'players_to_seats': [
        "ceresstation",
        "vs77bb",
        request.user.profile.handle,
        "connoroday",
      ],
      'gameboard':[
        [1, 1, 4, 5],
        [1, 1, 1, 1],
        [1, 1, 0, 0],
        [1, 1, 1, 1],
      ]
    }

    params = {
        "game_config_json": json.dumps(game_config),
        "game_config": game_config
    }
    response =  TemplateResponse(request, 'governance/games/diplomacy.html', params)
    return response
