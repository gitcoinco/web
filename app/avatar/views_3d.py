# -*- coding: utf-8 -*-
"""Define the Avatar views.

Copyright (C) 2021 Gitcoin Core

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
import logging
import xml.etree.ElementTree as ET

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from avatar.helpers import add_rgb_array, hex_to_rgb_array, rgb_array_to_hex, sub_rgb_array
from dashboard.utils import create_user_action

from .models import AvatarTextOverlayInput, CustomAvatar

logger = logging.getLogger(__name__)


def get_avatar_text_if_any():
    obj = AvatarTextOverlayInput.objects.filter(num_uses_remaining__gt=0, active=True).first()
    if obj:
        obj.num_uses_remaining -= 1
        obj.current_uses += 1
        obj.save()
        return f'<text id="text_injection" opacity="0.3" font-family="Muli" font-size="4" font-weight="normal" fill="#777777"><tspan x="7" y="14">{obj.text}</tspan></text>'
    return ''


def get_avatar_attrs(theme, key):
    avatar_attrs = {
        'bufficorn': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 200 200',
                'facial': '80 180 220 220',
                'glasses': '80 80 220 220',
                'hat': '20 30 300 300',
                'shirt': '130 200 200 200',
                'accessory': '50 180 150 200',
                'horn': '120 80 150 150',
            },
            'skin_tones': [
                'D7723B', 'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031',
                '593D26', '392D16'
            ],
            'hair_tones': [
                'F495A8', '000000', '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC',
                '0ECF7C', 'ca5200'
            ],
            'tone_maps': ['skin', 'blonde_hair', 'brown_hair', 'brown_hair2', 'dark_hair', 'grey_hair'],
            'path': 'assets/v2/images/avatar3d/avatar_bufficorn.svg',
        },
        'unisex': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'clothing': '60 80 260 300',
                'ears': '100 70 50 50',
                'head': '80 10 170 170',
                'mouth': '130 90 70 70',
                'nose': '140 80 50 50',
                'eyes': '120 40 80 80',
                'hair': '110 0 110 110',
            },
            'skin_tones': [
                'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031', '593D26',
                '392D16'
            ],
            'hair_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000',
                'ca5200'
            ],
            'tone_maps': ['skin', 'blonde_hair', 'brown_hair', 'brown_hair2', 'dark_hair', 'grey_hair', 'mage_skin'],
            'path': 'assets/v2/images/avatar3d/avatar.svg',
        },
        'female': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'body': '60 80 220 220',
                'ears': '100 70 50 50',
                'head': '80 10 170 170',
                'mouth': '130 90 70 70',
                'nose': '130 80 30 30',
                'lips': '120 80 50 50',
                'eyes': '110 40 70 70',
                'hair': '90 0 110 110',
                'accessories': '100 50 100 100',
            },
            'skin_tones': [
                'FFCAA6', 'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031',
                '593D26', '392D16'
            ],
            'hair_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000',
                'ca5200'
            ],
            'tone_maps': ['skin', 'blonde_hair', 'brown_hair', 'brown_hair2', 'dark_hair', 'grey_hair'],
            'path': 'assets/v2/images/avatar3d/avatar_female.svg',
        },
        'bot': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'arms': '50 50 300 300',
                'body': '60 80 220 220',
                'ears': '100 70 50 50',
                'head': '80 10 170 170',
                'mouth': '130 90 70 70',
                'nose': '130 80 30 30',
                'lips': '120 80 50 50',
                'eyes': '120 50 90 90',
                'accessories': '100 50 100 100',
            },
            'skin_tones': [],
            'hair_tones': [],
            'tone_maps': [''],
            'path': 'assets/v2/images/avatar3d/bot_avatar.svg',
        },
        'comic': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'back': '100 100 200 200',
                'legs': '150 200 120 120',
                'torso': '100 120 180 180',
                'arm': '100 130 200 200',
                'head': '20 20 250 250',
            },
            'skin_tones': [
                'FFCAA6', 'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031',
                '593D26', '392D16'
            ],
            'hair_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000',
                'ca5200'
            ],
            'background_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000'
            ],
            'tone_maps': ['comic', 'comic_hair', 'comic_background'],
            'path': 'assets/v2/images/avatar3d/comic.svg',
        },
        'flat': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'avatar': '0 0 350 350',
            },
            'skin_tones': [
                'FFCAA6', 'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031',
                '593D26', '392D16'
            ],
            'hair_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000',
                'ca5200'
            ],
            'background_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000'
            ],
            'tone_maps': ['flat_skin', 'flat_hair', 'flat_background'],
            'path': 'assets/v2/images/avatar3d/flat.svg',
        },
        'shiny': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'avatar': '0 0 350 350',
            },
            'skin_tones': [
                'FFCAA6', 'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031',
                '593D26', '392D16'
            ],
            'hair_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000',
                'ca5200'
            ],
            'background_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000'
            ],
            'tone_maps': ['shiny_skin', 'shiny_hair', 'flat_background'],
            'path': 'assets/v2/images/avatar3d/shiny.svg',
        },
        'people': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'avatar': '0 0 350 350',
            },
            'skin_tones': [
                'FFCAA6', 'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031',
                '593D26', '392D16'
            ],
            'hair_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000',
                'ca5200'
            ],
            'background_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000'
            ],
            'tone_maps': ['people_skin', 'people_hair', 'flat_background'],
            'path': 'assets/v2/images/avatar3d/people.svg',
        },
        'robot': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'avatar': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'background_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000'
            ],
            'tone_maps': ['flat_background'],
            'path': 'assets/v2/images/avatar3d/robot.svg',
        },
        'technology': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'avatar': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'background_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000',
                'ca5200'
            ],
            'tone_maps': ['flat_background'],
            'path': 'assets/v2/images/avatar3d/tech.svg',
        },
        'landscape': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'avatar': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'background_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000',
                'ca5200'
            ],
            'tone_maps': ['flat_background'],
            'path': 'assets/v2/images/avatar3d/landscape.svg',
        },
        'space': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'avatar': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'background_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000',
                'ca5200'
            ],
            'tone_maps': ['flat_background'],
            'path': 'assets/v2/images/avatar3d/space.svg',
        },
        'spring': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'avatar': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'background_tones': [
                '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C', '000000',
                'ca5200'
            ],
            'tone_maps': ['flat_background'],
            'path': 'assets/v2/images/avatar3d/spring.svg',
        },
        'masks': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'avatar': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'background_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/masks.svg',
        },
        'metacartel': {
            'preview_viewbox': {
                #section: x_pos y_pox x_size y_size
                'background': '0 0 350 350',
                'tatoos': '150 170 100 100',
                'eyes': '100 150 120 120',
                'eyebrows': '110 130 100 100',
                'mouth': '130 220 100 100',
                'hat': '20 0 250 250',
                'accessory': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [
                'ED495F', '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC', '0ECF7C',
                '000000'
            ],
            'tone_maps': ['metacartel_skin'],
            'path': 'assets/v2/images/avatar3d/metacartel.svg',
        },
        'jedi': {
            'preview_viewbox': {
                'background': '0 0 350 350',
                'clothes': '0 0 350 350',
                'facial': '100 80 100 100',
                'hair': '0 0 150 150',
                'eyebrows': '100 50 100 100',
                'accessory': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/jedi.svg',
        },
        'protoss': {
            'preview_viewbox': {
                'background': '0 0 350 350',
                'clothing': '0 120 200 200',
                'mouth': '100 200 200 200',
                'accessory': '100 0 200 200',
                'eyes': '80 50 200 200',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/protoss.svg',
        },
        'mage': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/mage.svg',
        },
        'powerrangers': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/powerrangers.svg',
        },
        'orc_gitcoin': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/orc_gitcoin.svg',
        },
        'terran': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'hair_tones': [],
            'skin_tones': ['FFFFFF', 'EEEEEE', 'DDDDDD', 'CCCCCC', 'E1C699', 'CFB997', 'F5F5DC', 'B3983', 'AAA9AD'],
            'tone_maps': ['terran_skin'],
            'path': 'assets/v2/images/avatar3d/terran.svg',
        },
        'zerg': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/zerg.svg',
        },
        'egypt': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/egypt.svg',
        },
        'lego': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/lego.svg',
        },
        'PixelBot': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/PixelBot.svg',
        },
        'iamthembot': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/iamthembot.svg',
        },
        'visible': {
            'preview_viewbox': {
                'back': '0 0 350 350',
                'eye': '120 40 70 70',
                'accessoire': '0 0 350 350',
                'body': '0 0 250 250',
            },
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/visible.svg',
        },
        'curly': {
            'preview_viewbox': {
                'back': '0 0 350 350',
                'skin': '0 0 250 250',
                'accessory': '220 200 100 100',
                'mouth': '90 150 100 100',
                'eyes': '140 140 50 50',
                'clothes': '0 150 250 250',
                'hair': '50 50 250 250',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/curly.svg',
        },
        'walle': {
            'preview_viewbox': {
                'background': '0 0 350 350',
                'tyres': '0 200 250 250',
                'accessory': '0 0 200 200',
                'cap': '100 0 150 150',
                'goggles': '100 0 150 150',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/walle.svg',
        },
        'megaman': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/megaman.svg',
        },
        'walle2': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/walle2.svg',
        },
        'walle3': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/walle3.svg',
        },
        'chappie': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/chappie.svg',
        },
        'chappie2': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/chappie2.svg',
        },
        'megaman2': {
            'preview_viewbox': {
                'Background': '0 0 350 350',
                'Arms': '50 50 250 250',
                'Ears': '80 30 100 100',
                'Mouth': '100 50 100 100',
                'Eyes': '100 50 150 150',
                'Accessory': '50 50 250 250',
            },
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/Mega2.svg',
        },
        'moloch': {
            'preview_viewbox': {
                'Background': '0 0 350 350',
                'fog': '0 0 350 350',
                'face': '0 0 350 350',
                'shoulder': '0 0 350 350',
                'horn': '0 0 350 350',
                'mid': '0 0 350 350',
                'leg': '0 0 350 350',
                'hand': '0 0 350 350',
            },
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/Moloch111.svg',
        },
        'ethbot': {
            'preview_viewbox': {
                'Background': '0 0 350 350',
                'fog': '0 0 350 350',
                'face': '0 0 350 350',
                'shoulder': '0 0 350 350',
                'horn': '0 0 350 350',
                'mid': '0 0 350 350',
                'leg': '0 0 350 350',
                'hand': '0 0 350 350',
            },
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/ETHbot.svg',
        },
        'starbot': {
            'preview_viewbox': {
                'Head': '50 20 250 250',
                'Backdrop': '0 0 350 350',
                'Accents': '0 100 250 250',
            },
            'hair_tones': [],
            'skin_tones': ['FFFFFF', 'EEEEEE', 'DDDDDD', 'CCCCCC', 'E1C699', 'CFB997', 'F5F5DC', 'B3983', 'AAA9AD'],
            'tone_maps': ['starbot_skin'],
            'path': 'assets/v2/images/avatar3d/starbot.svg',
        },
        'robocop': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/robocop.svg',
        },
        'wookie': {
            'preview_viewbox': {
                'Background': '0 0 350 350',
                'Eyes': '50 100 200 200',
                'Glasses': '50 50 200 200',
                'Headphone': '0 0 200 200',
                'Hat': '50 0 200 200',
                'Nose': '50 100 150 150',
                'Mouth': '90 140 130 130',
            },
            'skin_tones': [
                'AE7343', 'FFCAA6', 'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B',
                '715031', '593D26', '392D16', 'FFFF99'
            ],
            'hair_tones': [],
            'tone_maps': ['wookie_skin'],
            'path': 'assets/v2/images/avatar3d/wookie.svg',
        },
        'wolverine': {
            'preview_viewbox': {
                'background': '0 0 350 350',
                'Mouth': '90 140 130 130',
                'Eye': '50 100 200 200',
                'Mask': '0 0 300 300',
                'Mouth': '90 190 130 130',
                'Clothing': '0 150 250 250',
            },
            'skin_tones': [
                'ECE3C1', 'FFCAA6', 'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B',
                '715031', '593D26', '392D16', 'FFFF99'
            ],
            'hair_tones': [],
            'tone_maps': ['wolverine_skin'],
            'path': 'assets/v2/images/avatar3d/wolverine.svg',
        },
        'cartoon_jedi': {
            'preview_viewbox': {
                'background': '0 0 350 350',
                'face': '120 100 100 100',
                'clothes': '50 150 200 200',
                'hair': '100 50 200 201',
                'helmet': '100 50 200 200',
                'accessory': '0 50 200 200',
                'legs': '120 250 100 100',
            },
            'skin_tones': [
                'FFCAA6', 'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031',
                '593D26', '392D16', 'FFFF99'
            ],
            'hair_tones': [
                'F495A8', '000000', '4E3521', '8C3B28', 'B28E28', 'F4EA6E', 'F0E6FF', '4D22D2', '8E2ABE', '3596EC',
                '0ECF7C', 'ca5200'
            ],
            'tone_maps': ['cj_skin', 'cj_hair'],
            'path': 'assets/v2/images/avatar3d/cartoon_jedi.svg',
        },
        'square_bot': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'skin_tones': [
                'C3996B', '5F768F', 'ECC55F', 'E08156', 'F3A756', '8EA950', '62ADC9', '60C19D', 'A07AB5', 'ED5599'
            ],
            'hair_tones': [],
            'background_tones': [
                'C3996B', '5F768F', 'ECC55F', 'E08156', 'F3A756', '8EA950', '62ADC9', '60C19D', 'A07AB5', 'ED5599'
            ],
            'tone_maps': ['squarebot_skin', 'squarebot_background'],
            'path': 'assets/v2/images/avatar3d/square_bot.svg',
        },
        'orc': {
            'preview_viewbox': {
                'background': '0 0 350 350',
                'clothes': '0 0 350 350',
                'facial': '100 80 100 100',
                'hair': '0 0 250 250',
                'eyebrows': '120 50 200 200',
                'accessory': '0 0 350 350',
            },
            'skin_tones': [
                'FFCAA6', 'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031',
                '593D26', '392D16', 'FFFF99'
            ],
            'hair_tones': [],
            'tone_maps': ['orc_skin', 'orc_hair'],
            'path': 'assets/v2/images/avatar3d/orc.svg',
        },
        'terminator': {
            'preview_viewbox': {
                'bg': '0 0 350 350',
                'beard': '50 150 200 200',
                'eyes': '90 120 150 150',
                'accessoire': '50 0 200 200',
                'hair': '50 0 250 250',
                't-shirt': '0 200 300 300',
            },
            'skin_tones': [],
            'hair_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/terminator-4.svg',
        },
        'barbarian': {
            'preview_viewbox': {
                'BACK': '0 0 350 350',
                'ACC': '0 50 320 320',
                'BEARD': '80 130 200 200',
                'HAIR': '70 120 200 200',
                'EYE': '100 100 150 150',
                'CASK': '70 0 210 210',
            },
            'skin_tones': [
                'FFCAA6', 'FFFFF6', 'FEF7EB', 'F8D5C2', 'EEE3C1', 'D8BF82', 'D2946B', 'AE7242', '88563B', '715031',
                '593D26', '392D16', 'FFFF99'
            ],
            'hair_tones': [],
            'tone_maps': ['barb_skin'],
            'path': 'assets/v2/images/avatar3d/avatar_barbarian.svg',
        },
        'bender': {
            'preview_viewbox': {
                'background': '0 0 350 350',
                'legs': '30 150 300 300',
                'arms': '0 0 350 350',
                'head': '100 0 150 150',
                'mouth': '130 80 100 100',
                'eyes': '130 50 100 100',
                'body': '0 0 350 350',
                'accessory': '100 100 150 150',
            },
            'skin_tones': [],
            'hair_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/bender.svg',
        },
        'qpix': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/qlands_pix.svg',
        },
        'unicorn': {
            'preview_viewbox': {
                'background': '0 0 350 350',
            },
            'skin_tones': [],
            'hair_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/qlands_unicorn.svg',
        },
        'bendy': {
            'preview_viewbox': {
                'background': '0 0 250 250',
            },
            'skin_tones': [],
            'hair_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/bendy.svg',
        },
        'joker': {
            'preview_viewbox': {
                'background': '0 0 350 350',
                'clothes': '100 100 250 250',
                'facial': '120 70 250 250',
                'hair': '70 30 250 250',
                'accessory': '10 0 250 250',
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': 'assets/v2/images/avatar3d/joker.svg',
        },
    }
    new_avatars = ['SSShiine','avrilapril','eknobl','lkh','nanshulot','wahyu243','zak102','artipedia','azizyano','hasssan04','maystro4','riyasoganii','writeprovidence', 'petushka1', 'merit-tech', 'hamzaghz', 'bruno-tandon', 'KayZou', 'the-hack-god', 'old-monger', 'virtual-face', 'art-maniac', 'vinhbhn', 'masket-bask', 'panigale120']
    for _key in new_avatars:
        avatar_attrs[_key] = {
            'preview_viewbox': {
            },
            'skin_tones': [],
            'hair_tones': [],
            'skin_tones': [],
            'tone_maps': [],
            'path': f'assets/v2/images/avatar3d/{_key}.svg',
        }

    return avatar_attrs.get(theme, {}).get(key, {})


def get_avatar_tone_map(tone='skin', skinTone='', theme='unisex'):
    tones = {
        'D68876': 0,
        'BC8269': 0,
        'EEE3C1': 0,
        'FFCAA6': 0,
        'D68876': 0,
        'FFDBC2': 0,
        'D7723B': 0,  #base
        'F4B990': 0,
        'CCB293': 0,  # base - comic
        'EDCEAE': 0,  # base - flat
        'F3DBC4': 0,  # base - flat
    }
    base_3d_tone = 'F4B990'
    if theme == 'female':
        base_3d_tone = 'FFCAA6'
    if theme == 'comic':
        base_3d_tone = 'CCB293'
    if tone == 'blonde_hair':
        tones = {'F495A8': 0, 'C6526D': 0, 'F4C495': 0, }
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
    if tone == 'comic_hair':
        tones = {'8C6239': 0}
        base_3d_tone = '8C6239'
    if tone == 'comic_background':
        tones = {'9B9B9B': 0}
        base_3d_tone = '9B9B9B'
    if tone == 'flat_background':
        tones = {'A6D9EA': 0}
        base_3d_tone = 'A6D9EA'

    if tone == 'flat_skin':
        tones = {'EDCEAE': 0, 'F3DBC4': 0, 'E4B692': 0, 'F3DBC4': 0, 'EDCEAE': 0, 'F1C9A5': 0, }
        base_3d_tone = 'EDCEAE'
    if tone == 'metacartel_skin':
        tones = {'ED495F': 0, }
    if tone == 'mage_skin':
        tones = {'FFEDD9': 0, }
        base_3d_tone = 'FFEDD9'
    if tone == 'barb_skin':
        tones = {'F7D3C0': 0, }
        base_3d_tone = 'F7D3C0'
    if tone == 'orc_skin':
        tones = {'FFFF99': 0, }
        base_3d_tone = 'FFFF99'
    if tone == 'terran_skin':
        tones = {'FFD9B3': 0, }
        base_3d_tone = 'FFD9B3'
    if tone == 'starbot_skin':
        tones = {'FFFFFF': 0, }
        base_3d_tone = 'FFFFFF'
    if tone == 'wookie_skin':
        tones = {'AE7343': 0, }
        base_3d_tone = 'AE7343'
    if tone == 'wolverine_skin':
        tones = {'ECE3C1': 0, }
        base_3d_tone = 'ECE3C1'
    if tone == 'orc_hair':
        tones = {'010101': 0, }
        base_3d_tone = '010101'

    if tone == 'squarebot_background':
        tones = {'009345': 0, '29B474': 0}
        base_3d_tone = '29B474'
    if tone == 'squarebot_skin':
        tones = {'29B473': 0, }
        base_3d_tone = '29B473'
    if tone == 'cj_hair':
        tones = {'CCA352': 0, }
        base_3d_tone = 'CCA352'
    if tone == 'cj_skin':
        tones = {'D99678': 0, }
        base_3d_tone = 'D99678'
    if tone == 'people_skin':
        tones = {'FFE1B2': 0, 'FFD7A3': 0, }
        base_3d_tone = 'FFE1B2'
    if tone == 'people_hair':
        tones = {'FFD248': 0, '414042': 0, 'A18369': 0, 'E7ECED': 0, '8C6239': 0, '9B8579': 0, '8C6239': 0, }
        base_3d_tone = 'FFD248'
    if tone == 'shiny_skin':
        tones = {'FFD3AE': 0, '333333': 0, 'FFD3AE': 0, 'E8B974': 0, 'EDCEAE': 0, }
        base_3d_tone = 'FFD3AE'
    if tone == 'shiny_hair':
        tones = {'D68D51': 0, 'F7774B': 0, 'E8B974': 0, 'F7B239': 0, 'D3923C': 0, '666666': 0, }
        base_3d_tone = 'D68D51'
    if tone == 'flat_hair':
        tones = {
            '682234': 0,
            '581A2B': 0,
            '10303F': 0,
            '303030': 0,
            '265A68': 0,
            '583A2F': 0,
            'D1874A': 0,
            'E1A98C': 0,
            'D2987B': 0,
            '3C2A20': 0,
            'C64832': 0,
            'B2332D': 0,
            'A0756F': 0,
            '8C6762': 0,
            '471B18': 0,
            '5A3017': 0,
            'EC9A1C': 0,
            '545465': 0,
            '494857': 0,
            '231F20': 0,
            '0F303F': 0,
        }
        base_3d_tone = '8C6239'

    #mutate_tone
    for key in tones.keys():
        delta = sub_rgb_array(hex_to_rgb_array(key), hex_to_rgb_array(base_3d_tone), False)
        rgb_array = add_rgb_array(delta, hex_to_rgb_array(skinTone), True)
        tones[key] = rgb_array_to_hex(rgb_array)
        print(tone, key, tones[key])

    return tones


@csrf_exempt
def avatar3d(request):
    """Serve an 3d avatar."""

    theme = request.GET.get('theme', 'unisex')
    #get request
    accept_ids = request.GET.getlist('ids')
    if not accept_ids:
        accept_ids = request.GET.getlist('ids[]')
    skinTone = request.GET.get('skinTone', '')
    hairTone = request.GET.get('hairTone', '')
    backgroundTone = request.GET.get('backgroundTone', '')
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
        viewBox = get_avatar_attrs(theme, 'preview_viewbox').get(_type, '0 0 600 600')
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
        categories = avatar3dids_helper(theme)['by_category']
        for category_name, ids in categories.items():
            has_ids_in_category = any([ele in accept_ids for ele in ids])
            if not has_ids_in_category:
                accept_ids.append(ids[0])

    # asseble response
    avatar_3d_base_path = get_avatar_attrs(theme, 'path')
    if avatar_3d_base_path:
        with open(avatar_3d_base_path) as file:
            elements = []
            tree = ET.parse(file)
            for item in tree.getroot():
                include_item = item.attrib.get('id') in accept_ids \
                    or item.tag in tags or 'gradient' in item.attrib.get('id', '').lower() \
                    or 'defs' in str(item.tag)
                if include_item:
                    elements.append(ET.tostring(item).decode('utf-8'))
            if request.method == 'POST':
                _ele = get_avatar_text_if_any()
                if _ele:
                    elements.append(_ele)
            output = prepend + "".join(elements) + postpend
            tone_maps = get_avatar_attrs(theme, 'tone_maps')
            for _type in tone_maps:
                base_tone = skinTone
                if 'hair' in _type:
                    base_tone = hairTone
                if 'background' in _type:
                    base_tone = backgroundTone
                if base_tone:
                    for _from, to in get_avatar_tone_map(_type, base_tone, theme).items():
                        output = output.replace(_from, to)
            if request.method == 'POST':
                return save_custom_avatar(request, output)
            response = HttpResponse(output, content_type='image/svg+xml')
    return response


def avatar3dids_helper(theme):
    avatar_3d_base_path = get_avatar_attrs(theme, 'path')
    if avatar_3d_base_path:
        with open(avatar_3d_base_path) as file:
            tree = ET.parse(file)
            ids = [item.attrib.get('id') for item in tree.getroot()]
            ids = [ele for ele in ids if ele and ele != 'base']
            category_list = {ele.split("_")[0]: [] for ele in ids}
            for ele in ids:
                category = ele.split("_")[0]
                category_list[category].append(ele)

            response = {'ids': ids, 'by_category': category_list, }
            return response


def avatar3dids(request):
    """Serve an 3d avatar id list."""

    theme = request.GET.get('theme', 'unisex')
    response = JsonResponse(avatar3dids_helper(theme))
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
            messages.info(
                request,
                f'Your avatar has been updated & will be refreshed when the cache expires (every hour). Or hard refresh (Apple-Shift-R) to view it now.'
            )
            response['message'] = 'Avatar updated'
    except Exception as e:
        logger.exception(e)
    return JsonResponse(response, status=response['status'])
