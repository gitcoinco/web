# -*- coding: utf-8 -*-
"""Define the Avatar utilities.

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
import os
from io import BytesIO
from secrets import token_hex
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader

import pyvips
import requests
from git.utils import get_user
from PIL import Image, ImageOps
from pyvips.error import Error as VipsError
from svgutils.compose import SVG, Figure, Line

AVATAR_BASE = 'assets/other/avatars/'
COMPONENT_BASE = 'assets/v2/images/avatar/'

logger = logging.getLogger(__name__)


def get_avatar_context():
    return {
        'defaultSkinTone': 'AE7242',
        'defaultHairColor': '000000',
        'defaultClothingColor': 'CCCCCC',
        'defaultBackground': '25E899',
        'optionalSections': ['HairStyle', 'FacialHair', 'Accessories'],
        'sections': [{
            'name': 'Head',
            'title': 'Pick head shape',
            'options': ('0', '1', '2', '3', '4')
        }, {
            'name': 'Eyes',
            'title': 'Pick eyes shape',
            'options': ('0', '1', '2', '3', '4', '5', '6')
        }, {
            'name': 'Nose',
            'title': 'Pick nose shape',
            'options': ('0', '1', '2', '3', '4')
        }, {
            'name': 'Mouth',
            'title': 'Pick mouth shape',
            'options': ('0', '1', '2', '3', '4')
        }, {
            'name': 'Ears',
            'title': 'Pick ears shape',
            'options': ('0', '1', '2', '3')
        },
                     {
                         'name': 'Clothing',
                         'title': 'Pick your clothing',
                         'options': (
                             'cardigan', 'hoodie', 'knitsweater', 'plaid', 'shirt', 'shirtsweater', 'spacecadet',
                             'suit', 'ethlogo', 'cloak', 'robe'
                         )
                     },
                     {
                         'name': 'Hair Style',
                         'title': 'Pick a hairstyle',
                         'options': (['None', '0'], ['None', '1'], ['None', '2'], ['None', '3'], ['None', '4'],
                                     ['5', 'None'], ['6-back', '6-front'], ['7-back', '7-front'], ['8-back', '8-front'],
                                     ['9-back', '9-front'], ['None', '10'])
                     },
                     {
                         'name': 'Facial Hair',
                         'title': 'Pick a facial hair style',
                         'options': (
                             'Mustache-0', 'Mustache-1', 'Mustache-2', 'Mustache-3', 'Beard-0', 'Beard-1', 'Beard-2',
                             'Beard-3'
                         )
                     },
                     {
                         'name': 'Accessories',
                         'title': 'Pick your accessories',
                         'options': (['Glasses-0'], ['Glasses-1'], ['Glasses-2'], ['Glasses-3'], ['Glasses-4'], [
                             'HatShort-backwardscap'
                         ], ['HatShort-ballcap'], ['HatShort-cowboy'], ['HatShort-headphones'],
                                     ['HatShort-shortbeanie'], ['HatShort-tallbeanie'], ['Earring-0'], ['Earring-1'], [
                                         'EarringBack-2', 'Earring-2'
                                     ], ['Earring-3'], ['Earring-4'], ['Masks-jack-o-lantern'], ['Masks-guy-fawkes'],
                                     ['Masks-jack-o-lantern-lighted'], ['Extras-Parrot'], ['Masks-gitcoinbot'])
                     },
                     {
                         'name': 'Background',
                         'title': 'Pick a background color',
                         'options': (
                             '25E899', '9AB730', '00A55E', '3FCDFF', '3E00FF', '8E2ABE', 'D0021B', 'F9006C', 'FFCE08',
                             'F8E71C', '15003E', 'FFFFFF'
                         )
                     }],
    }


def get_upload_filename(instance, filename):
    salt = token_hex(16)
    file_path = os.path.basename(filename)
    return f"avatars/{getattr(instance, '_path', '')}/{salt}/{file_path}"


def get_svg_templates():
    """Get the SVG templates for all avatar categories."""
    template_data = {
        'accessories': {
            'earring': [],
            'glasses': [],
            'hat': [],
            'masks': [],
            'extras': [],
        },
        'clothing': [],
        'ears': [],
        'eyes': [],
        'facial_hair': {
            'beard': [],
            'mustache': []
        },
        'hair': [],
        'head': [],
        'mouth': [],
        'nose': [],
    }

    for category in template_data:
        path = f'avatar/templates/{category}'
        template_list = os.listdir(path)

        if isinstance(template_data[category], dict):
            for item in template_data[category]:
                inner_path = f'{path}/{item}'
                template_data[category][item] = os.listdir(inner_path)
        else:
            template_data[category] = template_list
    return template_data


def get_svg_template(category, item, primary_color, secondary_color=''):
    context = {'primary_color': primary_color}
    if secondary_color:
        context['secondary_color'] = secondary_color
    category = category.lower()
    item = item.lower()
    component_template = loader.get_template(f'{category}/{item}.txt')
    return component_template.render(context)


def build_avatar_component(path, icon_size=None, avatar_size=None):
    icon_size = icon_size or (215, 215)
    avatar_component_size = avatar_size or (899.2, 1415.7)
    scale_factor = icon_size[1] / avatar_component_size[1]
    x_to_center = (icon_size[0] / 2) - ((avatar_component_size[0] * scale_factor) / 2)
    svg = SVG(f'{COMPONENT_BASE}{path}').scale(scale_factor).move(x_to_center, 0)
    return svg


def build_temporary_avatar_component(
    icon_size=None,
    avatar_size=None,
    primary_color='#18C708',
    secondary_color='#FFF',
    component_type='cardigan',
    component_category='clothing'
):
    icon_size = icon_size or (215, 215)
    avatar_component_size = avatar_size or (899.2, 1415.7)
    scale_factor = icon_size[1] / avatar_component_size[1]
    x_to_center = (icon_size[0] / 2) - ((avatar_component_size[0] * scale_factor) / 2)
    payload = {
        'category': component_category,
        'item': component_type,
        'primary_color': primary_color,
        'secondary_color': secondary_color
    }
    with NamedTemporaryFile(mode='w+') as tmp:
        svg_data = get_svg_template(**payload)
        tmp.write(str(svg_data))
        tmp.seek(0)
        svg = SVG(tmp.name).scale(scale_factor).move(x_to_center, 0)
    return svg


def build_avatar_svg(svg_path='avatar.svg', line_color='#781623', icon_size=None, payload=None, temp=False):
    icon_size = icon_size or (215, 215)
    icon_width = icon_size[0]
    icon_height = icon_size[1]

    if payload is None:
        # Sample payload
        payload = {
            'background_color': line_color,
            'icon_size': (215, 215),
            'avatar_size': None,
            'skin_tone': '#3F2918',
            'ears': {
                'item_type': '0',
            },
            'clothing': {
                'primary_color': '#18C708',
                'item_type': 'cardigan',
            },
            'head': {
                'item_type': '0',
            },
            'hair': {
                'primary_color': '#29F998',
                'item_type': '0',
            },
            'mouth': '0',
            'nose': '0',
            'eyes': '0',
        }

    # Build the list of avatar components
    components = [
        icon_width, icon_height,
        Line([(0, icon_height / 2), (icon_width, icon_height / 2)],
             width=f'{icon_height}px',
             color=payload.get('background_color')),
    ]

    customizable_components = ['clothing', 'ears', 'head', 'hair']
    flat_components = ['eyes', 'mouth', 'nose']
    multi_components = ['accessories']

    for component in customizable_components:
        if component in payload:
            primary_color = payload.get(component, {}).get('primary_color') or payload.get('skin_tone')
            components.append(
                build_temporary_avatar_component(
                    component_category=component,
                    component_type=payload.get(component, {}).get('item_type', 'cardigan'),
                    primary_color=primary_color,
                )
            )

    for component in flat_components:
        if component in payload:
            components.append(
                build_avatar_component(f"{component.title()}/{payload.get(component, '0')}.svg", icon_size)
            )

    for component in multi_components:
        if component in payload:
            components.append(build_avatar_component(f"{component.title()}/{payload.get(component)}"))

    final_avatar = Figure(*components)

    if temp:
        return final_avatar
    result_path = f'{COMPONENT_BASE}{svg_path}'
    final_avatar.save(result_path)
    return result_path


def handle_avatar_payload(request):
    """Handle the Avatar payload."""
    avatar_dict = {}
    valid_component_keys = [
        'Beard', 'Clothing', 'Earring', 'EarringBack', 'Ears', 'Eyes', 'Glasses', 'Masks', 'HairLong', 'HairShort',
        'HatLong', 'HatShort', 'Head', 'Mouth', 'Mustache', 'Nose', 'Extras'
    ]
    valid_color_keys = ['Background', 'ClothingColor', 'HairColor', 'SkinTone']
    body = json.loads(request.body)
    for k, v in body.items():
        if v and k in valid_component_keys:
            component_type, svg_asset = v.lstrip(f'{settings.STATIC_URL}v2/images/avatar/').split('/')
            avatar_dict[k] = {'component_type': component_type, 'svg_asset': svg_asset, }
        elif v and k in valid_color_keys:
            avatar_dict[k] = v
    return avatar_dict


def get_avatar(_org_name):
    avatar = None
    filename = f"{_org_name}.png"
    filepath = AVATAR_BASE + filename
    if _org_name == 'gitcoinco':
        filepath = AVATAR_BASE + '../../v2/images/helmet.png'
    try:
        avatar = Image.open(filepath, 'r').convert("RGBA")
    except (IOError, FileNotFoundError):
        remote_user = get_user(_org_name)
        if not remote_user.get('avatar_url', False):
            return JsonResponse({'msg': 'invalid user'}, status=422)
        remote_avatar_url = remote_user['avatar_url']

        r = requests.get(remote_avatar_url, stream=True)
        chunk_size = 20000
        with open(filepath, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)
        avatar = Image.open(filepath, 'r').convert("RGBA")

        # make transparent
        datas = avatar.getdata()

        new_data = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)

        avatar.putdata(new_data)
        avatar.save(filepath, "PNG")
    return filepath


def add_gitcoin_logo_blend(avatar, icon_size):
    # setup
    sub_avatar_size = 50
    sub_avatar_offset = (165, 165)

    # get image for sub avatar
    gitcoin_filepath = get_avatar('gitcoinco')
    gitcoin_avatar = Image.open(gitcoin_filepath, 'r').convert("RGBA")
    gitcoin_avatar = ImageOps.fit(gitcoin_avatar, (sub_avatar_size, sub_avatar_size), Image.ANTIALIAS)

    # build new avatar
    img2 = Image.new("RGBA", icon_size)
    img2.paste(gitcoin_avatar, sub_avatar_offset)

    # blend these two images together
    img = Image.new("RGBA", avatar.size, (255, 255, 255))
    img = Image.alpha_composite(img, avatar)
    img = Image.alpha_composite(img, img2)

    return img


def get_err_response(request, blank_img=False):
    from .views import handle_avatar
    if not blank_img:
        return handle_avatar(request, 'Self')

    could_not_find = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    err_response = HttpResponse(content_type="image/jpeg")
    could_not_find.save(err_response, "PNG")
    return err_response


def get_temp_image_file(url):
    """Fetch an image from a remote URL and hold in temporary IO.

    Args:
        url (str): The remote image URL.

    Returns:
        BytesIO: The temporary BytesIO containing the image.

    """
    temp_io = None
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert('RGBA')
        temp_io = BytesIO()
        img.save(temp_io, format='PNG')
    except Exception as e:
        logger.error(e)
    return temp_io


def get_github_avatar(handle):
    """Pull the latest avatar from Github and store in Avatar.png.

    Returns:
        bool: Whether or not the Github avatar was updated.

    """
    remote_user = get_user(handle)
    avatar_url = remote_user.get('avatar_url')
    if not avatar_url:
        return False

    temp_avatar = get_temp_image_file(avatar_url)
    if not temp_avatar:
        return False

    return temp_avatar


def convert_img(obj, input_fmt='svg', output_fmt='png'):
    """Convert the provided buffer to another format.

    Args:
        obj (File): The File/ContentFile object.
        input_fmt (str): The input format. Defaults to: svg.
        output_fmt (str): The output format. Defaults to: png.

    Exceptions:
        Exception: Cowardly catch blanket exceptions here, log it, and return None.

    Returns:
        BytesIO: The BytesIO stream containing the converted File data.
        None: If there is an exception, the method returns None.

    """
    try:
        obj_data = obj.read()
        if obj_data:
            image = pyvips.Image.new_from_buffer(obj_data, f'.{input_fmt}')
            return BytesIO(image.write_to_buffer(f'.{output_fmt}'))
    except VipsError:
        pass
    except Exception as e:
        logger.error(e)
    return None
