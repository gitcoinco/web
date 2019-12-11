# -*- coding: utf-8 -*-
"""Define the Avatar views.

Copyright (C) 2018 Gitcoin Core

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
import xml.etree.ElementTree as ET

from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from avatar.helpers import add_rgb_array, hex_to_rgb_array, rgb_array_to_hex, sub_rgb_array
from dashboard.utils import create_user_action
from PIL import Image, ImageOps

from .models import BaseAvatar, CustomAvatar, SocialAvatar

logger = logging.getLogger(__name__)
avatar_3d_base_path = 'assets/v2/images/avatar3d/avatar.svg'

preview_viewbox = {
    'background': '0 0 350 350',
    'clothing': '60 80 260 300',
    'ears': '100 70 50 50',
    'head': '80 10 170 170',
    'mouth': '130 90 70 70',
    'nose': '140 80 50 50',
    'eyes': '120 40 80 80',
    'hair': '110 0 110 110',
}

skin_tones = [
    'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031', '593D26', '392D16'
]
hair_tones = ['000000', '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C']
tone_maps = ['skin', 'blonde_hair', 'brown_hair', 'brown_hair2', 'dark_hair', 'grey_hair']


def get_avatar_tone_map(tone='skin', skinTone=''):
    tones = {
        'D68876': 0,
        'BC8269': 0,
        'EEE3C1': 0,
        'FFCAA6': 0,
        'D68876': 0,
        'FFDBC2': 0,
        'F4B990': 0,  #base
    }
    base_3d_tone = 'F4B990'
    if tone == 'blonde_hair':
        tones = {'CEA578': 0, 'BA7056': 0, 'F4C495': 0, }
        base_3d_tone = 'CEA578'
    if tone == 'brown_hair':
        tones = {'775246': 0, '563532': 0, 'A3766A': 0, }
        base_3d_tone = '775246'
    if tone == 'brown_hair2':
        tones = {'683B38': 0, 'A56860': 0, '7F4C42': 0, }
        base_3d_tone = '683B38'
    if tone == 'dark_hair':
        tones = {
            '4C3D44': 0,
            '422D39': 0,
            '6D5E66': 0,
            '5E4F57': 0,
            '9B8886': 0,
            '896F6B': 0,
            '84767E': 0,
            '422C37': 0,
        }
        base_3d_tone = '6D5E66'
    if tone == 'grey_hair':
        tones = {'7C6761': 0, '5E433D': 0, 'AA8B87': 0, }
        base_3d_tone = '7C6761'

    #mutate_tone
    for key in tones.keys():
        delta = sub_rgb_array(hex_to_rgb_array(key), hex_to_rgb_array(base_3d_tone), False)
        rgb_array = add_rgb_array(delta, hex_to_rgb_array(skinTone), True)
        tones[key] = rgb_array_to_hex(rgb_array)

    return tones


@csrf_exempt
def avatar3d(request):
    """Serve an 3d avatar."""

    #get request
    accept_ids = request.GET.getlist('ids')
    if not accept_ids:
        accept_ids = request.GET.getlist('ids[]')
    skinTone = request.GET.get('skinTone', '')
    hairTone = request.GET.get('hairTone', '')
    viewBox = request.GET.get('viewBox', '')
    height = request.GET.get('height', '')
    width = request.GET.get('width', '')
    scale = request.GET.get('scale', '')
    mode = request.GET.get('mode', '')
    height = height if height else scale
    width = width if width else scale
    force_show_whole_body = request.GET.get('force_show_whole_body', True)
    if mode == 'preview' and len(accept_ids) == 1:
        height = 30
        width = 30
        _type = accept_ids[0].split('_')[0]
        viewBox = preview_viewbox.get(_type, '0 0 600 600')
        force_show_whole_body = False
    else:
        accept_ids.append('frame')

    # setup
    tags = ['{http://www.w3.org/2000/svg}style']
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    prepend = f'''<?xml version="1.0" encoding="utf-8"?>
<svg width="{width}%" height="{height}%" viewBox="{viewBox}" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
'''
    postpend = '''
</svg>
'''

    #ensure at least one per category

    if bool(int(force_show_whole_body)):
        categories = avatar3dids_helper()['by_category']
        for category_name, ids in categories.items():
            has_ids_in_category = any([ele in accept_ids for ele in ids])
            if not has_ids_in_category:
                accept_ids.append(ids[0])

    # asseble response
    with open(avatar_3d_base_path) as file:
        elements = []
        tree = ET.parse(file)
        for item in tree.getroot():
            include_item = item.attrib.get('id') in accept_ids or item.tag in tags
            if include_item:
                elements.append(ET.tostring(item).decode('utf-8'))
        output = prepend + "".join(elements) + postpend
        for _type in tone_maps:
            base_tone = skinTone if 'hair' not in _type else hairTone
            if base_tone:
                for _from, to in get_avatar_tone_map(_type, base_tone).items():
                    output = output.replace(_from, to)
        if request.method == 'POST':
            return save_custom_avatar(request, output)
        response = HttpResponse(output, content_type='image/svg+xml')
    return response


def avatar3dids_helper():
    with open(avatar_3d_base_path) as file:
        tree = ET.parse(file)
        ids = [item.attrib.get('id') for item in tree.getroot()]
        ids = [ele for ele in ids if ele]
        category_list = {ele.split("_")[0]: [] for ele in ids}
        for ele in ids:
            category = ele.split("_")[0]
            category_list[category].append(ele)

        response = {'ids': ids, 'by_category': category_list, }
        return response


def avatar3dids(request):
    """Serve an 3d avatar id list."""
    response = JsonResponse(avatar3dids_helper())
    return response


def save_custom_avatar(request, output):
    """Save the Custom Avatar."""
    response = {'status': 200, 'message': 'Avatar saved'}
    if not request.user.is_authenticated or request.user.is_authenticated and not getattr(
        request.user, 'profile', None
    ):
        return JsonResponse({'status': 405, 'message': 'Authentication required'}, status=405)
    profile = request.user.profile
    payload = dict(request.GET)
    try:
        with transaction.atomic():
            custom_avatar = CustomAvatar.create_3d(profile, payload, output)
            custom_avatar.save()
            profile.activate_avatar(custom_avatar.pk)
            profile.save()
            create_user_action(profile.user, 'updated_avatar', request)
            response['message'] = 'Avatar updated'
    except Exception as e:
        logger.exception(e)
    return JsonResponse(response, status=response['status'])
