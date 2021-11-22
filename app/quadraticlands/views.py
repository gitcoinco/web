# -*- coding: utf-8 -*-
"""Define the quadraticlands views.

Copyright (C) 2020 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

import json
import logging

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from dashboard.abi import erc20_abi
from dashboard.utils import get_web3
from eth_account.messages import defunct_hash_message
from quadraticlands.helpers import (
    get_coupon_code, get_FAQ, get_initial_dist, get_initial_dist_breakdown, get_mission_status, get_stewards,
)
from ratelimit.decorators import ratelimit
from web3 import Web3
import bleach

from .models import Game, GameFeed, GamePlayer, create_game_helper

logger = logging.getLogger(__name__)


def index(request):
    '''render template for base index page'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    return TemplateResponse(request, 'quadraticlands/index.html', context)


def base(request, base):
    '''render templates for /quadraticlands/'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    if base == 'faq':
        context.update(get_FAQ(request))
    return TemplateResponse(request, f'quadraticlands/{base}.html', context)


@login_required
def base_auth(request, base):
    '''render templates for /quadraticlands/'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    if base == 'stewards':
        context.update(get_stewards())
    return TemplateResponse(request, f'quadraticlands/{base}.html', context)


@login_required
def mission_index(request):
    '''render quadraticlands/mission/index.html'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    return TemplateResponse(request, 'quadraticlands/mission/index.html', context)


@login_required
def dashboard_index(request):
    '''render quadraticlands/dashboard/index.html'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    return TemplateResponse(request, 'quadraticlands/dashboard/index.html', context)


def workstream_index(request):
    '''Use to render quadraticlands/workstream/index.html'''
    return TemplateResponse(request, 'quadraticlands/workstream/index.html')


def workstream_base(request, stream_name):
    '''Used to render quadraticlands/workstream/<stream_name>.html'''
    return TemplateResponse(request, f'quadraticlands/workstream/{stream_name}.html')


@login_required
def mission_postcard(request):
    '''Used to handle quadraticlands/<mission_name>/<mission_state>/<question_num>'''
    attrs = {
        'front_frame': ['1', '2', '3', '4', '5', '6'],
        'front_background': ['a', 'b', 'c', 'd', 'e'],
        'back_background': ['a', 'b', 'c', 'd', 'e'],
        'color': ['light', 'dark'],
    }
    context = {
        'attrs': attrs,
    }
    return TemplateResponse(request, f'quadraticlands/mission/postcard/postcard.html', context)


@ratelimit(key='ip', rate='4/s', method=ratelimit.UNSAFE, block=True)
def mission_postcard_svg(request):
    import xml.etree.ElementTree as ET

    from django.http import HttpResponse

    width = 100
    height = 100
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    prepend = f'''<?xml version="1.0" encoding="utf-8"?>
<svg width="{width}%" height="{height}%" viewBox="0 0 1400 500" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
'''
    postpend = '''
</svg>
'''

    package = {
        k: bleach.clean(v) for k, v in
        request.GET.dict().items()
    }

    file = 'assets/v2/images/quadraticlands/postcard.svg'
    with open(file) as file:
        elements = []
        tree = ET.parse(file)
        for item in tree.getroot():
            output = ET.tostring(item).decode('utf-8')

            _id = item.attrib.get('id')
            include_item = _id == 'include'
            if _id == 'text':

                # get text
                replace_text = package.get('text')

                # chop up the text by word length to create line breaks.
                line_words_length = int(request.GET.get('line_words_length', 8))
                include_item = True
                end_wrap = '</tspan>'
                words = replace_text.split(' ')
                new_words = []
                line_offset = 0
                line_counter_for_newline_insert = 0
                for i in range(0, len(words)):
                    line_counter_for_newline_insert += 1
                    if words[i] == 'NEWLINE':
                        line_counter_for_newline_insert = 0
                    insert_newline = line_counter_for_newline_insert % line_words_length == 0
                    if words[i] == 'NEWLINE':
                        insert_newline = True
                    if insert_newline:
                        line_offset += 1

                    y = 26 + (line_offset) * 26
                    start_wrap = f'<tspan x="0" y="{y}">'

                    if i == 0:
                        new_words.append(start_wrap)
                    if insert_newline:
                        new_words.append(end_wrap)
                        new_words.append(start_wrap)
                    if words[i] != 'NEWLINE':
                        new_words.append(words[i])
                    if i == (len(words) - 1):
                        new_words.append(end_wrap)

                # actually insert the text
                replace_text = " ".join(new_words)
                output = output.replace('POSTCARD_TEXT_GOES_HERE', replace_text)
                replace_color = '#1a103d' if request.GET.get('color','') == 'light' else '#FFFFFF'
                output = output.replace('POSTCARD_COLOR_GOES_HERE', replace_color)
            if _id:
                val = _id.split(":")[-1]
                key = _id.split(":")[0]
                if val == package.get(key):
                    include_item = True
            if include_item:
                elements.append(output)
        output = prepend + "".join(elements) + postpend

        response = HttpResponse(output, content_type='image/svg+xml')
        return response


@login_required
@ratelimit(key='ip', rate='4/s', method=ratelimit.UNSAFE, block=True)
def mission_lore(request):
    from perftools.models import StaticJsonEnv
    data = StaticJsonEnv.objects.get(key='QL_LORE').data
    MOLOCH_COMIC_LINK = data['MOLOCH_COMIC_LINK']
    QL_SONG_LINK = data['QL_SONG_LINK']
    params = {
        'MOLOCH_COMIC_LINK': MOLOCH_COMIC_LINK,
        'QL_SONG_LINK': QL_SONG_LINK,
    }
    return TemplateResponse(request, f'quadraticlands/mission/lore/index.html', params)


@login_required
@ratelimit(key='ip', rate='4/s', method=ratelimit.UNSAFE, block=True)
def mission_schwag(request):

    context = {
        'coupon_code': get_coupon_code(request)
    }

    return TemplateResponse(request, f'quadraticlands/mission/schwag/index.html', context)


def handler403(request, exception=None):
    return error(request, 403)


def handler404(request, exception=None):
    return error(request, 404)


def handler500(request, exception=None):
    return error(request, 500)


def handler400(request, exception=None):
    return error(request, 400)


def error(request, code):
    context = {
        'code': code,
        'title': "Error {}".format(code)
    }
    return_as_json = 'api' in request.path

    if return_as_json:
        return JsonResponse(context, status=code)
    return TemplateResponse(request, f'quadraticlands/error.html', context, status=code)

@staff_member_required
def mission_diplomacy(request):
    return mission_diplomacy_helper(request)

max_games = 4
max_players_per_game = 16
def mission_diplomacy_helper(request, invited_to_game=None):
    games = []

    # check for what games the user is in
    if request.user.is_authenticated:
        players = GamePlayer.objects.filter(active=True, profile=request.user.profile)
        games = Game.objects.filter(pk__in=players.values_list("game"))

        # handle the creation of a new game.
        if request.POST:
            if games.count() > max_games:
                messages.info(
                    request,
                    f'You are already in the maximum number of games'
                )
            else:
                title = request.POST.get('title', '')
                if not title:
                    messages.info(
                        request,
                        f'Please enter a title'
                    )
                game = create_game_helper(request.user.profile.handle, title)
                messages.success(
                    request,
                    f'Your Game has been created successfully'
                )
                messages.success(
                    request,
                    f'Share this link with ur frens to have them join!'
                )
                return redirect(game.url)
    else:
        if request.POST:
            messages.error(
                request,
                f'You must login to create a game.'
            )



    # return the vite
    params = {
        'title': 'Quadratic Diplomacy',
        'games': games,
        'invite': invited_to_game,
    }
    return TemplateResponse(request, 'quadraticlands/mission/diplomacy/index.html', params)


@login_required
@staff_member_required
def mission_diplomacy_room(request, uuid, name):
    # get the game
    try:
        game = Game.objects.get(uuid=uuid)
    except:
        raise Http404
    return mission_diplomacy_room_helper(request, game)

def mission_diplomacy_room_helper(request, game):

    # handle invites
    users_players = GamePlayer.objects.filter(active=True, profile=request.user.profile)
    users_games = Game.objects.filter(pk__in=users_players.values_list("game"))
    users_player =  users_players.first()
    if game not in users_games:
        if request.user.is_authenticated:

            # too many user condition
            if game.active_players.count() >= max_players_per_game:
                messages.info(
                    request,
                    f'There are already {max_players_per_game} in the game.  Wait for someone to leave + try again.'
                )
                return mission_diplomacy_helper(request)

            # show invite
            if request.GET.get('join'):
                game.add_player(request.user.profile.handle)
            else:
                return mission_diplomacy_helper(request, invited_to_game=game)
        else:
            # logged out condition
            messages.info(
                request,
                f'Please login to join this game.'
            )

    # in game experience
    is_member = game.is_active_player(request.user.profile.handle)
    is_admin = game.players.filter(admin=True, profile=request.user.profile).exists()
    if is_admin:
        if request.GET.get('remove'):
            remove_this_fool = request.GET.get('remove')
            for player in game.players.filter(active=True, profile__handle=remove_this_fool):
                game.remove_player(player.profile.handle)
                messages.info(
                    request,
                    f'{remove_this_fool} has been removed'
                )
    
    # delete game
    if is_member and request.GET.get('delete'):
        game.remove_player(request.user.profile.handle)
        messages.info(
            request,
            f'You have left this game.'
        )
        return redirect('/quadraticlands/mission/diplomacy')

    # chat in game
    if is_member and request.POST.get('chat'):
        game.chat(request.user.profile.handle, request.POST.get('chat'))

    # make a move
    if is_member and request.POST.get('signature'):
        package = request.POST.get('package')
        moves = json.loads(package)
        signature = request.POST.get('signature')
        recipient_address = Web3.toChecksumAddress(moves['account'])
        web3 = get_web3('mainnet')
        gtc = web3.eth.contract(address=Web3.toChecksumAddress('0xde30da39c46104798bb5aa3fe8b9e0e1f348163f'), abi=erc20_abi)
        balance = int((gtc.functions.balanceOf(recipient_address).call()) / (10 ** 18))
        claimed_balance = int(moves['balance'])
        signer_address = Web3.toChecksumAddress(web3.eth.account.recoverHash(defunct_hash_message(text=package), signature=signature))
        claimed_address = Web3.toChecksumAddress(moves['account'])

        if claimed_balance != balance:
            return HttpResponse('not authorized - bad balance', status=401)

        if claimed_address != signer_address:
            return HttpResponse('not authorized - bad addr', status=401)

        data = {
            'moves': moves,
            'signature': signature,
        }
        game.make_move(request.user.profile.handle, data)
        return JsonResponse({'msg':'OK', 'url' : game.url})

    # game view
    params = {
        'title': game.title,
        'users_player': users_player,
        'game': game,
        'is_admin': is_admin,
        'max_players': max_players_per_game,
    }
    return TemplateResponse(request, 'quadraticlands/mission/diplomacy/room.html', params)
